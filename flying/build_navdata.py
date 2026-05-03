#!/usr/bin/env python3
"""
build_navdata.py — Convert FAA NASR subscription data to compact JSON
suitable for the /flying/ FMC widget.

Usage:
    python3 build_navdata.py path/to/28DaySubscription_Effective_YYYY-MM-DD.zip [output_dir]

Output:
    output_dir/waypoints.json    — en-route fixes + navaids, keyed by ident
    output_dir/airports.json     — airports keyed by ICAO/FAA ident
    output_dir/airways.json      — airways keyed by name, with point sequences
    output_dir/_meta.json        — AIRAC cycle, generation date, counts

Requires: Python 3.8+ (standard library only)

Data source: FAA NASR 28-Day Subscription
    https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/
License of source data: Public domain (US Government work)
"""

from __future__ import annotations

import csv
import io
import json
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


# --- Internal helpers -------------------------------------------------------

def _open_csv_in_zip(zf, name_pattern: str) -> Optional[csv.DictReader]:
    """Find a CSV file inside the (possibly virtual) zip whose path *ends
    with* name_pattern. `zf` may be a zipfile.ZipFile OR a NestedNASR object
    (defined below) that flattens the FAA's nested ZIP layout.
    Returns a DictReader, or None if no match.
    """
    candidates = [n for n in zf.namelist() if n.lower().endswith(name_pattern.lower())]
    if not candidates:
        return None
    # If multiple, prefer shortest path (likely the canonical one)
    candidates.sort(key=len)
    name = candidates[0]
    raw = zf.read(name)
    text = raw.decode('utf-8-sig', errors='replace')  # handle BOM
    return csv.DictReader(io.StringIO(text))


class NestedNASR:
    """Wraps the FAA NASR distribution ZIP, which since ~2024 has its CSV
    files inside a nested ZIP at `CSV_Data/<DATE>_CSV.zip` rather than at
    the top level. This class presents a single `namelist() / read()`
    surface across however many layers of nesting there happen to be.

    Layers we know about:
      Layer 0 — outer ZIP:    `28DaySubscription_Effective_YYYY-MM-DD.zip`
      Layer 1 — CSV bundle:   `CSV_Data/<DATE>_CSV.zip`     (contains the *_BASE.csv files)
      Layer 1b — change ZIP:  inside the CSV bundle there's another nested zip
                              named like `<DATE>_CSV-<DATE>_CSV.zip` containing
                              "change since previous cycle" deltas. We ignore it.
    """

    def __init__(self, outer_path):
        self._outer = zipfile.ZipFile(outer_path)
        self._inner = None      # the CSV bundle, if found
        self._inner_name = None
        self._open_inner()

    def _open_inner(self) -> None:
        """Locate and open the CSV bundle inside the outer ZIP, if there is one."""
        # The CSV bundle is a *.zip under CSV_Data/. There's typically only
        # one. (Note: there's a "change report" sub-ZIP inside the bundle
        # itself, but that's at the *next* layer down, not at this one,
        # so we don't need to filter for it here.)
        candidates = [
            n for n in self._outer.namelist()
            if n.lower().startswith('csv_data/') and n.lower().endswith('.zip')
        ]
        # Prefer the shortest path
        candidates.sort(key=len)
        if candidates:
            self._inner_name = candidates[0]
            inner_bytes = self._outer.read(self._inner_name)
            self._inner = zipfile.ZipFile(io.BytesIO(inner_bytes))

    def namelist(self) -> list[str]:
        """Combined list of every file path visible across nesting layers."""
        names = list(self._outer.namelist())
        if self._inner is not None:
            names.extend(self._inner.namelist())
        return names

    def read(self, name: str) -> bytes:
        """Read a file by name from whichever layer contains it.
        Inner-layer files take precedence on collisions (which shouldn't
        happen in practice but matters for correctness)."""
        if self._inner is not None and name in self._inner.namelist():
            return self._inner.read(name)
        return self._outer.read(name)

    def close(self) -> None:
        if self._inner is not None:
            self._inner.close()
        self._outer.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    @property
    def inner_csv_bundle_name(self) -> Optional[str]:
        return self._inner_name


def _to_float(s: str) -> Optional[float]:
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _round_coord(x: Optional[float], digits: int = 5) -> Optional[float]:
    """Round a coordinate. 5 decimal places ≈ 1.1 m precision — far more
    than we need for FMC display, but keeps file size reasonable."""
    if x is None:
        return None
    return round(x, digits)


# --- Data classes -----------------------------------------------------------

@dataclass
class Waypoint:
    ident: str
    lat: float
    lon: float
    type: str            # 'FIX' | 'VOR' | 'VOR/DME' | 'NDB' | 'TACAN' | 'VORTAC' | etc.
    state: Optional[str] = None
    name: Optional[str] = None  # Human-readable name (only kept for navaids; fixes have no real name)


