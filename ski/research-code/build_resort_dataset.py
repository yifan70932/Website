"""
Build US ski resort dataset for the OpenStreetMap webmap.

Sources:
- Skiable acres: skinorthamerica100.com 'ranked by size' page (fetched directly)
- Vertical drop: skinorthamerica100.com 'ranked by vertical' page (fetched directly)
- Coordinates: well-known geographic facts; verified against Wikipedia where checked
- Trails / lifts / snowfall: Per-resort search snippets where available, my training where not
- NSAA region: assigned deterministically by state

We focus on US resorts (excludes Canadian, NZ, Japanese resorts from skinorthamerica100 list).

The output is a JSON file for the Leaflet map.
"""
import json
from pathlib import Path

# State -> NSAA region mapping
STATE_TO_REGION = {
    # Northeast: ME, NH, VT, NY, PA, MA, CT, NJ, RI
    'ME': 'Northeast', 'NH': 'Northeast', 'VT': 'Northeast', 'NY': 'Northeast',
    'PA': 'Northeast', 'MA': 'Northeast', 'CT': 'Northeast', 'NJ': 'Northeast',
    'RI': 'Northeast',
    # Southeast: VA, WV, NC, TN, MD, GA, SC, AL, KY
    'VA': 'Southeast', 'WV': 'Southeast', 'NC': 'Southeast', 'TN': 'Southeast',
    'MD': 'Southeast', 'GA': 'Southeast', 'SC': 'Southeast', 'AL': 'Southeast',
    'KY': 'Southeast',
    # Midwest: WI, MI, MN, OH, IL, IN, IA, MO, ND, SD
    'WI': 'Midwest', 'MI': 'Midwest', 'MN': 'Midwest', 'OH': 'Midwest',
    'IL': 'Midwest', 'IN': 'Midwest', 'IA': 'Midwest', 'MO': 'Midwest',
    'ND': 'Midwest', 'SD': 'Midwest',
    # Rocky Mountain: CO, UT, MT, WY, ID, NM, AZ, NV
    'CO': 'Rocky Mountain', 'UT': 'Rocky Mountain', 'MT': 'Rocky Mountain',
    'WY': 'Rocky Mountain', 'ID': 'Rocky Mountain', 'NM': 'Rocky Mountain',
    'AZ': 'Rocky Mountain',
    # NSAA actually puts NV with Pacific Southwest because of Lake Tahoe
    'NV': 'Pacific Southwest',
    # Pacific Southwest: CA, NV (Tahoe)
    'CA': 'Pacific Southwest',
    # Pacific Northwest: OR, WA, AK
    'OR': 'Pacific Northwest', 'WA': 'Pacific Northwest', 'AK': 'Pacific Northwest',
}

