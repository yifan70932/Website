#!/usr/bin/env python3
"""
build_cn_resort_dataset.py
===========================

Builds research-data/cn_ski_resorts.json — the China outdoor ski resort dataset
used by map_cn.html.

SCOPE
-----
~100 OUTDOOR resorts. Indoor resorts (室内滑雪场) are deliberately excluded —
they raise different geographic questions and break the "drive-time market"
framing of the map.

INCLUSION CRITERIA
------------------
Targeting the resorts that, taken together, account for most of China's ski
visit volume per the 2024-2025 China Ski Industry White Book (which reports
57 outdoor resorts above 100k visits/year producing >50% of national total
visits, plus the long tail of regional resorts):

1. All 26 国家级滑雪旅游度假地 (national ski tourism resorts) confirmed by
   3 official MCT/General Administration of Sport batches (2022, 2023, 2024).
2. Headline resorts in the three "destination clusters" the white book
   highlights: 吉林 / 新疆阿勒泰 / 河北崇礼.
3. Major 城郊学习型 (peri-urban learning) resorts serving the Beijing,
   Shanghai-adjacent, Chengdu, and Xi'an metro markets.
4. Regional standouts in 黑龙江, 内蒙古, 陕西, 山西, 四川, 云南, 湖北.

REGION CLASSIFICATION
---------------------
Following the white book's 6-region scheme:
- 东北     (Dongbei): 黑龙江 吉林 辽宁
- 华北     (Huabei):  北京 天津 河北 山西 内蒙古
- 西北     (Xibei):   新疆 陕西 甘肃 宁夏 青海
- 华中     (Huazhong): 河南 湖北 湖南
- 华东     (Huadong): 上海 江苏 浙江 安徽 福建 江西 山东
- 西南     (Xinan):   四川 重庆 贵州 云南 西藏

DATA QUALITY NOTES
------------------
Coordinate precision: ±0.01° (~1 km) for major resorts; coarser for some smaller
resorts where multiple village-level locations are reported. Vertical drop and
trail counts are best-effort from public sources (ski resort official sites,
2024-2025 White Book where it discloses, regional government tourism portals).
"""

import json
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parent.parent / 'yifanova/ski/research-data/cn_ski_resorts.json'

# Region mapping (province -> region) — white book scheme
PROVINCE_TO_REGION = {
    '黑龙江': '东北', '吉林': '东北', '辽宁': '东北',
    '北京': '华北', '天津': '华北', '河北': '华北', '山西': '华北', '内蒙古': '华北',
    '新疆': '西北', '陕西': '西北', '甘肃': '西北', '宁夏': '西北', '青海': '西北',
    '河南': '华中', '湖北': '华中', '湖南': '华中',
    '上海': '华东', '江苏': '华东', '浙江': '华东', '安徽': '华东', '福建': '华东', '江西': '华东', '山东': '华东',
    '四川': '西南', '重庆': '西南', '贵州': '西南', '云南': '西南', '西藏': '西南',
}

# Region English names (white book convention)
REGION_EN = {
    '东北': 'Northeast',
    '华北': 'North China',
    '西北': 'Northwest',
    '华中': 'Central China',
    '华东': 'East China',
    '西南': 'Southwest',
}

# Pinyin / English province names
PROVINCE_EN = {
    '黑龙江': 'Heilongjiang', '吉林': 'Jilin', '辽宁': 'Liaoning',
    '北京': 'Beijing', '天津': 'Tianjin', '河北': 'Hebei', '山西': 'Shanxi', '内蒙古': 'Inner Mongolia',
    '新疆': 'Xinjiang', '陕西': 'Shaanxi', '甘肃': 'Gansu', '宁夏': 'Ningxia', '青海': 'Qinghai',
    '河南': 'Henan', '湖北': 'Hubei', '湖南': 'Hunan',
    '上海': 'Shanghai', '江苏': 'Jiangsu', '浙江': 'Zhejiang', '安徽': 'Anhui',
    '福建': 'Fujian', '江西': 'Jiangxi', '山东': 'Shandong',
    '四川': 'Sichuan', '重庆': 'Chongqing', '贵州': 'Guizhou', '云南': 'Yunnan', '西藏': 'Tibet',
}