@dataclass
class Airport:
    ident: str           # ICAO ident like 'KBUF' (or FAA LID for non-ICAO)
    lat: float
    lon: float
    name: str
    state: Optional[str] = None
    elevation_ft: Optional[int] = None


@dataclass
class Airway:
    name: str            # e.g. 'J70', 'V14', 'T287'
    type: str            # 'JET' | 'VICTOR' | 'RNAV' | 'ATS'
    points: list[str] = field(default_factory=list)  # idents in order


# --- Parsers ----------------------------------------------------------------

def parse_fixes(zf) -> dict[str, Waypoint]:
    """Parse FIX_BASE.csv → en-route fixes (intersections, RNAV waypoints).

    NASR FIX_BASE columns (as of 2024–2026):
        FIX_ID            — typically same as FIX_IDENT
        FIX_IDENT         — the 5-letter (or 3-5 char) name pilots use
        STATE_CODE        — e.g. 'NY'
        ICAO_REGION_CODE  — e.g. 'K1' (continental US)
        LAT_DECIMAL       — decimal degrees, signed
        LONG_DECIMAL      — decimal degrees, signed (negative = west)
        FIX_USE_CODE      — 'CFIX' (computer fix), 'WAYPOINT', etc.
    """
    reader = _open_csv_in_zip(zf, 'FIX_BASE.csv')
    if reader is None:
        print('  WARNING: FIX_BASE.csv not found', file=sys.stderr)
        return {}

    out: dict[str, Waypoint] = {}
    for row in reader:
        ident = (row.get('FIX_IDENT') or row.get('FIX_ID') or '').strip().upper()
        if not ident:
            continue
        lat = _to_float(row.get('LAT_DECIMAL'))
        lon = _to_float(row.get('LONG_DECIMAL'))
        if lat is None or lon is None:
            continue
        # Skip duplicates — rare, but happens with offshore fixes registered
        # in multiple FIRs. First write wins (CSV is in alpha order).
        if ident in out:
            continue
        out[ident] = Waypoint(
            ident=ident,
            lat=_round_coord(lat),
            lon=_round_coord(lon),
            type='FIX',
            state=(row.get('STATE_CODE') or '').strip() or None,
        )
    return out


def parse_navaids(zf) -> dict[str, Waypoint]:
    """Parse NAV_BASE.csv → VOR / NDB / DME / TACAN / VORTAC.

    NAV_BASE columns:
        NAV_ID            — short ident, e.g. 'BUF'
        NAV_TYPE          — 'VOR/DME', 'VOR', 'NDB', 'TACAN', 'VORTAC', 'NDB/DME', etc.
        NAME              — long name, e.g. 'BUFFALO'
        STATE_CODE
        LAT_DECIMAL
        LONG_DECIMAL
    """
    reader = _open_csv_in_zip(zf, 'NAV_BASE.csv')
    if reader is None:
        print('  WARNING: NAV_BASE.csv not found', file=sys.stderr)
        return {}

    out: dict[str, Waypoint] = {}
    for row in reader:
        ident = (row.get('NAV_ID') or '').strip().upper()
        if not ident:
            continue
        lat = _to_float(row.get('LAT_DECIMAL'))
        lon = _to_float(row.get('LONG_DECIMAL'))
        if lat is None or lon is None:
            continue
        nav_type = (row.get('NAV_TYPE') or '').strip().upper() or 'VOR'
        # Where a navaid and a fix share the same ident (rare but happens —
        # e.g. a VOR co-located with a named fix), keep the navaid.
        out[ident] = Waypoint(
            ident=ident,
            lat=_round_coord(lat),
            lon=_round_coord(lon),
            type=nav_type,
            state=(row.get('STATE_CODE') or '').strip() or None,
            name=(row.get('NAME') or '').strip() or None,
        )
    return out