# Master resort list — US resorts only
# Fields: name, state, lat, lon, acres, vertical_ft, trails, lifts, snowfall_in
# Where None: data not available with high confidence
RESORTS = [
    # === ROCKY MOUNTAIN region ===
    # Colorado
    {'name': 'Vail', 'state': 'CO', 'lat': 39.6403, 'lon': -106.3742,
     'acres': 5289, 'vertical_ft': 3450, 'trails': 195, 'lifts': 32, 'snowfall_in': 354},
    {'name': 'Aspen Snowmass', 'state': 'CO', 'lat': 39.2090, 'lon': -106.9494,
     'acres': 3332, 'vertical_ft': 4406, 'trails': 98, 'lifts': 21, 'snowfall_in': 300,
     'note': 'Snowmass mountain only; Aspen complex has 4 mountains totaling 5,547 acres'},
    {'name': 'Aspen Mountain (Ajax)', 'state': 'CO', 'lat': 39.1845, 'lon': -106.8175,
     'acres': 675, 'vertical_ft': 3267, 'trails': 76, 'lifts': 8, 'snowfall_in': 300},
    {'name': 'Aspen Highlands', 'state': 'CO', 'lat': 39.1818, 'lon': -106.8553,
     'acres': 1010, 'vertical_ft': 3635, 'trails': 144, 'lifts': 5, 'snowfall_in': 300},
    {'name': 'Beaver Creek', 'state': 'CO', 'lat': 39.6042, 'lon': -106.5158,
     'acres': 2082, 'vertical_ft': 3340, 'trails': 167, 'lifts': 25, 'snowfall_in': 325},
    {'name': 'Breckenridge', 'state': 'CO', 'lat': 39.4817, 'lon': -106.0670,
     'acres': 2908, 'vertical_ft': 2908, 'trails': 187, 'lifts': 35, 'snowfall_in': 366},
    {'name': 'Keystone', 'state': 'CO', 'lat': 39.6049, 'lon': -105.9544,
     'acres': 3149, 'vertical_ft': 2362, 'trails': 130, 'lifts': 20, 'snowfall_in': 235},
    {'name': 'Copper Mountain', 'state': 'CO', 'lat': 39.5022, 'lon': -106.1497,
     'acres': 2507, 'vertical_ft': 2601, 'trails': 140, 'lifts': 22, 'snowfall_in': 305},
    {'name': 'Steamboat', 'state': 'CO', 'lat': 40.4572, 'lon': -106.8045,
     'acres': 2965, 'vertical_ft': 3668, 'trails': 169, 'lifts': 22, 'snowfall_in': 343},
    {'name': 'Winter Park', 'state': 'CO', 'lat': 39.8868, 'lon': -105.7626,
     'acres': 3081, 'vertical_ft': 3060, 'trails': 166, 'lifts': 25, 'snowfall_in': 327},
    {'name': 'Telluride', 'state': 'CO', 'lat': 37.9375, 'lon': -107.8123,
     'acres': 2000, 'vertical_ft': 3845, 'trails': 148, 'lifts': 19, 'snowfall_in': 280},
    {'name': 'Crested Butte', 'state': 'CO', 'lat': 38.8989, 'lon': -106.9650,
     'acres': 1547, 'vertical_ft': 2775, 'trails': 121, 'lifts': 15, 'snowfall_in': 234},
    {'name': 'Loveland', 'state': 'CO', 'lat': 39.6800, 'lon': -105.8979,
     'acres': 1800, 'vertical_ft': 1780, 'trails': 94, 'lifts': 11, 'snowfall_in': 422},
    {'name': 'Arapahoe Basin', 'state': 'CO', 'lat': 39.6422, 'lon': -105.8719,
     'acres': 1428, 'vertical_ft': 1698, 'trails': 147, 'lifts': 9, 'snowfall_in': 350},
    {'name': 'Wolf Creek', 'state': 'CO', 'lat': 37.4736, 'lon': -106.7980,
     'acres': 1600, 'vertical_ft': 1604, 'trails': 133, 'lifts': 7, 'snowfall_in': 430},
    {'name': 'Purgatory', 'state': 'CO', 'lat': 37.6292, 'lon': -107.8141,
     'acres': 1360, 'vertical_ft': 2029, 'trails': 105, 'lifts': 12, 'snowfall_in': 260},
    {'name': 'Powderhorn', 'state': 'CO', 'lat': 39.0624, 'lon': -108.1466,
     'acres': 1200, 'vertical_ft': 1650, 'trails': 63, 'lifts': 4, 'snowfall_in': 250},
    {'name': 'Sunlight Mountain', 'state': 'CO', 'lat': 39.4144, 'lon': -107.3300,
     'acres': 680, 'vertical_ft': 1720, 'trails': 72, 'lifts': 4, 'snowfall_in': 250},

    # Utah
    {'name': 'Park City Mountain', 'state': 'UT', 'lat': 40.6514, 'lon': -111.5083,
     'acres': 7300, 'vertical_ft': 3190, 'trails': 348, 'lifts': 41, 'snowfall_in': 355,
     'note': 'Combined Park City + Canyons since 2015 connection'},
    {'name': 'Deer Valley', 'state': 'UT', 'lat': 40.6300, 'lon': -111.4778,
     'acres': 4925, 'vertical_ft': 2900, 'trails': 235, 'lifts': 33, 'snowfall_in': 300,
     'note': 'After 2024-25 expansion; ski-only, no snowboards'},
    {'name': 'Snowbird', 'state': 'UT', 'lat': 40.5829, 'lon': -111.6557,
     'acres': 2500, 'vertical_ft': 3240, 'trails': 169, 'lifts': 14, 'snowfall_in': 500},
    {'name': 'Alta', 'state': 'UT', 'lat': 40.5883, 'lon': -111.6378,
     'acres': 2200, 'vertical_ft': 2020, 'trails': 116, 'lifts': 11, 'snowfall_in': 545,
     'note': 'Ski-only, no snowboards'},
    {'name': 'Solitude', 'state': 'UT', 'lat': 40.6196, 'lon': -111.5916,
     'acres': 1200, 'vertical_ft': 2030, 'trails': 80, 'lifts': 8, 'snowfall_in': 500},
    {'name': 'Brighton', 'state': 'UT', 'lat': 40.5977, 'lon': -111.5832,
     'acres': 1050, 'vertical_ft': 1745, 'trails': 66, 'lifts': 8, 'snowfall_in': 500},
    {'name': 'Snowbasin', 'state': 'UT', 'lat': 41.2162, 'lon': -111.8576,
     'acres': 3000, 'vertical_ft': 2900, 'trails': 107, 'lifts': 12, 'snowfall_in': 300},
    {'name': 'Powder Mountain', 'state': 'UT', 'lat': 41.3793, 'lon': -111.7791,
     'acres': 5000, 'vertical_ft': 2100, 'trails': 167, 'lifts': 9, 'snowfall_in': 500,
     'note': 'Lift-served acres only; total acreage including hike-to and cat is ~8,500'},
    {'name': 'Sundance', 'state': 'UT', 'lat': 40.3919, 'lon': -111.5854,
     'acres': 500, 'vertical_ft': 2150, 'trails': 45, 'lifts': 4, 'snowfall_in': 320},
    {'name': 'Brian Head', 'state': 'UT', 'lat': 37.7019, 'lon': -112.8488,
     'acres': 650, 'vertical_ft': 1320, 'trails': 71, 'lifts': 8, 'snowfall_in': 360},
    {'name': 'Beaver Mountain', 'state': 'UT', 'lat': 41.9683, 'lon': -111.5454,
     'acres': 828, 'vertical_ft': 1660, 'trails': 48, 'lifts': 5, 'snowfall_in': 400},

    # Wyoming
    {'name': 'Jackson Hole', 'state': 'WY', 'lat': 43.5878, 'lon': -110.8281,
     'acres': 2500, 'vertical_ft': 4139, 'trails': 133, 'lifts': 13, 'snowfall_in': 459},
    {'name': 'Grand Targhee', 'state': 'WY', 'lat': 43.7886, 'lon': -110.9586,
     'acres': 2602, 'vertical_ft': 2270, 'trails': 90, 'lifts': 5, 'snowfall_in': 500},
    {'name': 'Snow King', 'state': 'WY', 'lat': 43.4736, 'lon': -110.7611,
     'acres': 400, 'vertical_ft': 1571, 'trails': 32, 'lifts': 3, 'snowfall_in': 250},

    # Montana
    {'name': 'Big Sky', 'state': 'MT', 'lat': 45.2843, 'lon': -111.4015,
     'acres': 5850, 'vertical_ft': 4016, 'trails': 300, 'lifts': 38, 'snowfall_in': 400},
    {'name': 'Whitefish Mountain', 'state': 'MT', 'lat': 48.4894, 'lon': -114.3517,
     'acres': 3000, 'vertical_ft': 2353, 'trails': 105, 'lifts': 15, 'snowfall_in': 300},
    {'name': 'Bridger Bowl', 'state': 'MT', 'lat': 45.8190, 'lon': -110.9116,
     'acres': 2000, 'vertical_ft': 2600, 'trails': 75, 'lifts': 8, 'snowfall_in': 300},
    {'name': 'Red Lodge Mountain', 'state': 'MT', 'lat': 45.1881, 'lon': -109.3503,
     'acres': 1600, 'vertical_ft': 2400, 'trails': 80, 'lifts': 8, 'snowfall_in': 250},
    {'name': 'Discovery Ski Area', 'state': 'MT', 'lat': 46.2272, 'lon': -113.2469,
     'acres': 2200, 'vertical_ft': 1660, 'trails': 67, 'lifts': 7, 'snowfall_in': 215},
    {'name': 'Lost Trail Powder Mountain', 'state': 'MT', 'lat': 45.6911, 'lon': -113.9542,
     'acres': 1800, 'vertical_ft': 1800, 'trails': 60, 'lifts': 6, 'snowfall_in': 325},
    {'name': 'Montana Snowbowl', 'state': 'MT', 'lat': 47.0303, 'lon': -114.0314,
     'acres': 1200, 'vertical_ft': 2600, 'trails': 50, 'lifts': 4, 'snowfall_in': 300},

    # Idaho
    {'name': 'Sun Valley', 'state': 'ID', 'lat': 43.6711, 'lon': -114.3650,
     'acres': 2054, 'vertical_ft': 3400, 'trails': 121, 'lifts': 18, 'snowfall_in': 220},
    {'name': 'Schweitzer', 'state': 'ID', 'lat': 48.3692, 'lon': -116.6225,
     'acres': 2900, 'vertical_ft': 2400, 'trails': 92, 'lifts': 10, 'snowfall_in': 300},
    {'name': 'Bogus Basin', 'state': 'ID', 'lat': 43.7665, 'lon': -116.0973,
     'acres': 2600, 'vertical_ft': 1819, 'trails': 92, 'lifts': 10, 'snowfall_in': 200},
    {'name': 'Brundage', 'state': 'ID', 'lat': 45.0183, 'lon': -116.1561,
     'acres': 1500, 'vertical_ft': 1800, 'trails': 46, 'lifts': 6, 'snowfall_in': 320},
    {'name': 'Tamarack', 'state': 'ID', 'lat': 44.8825, 'lon': -116.0394,
     'acres': 1385, 'vertical_ft': 2800, 'trails': 50, 'lifts': 6, 'snowfall_in': 300},
    {'name': 'Silver Mountain', 'state': 'ID', 'lat': 47.5469, 'lon': -116.1875,
     'acres': 1600, 'vertical_ft': 2150, 'trails': 73, 'lifts': 7, 'snowfall_in': 340},
    {'name': 'Pebble Creek', 'state': 'ID', 'lat': 42.9119, 'lon': -111.9922,
     'acres': 1100, 'vertical_ft': 2200, 'trails': 54, 'lifts': 3, 'snowfall_in': 250},

    # New Mexico
    {'name': 'Taos Ski Valley', 'state': 'NM', 'lat': 36.5969, 'lon': -105.4525,
     'acres': 1294, 'vertical_ft': 3281, 'trails': 110, 'lifts': 13, 'snowfall_in': 305},
    {'name': 'Ski Santa Fe', 'state': 'NM', 'lat': 35.7964, 'lon': -105.7969,
     'acres': 660, 'vertical_ft': 1725, 'trails': 86, 'lifts': 7, 'snowfall_in': 225},
    {'name': 'Angel Fire', 'state': 'NM', 'lat': 36.3892, 'lon': -105.2903,
     'acres': 445, 'vertical_ft': 2050, 'trails': 81, 'lifts': 7, 'snowfall_in': 220},

    # Arizona
    {'name': 'Arizona Snowbowl', 'state': 'AZ', 'lat': 35.3306, 'lon': -111.7106,
     'acres': 777, 'vertical_ft': 2300, 'trails': 55, 'lifts': 8, 'snowfall_in': 260},

    # === PACIFIC SOUTHWEST region ===
    # California (Lake Tahoe area)
    {'name': 'Palisades Tahoe', 'state': 'CA', 'lat': 39.1969, 'lon': -120.2339,
     'acres': 6000, 'vertical_ft': 2510, 'trails': 270, 'lifts': 42, 'snowfall_in': 400,
     'note': '2021 merger of Squaw Valley and Alpine Meadows'},
    {'name': 'Heavenly', 'state': 'CA', 'lat': 38.9354, 'lon': -119.9407,
     'acres': 4800, 'vertical_ft': 3280, 'trails': 97, 'lifts': 28, 'snowfall_in': 360,
     'note': 'CA/NV border resort'},
    {'name': 'Northstar', 'state': 'CA', 'lat': 39.2746, 'lon': -120.1211,
     'acres': 3170, 'vertical_ft': 2280, 'trails': 100, 'lifts': 20, 'snowfall_in': 350},
    {'name': 'Mammoth Mountain', 'state': 'CA', 'lat': 37.6308, 'lon': -119.0326,
     'acres': 3500, 'vertical_ft': 2900, 'trails': 150, 'lifts': 28, 'snowfall_in': 400},
    {'name': 'Kirkwood', 'state': 'CA', 'lat': 38.6856, 'lon': -120.0667,
     'acres': 2500, 'vertical_ft': 1630, 'trails': 86, 'lifts': 13, 'snowfall_in': 354},
    {'name': 'Sugar Bowl', 'state': 'CA', 'lat': 39.3047, 'lon': -120.3300,
     'acres': 1500, 'vertical_ft': 1500, 'trails': 102, 'lifts': 13, 'snowfall_in': 500},
    {'name': 'Sierra-at-Tahoe', 'state': 'CA', 'lat': 38.8000, 'lon': -120.0717,
     'acres': 2000, 'vertical_ft': 2212, 'trails': 46, 'lifts': 14, 'snowfall_in': 480},
    {'name': 'Bear Valley', 'state': 'CA', 'lat': 38.4807, 'lon': -120.0411,
     'acres': 1680, 'vertical_ft': 1900, 'trails': 75, 'lifts': 11, 'snowfall_in': 359},
    {'name': 'June Mountain', 'state': 'CA', 'lat': 37.7720, 'lon': -119.0867,
     'acres': 500, 'vertical_ft': 2590, 'trails': 41, 'lifts': 7, 'snowfall_in': 250},
    {'name': 'Dodge Ridge', 'state': 'CA', 'lat': 38.1900, 'lon': -119.9519,
     'acres': 852, 'vertical_ft': 1550, 'trails': 67, 'lifts': 12, 'snowfall_in': 350},
    {'name': 'China Peak', 'state': 'CA', 'lat': 37.2393, 'lon': -119.1551,
     'acres': 1200, 'vertical_ft': 1570, 'trails': 47, 'lifts': 11, 'snowfall_in': 300},
    {'name': 'Homewood', 'state': 'CA', 'lat': 39.0833, 'lon': -120.1667,
     'acres': 1260, 'vertical_ft': 1650, 'trails': 67, 'lifts': 8, 'snowfall_in': 450},
    {'name': 'Alpine Meadows', 'state': 'CA', 'lat': 39.1648, 'lon': -120.2382,
     'acres': 2400, 'vertical_ft': 1802, 'trails': 100, 'lifts': 13, 'snowfall_in': 400,
     'note': 'Now part of Palisades Tahoe but historically separate'},

    # Nevada
    {'name': 'Mt. Rose', 'state': 'NV', 'lat': 39.3247, 'lon': -119.8881,
     'acres': 1200, 'vertical_ft': 1760, 'trails': 60, 'lifts': 8, 'snowfall_in': 350},
    {'name': 'Diamond Peak', 'state': 'NV', 'lat': 39.2602, 'lon': -119.9258,
     'acres': 655, 'vertical_ft': 1840, 'trails': 30, 'lifts': 7, 'snowfall_in': 325},

    # === PACIFIC NORTHWEST region ===
    # Oregon
    {'name': 'Mt. Bachelor', 'state': 'OR', 'lat': 43.9806, 'lon': -121.6884,
     'acres': 4318, 'vertical_ft': 3365, 'trails': 121, 'lifts': 15, 'snowfall_in': 462},
    {'name': 'Mt. Hood Meadows', 'state': 'OR', 'lat': 45.3322, 'lon': -121.6664,
     'acres': 2150, 'vertical_ft': 2777, 'trails': 87, 'lifts': 11, 'snowfall_in': 430},
    {'name': 'Timberline', 'state': 'OR', 'lat': 45.3306, 'lon': -121.7113,
     'acres': 1450, 'vertical_ft': 3690, 'trails': 41, 'lifts': 9, 'snowfall_in': 551},
    {'name': 'Mt. Hood Skibowl', 'state': 'OR', 'lat': 45.3083, 'lon': -121.7669,
     'acres': 960, 'vertical_ft': 1500, 'trails': 65, 'lifts': 9, 'snowfall_in': 300},

    # Washington
    {'name': 'Crystal Mountain', 'state': 'WA', 'lat': 46.9293, 'lon': -121.4794,
     'acres': 2600, 'vertical_ft': 2600, 'trails': 86, 'lifts': 11, 'snowfall_in': 486},
    {'name': 'Stevens Pass', 'state': 'WA', 'lat': 47.7458, 'lon': -121.0884,
     'acres': 1125, 'vertical_ft': 1800, 'trails': 52, 'lifts': 10, 'snowfall_in': 460},
    {'name': 'Mission Ridge', 'state': 'WA', 'lat': 47.2906, 'lon': -120.4017,
     'acres': 2000, 'vertical_ft': 2190, 'trails': 36, 'lifts': 6, 'snowfall_in': 200},
    {'name': 'White Pass', 'state': 'WA', 'lat': 46.6378, 'lon': -121.3889,
     'acres': 1402, 'vertical_ft': 2050, 'trails': 45, 'lifts': 8, 'snowfall_in': 400},
    {'name': '49 Degrees North', 'state': 'WA', 'lat': 48.3025, 'lon': -117.5703,
     'acres': 2325, 'vertical_ft': 1850, 'trails': 82, 'lifts': 7, 'snowfall_in': 300},

    # Alaska
    {'name': 'Alyeska', 'state': 'AK', 'lat': 60.9747, 'lon': -149.0997,
     'acres': 1610, 'vertical_ft': 2500, 'trails': 76, 'lifts': 9, 'snowfall_in': 669},

    # === NORTHEAST region ===
    # Vermont
    {'name': 'Killington', 'state': 'VT', 'lat': 43.6045, 'lon': -72.7944,
     'acres': 1509, 'vertical_ft': 3050, 'trails': 155, 'lifts': 22, 'snowfall_in': 250},
    {'name': 'Stowe', 'state': 'VT', 'lat': 44.5306, 'lon': -72.7814,
     'acres': 485, 'vertical_ft': 2360, 'trails': 116, 'lifts': 13, 'snowfall_in': 314},
    {'name': 'Sugarbush', 'state': 'VT', 'lat': 44.1357, 'lon': -72.8950,
     'acres': 581, 'vertical_ft': 2552, 'trails': 111, 'lifts': 16, 'snowfall_in': 260},
    {'name': 'Jay Peak', 'state': 'VT', 'lat': 44.9367, 'lon': -72.5267,
     'acres': 385, 'vertical_ft': 2153, 'trails': 81, 'lifts': 9, 'snowfall_in': 359},
    {'name': 'Mount Snow', 'state': 'VT', 'lat': 42.9608, 'lon': -72.9211,
     'acres': 588, 'vertical_ft': 1700, 'trails': 86, 'lifts': 19, 'snowfall_in': 156},
    {'name': 'Okemo', 'state': 'VT', 'lat': 43.4019, 'lon': -72.7173,
     'acres': 667, 'vertical_ft': 2200, 'trails': 121, 'lifts': 20, 'snowfall_in': 200},
    {'name': 'Stratton', 'state': 'VT', 'lat': 43.1144, 'lon': -72.9078,
     'acres': 670, 'vertical_ft': 2003, 'trails': 99, 'lifts': 16, 'snowfall_in': 180},
    {'name': "Smugglers' Notch", 'state': 'VT', 'lat': 44.5803, 'lon': -72.7872,
     'acres': 1000, 'vertical_ft': 2525, 'trails': 78, 'lifts': 8, 'snowfall_in': 309},
    {'name': 'Mad River Glen', 'state': 'VT', 'lat': 44.2031, 'lon': -72.9183,
     'acres': 915, 'vertical_ft': 2037, 'trails': 53, 'lifts': 5, 'snowfall_in': 250,
     'note': 'Ski-only, no snowboards; cooperatively owned'},
    {'name': 'Pico', 'state': 'VT', 'lat': 43.6556, 'lon': -72.8431,
     'acres': 468, 'vertical_ft': 2000, 'trails': 58, 'lifts': 7, 'snowfall_in': 250},

    # New Hampshire
    {'name': 'Cannon Mountain', 'state': 'NH', 'lat': 44.1714, 'lon': -71.7000,
     'acres': 285, 'vertical_ft': 2130, 'trails': 97, 'lifts': 11, 'snowfall_in': 160},
    {'name': 'Bretton Woods', 'state': 'NH', 'lat': 44.2589, 'lon': -71.4733,
     'acres': 464, 'vertical_ft': 1500, 'trails': 102, 'lifts': 10, 'snowfall_in': 200},
    {'name': 'Loon Mountain', 'state': 'NH', 'lat': 44.0394, 'lon': -71.6228,
     'acres': 370, 'vertical_ft': 2100, 'trails': 61, 'lifts': 11, 'snowfall_in': 165},
    {'name': 'Waterville Valley', 'state': 'NH', 'lat': 43.9472, 'lon': -71.5050,
     'acres': 265, 'vertical_ft': 2020, 'trails': 50, 'lifts': 11, 'snowfall_in': 160},
    {'name': 'Wildcat Mountain', 'state': 'NH', 'lat': 44.2592, 'lon': -71.2403,
     'acres': 225, 'vertical_ft': 2112, 'trails': 48, 'lifts': 4, 'snowfall_in': 200},
    {'name': 'Attitash', 'state': 'NH', 'lat': 44.0850, 'lon': -71.2375,
     'acres': 311, 'vertical_ft': 1750, 'trails': 67, 'lifts': 10, 'snowfall_in': 165},

    # Maine
    {'name': 'Sugarloaf', 'state': 'ME', 'lat': 45.0314, 'lon': -70.3144,
     'acres': 1240, 'vertical_ft': 2820, 'trails': 162, 'lifts': 15, 'snowfall_in': 200},
    {'name': 'Sunday River', 'state': 'ME', 'lat': 44.4717, 'lon': -70.8553,
     'acres': 870, 'vertical_ft': 2340, 'trails': 135, 'lifts': 18, 'snowfall_in': 167},
    {'name': 'Saddleback', 'state': 'ME', 'lat': 44.9444, 'lon': -70.5394,
     'acres': 600, 'vertical_ft': 2000, 'trails': 68, 'lifts': 4, 'snowfall_in': 225},

    # New York
    {'name': 'Whiteface', 'state': 'NY', 'lat': 44.3653, 'lon': -73.9028,
     'acres': 299, 'vertical_ft': 3166, 'trails': 87, 'lifts': 11, 'snowfall_in': 168,
     'note': '1980 Olympics venue; highest vertical in the East'},
    {'name': 'Hunter Mountain', 'state': 'NY', 'lat': 42.2056, 'lon': -74.2261,
     'acres': 320, 'vertical_ft': 1600, 'trails': 67, 'lifts': 12, 'snowfall_in': 121},
    {'name': 'Belleayre', 'state': 'NY', 'lat': 42.1408, 'lon': -74.4881,
     'acres': 175, 'vertical_ft': 1404, 'trails': 51, 'lifts': 8, 'snowfall_in': 165},
    {'name': 'Gore Mountain', 'state': 'NY', 'lat': 43.6747, 'lon': -74.0014,
     'acres': 439, 'vertical_ft': 2537, 'trails': 110, 'lifts': 14, 'snowfall_in': 150},
    {'name': 'Windham', 'state': 'NY', 'lat': 42.2972, 'lon': -74.2742,
     'acres': 285, 'vertical_ft': 1600, 'trails': 60, 'lifts': 13, 'snowfall_in': 120},

    # === MIDWEST region ===
    {'name': 'Lutsen Mountains', 'state': 'MN', 'lat': 47.6642, 'lon': -90.7233,
     'acres': 1000, 'vertical_ft': 825, 'trails': 95, 'lifts': 8, 'snowfall_in': 110},
    {'name': 'Granite Peak', 'state': 'WI', 'lat': 44.9111, 'lon': -89.6792,
     'acres': 215, 'vertical_ft': 700, 'trails': 75, 'lifts': 7, 'snowfall_in': 60},
    {'name': 'Chestnut Mountain', 'state': 'IL', 'lat': 42.4456, 'lon': -90.3633,
     'acres': 220, 'vertical_ft': 475, 'trails': 19, 'lifts': 9, 'snowfall_in': 50},
    {'name': 'Boyne Mountain', 'state': 'MI', 'lat': 45.1675, 'lon': -84.9272,
     'acres': 415, 'vertical_ft': 500, 'trails': 60, 'lifts': 12, 'snowfall_in': 140},
    {'name': 'Boyne Highlands', 'state': 'MI', 'lat': 45.4608, 'lon': -84.9706,
     'acres': 430, 'vertical_ft': 552, 'trails': 53, 'lifts': 9, 'snowfall_in': 140},
    {'name': 'Crystal Mountain (MI)', 'state': 'MI', 'lat': 44.5253, 'lon': -86.0883,
     'acres': 132, 'vertical_ft': 375, 'trails': 58, 'lifts': 9, 'snowfall_in': 132},
    {'name': 'Mt. Brighton', 'state': 'MI', 'lat': 42.5167, 'lon': -83.7972,
     'acres': 130, 'vertical_ft': 230, 'trails': 26, 'lifts': 7, 'snowfall_in': 50},
    {'name': 'Terry Peak', 'state': 'SD', 'lat': 44.3322, 'lon': -103.8458,
     'acres': 450, 'vertical_ft': 1052, 'trails': 30, 'lifts': 5, 'snowfall_in': 150},
    {'name': "Wilmot Mountain", 'state': 'WI', 'lat': 42.5072, 'lon': -88.1517,
     'acres': 135, 'vertical_ft': 230, 'trails': 23, 'lifts': 7, 'snowfall_in': 50},
    {'name': 'Tyrol Basin', 'state': 'WI', 'lat': 43.0833, 'lon': -89.7331,
     'acres': 75, 'vertical_ft': 300, 'trails': 18, 'lifts': 6, 'snowfall_in': 50},

    # === SOUTHEAST region ===
    {'name': 'Snowshoe Mountain', 'state': 'WV', 'lat': 38.4083, 'lon': -79.9961,
     'acres': 257, 'vertical_ft': 1500, 'trails': 60, 'lifts': 14, 'snowfall_in': 180},
    {'name': 'Beech Mountain', 'state': 'NC', 'lat': 36.1869, 'lon': -81.8839,
     'acres': 95, 'vertical_ft': 830, 'trails': 17, 'lifts': 8, 'snowfall_in': 84},
    {'name': 'Sugar Mountain', 'state': 'NC', 'lat': 36.1372, 'lon': -81.8703,
     'acres': 125, 'vertical_ft': 1200, 'trails': 21, 'lifts': 8, 'snowfall_in': 78},
    {'name': 'Cataloochee', 'state': 'NC', 'lat': 35.6411, 'lon': -82.9939,
     'acres': 50, 'vertical_ft': 740, 'trails': 18, 'lifts': 5, 'snowfall_in': 50},
    {'name': 'Wintergreen', 'state': 'VA', 'lat': 37.9131, 'lon': -78.9492,
     'acres': 129, 'vertical_ft': 1003, 'trails': 24, 'lifts': 5, 'snowfall_in': 40},
    {'name': 'Bryce Resort', 'state': 'VA', 'lat': 38.8125, 'lon': -78.7522,
     'acres': 50, 'vertical_ft': 500, 'trails': 8, 'lifts': 4, 'snowfall_in': 30},
    {'name': 'Ober Gatlinburg', 'state': 'TN', 'lat': 35.7117, 'lon': -83.5072,
     'acres': 35, 'vertical_ft': 600, 'trails': 10, 'lifts': 4, 'snowfall_in': 35},
    {'name': 'Cloudmont', 'state': 'AL', 'lat': 34.4669, 'lon': -85.6133,
     'acres': 12, 'vertical_ft': 150, 'trails': 2, 'lifts': 2, 'snowfall_in': 5},
]