# Resort dictionary key meanings:
#   name_zh / name_en: bilingual display name
#   province:          Chinese province (used for region lookup)
#   lat, lon:          decimal degrees
#   vertical_m:        vertical drop in meters (from public source)
#   trails:            number of marked runs (best-effort)
#   lifts:             number of overhead lifts (chairs + gondola; excludes 魔毯)
#   tier:              one of '目的地度假型' / '城郊学习型' / '旅游体验型' (white book taxonomy)
#   national_tier:     true if on official 国家级滑雪旅游度假地 list
#   national_batch:    1, 2, or 3 — which batch awarded
#   note_zh / note_en: short notable fact
RESORTS = [

    # ============================================================
    # 东北 — JILIN (top destination cluster per white book)
    # ============================================================
    # Jilin's "三万一湖四家大型目的地" — Wanda Changbaishan + 北大湖 + 松花湖 + 长白山天池
    {'name_zh': '万达长白山', 'name_en': 'Wanda Changbaishan', 'province': '吉林',
     'lat': 42.0758, 'lon': 127.4669,
     'vertical_m': 470, 'trails': 43, 'lifts': 11,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '抚松县长白山西景区；首批国家级度假地（抚松长白山）',
     'note_en': 'West Changbaishan in Fusong; 1st batch national resort'},
    {'name_zh': '北大湖', 'name_en': 'Beidahu', 'province': '吉林',
     'lat': 43.5108, 'lon': 126.7967,
     'vertical_m': 870, 'trails': 41, 'lifts': 14,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 2,
     'note_zh': '中国垂直落差最大的滑雪场之一；2007 亚冬会主场地',
     'note_en': "One of China's largest verticals; 2007 Asian Winter Games venue"},
    {'name_zh': '万科松花湖', 'name_en': 'Vanke Songhua Lake', 'province': '吉林',
     'lat': 43.6361, 'lon': 126.6450,
     'vertical_m': 605, 'trails': 36, 'lifts': 11,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '吉林市丰满区；首批国家级度假地（丰满松花湖）',
     'note_en': 'Fengman, Jilin City; 1st batch national resort'},
    {'name_zh': '长白山国际度假区', 'name_en': 'Changbaishan International Resort', 'province': '吉林',
     'lat': 42.0728, 'lon': 128.0578,
     'vertical_m': 485, 'trails': 30, 'lifts': 6,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 3,
     'note_zh': '长白山池北区，第三批国家级度假地',
     'note_en': 'Changbaishan East district; 3rd batch national resort'},
    {'name_zh': '长白山鲁能胜地', 'name_en': 'Changbaishan Luneng', 'province': '吉林',
     'lat': 42.4242, 'lon': 127.6189,
     'vertical_m': 380, 'trails': 22, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '长白山北景区',
     'note_en': 'North Changbaishan slope'},
    {'name_zh': '吉林市庙香山', 'name_en': 'Miaoxiangshan (Jilin)', 'province': '吉林',
     'lat': 43.9436, 'lon': 126.5639,
     'vertical_m': 250, 'trails': 14, 'lifts': 4,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '吉林市城郊',
     'note_en': 'Peri-urban Jilin City'},
    {'name_zh': '净月潭', 'name_en': 'Jingyuetan', 'province': '吉林',
     'lat': 43.7900, 'lon': 125.4753,
     'vertical_m': 80, 'trails': 5, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '长春市内，亚布力以南最便利的城市学习型雪场',
     'note_en': 'Inside Changchun; major urban learning resort'},
    {'name_zh': '莲花山', 'name_en': 'Lianhuashan (Changchun)', 'province': '吉林',
     'lat': 43.9925, 'lon': 125.6361,
     'vertical_m': 195, 'trails': 18, 'lifts': 5,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '长春北郊',
     'note_en': 'North Changchun suburb'},

    # ============================================================
    # 东北 — HEILONGJIANG
    # ============================================================
    {'name_zh': '亚布力', 'name_en': 'Yabuli', 'province': '黑龙江',
     'lat': 44.7197, 'lon': 128.6536,
     'vertical_m': 905, 'trails': 17, 'lifts': 9,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '中国最早的现代滑雪场之一；1996 亚冬会主办地；首批国家级度假地',
     'note_en': "One of China's first modern resorts; 1996 Asian Winter Games; 1st batch national resort"},
    {'name_zh': '雪乡国家森林公园', 'name_en': 'Snow Town', 'province': '黑龙江',
     'lat': 44.5350, 'lon': 128.9447,
     'vertical_m': 195, 'trails': 6, 'lifts': 2,
     'tier': '旅游体验型', 'national_tier': False,
     'note_zh': '以雪景旅游为主，滑雪规模有限',
     'note_en': 'Primarily snow scenery; limited skiing'},
    {'name_zh': '帽儿山', 'name_en': 'Mao\'er Shan', 'province': '黑龙江',
     'lat': 45.3514, 'lon': 127.7253,
     'vertical_m': 260, 'trails': 9, 'lifts': 4,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '哈尔滨近郊',
     'note_en': 'Near Harbin'},
    {'name_zh': '二龙山', 'name_en': 'Erlongshan', 'province': '黑龙江',
     'lat': 45.7256, 'lon': 127.4297,
     'vertical_m': 110, 'trails': 8, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '哈尔滨周边老牌雪场',
     'note_en': 'Established Harbin-area resort'},
    {'name_zh': '亚布力新体委', 'name_en': 'Yabuli Xintiwei', 'province': '黑龙江',
     'lat': 44.7008, 'lon': 128.7008,
     'vertical_m': 700, 'trails': 11, 'lifts': 3,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '亚布力滑雪训练中心，国家队基地',
     'note_en': 'National team training base'},
    {'name_zh': '圣洁摇篮山', 'name_en': 'Shengjie Yaolanshan', 'province': '黑龙江',
     'lat': 46.3300, 'lon': 132.1900,
     'vertical_m': 180, 'trails': 8, 'lifts': 3,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 3,
     'note_zh': '宝清县；第三批国家级度假地',
     'note_en': 'Baoqing County; 3rd batch national resort'},
    {'name_zh': '齐齐哈尔碾子山', 'name_en': 'Nianzishan', 'province': '黑龙江',
     'lat': 47.5172, 'lon': 122.8631,
     'vertical_m': 90, 'trails': 5, 'lifts': 2,
     'tier': '城郊学习型', 'national_tier': False},
    {'name_zh': '虎峰岭', 'name_en': 'Hufengling', 'province': '黑龙江',
     'lat': 45.2400, 'lon': 130.7800,
     'vertical_m': 320, 'trails': 14, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '七台河',
     'note_en': 'Qitaihe area'},

    # ============================================================
    # 东北 — LIAONING
    # ============================================================
    {'name_zh': '本溪东风湖', 'name_en': 'Dongfenghu (Benxi)', 'province': '辽宁',
     'lat': 41.3056, 'lon': 124.0894,
     'vertical_m': 220, 'trails': 12, 'lifts': 4,
     'tier': '城郊学习型', 'national_tier': False},
    {'name_zh': '沈阳棋盘山', 'name_en': 'Qipanshan (Shenyang)', 'province': '辽宁',
     'lat': 41.8806, 'lon': 123.6611,
     'vertical_m': 150, 'trails': 9, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '沈阳市区',
     'note_en': 'Within Shenyang metropolitan area'},
    {'name_zh': '弓长岭温泉滑雪场', 'name_en': 'Gongchangling Hot Spring', 'province': '辽宁',
     'lat': 41.1486, 'lon': 123.4244,
     'vertical_m': 220, 'trails': 13, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '辽阳，温泉+滑雪',
     'note_en': 'Liaoyang; hot spring + skiing combo'},
    {'name_zh': '天桥沟', 'name_en': 'Tianqiaogou', 'province': '辽宁',
     'lat': 40.6300, 'lon': 124.4500,
     'vertical_m': 380, 'trails': 17, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 2,
     'note_zh': '丹东宽甸；第二批国家级度假地',
     'note_en': 'Dandong Kuandian; 2nd batch national resort'},

    # ============================================================
    # 华北 — BEIJING
    # ============================================================
    {'name_zh': '南山', 'name_en': 'Nanshan', 'province': '北京',
     'lat': 40.4150, 'lon': 116.8761,
     'vertical_m': 218, 'trails': 25, 'lifts': 7,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '密云；北京最大的城郊雪场之一',
     'note_en': 'Miyun; major Beijing-area resort'},
    {'name_zh': '军都山', 'name_en': 'Jundushan', 'province': '北京',
     'lat': 40.2614, 'lon': 116.2317,
     'vertical_m': 230, 'trails': 11, 'lifts': 4,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '昌平；北京近郊',
     'note_en': 'Changping; close to Beijing'},
    {'name_zh': '渔阳', 'name_en': 'Yuyang', 'province': '北京',
     'lat': 40.0925, 'lon': 117.0828,
     'vertical_m': 235, 'trails': 16, 'lifts': 6,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '平谷',
     'note_en': 'Pinggu'},
    {'name_zh': '怀北国际', 'name_en': 'Huaibei International', 'province': '北京',
     'lat': 40.4278, 'lon': 116.6800,
     'vertical_m': 268, 'trails': 14, 'lifts': 4,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '怀柔',
     'note_en': 'Huairou'},
    {'name_zh': '八达岭', 'name_en': 'Badaling', 'province': '北京',
     'lat': 40.3531, 'lon': 116.0247,
     'vertical_m': 158, 'trails': 11, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '延庆',
     'note_en': 'Yanqing'},
    {'name_zh': '石京龙', 'name_en': 'Shijinglong', 'province': '北京',
     'lat': 40.4856, 'lon': 116.0508,
     'vertical_m': 235, 'trails': 9, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '延庆',
     'note_en': 'Yanqing'},
    {'name_zh': '延庆海陀', 'name_en': 'Haituo (Yanqing)', 'province': '北京',
     'lat': 40.5544, 'lon': 115.7919,
     'vertical_m': 900, 'trails': 21, 'lifts': 9,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '2022 北京冬奥会延庆赛区；首批国家级度假地',
     'note_en': '2022 Olympics Yanqing zone; 1st batch national resort'},

    # ============================================================
    # 华北 — HEBEI (崇礼 + 涞源 + 金山岭 + 张家口区域)
    # ============================================================
    # 崇礼"七大雪场"
    {'name_zh': '太舞', 'name_en': 'Thaiwoo', 'province': '河北',
     'lat': 40.9914, 'lon': 115.4906,
     'vertical_m': 510, 'trails': 38, 'lifts': 8,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '崇礼；2022 冬奥越野滑雪+冬两赛场所在区',
     'note_en': 'Chongli; 2022 Olympics cross-country/biathlon area'},
    {'name_zh': '云顶', 'name_en': 'Genting Secret Garden', 'province': '河北',
     'lat': 40.9783, 'lon': 115.5247,
     'vertical_m': 490, 'trails': 87, 'lifts': 18,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '崇礼；2022 冬奥自由式滑雪+单板赛场',
     'note_en': 'Chongli; 2022 Olympics freestyle/snowboard venue'},
    {'name_zh': '万龙', 'name_en': 'Wanlong', 'province': '河北',
     'lat': 40.9422, 'lon': 115.4569,
     'vertical_m': 550, 'trails': 31, 'lifts': 9,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '崇礼；老牌技术性雪场',
     'note_en': 'Chongli; established technical resort'},
    {'name_zh': '富龙', 'name_en': 'Fulong', 'province': '河北',
     'lat': 40.9744, 'lon': 115.2856,
     'vertical_m': 360, 'trails': 36, 'lifts': 6,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '崇礼；最近市区，"夜场之王"',
     'note_en': 'Chongli; closest to town, night-skiing focused'},
    {'name_zh': '长城岭', 'name_en': 'Changchengling', 'province': '河北',
     'lat': 40.9689, 'lon': 115.4106,
     'vertical_m': 220, 'trails': 16, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '崇礼；国家越野滑雪训练基地',
     'note_en': 'Chongli; national XC training base'},
    {'name_zh': '银河', 'name_en': 'Yinhe', 'province': '河北',
     'lat': 40.9628, 'lon': 115.5036,
     'vertical_m': 215, 'trails': 14, 'lifts': 3,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '崇礼；老雪场',
     'note_en': 'Chongli; legacy resort'},
    {'name_zh': '密苑', 'name_en': 'Miyun (Chongli)', 'province': '河北',
     'lat': 40.9806, 'lon': 115.4525,
     'vertical_m': 320, 'trails': 21, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '崇礼',
     'note_en': 'Chongli'},
    {'name_zh': '崇礼度假地', 'name_en': 'Chongli National Resort Designation', 'province': '河北',
     'lat': 40.9742, 'lon': 115.2772,
     'vertical_m': None, 'trails': None, 'lifts': None,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '崇礼区作为整体被认定为首批国家级度假地（不是单一雪场）',
     'note_en': 'County-level designation, not a single resort (1st batch)'},
    # Hebei other
    {'name_zh': '涞源七山', 'name_en': 'Qishan (Laiyuan)', 'province': '河北',
     'lat': 39.3550, 'lon': 114.6917,
     'vertical_m': 408, 'trails': 19, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '涞源七山度假区；首批国家级度假地',
     'note_en': 'Laiyuan Qishan; 1st batch national resort'},
    {'name_zh': '滦平金山岭', 'name_en': 'Jinshanling (Luanping)', 'province': '河北',
     'lat': 40.6900, 'lon': 117.2369,
     'vertical_m': 600, 'trails': 31, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 2,
     'note_zh': '滦平；第二批国家级度假地；规划落差 600 m',
     'note_en': 'Luanping; 2nd batch national resort'},
    {'name_zh': '翠云山银河', 'name_en': 'Cuiyunshan Yinhe', 'province': '河北',
     'lat': 40.9528, 'lon': 115.3458,
     'vertical_m': 230, 'trails': 12, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': False},

    # ============================================================
    # 华北 — INNER MONGOLIA
    # ============================================================
    {'name_zh': '扎兰屯金龙山', 'name_en': 'Jinlongshan (Zhalantun)', 'province': '内蒙古',
     'lat': 47.9461, 'lon': 122.6544,
     'vertical_m': 305, 'trails': 18, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '扎兰屯；首批国家级度假地',
     'note_en': 'Zhalantun; 1st batch national resort'},
    {'name_zh': '牙克石凤凰山', 'name_en': 'Fenghuangshan (Yakeshi)', 'province': '内蒙古',
     'lat': 49.2867, 'lon': 120.7325,
     'vertical_m': 405, 'trails': 24, 'lifts': 6,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 2,
     'note_zh': '牙克石；第二批国家级度假地',
     'note_en': 'Yakeshi; 2nd batch national resort'},
    {'name_zh': '喀喇沁美林谷', 'name_en': 'Meilin Valley (Harqin)', 'province': '内蒙古',
     'lat': 41.9469, 'lon': 118.7011,
     'vertical_m': 503, 'trails': 12, 'lifts': 1,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 2,
     'note_zh': '赤峰喀喇沁旗；第二批国家级度假地',
     'note_en': 'Chifeng Harqin; 2nd batch national resort'},
    {'name_zh': '马鬃山', 'name_en': 'Mazongshan (Hohhot)', 'province': '内蒙古',
     'lat': 40.7250, 'lon': 111.7850,
     'vertical_m': 300, 'trails': 12, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 3,
     'note_zh': '呼和浩特赛罕区；第三批国家级度假地',
     'note_en': 'Hohhot Saihan; 3rd batch national resort'},

    # ============================================================
    # 华北 — SHANXI
    # ============================================================
    {'name_zh': '广武', 'name_en': 'Guangwu (Shanyin)', 'province': '山西',
     'lat': 39.5039, 'lon': 112.7806,
     'vertical_m': 290, 'trails': 14, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 3,
     'note_zh': '朔州山阴；第三批国家级度假地',
     'note_en': 'Shuozhou Shanyin; 3rd batch national resort'},
    {'name_zh': '采薇庄园', 'name_en': 'Caiwei Estate (Taiyuan)', 'province': '山西',
     'lat': 37.7361, 'lon': 112.5497,
     'vertical_m': 180, 'trails': 9, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '太原市郊',
     'note_en': 'Taiyuan suburb'},
    {'name_zh': '云丘山', 'name_en': 'Yunqiushan', 'province': '山西',
     'lat': 35.7989, 'lon': 111.4631,
     'vertical_m': 280, 'trails': 13, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '临汾',
     'note_en': 'Linfen'},

    # ============================================================
    # 西北 — XINJIANG (大头部之一)
    # ============================================================
    # 阿勒泰泰旅集团 + 国家级度假地
    {'name_zh': '将军山', 'name_en': 'Jiangjunshan (Altay)', 'province': '新疆',
     'lat': 47.8633, 'lon': 88.1361,
     'vertical_m': 360, 'trails': 17, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '阿勒泰市区；首批国家级度假地（阿勒泰滑雪旅游度假地）核心',
     'note_en': 'Altay City; core of 1st batch Altay national resort'},
    {'name_zh': '可可托海国际', 'name_en': 'Koktokay International', 'province': '新疆',
     'lat': 47.1786, 'lon': 89.7167,
     'vertical_m': 1170, 'trails': 28, 'lifts': 8,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 2,
     'note_zh': '富蕴县；第二批国家级度假地；中国最大垂直落差',
     'note_en': "Fuyun; 2nd batch national resort; China's largest vertical drop"},
    {'name_zh': '吉克普林国际', 'name_en': 'Jikpurin International', 'province': '新疆',
     'lat': 48.7472, 'lon': 86.8186,
     'vertical_m': 920, 'trails': 56, 'lifts': 14,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 3,
     'note_zh': '布尔津；第三批国家级度假地；2024 新开业旗舰',
     'note_en': "Burqin; 3rd batch national resort; 2024 flagship opening"},
    {'name_zh': '阿勒泰野卡峡野雪公园', 'name_en': 'Yekaxia Backcountry Park', 'province': '新疆',
     'lat': 47.7700, 'lon': 88.1100,
     'vertical_m': 600, 'trails': 8, 'lifts': 3,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '将军山周边野雪公园',
     'note_en': 'Backcountry park near Jiangjunshan'},
    {'name_zh': '阿尔泰山野雪公园', 'name_en': 'Altai Mountain Backcountry Park', 'province': '新疆',
     'lat': 47.7900, 'lon': 88.0900,
     'vertical_m': 520, 'trails': 6, 'lifts': 2,
     'tier': '目的地度假型', 'national_tier': False},
    {'name_zh': '禾木', 'name_en': 'Hemu', 'province': '新疆',
     'lat': 48.6464, 'lon': 87.4194,
     'vertical_m': 380, 'trails': 12, 'lifts': 3,
     'tier': '旅游体验型', 'national_tier': False,
     'note_zh': '布尔津；以毛皮滑雪传统闻名',
     'note_en': 'Burqin; famed for traditional fur-ski heritage'},
    # 乌鲁木齐南山
    {'name_zh': '丝绸之路国际度假区', 'name_en': 'Silk Road International', 'province': '新疆',
     'lat': 43.4464, 'lon': 87.2750,
     'vertical_m': 510, 'trails': 31, 'lifts': 11,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '乌鲁木齐南山；首批国家级度假地核心',
     'note_en': 'Urumqi Nanshan; core of 1st batch national resort'},
    {'name_zh': '白云国际', 'name_en': 'Baiyun International', 'province': '新疆',
     'lat': 43.4297, 'lon': 87.3025,
     'vertical_m': 380, 'trails': 18, 'lifts': 6,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '乌鲁木齐南山片区',
     'note_en': 'Urumqi Nanshan area'},
    {'name_zh': '雪莲山', 'name_en': 'Xuelianshan (Urumqi)', 'province': '新疆',
     'lat': 43.6831, 'lon': 87.6086,
     'vertical_m': 80, 'trails': 6, 'lifts': 2,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '乌鲁木齐市区',
     'note_en': 'Within Urumqi city'},
    {'name_zh': '伊犁新源', 'name_en': 'Xinyuan (Yili)', 'province': '新疆',
     'lat': 43.4350, 'lon': 83.2467,
     'vertical_m': 350, 'trails': 14, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 3,
     'note_zh': '伊犁哈萨克自治州新源县；第三批国家级度假地',
     'note_en': 'Yili Xinyuan; 3rd batch national resort'},

    # ============================================================
    # 西北 — SHAANXI (rising)
    # ============================================================
    {'name_zh': '太白山鳌山', 'name_en': 'Aoshan (Taibai)', 'province': '陕西',
     'lat': 34.0467, 'lon': 107.6889,
     'vertical_m': 520, 'trails': 23, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '宝鸡太白；首批国家级度假地；陕西头部',
     'note_en': 'Baoji Taibai; 1st batch national resort; Shaanxi flagship'},
    {'name_zh': '照金国际', 'name_en': 'Zhaojin International', 'province': '陕西',
     'lat': 35.0697, 'lon': 108.7456,
     'vertical_m': 240, 'trails': 14, 'lifts': 4,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '铜川；陕西头部之一',
     'note_en': 'Tongchuan; Shaanxi major'},
    {'name_zh': '翠华山', 'name_en': 'Cuihuashan', 'province': '陕西',
     'lat': 33.9647, 'lon': 109.1239,
     'vertical_m': 180, 'trails': 8, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '西安近郊',
     'note_en': 'Xi\'an suburb'},

    # ============================================================
    # 西北 — GANSU
    # ============================================================
    {'name_zh': '法台山', 'name_en': 'Fataishan', 'province': '甘肃',
     'lat': 35.4308, 'lon': 103.3083,
     'vertical_m': 260, 'trails': 12, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 3,
     'note_zh': '临夏和政县；第三批国家级度假地',
     'note_en': 'Linxia Hezheng; 3rd batch national resort'},
    {'name_zh': '崆峒山', 'name_en': 'Kongtongshan', 'province': '甘肃',
     'lat': 35.5444, 'lon': 106.5311,
     'vertical_m': 200, 'trails': 9, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '平凉',
     'note_en': 'Pingliang'},

    # ============================================================
    # 西北 — QINGHAI / NINGXIA
    # ============================================================
    {'name_zh': '岗什卡', 'name_en': 'Gangshika', 'province': '青海',
     'lat': 37.8689, 'lon': 101.7167,
     'vertical_m': 1200, 'trails': 6, 'lifts': 2,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '门源；以越野滑雪登山闻名',
     'note_en': 'Menyuan; ski mountaineering destination'},
    {'name_zh': '互助北山', 'name_en': 'Beishan (Huzhu)', 'province': '青海',
     'lat': 36.9222, 'lon': 102.0500,
     'vertical_m': 350, 'trails': 14, 'lifts': 4,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '西宁周边',
     'note_en': 'Near Xining'},
    {'name_zh': '苏峪口', 'name_en': 'Suyukou', 'province': '宁夏',
     'lat': 38.6056, 'lon': 105.9550,
     'vertical_m': 280, 'trails': 11, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '银川贺兰山',
     'note_en': 'Helan Mountain near Yinchuan'},

    # ============================================================
    # 华中 — HUBEI
    # ============================================================
    {'name_zh': '神农架国际', 'name_en': 'Shennongjia International', 'province': '湖北',
     'lat': 31.6500, 'lon': 110.6800,
     'vertical_m': 220, 'trails': 18, 'lifts': 6,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '神农架；首批国家级度假地；中国南方少数有真雪外场之一',
     'note_en': "Shennongjia; 1st batch national resort; rare southern outdoor"},
    {'name_zh': '九宫山', 'name_en': 'Jiugongshan', 'province': '湖北',
     'lat': 29.4128, 'lon': 114.6925,
     'vertical_m': 130, 'trails': 8, 'lifts': 3,
     'tier': '旅游体验型', 'national_tier': False,
     'note_zh': '咸宁',
     'note_en': 'Xianning'},

    # ============================================================
    # 华中 — HENAN
    # ============================================================
    {'name_zh': '老界岭', 'name_en': 'Laojieling', 'province': '河南',
     'lat': 33.5167, 'lon': 111.9667,
     'vertical_m': 280, 'trails': 13, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 2,
     'note_zh': '南阳西峡；第二批国家级度假地；河南头部',
     'note_en': "Nanyang Xixia; 2nd batch national resort"},
    {'name_zh': '伏牛山', 'name_en': 'Funiushan', 'province': '河南',
     'lat': 33.6311, 'lon': 111.8472,
     'vertical_m': 175, 'trails': 9, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},

    # ============================================================
    # 西南 — SICHUAN (active development zone)
    # ============================================================
    {'name_zh': '西岭雪山', 'name_en': 'Xiling Snow Mountain', 'province': '四川',
     'lat': 30.7800, 'lon': 103.1900,
     'vertical_m': 432, 'trails': 21, 'lifts': 7,
     'tier': '目的地度假型', 'national_tier': True, 'national_batch': 1,
     'note_zh': '大邑；首批国家级度假地；西南最大；核心区 483 km² 列国家级最大',
     'note_en': "Dayi; 1st batch national resort; largest in Southwest"},
    {'name_zh': '太子岭', 'name_en': 'Taiziling', 'province': '四川',
     'lat': 31.0533, 'lon': 102.9244,
     'vertical_m': 320, 'trails': 14, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '理县；藏区',
     'note_en': 'Lixian; Tibetan area'},
    {'name_zh': '鹧鸪山', 'name_en': 'Zhegushan', 'province': '四川',
     'lat': 31.7814, 'lon': 102.8553,
     'vertical_m': 400, 'trails': 16, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '理县米亚罗',
     'note_en': 'Lixian Miyaluo'},
    {'name_zh': '九鼎山太子岭', 'name_en': 'Jiudingshan', 'province': '四川',
     'lat': 31.8458, 'lon': 103.7864,
     'vertical_m': 280, 'trails': 12, 'lifts': 3,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '茂县',
     'note_en': 'Maoxian'},
    {'name_zh': '峨眉山', 'name_en': 'Emeishan', 'province': '四川',
     'lat': 29.5167, 'lon': 103.3333,
     'vertical_m': 150, 'trails': 5, 'lifts': 2,
     'tier': '旅游体验型', 'national_tier': False,
     'note_zh': '峨眉山金顶',
     'note_en': 'Mt. Emei summit area'},

    # ============================================================
    # 西南 — CHONGQING / GUIZHOU / YUNNAN
    # ============================================================
    {'name_zh': '仙女山', 'name_en': 'Xiannvshan', 'province': '重庆',
     'lat': 29.4400, 'lon': 107.7350,
     'vertical_m': 200, 'trails': 9, 'lifts': 3,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '武隆',
     'note_en': 'Wulong'},
    {'name_zh': '金佛山北坡', 'name_en': 'Jinfoshan North', 'province': '重庆',
     'lat': 29.0297, 'lon': 107.1583,
     'vertical_m': 235, 'trails': 11, 'lifts': 3,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '南川',
     'note_en': 'Nanchuan'},
    {'name_zh': '六盘水梅花山', 'name_en': 'Meihuashan (Liupanshui)', 'province': '贵州',
     'lat': 26.4567, 'lon': 104.7536,
     'vertical_m': 300, 'trails': 15, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '六盘水；中国最南端的高山滑雪场之一',
     'note_en': "Liupanshui; among China's southernmost real-snow resorts"},
    {'name_zh': '玉舍', 'name_en': 'Yushe', 'province': '贵州',
     'lat': 26.4072, 'lon': 104.7183,
     'vertical_m': 250, 'trails': 10, 'lifts': 3,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '六盘水',
     'note_en': 'Liupanshui'},
    {'name_zh': '玉龙雪山', 'name_en': 'Yulong Snow Mountain', 'province': '云南',
     'lat': 27.1019, 'lon': 100.1858,
     'vertical_m': 200, 'trails': 5, 'lifts': 2,
     'tier': '旅游体验型', 'national_tier': False,
     'note_zh': '丽江；高海拔自然雪',
     'note_en': 'Lijiang; high-altitude natural snow'},
    {'name_zh': '会泽大海草山', 'name_en': 'Dahaicaoshan (Huize)', 'province': '云南',
     'lat': 26.4639, 'lon': 103.4344,
     'vertical_m': 180, 'trails': 7, 'lifts': 2,
     'tier': '旅游体验型', 'national_tier': False},

    # ============================================================
    # 华东 — small but representative outdoor (mostly low-elevation)
    # ============================================================
    {'name_zh': '绍兴乔波', 'name_en': 'Qiaobo Shaoxing', 'province': '浙江',
     'lat': 29.9367, 'lon': 120.6300,
     'vertical_m': 60, 'trails': 5, 'lifts': 2,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '绍兴；江南罕见户外雪场',
     'note_en': 'Shaoxing; rare southern outdoor resort'},
    {'name_zh': '安吉江南天池', 'name_en': 'Tianchi (Anji)', 'province': '浙江',
     'lat': 30.6500, 'lon': 119.7333,
     'vertical_m': 100, 'trails': 6, 'lifts': 2,
     'tier': '旅游体验型', 'national_tier': False,
     'note_zh': '湖州安吉',
     'note_en': 'Anji'},
    {'name_zh': '徽州大青山', 'name_en': 'Daqingshan (Huizhou)', 'province': '安徽',
     'lat': 30.0167, 'lon': 118.0333,
     'vertical_m': 120, 'trails': 7, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},

    # ============================================================
    # 东北 — additional Heilongjiang & supplementals
    # ============================================================
    {'name_zh': '阿尔山', 'name_en': 'Arxan', 'province': '内蒙古',
     'lat': 47.1761, 'lon': 119.9425,
     'vertical_m': 380, 'trails': 16, 'lifts': 5,
     'tier': '目的地度假型', 'national_tier': False,
     'note_zh': '兴安盟；高纬度长雪期',
     'note_en': "High latitude; long season"},
    {'name_zh': '伊春梅花山', 'name_en': 'Meihuashan (Yichun)', 'province': '黑龙江',
     'lat': 47.7281, 'lon': 128.8400,
     'vertical_m': 240, 'trails': 11, 'lifts': 4,
     'tier': '目的地度假型', 'national_tier': False},
    {'name_zh': '北极星', 'name_en': 'Beijixing (Mohe)', 'province': '黑龙江',
     'lat': 53.4717, 'lon': 122.3603,
     'vertical_m': 150, 'trails': 6, 'lifts': 2,
     'tier': '旅游体验型', 'national_tier': False,
     'note_zh': '漠河；中国最北滑雪场',
     'note_en': "Mohe; China's northernmost ski area"},

    # ============================================================
    # 山东 — small but indicative
    # ============================================================
    {'name_zh': '青岛藏马山', 'name_en': 'Cangmashan (Qingdao)', 'province': '山东',
     'lat': 35.7619, 'lon': 119.7811,
     'vertical_m': 180, 'trails': 10, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},
    {'name_zh': '威海里口山', 'name_en': 'Likoushan (Weihai)', 'province': '山东',
     'lat': 37.4933, 'lon': 122.0539,
     'vertical_m': 75, 'trails': 5, 'lifts': 2,
     'tier': '城郊学习型', 'national_tier': False},

    # ============================================================
    # 河北 — additional supplementals (outside Chongli cluster)
    # ============================================================
    {'name_zh': '承德元宝山', 'name_en': 'Yuanbaoshan (Chengde)', 'province': '河北',
     'lat': 40.9700, 'lon': 117.9275,
     'vertical_m': 220, 'trails': 12, 'lifts': 4,
     'tier': '城郊学习型', 'national_tier': False},
    {'name_zh': '秦皇岛紫金山', 'name_en': 'Zijinshan (Qinhuangdao)', 'province': '河北',
     'lat': 40.0500, 'lon': 119.5500,
     'vertical_m': 110, 'trails': 7, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},
    {'name_zh': '保定狼牙山', 'name_en': 'Langyashan (Baoding)', 'province': '河北',
     'lat': 39.3508, 'lon': 114.7333,
     'vertical_m': 160, 'trails': 8, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},

    # ============================================================
    # 吉林 — additional supplementals
    # ============================================================
    {'name_zh': '延吉帽儿山', 'name_en': 'Mao\'er Shan (Yanji)', 'province': '吉林',
     'lat': 42.8825, 'lon': 129.5172,
     'vertical_m': 165, 'trails': 8, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False,
     'note_zh': '延边朝鲜族自治州',
     'note_en': 'Yanbian Korean Autonomous Prefecture'},
    {'name_zh': '通化金厂', 'name_en': 'Jinchang (Tonghua)', 'province': '吉林',
     'lat': 41.6508, 'lon': 125.7847,
     'vertical_m': 170, 'trails': 9, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},

    # ============================================================
    # 辽宁 — additional supplementals
    # ============================================================
    {'name_zh': '大连林海', 'name_en': 'Linhai (Dalian)', 'province': '辽宁',
     'lat': 39.1450, 'lon': 121.7194,
     'vertical_m': 105, 'trails': 7, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},
    {'name_zh': '抚顺御龙湾', 'name_en': 'Yulongwan (Fushun)', 'province': '辽宁',
     'lat': 41.8950, 'lon': 124.0011,
     'vertical_m': 175, 'trails': 9, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},
    {'name_zh': '鞍山千山温泉', 'name_en': 'Qianshan Hot Spring', 'province': '辽宁',
     'lat': 41.0269, 'lon': 122.9583,
     'vertical_m': 130, 'trails': 7, 'lifts': 3,
     'tier': '城郊学习型', 'national_tier': False},
]


def main():
    # Augment each resort with derived fields
    out_resorts = []
    for r in RESORTS:
        province = r['province']
        region = PROVINCE_TO_REGION[province]
        r_out = dict(r)
        r_out['region'] = region
        r_out['region_en'] = REGION_EN[region]
        r_out['province_en'] = PROVINCE_EN[province]
        out_resorts.append(r_out)

    # Stats
    from collections import Counter
    by_region = Counter(r['region'] for r in out_resorts)
    by_province = Counter(r['province'] for r in out_resorts)
    by_tier = Counter(r['tier'] for r in out_resorts)
    n_national = sum(1 for r in out_resorts if r.get('national_tier'))

    print(f'Total resorts: {len(out_resorts)}')
    print(f'\nBy region:')
    for region, count in sorted(by_region.items(), key=lambda x: -x[1]):
        print(f'  {region}: {count}')
    print(f'\nBy province:')
    for province, count in sorted(by_province.items(), key=lambda x: -x[1]):
        print(f'  {province} ({PROVINCE_EN[province]}): {count}')
    print(f'\nBy tier:')
    for tier, count in by_tier.items():
        print(f'  {tier}: {count}')
    print(f'\nNational tier resorts: {n_national}')

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = {
        'meta': {
            'description': 'Outdoor ski resorts in China; ~100 resorts representing the bulk of national skier visits per the 2024-2025 China Ski Industry White Book',
            'count': len(out_resorts),
            'source_notes': 'Coordinates and stats from public sources (resort sites, white book disclosures, government tourism portals). National-tier flag from official MCT/Sports Administration designations across 3 batches (2022/2023/2024).',
            'scope': 'Outdoor only (室内滑雪场 indoor resorts deliberately excluded)',
            'regions': list(REGION_EN.keys()),
        },
        'resorts': out_resorts,
    }
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\nSaved to {OUTPUT_PATH}: {OUTPUT_PATH.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