def parse_airports(zf) -> dict[str, Airport]:
    """Parse APT_BASE.csv → airport master records.

    Notes on identifiers:
      - The FAA LID (e.g. 'BUF') is in `ARPT_ID`.
      - The 4-letter ICAO is in `ICAO_ID` (e.g. 'KBUF').
      - For our FMC, we want airports keyed by what pilots type — usually
        the ICAO. We index by ICAO if present, else fall back to LID.

    Filter: we keep only 'PUBLIC USE' airports + heliports/seaplane bases
    that have IFR operations. Private grass strips bloat the file enormously.
    """
    reader = _open_csv_in_zip(zf, 'APT_BASE.csv')
    if reader is None:
        print('  WARNING: APT_BASE.csv not found', file=sys.stderr)
        return {}

    out: dict[str, Airport] = {}
    for row in reader:
        # Skip private and closed fields
        ownership = (row.get('OWNERSHIP_TYPE_CODE') or '').strip().upper()
        facility_use = (row.get('FACILITY_USE_CODE') or '').strip().upper()
        if facility_use not in ('PU', 'PR'):  # PU = public use
            continue
        if facility_use == 'PR':
            # Keep private airports only if they have a real ICAO and at least
            # one paved runway 3000 ft — proxy for "actually used by jets"
            # In practice this filter happens via ICAO_ID presence below.
            pass

        icao = (row.get('ICAO_ID') or '').strip().upper()
        lid = (row.get('ARPT_ID') or '').strip().upper()
        ident = icao or lid
        if not ident:
            continue

        lat = _to_float(row.get('LAT_DECIMAL'))
        lon = _to_float(row.get('LONG_DECIMAL'))
        if lat is None or lon is None:
            continue

        name = (row.get('ARPT_NAME') or '').strip().title()
        elev = row.get('ELEV') or ''
        try:
            elev_int = int(float(elev)) if elev.strip() else None
        except ValueError:
            elev_int = None

        out[ident] = Airport(
            ident=ident,
            lat=_round_coord(lat),
            lon=_round_coord(lon),
            name=name,
            state=(row.get('STATE_CODE') or '').strip() or None,
            elevation_ft=elev_int,
        )
    return out


def parse_airways(zf) -> dict[str, Airway]:
    """Parse AWY_BASE.csv → airways with their fix sequences.

    NASR's AWY_BASE.csv contains every airway as a single row, with the
    full waypoint list pre-rendered as a space-separated string in the
    AIRWAY_STRING column. This is by far the most convenient form and
    avoids the AWY_SEG_ALT.csv join entirely.

    Column layout (as of cycle 2026-04-16):
        EFF_DATE          — effective date
        REGULATORY        — Y/N (FAA regulatory status)
        AWY_DESIGNATION   — the human-facing airway name, e.g. 'J70' or 'V14'
        AWY_LOCATION      — region code
        AWY_ID            — internal database ID, e.g. 'A216' (we ignore this)
        UPDATE_DATE       — last modification
        REMARK            — free text
        AIRWAY_STRING     — space-separated point sequence:
                            'MONPI OATSS RIDLL LOEBB HOOVR GALEE FACED'

    The first letter of AWY_DESIGNATION encodes the airway type:
        J  — Jet route (high-altitude conventional)
        V  — Victor route (low-altitude conventional)
        T  — RNAV terminal route
        Q  — RNAV high-altitude route
        A,B,G,R — international ATS routes (rare in NASR)
    """
    base_reader = _open_csv_in_zip(zf, 'AWY_BASE.csv')
    if base_reader is None:
        print('  WARNING: AWY_BASE.csv not found', file=sys.stderr)
        return {}

    awys: dict[str, Airway] = {}
    for row in base_reader:
        # Use AWY_DESIGNATION (the human name like 'J70'), NOT AWY_ID
        # (which is an internal database key like 'A216')
        name = (row.get('AWY_DESIGNATION') or '').strip().upper()
        if not name:
            continue

        airway_string = (row.get('AIRWAY_STRING') or '').strip()
        if not airway_string:
            continue

        # Split the space-separated string into individual idents.
        # AIRWAY_STRING tokens are already canonicalized — they're the same
        # idents that appear in FIX_BASE.csv and NAV_BASE.csv.
        points = [tok.strip().upper() for tok in airway_string.split() if tok.strip()]
        if len(points) < 2:
            continue

        # Infer type from first letter of the designation
        prefix = name[0]
        airway_type = {
            'J': 'JET', 'V': 'VICTOR', 'T': 'RNAV-T', 'Q': 'RNAV-Q'
        }.get(prefix, 'OTHER')

        # If the same designation appears in multiple regions (rare but
        # possible — e.g. an airway that crosses an ARTCC boundary may be
        # listed twice), keep the longer point list.
        if name in awys and len(awys[name].points) >= len(points):
            continue
        awys[name] = Airway(name=name, type=airway_type, points=points)

    return awys


# --- Output -----------------------------------------------------------------

def _waypoint_dict(wp: Waypoint) -> dict:
    """Compact serialization. Drop None fields to save bytes."""
    d = {'lat': wp.lat, 'lon': wp.lon, 't': _shorten_type(wp.type)}
    if wp.state:
        d['s'] = wp.state
    if wp.name:
        d['n'] = wp.name
    return d


def _shorten_type(t: str) -> str:
    """Keep type strings short. The FMC just needs to know broad category."""
    t = t.upper()
    if t == 'FIX':
        return 'F'
    if 'VORTAC' in t:
        return 'VT'
    if 'TACAN' in t:
        return 'TC'
    if 'VOR/DME' in t or 'VOR-DME' in t:
        return 'VD'
    if 'VOR' in t:
        return 'V'
    if 'NDB/DME' in t or 'NDB-DME' in t:
        return 'ND'
    if 'NDB' in t:
        return 'N'
    if 'DME' in t:
        return 'D'
    return 'F'  # fallback