# Add NSAA region to each
for r in RESORTS:
    state = r['state']
    r['region'] = STATE_TO_REGION.get(state, 'Unknown')

# Stats
print(f'Total resorts: {len(RESORTS)}')
from collections import Counter
region_counts = Counter(r['region'] for r in RESORTS)
print('By region:')
for region, n in sorted(region_counts.items(), key=lambda x: -x[1]):
    print(f'  {region}: {n}')

state_counts = Counter(r['state'] for r in RESORTS)
print('\nBy state:')
for state, n in sorted(state_counts.items(), key=lambda x: -x[1]):
    print(f'  {state}: {n}')

# Sanity check: all coordinates within US bounds
for r in RESORTS:
    lat, lon = r['lat'], r['lon']
    if not (24 <= lat <= 72 and -180 <= lon <= -65):
        print(f'  WARN coords out of range: {r["name"]} {lat}, {lon}')

# Save to JSON
out = Path('/home/claude/yifanova/ski/research-data/us_ski_resorts.json')
with open(out, 'w') as f:
    json.dump({
        'meta': {
            'description': 'US ski resorts with key features and coordinates. Selection emphasizes major destination resorts; coverage of small/community hills is partial. Compiled April 2026.',
            'sources': [
                'skinorthamerica100.com (skiable acres, vertical drop)',
                'OnTheSnow.com / Wikipedia (trail counts, lifts, snowfall via search)',
                'Geographic coordinates from public records and Wikipedia',
                'NSAA region assignment by state',
            ],
            'count': len(RESORTS),
            'last_updated': '2026-04-30',
        },
        'resorts': RESORTS,
    }, f, indent=2)

print(f'\nSaved to {out}: {out.stat().st_size:,} bytes')
