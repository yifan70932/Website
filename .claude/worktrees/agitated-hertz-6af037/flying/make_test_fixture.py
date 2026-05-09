#!/usr/bin/env python3
"""
make_test_fixture.py — Build a tiny synthetic NASR-shaped ZIP for testing
build_navdata.py without downloading the real 200 MB subscription.

This generates the **nested** layout the FAA actually ships: an outer ZIP
that contains 'CSV_Data/<DATE>_CSV.zip', which in turn contains the CSV
data files (and a 'change report' sub-zip we ignore).

The CSV schemas here mirror the real FAA columns as documented in the
NASR layout PDFs. Real cycle ZIPs have ~70 CSV files; we synthesize only
the four needed by build_navdata.py.
"""

import zipfile
import io
import csv
from pathlib import Path


def _csv_bytes(rows: list[list]) -> bytes:
    """Render a 2D row list to UTF-8 CSV bytes."""
    buf = io.StringIO()
    w = csv.writer(buf)
    for r in rows:
        w.writerow(r)
    return buf.getvalue().encode('utf-8')


def _build_inner_csv_zip() -> bytes:
    """Build the inner CSV bundle (CSV_Data/16_Apr_2026_CSV.zip equivalent)."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        # FIX_BASE.csv — en-route fixes
        zf.writestr('FIX_BASE.csv', _csv_bytes([
            ['EFF_DATE', 'FIX_ID', 'FIX_IDENT', 'STATE_CODE', 'COUNTRY_CODE',
             'ICAO_REGION_CODE', 'LAT_DECIMAL', 'LONG_DECIMAL',
             'FIX_USE_CODE', 'CHARTING_REMARK'],
            ['02/19/2026', 'BUFFY', 'BUFFY', 'NY', 'US', 'K1', 42.85, -78.50, 'WAYPOINT', ''],
            ['02/19/2026', 'GREKI', 'GREKI', 'NY', 'US', 'K1', 43.20, -78.10, 'WAYPOINT', ''],
            ['02/19/2026', 'KASTL', 'KASTL', 'PA', 'US', 'K1', 41.50, -78.30, 'WAYPOINT', ''],
            # Duplicate ident — should be silently deduped
            ['02/19/2026', 'BUFFY', 'BUFFY', 'XX', 'US', 'K1', 0.0, 0.0, 'WAYPOINT', ''],
            # Garbage row missing coords — should be skipped
            ['02/19/2026', 'BAD01', 'BAD01', 'NY', 'US', 'K1', '', '', 'WAYPOINT', ''],
        ]))

        # NAV_BASE.csv — navaids
        zf.writestr('NAV_BASE.csv', _csv_bytes([
            ['EFF_DATE', 'NAV_ID', 'NAV_TYPE', 'NAME', 'STATE_CODE',
             'COUNTRY_CODE', 'LAT_DECIMAL', 'LONG_DECIMAL', 'ELEV',
             'FREQ', 'CHANNEL'],
            ['02/19/2026', 'BUF', 'VOR/DME', 'BUFFALO',     'NY', 'US', 42.9405, -78.7325,  728, '116.40', '111X'],
            ['02/19/2026', 'SYR', 'VOR/DME', 'SYRACUSE',    'NY', 'US', 43.1614, -76.1003,  423, '117.00', '117X'],
            ['02/19/2026', 'PSB', 'VOR/DME', 'PHILIPSBURG', 'PA', 'US', 40.9166, -78.0040, 1956, '112.00', '57X'],
            ['02/19/2026', 'AGC', 'VOR/DME', 'PITTSBURGH',  'PA', 'US', 40.2658, -80.0394, 1248, '108.40', '21X'],
            ['02/19/2026', 'JFK', 'VOR/DME', 'KENNEDY',     'NY', 'US', 40.6328, -73.7728,   12, '115.90', '106X'],
            ['02/19/2026', 'NDB1', 'NDB',    'TESTNDB',     'NY', 'US', 42.0,    -78.0,     100, '350.0',  ''],
        ]))

        # APT_BASE.csv — airports
        zf.writestr('APT_BASE.csv', _csv_bytes([
            ['EFF_DATE', 'ARPT_ID', 'ICAO_ID', 'ARPT_NAME',
             'OWNERSHIP_TYPE_CODE', 'FACILITY_USE_CODE',
             'STATE_CODE', 'CITY', 'LAT_DECIMAL', 'LONG_DECIMAL', 'ELEV'],
            ['02/19/2026', 'BUF', 'KBUF', 'BUFFALO NIAGARA INTL', 'PU', 'PU', 'NY', 'BUFFALO',         42.9405, -78.7325,  728],
            ['02/19/2026', 'JFK', 'KJFK', 'JOHN F KENNEDY INTL',   'PU', 'PU', 'NY', 'NEW YORK',        40.6398, -73.7789,   13],
            ['02/19/2026', 'DFW', 'KDFW', 'DALLAS FT WORTH INTL',  'PU', 'PU', 'TX', 'DALLAS-FT WORTH', 32.8968, -97.0380,  607],
            ['02/19/2026', 'LAX', 'KLAX', 'LOS ANGELES INTL',      'PU', 'PU', 'CA', 'LOS ANGELES',     33.9425, -118.4081, 125],
            # Closed/private — should be filtered
            ['02/19/2026', 'XYZ', '',     'PRIVATE GRASS STRIP',   'PR', 'CL', 'NY', 'NOWHERE',        42.0,    -78.0,    200],
        ]))

        # AWY_BASE.csv — airways with their full point sequence in AIRWAY_STRING
        # The real FAA schema (cycle 2026-04-16) has these columns:
        #   EFF_DATE, REGULATORY, AWY_DESIGNATION, AWY_LOCATION, AWY_ID,
        #   UPDATE_DATE, REMARK, AIRWAY_STRING
        # AWY_DESIGNATION is the human name ('J70'); AWY_ID is an internal
        # database key ('A216') we don't use.
        zf.writestr('AWY_BASE.csv', _csv_bytes([
            ['EFF_DATE', 'REGULATORY', 'AWY_DESIGNATION', 'AWY_LOCATION',
             'AWY_ID', 'UPDATE_DATE', 'REMARK', 'AIRWAY_STRING'],
            # J70: BUF -> SYR -> PSB -> AGC, all in one space-separated string
            ['2026/04/16', 'Y', 'J70', 'C', 'A100', '2024/01/01', '', 'BUF SYR PSB AGC'],
            # V14: BUF -> KASTL
            ['2026/04/16', 'Y', 'V14', 'E', 'A101', '2024/01/01', '', 'BUF KASTL'],
            # Empty AIRWAY_STRING — should be silently skipped
            ['2026/04/16', 'Y', 'J999', 'C', 'A102', '2024/01/01', '', ''],
            # Empty designation — should be silently skipped
            ['2026/04/16', 'Y', '', 'C', 'A103', '2024/01/01', '', 'BUF SYR'],
        ]))

        # AWY_SEG_ALT.csv — included for completeness (real archives have it),
        # but our parser doesn't use it any more. Just one decoy row so the
        # file isn't empty.
        zf.writestr('AWY_SEG_ALT.csv', _csv_bytes([
            ['EFF_DATE', 'AWY_ID', 'POINT_SEQ', 'NAV_ID'],
            ['2026/04/16', 'A100', '10', 'BUF'],
        ]))

        # Add a fake change-report sub-ZIP — we want to verify our parser
        # ignores it and reads the real CSVs in the same bundle.
        change_report_inner = io.BytesIO()
        with zipfile.ZipFile(change_report_inner, 'w') as crz:
            crz.writestr('CHG_NAV.csv', b'this should never be read\n')
        zf.writestr('19_Mar_2026_CSV-16_Apr_2026_CSV.zip', change_report_inner.getvalue())

        # README PDFs that real archives have — should not interfere
        zf.writestr('CSV_README.pdf', b'%PDF-fake\n')
        zf.writestr('CSV_CHG_RPT_README.pdf', b'%PDF-fake\n')

    return out.getvalue()


def main():
    out_path = Path(__file__).parent / '28DaySubscription_Effective_2026-04-16.zip'

    inner_csv_zip = _build_inner_csv_zip()

    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as outer:
        # Mimic the real layout exactly: one nested ZIP under CSV_Data/
        outer.writestr('CSV_Data/16_Apr_2026_CSV.zip', inner_csv_zip)
        # A few decoy AIXM XSD files at the outer layer (real archives have hundreds)
        outer.writestr('Additional_Data/AIXM/AIXM_5.1/AIXM/extension/Airport_DataTypes.xsd',
                       b'<?xml version="1.0"?><schema/>')
        outer.writestr('Additional_Data/AIXM/AIXM_5.1/AIXM/extension/Navaid_DataTypes.xsd',
                       b'<?xml version="1.0"?><schema/>')

    print(f'Wrote test fixture: {out_path}')
    print(f'Size: {out_path.stat().st_size} bytes')


if __name__ == '__main__':
    main()

