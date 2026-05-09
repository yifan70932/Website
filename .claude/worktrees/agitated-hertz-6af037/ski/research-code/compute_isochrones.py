#!/usr/bin/env python3
"""
compute_isochrones.py
=====================

Generate drive-time isochrones for all US ski resorts using OpenRouteService API.

WHY THIS SCRIPT EXISTS
----------------------
Drive-time accessibility is the proper geographic measure of a ski resort's market
reach. Naive distance-buffers (Euclidean circles) systematically over-estimate
accessibility in mountainous terrain — the principal terrain on which ski resorts
are sited. True isochrones, computed against the road network with realistic speed
profiles, are the standard tool in spatial accessibility analysis.

This script calls the OpenRouteService /v2/isochrones/driving-car endpoint for each
resort in us_ski_resorts.json and produces a single GeoJSON FeatureCollection that
can be loaded as an overlay layer in Leaflet.

USAGE
-----
1. Register a free account at https://openrouteservice.org and obtain an API key.
   (Free tier: 2,500 requests/day, 40 req/min — sufficient for this script.)

2. Set the API key as an environment variable, then run:

       export ORS_API_KEY='your-key-here'
       python3 compute_isochrones.py

   Or pass it on the command line:

       python3 compute_isochrones.py --api-key your-key-here

3. The script writes:
       /home/claude/yifanova/ski/research-data/resort_isochrones.geojson

   (or wherever --output points to). This file should be committed alongside
   us_ski_resorts.json and deployed with the site.

REQUEST BUDGET
--------------
With 217 resorts and 3 isochrone bands (60/90/120 min) per request, this is 217
API calls (one call returns all three bands as separate polygons).
At 40 req/min, this takes ~6 minutes wall clock.

OUTPUT FORMAT
-------------
GeoJSON FeatureCollection. Each feature is a single isochrone polygon with
properties:
    {
        "resort_name": "Vail",
        "state": "CO",
        "value": 5400,         # seconds (90 minutes)
        "value_minutes": 90,
        "lat": 39.6403,
        "lon": -106.3742
    }

So for 217 resorts × 3 bands = 651 features in the output file.
Estimated file size: ~500 KB to 2 MB depending on polygon complexity.

DEPENDENCIES
------------
Only the standard library + `requests` (or you can use urllib if you prefer
zero dependencies — see the use_stdlib flag).

REPRODUCIBILITY
---------------
ORS results depend on the underlying OSM road network snapshot. ORS rebuilds this
periodically. For perfect reproducibility you would need to record the ORS version
metadata returned in response headers; this script logs that to stderr.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib import request as urlrequest, error as urlerror

# Default paths
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR.parent / 'research-data' / 'us_ski_resorts.json'
DEFAULT_OUTPUT = SCRIPT_DIR.parent / 'research-data' / 'resort_isochrones.geojson'

# OpenRouteService config
ORS_ENDPOINT = 'https://api.openrouteservice.org/v2/isochrones/driving-car'
RATE_LIMIT_DELAY = 1.6  # seconds between requests; 60/40 = 1.5, +buffer
MAX_RETRIES = 3
ISOCHRONE_RANGES_SEC = [3600, 5400, 7200]  # 60, 90, 120 minutes


def call_ors_isochrone(lon, lat, api_key, ranges_sec):
    """Call OpenRouteService isochrone API for one point. Returns parsed JSON or raises."""
    body = json.dumps({
        'locations': [[lon, lat]],
        'range': ranges_sec,
        'range_type': 'time',
        'attributes': ['area'],
        'smoothing': 5.0,  # mild polygon smoothing; 0..100, lower = more detail
    }).encode('utf-8')

    req = urlrequest.Request(
        ORS_ENDPOINT,
        data=body,
        headers={
            'Accept': 'application/json, application/geo+json',
            'Content-Type': 'application/json',
            'Authorization': api_key,
        },
        method='POST',
    )

    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            with urlrequest.urlopen(req, timeout=30) as resp:
                if attempt == 0:
                    # Log ORS version once at the start
                    server = resp.headers.get('Server', 'unknown')
                    sys.stderr.write(f'  [ORS server: {server}]\n')
                return json.loads(resp.read().decode('utf-8'))
        except urlerror.HTTPError as e:
            last_err = e
            if e.code == 429:
                # Rate limited; back off
                wait = 5 * (attempt + 1)
                sys.stderr.write(f'  [rate limit; sleeping {wait}s]\n')
                time.sleep(wait)
            elif e.code in (500, 502, 503, 504):
                # Transient server error
                wait = 2 * (attempt + 1)
                sys.stderr.write(f'  [server {e.code}; retrying in {wait}s]\n')
                time.sleep(wait)
            else:
                # Hard error (400, 401, 403, etc.) — don't retry
                body = e.read().decode('utf-8', errors='replace')[:300]
                raise RuntimeError(f'ORS HTTP {e.code}: {body}') from e
        except Exception as e:
            last_err = e
            wait = 2 * (attempt + 1)
            sys.stderr.write(f'  [{type(e).__name__}: {e}; retrying in {wait}s]\n')
            time.sleep(wait)
    raise RuntimeError(f'Exceeded {MAX_RETRIES} retries; last error: {last_err}')


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.split('USAGE')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--api-key', default=os.environ.get('ORS_API_KEY'),
                   help='OpenRouteService API key (or set ORS_API_KEY env var)')
    p.add_argument('--input', type=Path, default=DEFAULT_INPUT,
                   help=f'Input resorts JSON (default: {DEFAULT_INPUT})')
    p.add_argument('--output', type=Path, default=DEFAULT_OUTPUT,
                   help=f'Output GeoJSON (default: {DEFAULT_OUTPUT})')
    p.add_argument('--limit', type=int, default=None,
                   help='Process only the first N resorts (for testing)')
    p.add_argument('--resume', action='store_true',
                   help='Skip resorts already present in output file')
    p.add_argument('--ranges', type=int, nargs='+', default=ISOCHRONE_RANGES_SEC,
                   help=f'Isochrone time bands in seconds (default: {ISOCHRONE_RANGES_SEC})')
    return p.parse_args()


def main():
    args = parse_args()

    if not args.api_key:
        sys.stderr.write('ERROR: No API key. Set ORS_API_KEY env var or pass --api-key.\n')
        sys.stderr.write('       Get one free at https://openrouteservice.org/dev/#/signup\n')
        sys.exit(1)

    # Load resorts
    with open(args.input) as f:
        data = json.load(f)
    resorts = data['resorts']
    if args.limit:
        resorts = resorts[:args.limit]

    sys.stderr.write(f'Loaded {len(resorts)} resorts from {args.input}\n')
    sys.stderr.write(f'Isochrone bands: {args.ranges} sec ({[r//60 for r in args.ranges]} min)\n')
    sys.stderr.write(f'Output: {args.output}\n')

    # Resume support: load existing features and skip resorts that have all bands present
    existing_features = []
    completed_names = set()
    if args.resume and args.output.exists():
        try:
            with open(args.output) as f:
                existing = json.load(f)
            existing_features = existing.get('features', [])
            from collections import Counter
            name_counts = Counter(f['properties']['resort_name'] for f in existing_features)
            completed_names = {n for n, c in name_counts.items() if c >= len(args.ranges)}
            sys.stderr.write(f'Resume: {len(completed_names)} resorts already complete in output file\n')
        except Exception as e:
            sys.stderr.write(f'Resume failed ({e}); starting fresh\n')

    out_features = list(existing_features)
    n_done = 0
    n_skipped = 0
    n_failed = 0

    for i, r in enumerate(resorts):
        name = r['name']
        if name in completed_names:
            n_skipped += 1
            continue

        sys.stderr.write(f'[{i+1}/{len(resorts)}] {name} ({r["state"]}) ... ')
        sys.stderr.flush()

        try:
            result = call_ors_isochrone(r['lon'], r['lat'], args.api_key, args.ranges)
            for feat in result.get('features', []):
                value_sec = feat.get('properties', {}).get('value')
                feat['properties'] = {
                    'resort_name': name,
                    'state': r['state'],
                    'region': r['region'],
                    'value': value_sec,
                    'value_minutes': value_sec // 60 if value_sec else None,
                    'lat': r['lat'],
                    'lon': r['lon'],
                    'area_m2': feat.get('properties', {}).get('area'),
                }
                out_features.append(feat)
            n_done += 1
            sys.stderr.write('ok\n')

            # Save incrementally every 10 resorts so a crash doesn't lose progress
            if n_done % 10 == 0:
                save_geojson(out_features, args.output)
                sys.stderr.write(f'  [checkpoint: {len(out_features)} features saved]\n')

        except Exception as e:
            n_failed += 1
            sys.stderr.write(f'FAILED: {e}\n')

        time.sleep(RATE_LIMIT_DELAY)

    # Final save
    save_geojson(out_features, args.output)

    sys.stderr.write('\n=== Summary ===\n')
    sys.stderr.write(f'Resorts processed:    {n_done}\n')
    sys.stderr.write(f'Resorts skipped:      {n_skipped} (resume)\n')
    sys.stderr.write(f'Resorts failed:       {n_failed}\n')
    sys.stderr.write(f'Total features saved: {len(out_features)}\n')
    sys.stderr.write(f'Output written to:    {args.output}\n')
    sys.stderr.write(f'Output size:          {args.output.stat().st_size / 1024:.0f} KB\n')


def save_geojson(features, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump({
            'type': 'FeatureCollection',
            'metadata': {
                'description': 'Drive-time isochrones for US ski resorts, generated via OpenRouteService',
                'generator': 'compute_isochrones.py',
            },
            'features': features,
        }, f, separators=(',', ':'))  # compact format saves space


if __name__ == '__main__':
    main()