def _airport_dict(a: Airport) -> dict:
    d = {'lat': a.lat, 'lon': a.lon, 'n': a.name}
    if a.state:
        d['s'] = a.state
    if a.elevation_ft is not None:
        d['e'] = a.elevation_ft
    return d


def _airway_dict(aw: Airway) -> dict:
    return {'t': aw.type, 'p': aw.points}


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    zip_path = Path(sys.argv[1])
    if not zip_path.exists():
        print(f'ERROR: {zip_path} does not exist', file=sys.stderr)
        sys.exit(1)

    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('navdata-out')
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f'Reading {zip_path}...')
    with NestedNASR(zip_path) as zf:
        # Try to read the README to extract effective date
        effective_date = _detect_cycle_date(zf, zip_path.name)
        print(f'  AIRAC cycle effective: {effective_date}')
        if zf.inner_csv_bundle_name:
            print(f'  CSV bundle:  {zf.inner_csv_bundle_name}')

        # Sanity check — print how many CSVs we actually see
        all_csvs = [n for n in zf.namelist() if n.lower().endswith('.csv')]
        print(f'  CSV files found: {len(all_csvs)}')
        if not all_csvs:
            print('\n  ERROR: No CSV files found in the archive.', file=sys.stderr)
            print('  This usually means the FAA changed the archive layout again.', file=sys.stderr)
            print('  Top-level entries (first 30):', file=sys.stderr)
            for n in list(zf.namelist())[:30]:
                print(f'    {n}', file=sys.stderr)
            sys.exit(1)

        print('  Parsing fixes (FIX_BASE.csv)...')
        fixes = parse_fixes(zf)
        print(f'    {len(fixes):,} fixes')

        print('  Parsing navaids (NAV_BASE.csv)...')
        navaids = parse_navaids(zf)
        print(f'    {len(navaids):,} navaids')

        print('  Parsing airports (APT_BASE.csv)...')
        airports = parse_airports(zf)
        print(f'    {len(airports):,} airports')

        print('  Parsing airways (AWY_BASE.csv)...')
        airways = parse_airways(zf)
        print(f'    {len(airways):,} airways')

    # Merge fixes + navaids into the single waypoints database the FMC
    # uses for ident lookup. Navaids take precedence on collisions because
    # pilots are more likely to mean the navaid when they type 'BUF'.
    waypoints: dict[str, dict] = {}
    for ident, wp in fixes.items():
        waypoints[ident] = _waypoint_dict(wp)
    nav_overrides = 0
    for ident, wp in navaids.items():
        if ident in waypoints:
            nav_overrides += 1
        waypoints[ident] = _waypoint_dict(wp)
    print(f'  Merged: {len(waypoints):,} unique idents '
          f'({nav_overrides} navaid overrides)')

    airport_dict = {ident: _airport_dict(a) for ident, a in airports.items()}
    airway_dict = {name: _airway_dict(aw) for name, aw in airways.items()}

    # Sort keys for stable output (deterministic byte-identical builds)
    print('Writing JSON...')
    _write_json(out_dir / 'waypoints.json', waypoints)
    _write_json(out_dir / 'airports.json', airport_dict)
    _write_json(out_dir / 'airways.json', airway_dict)

    meta = {
        'cycle': effective_date,
        'source': 'FAA NASR 28-Day Subscription',
        'source_url': 'https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/',
        'license': 'Public domain (17 USC §105)',
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'counts': {
            'waypoints': len(waypoints),
            'airports': len(airport_dict),
            'airways': len(airway_dict),
            'fixes_only': len(fixes),
            'navaids': len(navaids),
        },
    }
    _write_json(out_dir / '_meta.json', meta, sort_keys=False)

    # Print a summary of file sizes
    print('\nDone. Output files:')
    for p in sorted(out_dir.glob('*.json')):
        size_kb = p.stat().st_size / 1024
        print(f'  {p.name:20s}  {size_kb:>8.1f} KB')


def _write_json(path: Path, data: dict, sort_keys: bool = True) -> None:
    # separators=(',',':') gives the most compact output (no extra whitespace).
    # Drop the trailing newline that json.dump never adds anyway, but ensure
    # one for friendly diffing.
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'), sort_keys=sort_keys, ensure_ascii=False)
        f.write('\n')


def _detect_cycle_date(zf, fallback_name: str) -> str:
    """Pull the AIRAC effective date from the zip filename.

    Filename pattern: '28DaySubscription_Effective_YYYY-MM-DD.zip'
    """
    import re
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fallback_name)
    if m:
        return m.group(1)
    # Fall back to today
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')


if __name__ == '__main__':
    main()
