// Aviation safety map: hull-loss and significant accidents in commercial aviation.
// Each entry is fact-only — no editorial framing or "lessons" — written for personal
// reference and conversation, not pedagogy. Entries are in chronological order.
//
// Field schema:
//   id            — short slug
//   date          — YYYY-MM-DD
//   airline       — operating airline at time of accident
//   flight        — flight number
//   aircraft      — model + variant
//   registration  — tail/registration number
//   lat, lon      — crash site coordinates (decimal degrees)
//   location      — human-readable location
//   fatalities    — { onboard, ground, total, occupants } where occupants is total persons aboard
//   phase         — flight phase (taxi/takeoff/climb/cruise/descent/approach/landing)
//   category      — primary category (CFIT, LOC-I, runway, midair, fire, structural, weather, security, other)
//   summary_zh    — 中文事实陈述 (2-5 sentences)
//   summary_en    — English fact statement (2-5 sentences)
//   links         — array of { label, url } pointing to authoritative sources

window.ACCIDENTS = [

  // 1. ─── Eastern Air Lines Flight 401 ──────────────────────────────────
  {
    id: 'ea401',
    date: '1972-12-29',
    airline: 'Eastern Air Lines',
    flight: '401',
    aircraft: 'Lockheed L-1011-1 TriStar',
    registration: 'N310EA',
    lat: 25.8588,
    lon: -80.5905,
    location: 'Florida Everglades, USA (18.7 mi WNW of Miami International)',
    fatalities: { onboard: 101, ground: 0, total: 101, occupants: 176 },
    phase: 'approach',
    category: 'CFIT',
    summary_zh: '夜间飞往迈阿密的进近段，前起落架指示灯未亮起。三名机组成员均被这一灯泡问题占据注意力，未察觉自动驾驶在某次轻微的驾驶杆触碰后切出高度保持模式，飞机以缓慢恒定的下沉率撞入沼泽。NTSB 将事故归因于飞行机组未能监控仪表，由此事故与 1978 年的联合 173 号航班一同成为机组资源管理（CRM）训练在 1980 年代成为业内标准做法的直接催化剂。该机为洛克希德 L-1011 的首次坠毁。',
    summary_en: 'On a night approach to Miami, the nose-gear indicator light failed to illuminate. All three flight-deck crew became preoccupied with the bulb problem; none noticed that the autopilot had disengaged from altitude hold after a slight inadvertent yoke touch, and the aircraft descended at a slow constant rate into the swamp. The NTSB attributed the accident to failure to monitor flight instruments. Together with United 173 (1978), this accident is the direct catalyst for crew resource management (CRM) training becoming standard industry practice in the 1980s. It was the first hull loss of the Lockheed L-1011.',
    links: [
      { label: "NTSB Aircraft Accident Report AAR-73/14", url: "https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR7314.pdf" },
      { label: "FAA Lessons Learned: L-1011 N310EA", url: "https://www.faa.gov/lessons_learned/transport_airplane/accidents/N310EA" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/Eastern_Air_Lines_Flight_401" }
    ]
  },

  // 2. ─── Turkish Airlines Flight 981 ──────────────────────────────────
  {
    id: 'thy981',
    date: '1974-03-03',
    airline: 'Turkish Airlines (THY)',
    flight: '981',
    aircraft: 'McDonnell Douglas DC-10-10',
    registration: 'TC-JAV',
    lat: 49.1457,
    lon: 2.6346,
    location: 'Ermenonville Forest, France (37 km NE of Paris)',
    fatalities: { onboard: 346, ground: 0, total: 346, occupants: 346 },
    phase: 'climb',
    category: 'structural',
    summary_zh: '起飞后约十分钟，DC-10 后货舱门在 11,000 英尺高度脱落。爆炸性减压使客舱地板部分塌陷，并切断了铺设在地板下的全部俯仰操纵索；机组失去俯仰控制，77 秒后飞机以 800 公里/时撞入森林，机上 346 人全部罹难。两年前美国航空 96 号航班在加拿大温莎已发生同型货舱门爆开事件，机组凭运气改出降落；麦道公司内部备忘（"阿普尔盖特备忘录"）已识别该设计缺陷，但相关服务通告不具强制性。事故后 FAA 立即发布强制性适航指令重新设计 DC-10 货舱门并要求所有大型客机加装地板泄压通风口。',
    summary_en: 'About ten minutes after takeoff, the DC-10\'s aft cargo door blew off at 11,000 feet. The explosive decompression collapsed part of the cabin floor and severed all pitch-control cables routed beneath it; the crew lost pitch control, and 77 seconds later the aircraft struck forest at 800 km/h, killing all 346 aboard. American Airlines flight 96 had suffered the same door failure two years earlier over Windsor, Ontario, and survived only by luck; McDonnell Douglas had internally identified the flaw (the "Applegate memo"), but service bulletins were non-mandatory. After the crash the FAA issued an immediate airworthiness directive redesigning the DC-10 cargo door and requiring vented cabin floors on all large jets.',
    links: [
      { label: "FAA Lessons Learned: DC-10 TC-JAV", url: "https://www.faa.gov/lessons_learned/transport_airplane/accidents/TC-JAV" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/Turkish_Airlines_Flight_981" }
    ]
  },

  // 3. ─── Tenerife (KLM 4805 + Pan Am 1736) ────────────────────────────
  {
    id: 'tenerife',
    date: '1977-03-27',
    airline: 'KLM / Pan Am',
    flight: '4805 / 1736 (Tenerife)',
    aircraft: 'Boeing 747-206B (KLM) + Boeing 747-121 (Pan Am)',
    registration: 'PH-BUF + N736PA',
    lat: 28.4827,
    lon: -16.3415,
    location: 'Los Rodeos Airport (TFN), Tenerife, Canary Islands, Spain',
    fatalities: { onboard: 583, ground: 0, total: 583, occupants: 644 },
    phase: 'takeoff',
    category: 'runway',
    summary_zh: '两架被前一日大加那利岛炸弹爆炸事件改飞至此的 747 在浓雾中的同一条跑道上相撞。荷兰皇家航空机长在塔台未发出起飞许可的情况下开始起飞滑跑，原因系一段含糊的发话被同时无线电传输部分覆盖。泛美航空 747 当时仍在沿同一跑道反向滑行寻找出口。荷航撞穿泛美机身后段；荷航全部 248 人遇难，泛美 396 人中 335 人遇难，幸存 61 人。这是民用航空史上死亡人数最多的事故，并直接催生了对国际通话用语的全面整改和机组资源管理（CRM）的概念。',
    summary_en: 'Two 747s, both diverted to Tenerife by a bombing the previous day at Gran Canaria, collided on the same runway in heavy fog. The KLM captain began his takeoff roll without takeoff clearance, after an ambiguous transmission was partly stepped on by simultaneous radio traffic. The Pan Am aircraft was still backtracking on the same runway looking for its exit. KLM struck the Pan Am 747 in the upper fuselage; all 248 aboard KLM died, and 335 of 396 aboard Pan Am died, with 61 survivors. It remains the deadliest accident in civil aviation history, and led directly to the global overhaul of standard radiotelephony phraseology and to the formal development of crew resource management (CRM).',
    links: [

      { label: "SKYbrary: Tenerife disaster", url: "https://skybrary.aero/accidents-and-incidents/b742-b741-tenerife-canary-islands-spain-1977" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/Tenerife_airport_disaster" }
    ]
  },

  // 4. ─── United Airlines Flight 173 ───────────────────────────────────
  {
    id: 'ua173',
    date: '1978-12-28',
    airline: 'United Airlines',
    flight: '173',
    aircraft: 'McDonnell Douglas DC-8-61',
    registration: 'N8082U',
    lat: 45.5316,
    lon: -122.5347,
    location: 'Portland, Oregon, USA (suburban, ~6 nmi SE of PDX)',
    fatalities: { onboard: 10, ground: 0, total: 10, occupants: 189 },
    phase: 'approach',
    category: 'fuel exhaustion',
    summary_zh: '波音 DC-8 在波特兰进近时因起落架指示异常进入等待航线排查问题。机长被起落架问题占据注意力达约一小时，副驾驶与飞行机械员的燃油警示未能有效传达；四台发动机相继因燃油耗尽停车，飞机滑翔坠入郊区树林。NTSB 将此案与 Eastern 401 一并视为机组互动模式失效的典型事例。次年 NASA 召集了一次研讨会催生了机组资源管理（CRM），联合航空 1980 年率先在业内实施——这次事故是 CRM 项目的直接命名起源。',
    summary_en: 'A DC-8 entered a hold near Portland with a landing-gear indication problem. The captain spent about an hour on the gear issue while fuel warnings from the first officer and flight engineer failed to register; all four engines flamed out from fuel exhaustion, and the aircraft glided into a wooded suburb. The NTSB grouped this case with Eastern 401 as a paradigm of crew-interaction failure. NASA convened a workshop the following year that produced what became crew resource management (CRM); United Airlines became the first carrier to implement it, in 1980 — this accident is the program\'s naming origin.',
    links: [
      { label: "NTSB Accident Report AAR-79/07", url: "https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR7907.pdf" },
      { label: "NTSB Investigation Page", url: "https://www.ntsb.gov/investigations/Pages/DCA79AA005.aspx" },
      { label: "FAA Lessons Learned: DC-8 N8082U", url: "https://www.faa.gov/lessons_learned/transport_airplane/accidents/N8082U" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/United_Airlines_Flight_173" }
    ]
  },

  // 5. ─── American Airlines Flight 191 ─────────────────────────────────
  {
    id: 'aa191',
    date: '1979-05-25',
    airline: 'American Airlines',
    flight: '191',
    aircraft: 'McDonnell Douglas DC-10-10',
    registration: 'N110AA',
    lat: 41.9942,
    lon: -87.9069,
    location: 'Chicago O\'Hare International Airport, USA',
    fatalities: { onboard: 271, ground: 2, total: 273, occupants: 271 },
    phase: 'takeoff',
    category: 'structural',
    summary_zh: '起飞旋转瞬间，左侧发动机连同其挂架从机翼整体脱落，向上向后翻越机翼。脱落过程切断了多条液压管路并锁定了左翼前缘缝翼，导致左翼失速、飞机迅速向左滚转，在距跑道头不到一英里处近乎倒扣撞地。31 秒过程。NTSB 调查发现脱落根源是美国航空采用的非标准维护规程——以叉车整体安装"发动机加挂架"组件——在挂架后接耳处累积疲劳裂纹。该事故仍是美国本土死亡人数最多的民航事故，导致 DC-10 短暂全球停飞与维护规程整改。',
    summary_en: 'At the moment of takeoff rotation, the left engine and its pylon separated as a unit from the wing and flipped up and over the leading edge. The separation severed multiple hydraulic lines and locked the left-wing slats retracted; the asymmetric stall rolled the aircraft sharply left, and it struck the ground in a near-inverted attitude less than a mile past the runway end. Total elapsed time: 31 seconds. The NTSB found the root cause in a non-standard maintenance procedure adopted by American Airlines — using a forklift to install the engine-and-pylon as a single unit — which had introduced fatigue cracks in the rear pylon attachment. It remains the deadliest aviation accident on U.S. soil, and led to a temporary global grounding of the DC-10 and an overhaul of maintenance procedures.',
    links: [
      { label: "NTSB Accident Report AAR-79/17", url: "https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR7917.pdf" },
      { label: "FAA Lessons Learned: DC-10 N110AA", url: "https://www.faa.gov/lessons_learned/transport_airplane/accidents/N110AA" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/American_Airlines_Flight_191" }
    ]
  },

  // 6. ─── Air Canada Flight 797 ────────────────────────────────────────
  {
    id: 'ac797',
    date: '1983-06-02',
    airline: 'Air Canada',
    flight: '797',
    aircraft: 'McDonnell Douglas DC-9-32',
    registration: 'C-FTLU',
    lat: 39.0488,
    lon: -84.6678,
    location: 'Greater Cincinnati Airport (CVG), Kentucky, USA',
    fatalities: { onboard: 23, ground: 0, total: 23, occupants: 46 },
    phase: 'descent',
    category: 'fire',
    summary_zh: '巡航高度上后部洗手间起火，机组在四分钟内决定改飞辛辛那提紧急落地。烟雾迅速充满机舱，电子系统逐一失效。落地后机舱门与紧急出口打开瞬间引入新鲜空气，残余热气与可燃气体发生闪燃（flashover），尚未撤离的 23 名乘客瞬间罹难。事故直接催生了一系列机舱安全标准重写：座椅靠垫使用阻燃材料、洗手间废纸桶强制配备烟雾探测器、地板紧急出口指示灯（用于烟雾中辨识方向）、机组烟雾应急训练规范化。',
    summary_en: 'A fire began in the rear lavatory at cruise altitude. The crew diverted to Cincinnati within four minutes, but smoke filled the cabin and electrical systems failed one by one. When the doors and exits opened on landing, the inrush of fresh air caused the remaining hot combustible gases to flash over; 23 passengers who had not yet evacuated died instantly. The accident drove a comprehensive rewrite of cabin safety standards: fire-blocking seat covers, mandatory lavatory smoke detectors, floor-level emergency lighting strips (for smoke navigation), and standardised crew smoke-and-fire response training.',
    links: [
      { label: "NTSB Accident Report AAR-86/02 (re-investigated)", url: "https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR8602.pdf" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/Air_Canada_Flight_797" }
    ]
  },

  // 7. ─── KAL 007 (Sakhalin shoot-down) ───────────────────────
  {
    id: 'kal007',
    date: '1983-09-01',
    airline: 'Korean Air Lines',
    flight: '007',
    aircraft: 'Boeing 747-230B',
    registration: 'HL7442',
    lat: 46.6,
    lon: 141.3,
    location: 'Sea of Japan, near Sakhalin Island, USSR',
    fatalities: { onboard: 269, ground: 0, total: 269, occupants: 269 },
    phase: 'cruise',
    category: 'security',
    summary_zh: '由纽约经安克雷奇飞往汉城（首尔）的 747-200 偏离航线进入苏联领空（堪察加半岛与库页岛上空），被苏军 Su-15 截击机以两枚 R-98 导弹击落。机上 269 人全部罹难，包括美国国会议员 Larry McDonald。冷战期间著名事件之一；事后美国总统里根下令 GPS 在系统建成后向民用全面开放，从军用专属转为民用基础设施——这是现代民航全球导航的基础。事故偏航原因调查结论：机组在起飞后将自动驾驶设为磁航向（HDG）模式而非 INS（惯性导航）模式，未察觉持续的航向偏差。',
    summary_en: 'A 747-200 from New York via Anchorage to Seoul deviated from its assigned track and entered Soviet airspace over Kamchatka and Sakhalin, where it was shot down by a Soviet Su-15 interceptor with two R-98 missiles. All 269 aboard died, including U.S. Congressman Larry McDonald. A signature event of the late Cold War; in its aftermath, U.S. President Reagan ordered that GPS — then a military-only system — be opened to civilian use upon completion. That decision is the foundation of modern global civil navigation. The investigation concluded that the crew had set the autopilot to magnetic heading (HDG) mode rather than INS (inertial navigation), and had not noticed the slowly accumulating cross-track error.',
    links: [
      { label: 'ICAO 1993 Final Report (English)', url: 'https://reports.aviation-safety.net/1983/19830901-0_B742_HL7442.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Korean_Air_Lines_Flight_007' }
    ]
  },

  // 8. ─── Delta Air Lines Flight 191 ───────────────────────────────────
  {
    id: 'dl191',
    date: '1985-08-02',
    airline: 'Delta Air Lines',
    flight: '191',
    aircraft: 'Lockheed L-1011-385-1 TriStar',
    registration: 'N726DA',
    lat: 32.8998,
    lon: -97.0403,
    location: 'Dallas-Fort Worth International Airport (DFW), Texas, USA',
    fatalities: { onboard: 134, ground: 1, total: 135, occupants: 163 },
    phase: 'approach',
    category: 'weather',
    summary_zh: 'L-1011 在 DFW 五边进近段穿越一团孤立雷暴胞，遭遇强微下击暴流，顶风在数秒内变为强尾风，空速骤降，飞机失去升力撞地。撞击点位于跑道入口前一英里处，飞机弹起后撞上一辆水箱与机场跑道附近的两座大型水罐起火。134 人罹难。事故直接推动美国全境部署多普勒终端气象雷达（TDWR）、机载预测式风切变探测系统标准化，并促成微下击暴流回避程序写入所有航线运行手册。',
    summary_en: 'The L-1011 flew through an isolated thunderstorm cell on final to DFW and encountered a severe microburst: the headwind reversed to a strong tailwind within seconds, airspeed collapsed, and the aircraft lost lift and struck the ground a mile short of the runway. After bouncing, it struck a water tank near the field and burned. 134 died. The accident drove the U.S.-wide deployment of Terminal Doppler Weather Radar (TDWR), the standardisation of airborne predictive wind-shear warning systems, and the inclusion of microburst-avoidance procedures in every airline operations manual.',
    links: [
      { label: "NTSB Accident Report AAR-86/05", url: "https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR8605.pdf" },
      { label: "FAA Lessons Learned: L-1011 N726DA", url: "https://www.faa.gov/lessons_learned/transport_airplane/accidents/N726DA" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/Delta_Air_Lines_Flight_191" }
    ]
  },

  // 9. ─── Japan Airlines Flight 123 ────────────────────────────────────
  {
    id: 'jal123',
    date: '1985-08-12',
    airline: 'Japan Airlines',
    flight: '123',
    aircraft: 'Boeing 747SR-46',
    registration: 'JA8119',
    lat: 36.0010,
    lon: 138.6924,
    location: 'Mount Takamagahara (Osutaka Ridge), Gunma Prefecture, Japan',
    fatalities: { onboard: 520, ground: 0, total: 520, occupants: 524 },
    phase: 'climb',
    category: 'structural',
    summary_zh: '起飞后约十二分钟，机身后部加压隔框（aft pressure bulkhead）爆裂性失效，扯断垂直安定面与四套液压系统，飞机失去全部常规飞行操纵。机组通过差动推力维持空中悬浮长达 32 分钟——驾驶舱话音记录显示机长林、副驾驶佐佐木、机械师福田在不可能的处境下持续做着教科书无解的工作——最终撞入御巢鹰山脊。524 人中 520 人罹难，4 名女性幸存。失效的 aft pressure bulkhead 在 1978 年大阪机场尾擦事故后由波音工程师以非标准的单排铆钉修复（应为双排），疲劳累积约 12,000 起降循环后断裂。这是单架飞机死亡人数最多的事故，至今仍是日本航空业最深的伤痕。',
    summary_en: 'About twelve minutes after takeoff, the aft pressure bulkhead failed explosively, tearing off most of the vertical stabilizer and severing all four hydraulic systems; the aircraft lost all conventional flight controls. The crew kept it airborne for 32 minutes using differential thrust — the cockpit voice recording shows captain Takahama, first officer Sasaki, and flight engineer Fukuda working a problem with no textbook solution under impossible conditions — before it struck the Osutaka ridge. 520 of 524 aboard died; four women survived. The failed bulkhead had been repaired by a Boeing engineer following a 1978 tail-strike at Osaka with a non-standard single-row rivet splice (the correct repair specified two rows), and fatigue cracks propagated over roughly 12,000 pressurisation cycles before failure. It remains the deadliest single-aircraft accident in history and the deepest scar in Japanese commercial aviation.',
    links: [
      { label: "Aircraft Accident Investigation Commission Final Report (English)", url: "https://www.mlit.go.jp/jtsb/eng-air_report/JA8119.pdf" },
      { label: "SKYbrary: JL123", url: "https://skybrary.aero/accidents-and-incidents/b742-mt-osutaka-japan-1985" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/Japan_Air_Lines_Flight_123" }
    ]
  },

  // 10. ─── Arrow Air Flight 1285 ────────────────────────────────────────
  {
    id: 'arrow1285',
    date: '1985-12-12',
    airline: 'Arrow Air',
    flight: '1285R',
    aircraft: 'McDonnell Douglas DC-8-63',
    registration: 'N950JW',
    lat: 48.9469,
    lon: -54.5644,
    location: 'Gander International Airport (CYQX), Newfoundland, Canada',
    fatalities: { onboard: 256, ground: 0, total: 256, occupants: 256 },
    phase: 'takeoff',
    category: 'weather',
    summary_zh: '包机搭载第 101 空降师官兵从西奈半岛维和任务返回美国，在加拿大冈德机场加油后起飞失败，撞地起火，机上 256 人全部罹难——其中 248 名美军士兵。这是加拿大境内死亡人数最多的航空事故。加拿大航空安全委员会（CASB）对原因结论分裂：多数意见认为机翼污染（结冰）加上飞机超重导致升力不足；少数意见怀疑机内炸弹（事故政治背景敏感，尤其涉及黎巴嫩真主党人质交换议题）。少数意见从未被官方采信但争议至今未息。',
    summary_en: 'A charter flight returning U.S. 101st Airborne Division soldiers from Sinai peacekeeping duty failed to take off after refueling at Gander; the DC-8 struck terrain and burned, killing all 256 aboard, including 248 U.S. servicemen. It remains the deadliest aviation accident on Canadian soil. The Canadian Aviation Safety Board (CASB) split on cause: the majority concluded that wing-surface contamination (icing) plus aircraft overweight produced insufficient lift; a minority suspected an onboard bomb (the political context — Lebanon hostage exchanges — was sensitive). The minority view has never been officially adopted but the dispute persists.',
    links: [
      { label: "CASB Final Report (1988)", url: "https://www.bst-tsb.gc.ca/eng/rapports-reports/aviation/1985/a85h0002/a85h0002.html" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/Arrow_Air_Flight_1285R" }
    ]
  },

  // 11. ─── Aloha Airlines Flight 243 ───────────────────────────────────
  {
    id: 'aq243',
    date: '1988-04-28',
    airline: 'Aloha Airlines',
    flight: '243',
    aircraft: 'Boeing 737-297',
    registration: 'N73711',
    lat: 20.8987,
    lon: -156.4305,
    location: 'Maui (en route, near Kahului OGG), Hawaii, USA',
    fatalities: { onboard: 1, ground: 0, total: 1, occupants: 95 },
    phase: 'cruise',
    category: 'structural',
    summary_zh: '巡航高度 24,000 英尺时，机身上半段从前舱门后至机翼前缘整体撕裂剥离——约 5.5 米长的客舱顶部被风掀掉，一名乘务员被吸出机外（唯一遇难者）。机组在严重结构损伤下成功降落毛伊岛卡胡卢伊机场，剩余 94 人全部生还。该机为波音 737-200 早期型，频繁起降夏威夷岛屿间短航段（执行约 89,680 次起降循环，远超设计预期），盐雾环境加速腐蚀，机身蒙皮搭接缝沿铆钉孔形成的疲劳裂纹"链式连接"（widespread fatigue damage）最终断裂。事故催生了 FAA 对老龄飞机检查规则的全面重写，"广泛疲劳损伤"概念成为飞机适航管理的核心。',
    summary_en: 'At 24,000 feet in cruise, the upper fuselage from just aft of the forward door to the wing\'s leading edge tore off as a single piece — about 5.5 metres of cabin roof was peeled away, and a flight attendant was swept out of the aircraft (the sole fatality). The crew landed the structurally devastated aircraft at Kahului on Maui; the remaining 94 occupants survived. The aircraft was an early-build 737-200 used on short inter-island Hawaii hops, with about 89,680 cycles (far beyond design assumptions); the salt-air environment had accelerated corrosion, and fatigue cracks at fuselage skin lap joints had linked into a continuous structural failure path (widespread fatigue damage). The accident drove a comprehensive FAA rewrite of aging-aircraft inspection rules; the concept of "widespread fatigue damage" became central to airworthiness management.',
    links: [
      { label: "NTSB Accident Report AAR-89/03", url: "https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR8903.pdf" },
      { label: "FAA Lessons Learned: 737 N73711", url: "https://www.faa.gov/lessons_learned/transport_airplane/accidents/N73711" },
      { label: "Wikipedia", url: "https://en.wikipedia.org/wiki/Aloha_Airlines_Flight_243" }
    ]
  },

  // 12. ─── Pan Am Flight 103 (Lockerbie) ──────────────────────────────
  {
    id: 'panam103',
    date: '1988-12-21',
    airline: 'Pan Am',
    flight: '103',
    aircraft: 'Boeing 747-121',
    registration: 'N739PA',
    lat: 55.1119,
    lon: -3.3589,
    location: 'Lockerbie, Scotland',
    fatalities: { onboard: 259, ground: 11, total: 270, occupants: 259 },
    phase: 'cruise',
    category: 'security',
    summary_zh: '由伦敦希思罗飞往纽约 JFK 的 747 在苏格兰洛克比上空 31,000 英尺巡航时，前货舱内一只藏有塑性炸药的飞利浦收音机磁带录音机爆炸。前机身在数秒内解体，残骸散落约 845 平方公里。机上 259 人无一生还；坠落的机身段砸毁洛克比镇 Sherwood Crescent 街区民居，11 名地面居民罹难。利比亚情报官员 Abdelbaset al-Megrahi 于 2001 年被苏格兰法庭定罪。事故推动了行李—乘客匹配规则全球化、机场行李 X 光与爆炸物探测的强制部署、以及 ICAO 塑性炸药标记物公约的签署。',
    summary_en: 'A 747 from London Heathrow to New York JFK was at 31,000 feet over southern Scotland when a Toshiba radio-cassette player containing plastic explosive detonated in the forward cargo hold. The forward fuselage broke up within seconds; debris fell across about 845 km². All 259 aboard were killed, and falling fuselage struck Sherwood Crescent in Lockerbie, killing 11 residents on the ground. Libyan intelligence officer Abdelbaset al-Megrahi was convicted by a Scottish court in 2001. The accident drove the global rollout of passenger-baggage reconciliation, mandatory X-ray and explosive-detection screening of hold baggage, and the ICAO Convention on the Marking of Plastic Explosives.',
    links: [
      { label: 'AAIB Aircraft Accident Report 2/1990', url: 'https://www.gov.uk/aaib-reports/2-1990-boeing-747-121-n739pa' },
      { label: 'FAA Lessons Learned: 747 N739PA', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/N739PA' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Pan_Am_Flight_103' }
    ]
  },

  // 13. ─── British Midland Flight 92 (Kegworth) ─────────────────────
  {
    id: 'bd92',
    date: '1989-01-08',
    airline: 'British Midland',
    flight: '92',
    aircraft: 'Boeing 737-4Y0',
    registration: 'G-OBME',
    lat: 52.8302,
    lon: -1.3608,
    location: 'M1 motorway embankment near Kegworth, Leicestershire, UK',
    fatalities: { onboard: 47, ground: 0, total: 47, occupants: 126 },
    phase: 'approach',
    category: 'LOC-I',
    summary_zh: '伦敦希思罗飞往贝尔法斯特途中，左侧 CFM56 发动机一片风扇叶片疲劳断裂，引发振动与黑烟进入客舱。机组误判为右发故障并将其关闭，振动暂时减轻——但实际上是因为左发自动减推力。当机组在东米德兰兹机场进近、加大左发推力以拉起复飞时，受损发动机彻底失效，飞机失去全部推力，于跑道前 900 米的 M1 高速公路路堤撞地。47 人罹难，79 人重伤幸存。事故关键点之一是新型 EFIS（电子飞行仪表系统）显示与机组的型号转换训练不充分——他们认为新机型的客舱空调引气来自右发，而 737-400 改成了左发供气。事故后机型转换训练规则、机舱与驾驶舱通信（乘务员能否质疑机长判断）、CRM 内容均被重写。',
    summary_en: 'En route from Heathrow to Belfast, a fan blade failed on the left CFM56 engine, producing vibration and smoke into the cabin. The crew misidentified the failure as the right engine and shut it down; vibration eased temporarily — but only because the autothrottle had reduced the still-running damaged left engine\'s thrust. On approach to East Midlands Airport, when the crew advanced the (left) throttle to arrest a sink rate, the damaged engine failed completely, and the aircraft struck the M1 motorway embankment 900 m short of the runway. 47 died; 79 survived with serious injuries. A key factor was inadequate type conversion training to the new EFIS-equipped 737-400: the crew believed bleed air for the cabin came from the right engine (true on the 737-200 they had flown previously) when on the -400 it came from the left. The accident drove a rewrite of type conversion training, cabin-to-cockpit communication protocols (whether cabin crew should challenge a captain\'s diagnosis), and CRM content.',
    links: [
      { label: 'AAIB Aircraft Accident Report 4/1990', url: 'https://www.gov.uk/aaib-reports/4-1990-boeing-737-400-g-obme' },
      { label: 'FAA Lessons Learned: 737-400 G-OBME', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/G-OBME' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Kegworth_air_disaster' }
    ]
  },

  // 14. ─── PIA Flight 268 ──────────────────────────────────────────
  {
    id: 'pk268',
    date: '1992-09-28',
    airline: 'Pakistan International Airlines',
    flight: '268',
    aircraft: 'Airbus A300B4-203',
    registration: 'AP-BCP',
    lat: 27.6885,
    lon: 85.3192,
    location: 'Bhattedanda Hills, ~13 km S of Kathmandu, Nepal',
    fatalities: { onboard: 167, ground: 0, total: 167, occupants: 167 },
    phase: 'approach',
    category: 'CFIT',
    summary_zh: '由卡拉奇飞往加德满都的空客 A300，在向 02 号跑道进行非精密 VOR/DME 进近时，过早开始下降并撞入特里布万机场南侧山区。机组未能正确执行多步阶梯式下降程序——加德满都进近因山地地形要求严格的逐段高度限制——而是按一个连续下降率下降。机上 167 人全部罹难。两个月前 1992 年 7 月，泰航 311 号航班在同一进近程序的同一山脊以同样方式坠毁。两次事故共促成尼泊尔 VOR/DME 进近程序的修订与 EGPWS（增强型近地警告系统）在山地航线运营商中的广泛部署。',
    summary_en: 'An A300 from Karachi to Kathmandu was on a non-precision VOR/DME approach to runway 02 when it descended prematurely and struck mountainous terrain south of Tribhuvan International Airport. The crew failed to execute the stepped descent profile correctly — the Kathmandu approach requires strict segmented altitude crossings due to the surrounding terrain — and descended at a constant rate instead. All 167 aboard died. Two months earlier, in July 1992, Thai Airways flight 311 had crashed on the same approach into the same ridge in nearly the same way. Together the two accidents drove revisions to Nepal\'s VOR/DME approach procedures and accelerated EGPWS (enhanced GPWS) adoption among carriers operating in mountainous terrain.',
    links: [
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Pakistan_International_Airlines_Flight_268' }
    ]
  },

  // 15. ─── China Southern Flight 3943 (Guilin) ────────────────────
  {
    id: 'cz3943',
    date: '1992-11-24',
    airline: 'China Southern Airlines',
    flight: '3943',
    aircraft: 'Boeing 737-3Y0',
    registration: 'B-2523',
    lat: 25.0500,
    lon: 110.4500,
    location: 'Yangshuo, Guilin, Guangxi, China',
    fatalities: { onboard: 141, ground: 0, total: 141, occupants: 141 },
    phase: 'approach',
    category: 'CFIT',
    summary_zh: '广州飞桂林的 737-300 在桂林进近期间撞入桂林市东南约 30 公里阳朔境内的高山。机组在恶劣天气下未能维持下滑道与最低安全高度，飞机在 1,140 米高度撞山，全机解体。机上 141 人全部罹难。该事故是中国 1990 年代连续重大事故的开端——至 2002 年间还包括 1994 年西安西北航 2303、1997 年深圳南航 3456、2000 年武汉武航 343、2002 年釜山国航 129 与大连北方航 6136——直接催生了民航总局的体系性安全改革。',
    summary_en: 'A 737-300 from Guangzhou to Guilin struck high terrain near Yangshuo, about 30 km southeast of Guilin, during approach. In poor weather, the crew failed to maintain glidepath and minimum safe altitude; the aircraft struck a mountain at about 1,140 metres elevation and disintegrated. All 141 aboard died. This crash opened a sequence of major Chinese accidents in the 1990s and early 2000s — China Northwest 2303 (1994), China Southern 3456 (1997), Wuhan Air 343 (2000), Air China 129 and China Northern 6136 (2002) — that drove the systemic safety reforms led by the Civil Aviation Administration of China.',
    links: [
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/China_Southern_Airlines_Flight_3943' }
    ]
  },

  // 16. ─── China Airlines Flight 140 (Nagoya) ─────────────────────
  {
    id: 'ci140',
    date: '1994-04-26',
    airline: 'China Airlines (Taiwan)',
    flight: '140',
    aircraft: 'Airbus A300B4-622R',
    registration: 'B-1816',
    lat: 35.2557,
    lon: 136.9244,
    location: 'Nagoya Airport (NGO), Japan',
    fatalities: { onboard: 264, ground: 0, total: 264, occupants: 271 },
    phase: 'landing',
    category: 'LOC-I',
    summary_zh: '由台北飞往名古屋的 A300-600 在五边进近期间，副驾驶误触发 TOGA（起飞/复飞）杆，自动驾驶进入复飞模式，配平向上偏转。机组试图通过推杆下压保持下滑道，但 A300-600 的自动驾驶系统设计将这种"反向力"视为机组手动干预之外的输入，配平并未自动撤回——机组与自动配平形成长达 30 秒的"拉锯"。最终飞机在跑道入口前进入剧烈失速、机头上仰，从约 1,800 英尺翻覆坠地。271 人中 264 人罹难，7 人幸存。事故揭示了 A300-600 自动驾驶设计的根本缺陷——飞行机组介入时系统不放弃控制权——空客随后修改了 A300/A310 的飞行控制软件并扩展到所有后续机型。',
    summary_en: 'On final to Nagoya, the first officer of an A300-600 inadvertently engaged the takeoff/go-around (TOGA) lever; the autopilot entered go-around mode and trimmed nose-up. The crew tried to push the nose down to stay on the glidepath, but the A300-600\'s autopilot logic did not interpret this opposing force as manual override — the autotrim did not back off — and a 30-second tug-of-war developed between crew and autotrim. The aircraft finally entered a violent nose-high stall just short of the threshold, pitched up to near vertical, and fell to the ground from about 1,800 feet. Of 271 aboard, 264 died and 7 survived. The accident exposed a fundamental flaw in the A300-600 autopilot design — the system did not yield control when the crew acted against it — and Airbus subsequently revised the flight control software on A300/A310 and extended the change to all later types.',
    links: [
      { label: 'JTSB final report (English)', url: 'https://www.mlit.go.jp/jtsb/eng-air_report/B-1816.pdf' },
      { label: 'FAA Lessons Learned: A300-600 B-1816', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/B-1816' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/China_Airlines_Flight_140' }
    ]
  },

  // 17. ─── China Northwest Flight 2303 (Xi'an) ─────────────────────
  {
    id: 'cnw2303',
    date: '1994-06-06',
    airline: 'China Northwest Airlines',
    flight: '2303',
    aircraft: 'Tupolev Tu-154M',
    registration: 'B-2610',
    lat: 34.4467,
    lon: 109.0297,
    location: 'Xi\'an, Shaanxi, China',
    fatalities: { onboard: 160, ground: 0, total: 160, occupants: 160 },
    phase: 'climb',
    category: 'LOC-I',
    summary_zh: '由西安飞广州的图-154 起飞后约九分钟，在 4,700 米高度发生剧烈滚转与振荡，最终空中解体，残骸散落于咸阳上空数公里范围。调查发现自动驾驶的偏航阻尼器（yaw damper）插头在维护时被错接到滚转通道——飞行员的方向舵输入触发了滚转通道的反应，反之亦然。这一接线错误已存在 7 个月、累计 100+ 飞行小时未被发现，因为只有在高速大幅度操纵时才会显现失稳模式。机上 160 人全部罹难。这是中国境内死亡人数最多的航空事故，也是后续民航维护程序与图-154 退役决策的关键案例。',
    summary_en: 'A Tu-154 from Xi\'an to Guangzhou, about nine minutes after takeoff at 4,700 metres, entered violent roll oscillations, broke up in flight, and scattered debris over several kilometres around Xianyang. The investigation found that the yaw damper plug had been miswired to the roll channel during maintenance — the pilot\'s rudder inputs triggered the roll channel and vice versa. The miswiring had been present for seven months and roughly 100 flight hours, undetected because the instability mode appeared only under high-speed, large-amplitude inputs. All 160 aboard died. This remains the deadliest aviation accident on Chinese soil, and was a key case in the subsequent overhaul of Chinese civil aviation maintenance procedures and the gradual retirement of the Tu-154 from Chinese service.',
    links: [
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/China_Northwest_Airlines_Flight_2303' }
    ]
  },

  // 18. ─── TWA Flight 800 ──────────────────────────────────────────
  {
    id: 'twa800',
    date: '1996-07-17',
    airline: 'Trans World Airlines',
    flight: '800',
    aircraft: 'Boeing 747-131',
    registration: 'N93119',
    lat: 40.6614,
    lon: -72.6353,
    location: 'Atlantic Ocean, off Long Island, New York, USA',
    fatalities: { onboard: 230, ground: 0, total: 230, occupants: 230 },
    phase: 'climb',
    category: 'structural',
    summary_zh: '由 JFK 起飞前往巴黎的 747 在长岛南岸海域 13,800 英尺高度爆炸解体，残骸散落数英里海域。机上 230 人全部罹难。NTSB 历时四年的调查（这是当时美国国家运输安全委员会规模最大的事故调查）确定起因：中央油箱内部因空调机组散热而蓄热，使少量残余燃油挥发为可燃气体，被一处暴露的电线短路点火爆炸。事故催生了 FAA 的 SFAR 88（特别联邦航空规则 88），要求所有商用客机加装油箱惰性化系统（Fuel Tank Inerting System）以氮气替换油箱顶部空气，至今仍是大型客机的强制配置。',
    summary_en: 'A 747 from JFK bound for Paris exploded at 13,800 feet over the Atlantic off Long Island\'s south shore, scattering wreckage across miles of ocean. All 230 aboard died. The NTSB\'s four-year investigation (the largest in the agency\'s history at the time) determined that residual fuel vapours in the empty centre wing tank — heated by the air-conditioning packs running below it on the ground — were ignited by a short circuit in exposed wiring inside the tank. The accident drove SFAR 88 (Special Federal Aviation Regulation 88), the FAA mandate requiring fuel tank inerting systems (which displace tank ullage with nitrogen) on all transport-category aircraft — still the standard today.',
    links: [
      { label: 'NTSB Accident Report AAR-00/03', url: 'https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR0003.pdf' },
      { label: 'FAA Lessons Learned: 747 N93119', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/N93119' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/TWA_Flight_800' }
    ]
  },

  // 19. ─── Charkhi Dadri midair (Saudia 763 + Kazakhstan 1907) ─────
  {
    id: 'charkhi_dadri',
    date: '1996-11-12',
    airline: 'Saudia + Kazakhstan Airlines',
    flight: 'SV 763 + KZA 1907',
    aircraft: 'Boeing 747-168B + Ilyushin Il-76TD',
    registration: 'HZ-AIH + UN-76435',
    lat: 28.5806,
    lon: 76.4106,
    location: 'Charkhi Dadri, Haryana, India (~75 km W of Delhi)',
    fatalities: { onboard: 349, ground: 0, total: 349, occupants: 349 },
    phase: 'cruise',
    category: 'midair',
    summary_zh: '从德里起飞的沙特航空 747 上升至 14,000 英尺巡航，与下降至 15,000 英尺、自哈萨克斯坦楚伊姆肯特方向飞来的伊尔-76 在德里西约 75 公里处迎面相撞。哈航机组英语水平不足、未严格保持指定高度（实际下降至约 14,500 英尺），且没有 TCAS（机载防撞系统）。这是民用航空史上死亡人数最多的空中相撞事故；事故直接推动了 TCAS II 在所有商用客机上的强制部署，及全球范围内对管制员—机组通话英语标准的整顿。',
    summary_en: 'A Saudi 747 climbing out of Delhi to 14,000 feet collided head-on at about 75 km west of Delhi with an Il-76 from Chimkent, Kazakhstan, descending to 15,000 feet. The Kazakh crew\'s English proficiency was inadequate; they had not held their assigned altitude (descending to about 14,500 feet); and they had no TCAS. This remains the deadliest midair collision in civil aviation history. It drove the global mandate for TCAS II on all commercial transport aircraft, and a worldwide tightening of controller-crew radiotelephony English standards.',
    links: [
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Charkhi_Dadri_mid-air_collision' }
    ]
  },

  // 20. ─── CZ3456 — central case for this wiki ────────────────────
  {
    id: 'cz3456',
    date: '1997-05-08',
    airline: 'China Southern Airlines',
    flight: '3456',
    aircraft: 'Boeing 737-31B',
    registration: 'B-2925',
    lat: 22.6394,
    lon: 113.8108,
    location: 'Huangtian Airport (SZX), Shenzhen, China',
    fatalities: { onboard: 35, ground: 0, total: 35, occupants: 74 },
    phase: 'landing',
    category: 'runway',
    summary_zh: '由重庆飞往深圳的 737-300 在强对流降水中执行 33 号跑道 ILS 进近。第一次着陆中，飞机在跑道上连续四次重落跳跃，机身结构（前起落架支柱、机翼根部、后部蒙皮）严重受损。机长林友贵决定复飞，操纵系统已部分失效。机组在天气与位置混乱中尝试第二次进近，目标改为 15 号跑道（反向）。第二次落地以极高下降率撞地，飞机断成三截并起火。74 人中 35 人罹难（多数为靠近第二处断裂面的乘客）。本事故直接催生了中国民航总局 1990 年代末至 2000 年代初的系统性安全改革——飞行员资质收紧、机组搭配规则重构、CRM 训练扩展、强对流天气签派与空管程序修订——其后十年中国主要定期航空公司未再发生致命事故。本网页的 §6 与图 5 详细呈现 CZ3456 的驾驶舱通话与时间线。',
    summary_en: 'A 737-300 from Chongqing was on an ILS approach to runway 33 at Shenzhen Huangtian in heavy convective rain. On the first landing attempt, the aircraft bounced four times along the runway, severely damaging the nose gear strut, wing roots, and rear fuselage skin. Captain Lin Yougui initiated a go-around with degraded flight controls. The crew, in confusion about position and weather, attempted a second approach — this time to runway 15 (the reciprocal direction). The second landing struck the ground at very high descent rate; the aircraft broke into three sections and burned. 35 of 74 aboard died, most of them passengers near the second fracture line. This accident was the direct driver of the late-1990s and early-2000s systemic safety reforms by the Civil Aviation Administration of China — tightened pilot qualification, restructured crew pairing rules, expanded CRM training, revised severe-weather dispatch and ATC procedures — after which no major Chinese scheduled carrier had a fatal accident for a decade. §6 and Figure 5 of this page present the CZ3456 cockpit voice recording and timeline in detail.',
    links: [
      { label: '§6 of this page (full account)', url: '#sec-defense' },
      { label: 'Figure 5: CVR audio + bilingual transcript', url: '#cvr-widget' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/China_Southern_Airlines_Flight_3456' }
    ]
  },

  // 21. ─── Korean Air Flight 801 (Guam) ───────────────────────────
  {
    id: 'kal801',
    date: '1997-08-06',
    airline: 'Korean Air',
    flight: '801',
    aircraft: 'Boeing 747-3B5',
    registration: 'HL7468',
    lat: 13.4555,
    lon: 144.7253,
    location: 'Nimitz Hill, ~5 km SW of Antonio B. Won Pat International Airport, Guam',
    fatalities: { onboard: 228, ground: 0, total: 228, occupants: 254 },
    phase: 'approach',
    category: 'CFIT',
    summary_zh: '由首尔金浦飞往关岛的 747-300 在 06L 跑道夜间 ILS 进近时撞入跑道入口前 5 公里的尼米兹山。机组按 ILS 程序下降，但当时关岛 ILS 下滑道发射机停用维护——机组未注意到 NOTAM 通告，仍按完整 ILS 进近程序操作；同时关岛进近的 MSAW（最低安全告警系统）也因过去误报频繁被技术员"调教"成 Andersen 空军基地范围之外不发出警告，因此飞机进入山区下方时无任何告警。254 人中 228 人罹难。NTSB 调查特别强调了大韩航空机组训练体系中"机长权威不容质疑"的文化问题——副驾驶在最后下降段曾两次质疑高度，但未被采纳。事故是亚洲航司 CRM 训练改革的关键节点。',
    summary_en: 'A 747-300 from Seoul Gimpo to Guam struck Nimitz Hill, about 5 km short of runway 06L, during a night ILS approach. The crew flew the ILS procedure as if it were complete, but the Guam glideslope transmitter was out of service for maintenance — the crew had not noted the NOTAM. The Guam MSAW (Minimum Safe Altitude Warning) system had earlier been "tuned" by technicians to suppress false alarms outside Andersen Air Force Base airspace, so no warning was generated as the aircraft descended below safe altitude. 228 of 254 aboard died. The NTSB explicitly cited Korean Air\'s training culture, in which captain authority was difficult to challenge — the first officer queried the altitude twice during the final descent and was not heeded. The accident is a key reference point for Asian airline CRM reform.',
    links: [
      { label: 'NTSB Accident Report AAR-00/01', url: 'https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR0001.pdf' },
      { label: 'FAA Lessons Learned: 747 HL7468', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/HL7468' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Korean_Air_Flight_801' }
    ]
  },

  // 22. ─── Swissair Flight 111 ────────────────────────────────────
  {
    id: 'sr111',
    date: '1998-09-02',
    airline: 'Swissair',
    flight: '111',
    aircraft: 'McDonnell Douglas MD-11',
    registration: 'HB-IWF',
    lat: 44.4022,
    lon: -63.5292,
    location: 'Atlantic Ocean, off Peggy\'s Cove, Nova Scotia, Canada',
    fatalities: { onboard: 229, ground: 0, total: 229, occupants: 229 },
    phase: 'cruise',
    category: 'fire',
    summary_zh: '由 JFK 飞往日内瓦的 MD-11 在巡航高度察觉到驾驶舱后部异味与烟雾。机组改飞哈利法克斯紧急落地，开始放油下降。从首次发现烟雾到电气系统失效仅约 14 分钟，多个仪表逐一熄灭、自动驾驶解除。飞机最终在哈利法克斯东南海面坠毁，机上 229 人全部罹难。加拿大运输安全委员会（TSB）调查历时四年，确定起火源为客舱娱乐系统的电源线在驾驶舱顶部线槽内的电弧短路，引燃了周边的 MPET 隔热毯材料——该材料在地面火焰测试中通过，但在持续电弧条件下会传播明火。事故催生了航空电气线路标准（EWIS）的全面重写、机舱隔热材料的可燃性新标准、驾驶舱"立即着陆"vs"走完检查单"的应急决策原则修订。',
    summary_en: 'An MD-11 from JFK to Geneva detected an unusual odor and smoke in the cockpit at cruise altitude. The crew diverted to Halifax and began a fuel-dump descent. About 14 minutes elapsed between the first smoke detection and the loss of electrical systems; instruments failed one by one and the autopilot disconnected. The aircraft crashed into the Atlantic southwest of Peggy\'s Cove. All 229 aboard died. The Canadian Transportation Safety Board\'s four-year investigation traced ignition to arcing in wiring for the in-flight entertainment system, in a duct above the cockpit; the arc ignited surrounding MPET thermal-acoustic insulation blankets — which had passed ground flame tests but would propagate fire under sustained arc conditions. The accident drove a comprehensive rewrite of the Electrical Wiring Interconnection Systems (EWIS) regulations, new flammability standards for cabin insulation materials, and revised guidance on the "land immediately versus complete the checklist" cockpit decision in smoke events.',
    links: [
      { label: 'TSB Aviation Investigation Report A98H0003', url: 'https://www.tsb.gc.ca/eng/rapports-reports/aviation/1998/a98h0003/a98h0003.html' },
      { label: 'FAA Lessons Learned: MD-11 HB-IWF', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/HB-IWF' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Swissair_Flight_111' }
    ]
  },

  // 23. ─── EgyptAir 990 ───────────────────────────────────────
  {
    id: 'ms990',
    date: '1999-10-31',
    airline: 'EgyptAir',
    flight: '990',
    aircraft: 'Boeing 767-366ER',
    registration: 'SU-GAP',
    lat: 40.3508,
    lon: -69.7553,
    location: 'Atlantic Ocean, ~100 km S of Nantucket, USA',
    fatalities: { onboard: 217, ground: 0, total: 217, occupants: 217 },
    phase: 'cruise',
    category: 'LOC-I',
    summary_zh: '由洛杉矶经纽约 JFK 飞往开罗的 767-300ER，在巡航高度上副驾驶 Gameel al-Batouti 单独在驾驶舱时，将自动驾驶解除并将操纵杆推杆下压，飞机进入近垂直俯冲。机长返回驾驶舱后试图拉杆改出，但副驾驶反向操作；两人同时控制操纵杆形成相反方向输入，飞机在 6,500 米解体。机上 217 人全部罹难。NTSB 结论为副驾驶蓄意自杀坠机；埃及民航当局拒绝接受这一结论，转而强调机械故障可能性。事故是少数 NTSB 与外国调查机构结论严重分歧的案例。',
    summary_en: 'A 767-300ER from Los Angeles via JFK to Cairo entered a near-vertical dive at cruise altitude when the relief first officer Gameel al-Batouti, alone in the cockpit, disengaged the autopilot and pushed the column forward. The captain returned and tried to pull up, but the first officer pushed in the opposite direction; the two control columns moved against each other, and the aircraft broke up at 6,500 metres. All 217 aboard died. The NTSB concluded the cause was a deliberate act by the first officer; Egyptian civil aviation authorities rejected this finding and emphasised possible mechanical causes. It is one of a small number of cases in which NTSB findings and a foreign investigating authority strongly diverge.',
    links: [
      { label: 'NTSB Aircraft Accident Brief AAB-02/01', url: 'https://www.ntsb.gov/investigations/AccidentReports/Reports/AAB0201.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/EgyptAir_Flight_990' }
    ]
  },

  // 24. ─── Alaska Airlines 261 ────────────────────────────────
  {
    id: 'as261',
    date: '2000-01-31',
    airline: 'Alaska Airlines',
    flight: '261',
    aircraft: 'McDonnell Douglas MD-83',
    registration: 'N963AS',
    lat: 34.0539,
    lon: -119.4108,
    location: 'Pacific Ocean, off Anacapa Island, California, USA',
    fatalities: { onboard: 88, ground: 0, total: 88, occupants: 88 },
    phase: 'cruise',
    category: 'structural',
    summary_zh: '由墨西哥巴亚尔塔港飞往西雅图的 MD-83 在巡航中察觉水平安定面配平卡阻。机组试图排故时，水平安定面突然全行程偏转至机头下俯，飞机进入持续俯冲。机组短暂改出后再次失去控制，飞机倒扣坠入太平洋。机上 88 人全部罹难。调查发现根本原因是水平安定面千斤顶螺纹（jackscrew）严重磨损：阿拉斯加航空将润滑维护周期从制造商建议的 600 飞行小时延长至 2,550 小时，磨损超出标准 20 倍仍未发现。FAA 强制收紧维护审计程序，多家航空公司因此案被处罚。',
    summary_en: 'An MD-83 from Puerto Vallarta to Seattle developed a horizontal stabilizer trim jam at cruise. As the crew worked the problem, the stabilizer suddenly drove full nose-down and the aircraft pitched into a sustained dive. After a brief recovery, control was lost again and the aircraft crashed inverted into the Pacific. All 88 aboard died. The investigation traced the cause to severe wear on the horizontal stabilizer\'s jackscrew assembly: Alaska Airlines had stretched the lubrication interval from the manufacturer\'s recommended 600 flight hours to 2,550 hours, and the resulting wear was 20× the design limit yet undetected. The FAA forced a tightening of maintenance audit procedures across U.S. carriers; several airlines were penalised in the wake of the case.',
    links: [
      { label: 'NTSB Accident Report AAR-02/01', url: 'https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR0201.pdf' },
      { label: 'FAA Lessons Learned: MD-83 N963AS', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/N963AS' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Alaska_Airlines_Flight_261' }
    ]
  },

  // 25. ─── Air France 4590 (Concorde) ──────────────────────────
  {
    id: 'af4590',
    date: '2000-07-25',
    airline: 'Air France',
    flight: '4590',
    aircraft: 'Aérospatiale/BAC Concorde',
    registration: 'F-BTSC',
    lat: 49.0211,
    lon: 2.4925,
    location: 'Gonesse, near Paris Charles de Gaulle, France',
    fatalities: { onboard: 109, ground: 4, total: 113, occupants: 109 },
    phase: 'takeoff',
    category: 'runway',
    summary_zh: '协和飞机从巴黎戴高乐 26R 跑道起飞滑跑期间，左主轮组碾过跑道上 5 分钟前由先行 Continental DC-10 起飞时脱落的一条长 43 厘米钛合金条形修补片。轮胎爆裂的橡胶碎片以高速冲击左翼下表面 5 号油箱，引发液压冲击波导致油箱内壁破裂，泄漏燃油被起落架附近热源点燃。两台左侧发动机相继因烟气吸入失效，飞机无法爬升，撞入哥内斯一家旅馆。机上 109 人全部罹难，地面 4 人罹难。这是协和唯一的致命事故；事故后协和加装 Kevlar 油箱衬里，但此后客流锐减、空客与英航终止支持，2003 年全球退役。',
    summary_en: 'A Concorde taking off from Paris Charles de Gaulle runway 26R ran over a 43 cm titanium wear strip dropped on the runway five minutes earlier by a departing Continental DC-10. A burst tyre threw rubber fragments into the left wing\'s number 5 fuel tank at high speed; the hydraulic shock burst the tank from inside, leaking fuel that was ignited by an electrical arc near the landing gear. Both left engines failed in succession from smoke ingestion; the aircraft could not climb and struck a hotel in Gonesse. All 109 aboard died, plus 4 on the ground. This was Concorde\'s only fatal accident; the type returned to service with Kevlar tank liners, but with collapsed demand Air France and British Airways retired the type globally in 2003.',
    links: [
      { label: 'BEA Final Report (English)', url: 'https://bea.aero/docspa/2000/f-sc000725a/pdf/f-sc000725a.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Air_France_Flight_4590' }
    ]
  },

  // 26. ─── Air China 129 (Busan) ──────────────────────────────
  {
    id: 'ca129',
    date: '2002-04-15',
    airline: 'Air China',
    flight: '129',
    aircraft: 'Boeing 767-2J6ER',
    registration: 'B-2552',
    lat: 35.2106,
    lon: 128.9533,
    location: 'Mt. Dotdae, Gimhae-si, near Busan, South Korea',
    fatalities: { onboard: 129, ground: 0, total: 129, occupants: 166 },
    phase: 'approach',
    category: 'CFIT',
    summary_zh: '由北京飞往釜山的 767-200ER 在恶劣天气下进近金海机场。机场只有 18R 跑道有 ILS，但当天风向要求使用 36L 跑道（无 ILS，需绕场目视进近）。机组在云中执行绕场程序时偏离标准航线，撞入机场北侧 Dotdae 山，机身解体起火。166 人中 129 人罹难，37 人幸存。这是中国国际航空公司迄今唯一的致命事故。事故后中国民航总局收紧远程国际航线机长资质要求；韩国延后了金海机场使用 36L 跑道时的目视绕场进近程序。',
    summary_en: 'A 767-200ER from Beijing to Busan was on approach to Gimhae in poor weather. Only runway 18R had an ILS; the prevailing wind that day required runway 36L, which has no ILS and requires a circling visual approach. The crew, manoeuvring in cloud during the circling procedure, strayed from the standard track and struck Mount Dotdae north of the field; the aircraft broke up and burned. 129 of 166 aboard died, 37 survived. This remains Air China\'s only fatal accident. The CAAC subsequently tightened captain qualification requirements for international long-haul routes; South Korea later phased out circling visual approaches to Gimhae 36L.',
    links: [
      { label: 'KARAIB Final Report', url: 'https://www.skybrary.aero/sites/default/files/bookshelf/921.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Air_China_Flight_129' }
    ]
  },

  // 27. ─── China Northern 6136 (Dalian) ────────────────────────
  {
    id: 'cj6136',
    date: '2002-05-07',
    airline: 'China Northern Airlines',
    flight: '6136',
    aircraft: 'McDonnell Douglas MD-82',
    registration: 'B-2138',
    lat: 38.7167,
    lon: 121.6500,
    location: 'Dalian Bay, Liaoning, China',
    fatalities: { onboard: 112, ground: 0, total: 112, occupants: 112 },
    phase: 'approach',
    category: 'fire',
    summary_zh: '由北京飞往大连的 MD-82 在大连进近期间，一名乘客在机舱后部使用汽油纵火。机组报告"机舱失火"后与控制塔失去联系，飞机失控坠入大连湾。机上 112 人全部罹难。调查确认纵火乘客张丕林为骗取保险金而蓄意纵火（其本人也死于事故）。事故推动了中国民航对客票实名制、行李 X 光检查、客舱液体携带规则的提前布局，及保险骗保案件刑事司法的关注。',
    summary_en: 'An MD-82 from Beijing to Dalian was on approach to Dalian when a passenger set fire to the rear cabin using gasoline. The crew reported "cabin fire" and shortly afterwards lost contact with the tower; the aircraft fell out of control into Dalian Bay. All 112 aboard died. The investigation concluded that passenger Zhang Pilin had set the fire deliberately to claim life insurance (he died in the crash). The accident prompted the early Chinese rollout of identity-verified ticketing, expanded passenger baggage screening, and rules on cabin liquids — and turned a spotlight on insurance-motivated criminal cases.',
    links: [
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/China_Northern_Airlines_Flight_6136' }
    ]
  },

  // 28. ─── Überlingen midair ──────────────────────────────────
  {
    id: 'ueberlingen',
    date: '2002-07-01',
    airline: 'Bashkirian Airlines + DHL',
    flight: 'BTC 2937 + DHX 611',
    aircraft: 'Tupolev Tu-154M + Boeing 757-23APF',
    registration: 'RA-85816 + A9C-DHL',
    lat: 47.7717,
    lon: 9.1781,
    location: 'Überlingen, Lake Constance, Germany',
    fatalities: { onboard: 71, ground: 0, total: 71, occupants: 71 },
    phase: 'cruise',
    category: 'midair',
    summary_zh: '巴什基尔航空 Tu-154 与 DHL 757 货机在德国南部上空 36,000 英尺迎面接近。两机的 TCAS（机载防撞系统）同时发出避让指令——TCAS 让 Tu-154 上升、757 下降。然而瑞士天空导航（Skyguide）唯一在岗的管制员（同事休息中、同时管两个频率、电话线路又出故障）在 TCAS 指令发出后约 14 秒发出相反指令——要求 Tu-154 下降。Tu-154 机组按管制员指令下降，与正在按 TCAS 指令下降的 757 在 Überlingen 上空相撞，全部 71 人罹难。事故催生了 ICAO 全球规则修订：TCAS 决断指令优先于管制员指令。事故后续：2004 年 Skyguide 一名管制员（虽不是事发当晚的那位）被 Tu-154 机长之妻的兄弟刺杀。',
    summary_en: 'A Bashkirian Tu-154 and a DHL 757 cargo were on converging tracks at 36,000 feet over southern Germany. Both aircraft\'s TCAS issued resolution advisories — TCAS told the Tu-154 to climb and the 757 to descend. The sole on-duty Swiss Skyguide controller (a colleague was on break, two sectors were combined onto one frequency, and the phone lines were down for maintenance) issued a contradictory instruction about 14 seconds after the TCAS advisory, telling the Tu-154 to descend. The Tu-154 crew followed ATC and descended into the path of the 757, which was descending per its TCAS. The aircraft collided over Überlingen; all 71 aboard died. The accident drove an ICAO rule change worldwide: TCAS resolution advisories take precedence over ATC instructions. A bitter postscript: in 2004, a Skyguide controller (not the one on duty that night) was murdered at his home by the brother of the Tu-154 captain\'s wife.',
    links: [
      { label: 'BFU Final Investigation Report', url: 'https://www.bfu-web.de/EN/Publications/Investigation%20Report/2002/Report_02_AX001-1-2_Ueberlingen_Report.pdf?__blob=publicationFile' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/2002_%C3%9Cberlingen_mid-air_collision' }
    ]
  },

  // 29. ─── China Eastern 5210 (Baotou) ─────────────────────────
  {
    id: 'mu5210',
    date: '2004-11-21',
    airline: 'China Eastern Airlines',
    flight: '5210',
    aircraft: 'Bombardier CRJ-200LR',
    registration: 'B-3072',
    lat: 40.5600,
    lon: 109.9967,
    location: 'Nanhai Park lake, Baotou, Inner Mongolia, China',
    fatalities: { onboard: 53, ground: 2, total: 55, occupants: 53 },
    phase: 'takeoff',
    category: 'weather',
    summary_zh: '由包头飞往上海的 CRJ-200 在包头机场起飞后约 1 分钟，因机翼结冰失速失控，坠入机场南侧南海公园湖中。机上 53 人全部罹难，地面 2 人因被坠机砸中罹难。机组未在起飞前进行除冰程序——气温接近冰点、有积雪，符合除冰条件，但飞机停在停机坪过夜未除冰即起飞。事故催生中国民航对支线机型起飞前除冰程序的强制化与机组训练加强。',
    summary_en: 'A CRJ-200 from Baotou to Shanghai stalled and lost control about one minute after takeoff due to wing-surface icing, crashing into the lake at Nanhai Park south of the airport. All 53 aboard died, plus 2 on the ground struck by wreckage. The crew had not de-iced before departure: the temperature was near freezing, snow had fallen, and the aircraft had been parked overnight on the apron — conditions that required de-icing. The accident drove the mandatory de-icing procedures and crew training requirements for regional aircraft in Chinese civil aviation.',
    links: [
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/China_Eastern_Airlines_Flight_5210' }
    ]
  },

  // 30. ─── Colgan 3407 (Buffalo) ───────────────────────────────
  {
    id: 'colgan3407',
    date: '2009-02-12',
    airline: 'Colgan Air (operating as Continental Connection)',
    flight: '3407',
    aircraft: 'Bombardier Q400',
    registration: 'N200WQ',
    lat: 42.9472,
    lon: -78.6322,
    location: 'Clarence Center, near Buffalo Niagara International, New York, USA',
    fatalities: { onboard: 49, ground: 1, total: 50, occupants: 49 },
    phase: 'approach',
    category: 'LOC-I',
    summary_zh: '由纽瓦克飞往布法罗的 Q400 在布法罗进近期间因机翼结冰使失速速度提高，触发失速保护系统（stick shaker / stick pusher）。机长 Marvin Renslow 对失速警告做出错误反应——拉杆而非推杆，使飞机进入完全失速并失控坠地。机上 49 人罹难，地面 1 人罹难。NTSB 调查暴露多项问题：机长曾多次未通过型号资质考试、副驾驶 Rebecca Shaw 时薪仅 16 美元、机组在底特律一直熬到清晨才到岗（疲劳）。事故直接催生美国《Airline Safety and Federal Aviation Administration Extension Act of 2010》：副驾驶必须持 ATP 执照（要求 1,500 小时飞行时间）、修订机组休息时间规则。这是美国民航 2025 年 1 月 PSA 5342 之前最近一次商业客机致命事故——长达近 16 年。',
    summary_en: 'A Q400 from Newark to Buffalo experienced ice buildup that raised stall speed; the stall protection system (stick shaker, then stick pusher) activated. Captain Marvin Renslow reacted incorrectly — pulling on the column rather than pushing — driving the aircraft into a full aerodynamic stall and loss of control. It crashed into a house in Clarence Center; 49 aboard plus 1 on the ground died. The NTSB investigation exposed: the captain had failed multiple type checks, first officer Rebecca Shaw was paid $16/hour, and the crew had been in Detroit through dawn before the flight (fatigue). The accident drove the U.S. Airline Safety and FAA Extension Act of 2010 — first officers must hold an ATP certificate (1,500 hours), and crew rest rules were rewritten. It was the most recent fatal U.S. scheduled airline accident until PSA 5342 in January 2025 — nearly 16 years.',
    links: [
      { label: 'NTSB Accident Report AAR-10/01', url: 'https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1001.pdf' },
      { label: 'FAA Lessons Learned: Q400 N200WQ', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/N200WQ' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Colgan_Air_Flight_3407' }
    ]
  },

  // 31. ─── Air France 447 ──────────────────────────────────────
  {
    id: 'af447',
    date: '2009-06-01',
    airline: 'Air France',
    flight: '447',
    aircraft: 'Airbus A330-203',
    registration: 'F-GZCP',
    lat: 3.5775,
    lon: -30.3742,
    location: 'Atlantic Ocean, ~600 km NE of Fernando de Noronha, Brazil',
    fatalities: { onboard: 228, ground: 0, total: 228, occupants: 228 },
    phase: 'cruise',
    category: 'LOC-I',
    summary_zh: '由里约热内卢飞往巴黎的 A330-200 在巴西东北海面上空巡航时，皮托管在大西洋赤道辐合带（ITCZ）中遭遇过冷水滴结冰堵塞。空速指示瞬间不一致，自动驾驶按设计自动断开。低经验值班的副驾驶 Pierre-Cédric Bonin 在三秒内将操纵杆拉至最大上仰位置——飞机在 35,000 英尺进入失速。机长 Marc Dubois 此时正在休息舱睡觉，副驾驶持续拉杆约三分半钟，飞机在 16,000 ft/min 下沉率中完全失速直至撞海。机上 228 人全部罹难。残骸于事故后两年才在 4,000 米深海中找到。事故引发关于"飞行员手动飞行能力随高度自动化提高而退化"的全球讨论；空客修改 A330/A340 失速恢复程序训练；此后所有大型客机进行 manual flying refresher 训练成为业界标准。CVR 中机长返回驾驶舱后说出的"Mais qu\'est-ce qui se passe?"（"到底怎么了？"）成为这次事故的标志性问句。',
    summary_en: 'An A330-200 from Rio de Janeiro to Paris, cruising over the Atlantic in the Inter-Tropical Convergence Zone, experienced pitot tube blockage by supercooled water droplets. Airspeed indications became briefly inconsistent and the autopilot disconnected by design. Junior first officer Pierre-Cédric Bonin pulled the sidestick to its full nose-up position within three seconds — the aircraft entered a stall at 35,000 feet. Captain Marc Dubois was in the rest bunk; Bonin held nose-up for nearly three and a half minutes as the aircraft fell at 16,000 ft/min in a fully stalled condition until it hit the ocean. All 228 aboard died. The wreckage was not found for two years, in 4,000 metres of water. The accident prompted a global conversation about pilot manual-flying skill degradation as automation deepens; Airbus rewrote stall recovery training for the A330/A340 family, and recurrent manual flying training became standard industry practice. The captain\'s words on returning to the cockpit — "Mais qu\'est-ce qui se passe?" ("But what\'s happening?") — became the emblematic question of the accident.',
    links: [
      { label: 'BEA Final Report (English)', url: 'https://bea.aero/docspa/2009/f-cp090601.en/pdf/f-cp090601.en.pdf' },
      { label: 'FAA Lessons Learned: A330 F-GZCP', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/F-GZCP' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Air_France_Flight_447' }
    ]
  },

  // 32. ─── Polish Air Force 101 (Smolensk) ────────────────────
  {
    id: 'plf101',
    date: '2010-04-10',
    airline: 'Polish Air Force (Tu-154 36th Special Regiment)',
    flight: '101',
    aircraft: 'Tupolev Tu-154M',
    registration: '101',
    lat: 54.8244,
    lon: 32.0506,
    location: 'Smolensk North Airport, Russia',
    fatalities: { onboard: 96, ground: 0, total: 96, occupants: 96 },
    phase: 'approach',
    category: 'CFIT',
    summary_zh: '搭载波兰总统 Lech Kaczyński 与 95 名波兰高级官员（前往参加卡廷大屠杀 70 周年纪念）的图-154 在斯摩棱斯克机场进近期间，浓雾中下降至决断高度以下，撞上跑道入口前约 1.1 公里的桦树林后解体。机上 96 人全部罹难。调查暴露多重失败：俄方军用机场 NDB（无方向信标）程序精度本就低、机组未受该机场训练、塔台未发出复飞建议、机长承受了来自高级乘客的"必须落地"政治压力（CVR 显示陆军参谋长进入驾驶舱与机组交谈）。波兰与俄罗斯的事故调查结论持续争议，至今仍是双边关系敏感话题。',
    summary_en: 'A Tu-154M carrying Polish President Lech Kaczyński and 95 senior Polish officials (en route to a 70th-anniversary commemoration of the Katyn massacre) descended below decision height in dense fog at Smolensk North Airport, struck a birch about 1.1 km short of the runway, and broke up. All 96 aboard died. The investigation exposed multiple failures: low-precision Russian military airfield NDB approach, crew not trained for the field, no go-around advisory from the tower, and political pressure on the captain from senior passengers (the CVR captures the army chief of staff entering the cockpit). Polish and Russian conclusions diverged sharply and remain a sensitive bilateral issue.',
    links: [
      { label: 'MAK Final Report (English)', url: 'https://reports.aviation-safety.net/2010/20100410-0_T154_PLF101.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/2010_Polish_Air_Force_Tu-154_crash' }
    ]
  },

  // 33. ─── Air India Express 812 ──────────────────────────────
  {
    id: 'aix812',
    date: '2010-05-22',
    airline: 'Air India Express',
    flight: '812',
    aircraft: 'Boeing 737-8HG',
    registration: 'VT-AXV',
    lat: 12.9612,
    lon: 74.8900,
    location: 'Mangalore International Airport (IXE), Karnataka, India',
    fatalities: { onboard: 158, ground: 0, total: 158, occupants: 166 },
    phase: 'landing',
    category: 'runway',
    summary_zh: '由迪拜飞往芒格洛尔的 737-800 在芒格洛尔的台地式机场（tabletop airport）落地。机长在长时间夜航后处于睡眠惯性状态（CVR 录到约 1 小时 40 分鼾声），落地点远超跑道接地区。副驾驶呼叫复飞，机长拒绝。飞机以高速度冲出跑道末端、跌落约 60 米高的悬崖、解体起火。166 人中 158 人罹难，8 人通过机翼破口逃生幸存。事故凸显台地式机场的极端风险（无 overrun area、跑道末端即悬崖）和长航程后机长疲劳问题。印度民航当局事后修订了机长休息规定与多项目标场训练要求。',
    summary_en: 'A 737-800 from Dubai to Mangalore landed at the tabletop airport with a long flare and touched down well past the touchdown zone. The captain, after a long night sector, was in a sleep-inertia state (the CVR records about 1 hour 40 minutes of snoring during cruise); the first officer called for a go-around, which the captain rejected. The aircraft overran the runway end at high speed, fell off a ~60 m cliff, broke up and burned. 158 of 166 aboard died; 8 escaped through a wing breach. The accident highlighted the extreme risk of tabletop airports (no overrun area; runway ends at a cliff) and post-long-haul captain fatigue. The Indian DGCA subsequently revised crew rest regulations and target-airport familiarisation training.',
    links: [
      { label: 'Court of Inquiry Final Report', url: 'http://reports.aviation-safety.net/2010/20100522-0_B738_VT-AXV.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Air_India_Express_Flight_812' }
    ]
  },

  // 34. ─── Asiana 214 (San Francisco) ─────────────────────────
  {
    id: 'oz214',
    date: '2013-07-06',
    airline: 'Asiana Airlines',
    flight: '214',
    aircraft: 'Boeing 777-28EER',
    registration: 'HL7742',
    lat: 37.6189,
    lon: -122.3750,
    location: 'San Francisco International Airport (SFO), California, USA',
    fatalities: { onboard: 3, ground: 0, total: 3, occupants: 307 },
    phase: 'landing',
    category: 'runway',
    summary_zh: '由首尔仁川飞往旧金山的 777-200ER 在 SFO 28L 跑道目视进近时，速度持续低于目标，下降率过大，机尾撞上跑道入口前的海堤。机尾断裂，机身在跑道上滚转滑行。307 人中 3 人罹难（其中 1 人为机外救援车辆碾压致死），众多乘客重伤。机长 Lee Kang-kuk 是 777 转型训练飞行员，机组依赖自动油门保持速度——但 FLCH 模式下自动油门并不主动控制速度，机组未察觉。事故重新引发对自动化误解（automation surprise）和亚洲航司机长权威文化的讨论。NTSB 调查特别批评了波音对 777 自动飞行系统模式逻辑的训练材料不充分。',
    summary_en: 'A 777-200ER from Seoul Incheon was on a visual approach to SFO runway 28L when speed decayed below target, descent rate increased, and the tail struck the seawall short of the threshold. The tail separated, and the fuselage rolled and slid down the runway. Of 307 aboard, 3 died (one struck by an emergency vehicle outside the aircraft) with many serious injuries. Captain Lee Kang-kuk was undergoing 777 type training; the crew relied on autothrottle to hold speed — but in FLCH mode the autothrottle does not actively control speed, and the crew did not notice. The accident reopened the discussion of automation surprise and Asian carrier authority culture. The NTSB explicitly criticised Boeing\'s training materials for the 777 autoflight mode logic.',
    links: [
      { label: 'NTSB Accident Report AAR-14/01', url: 'https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1401.pdf' },
      { label: 'FAA Lessons Learned: 777 HL7742', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/HL7742' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Asiana_Airlines_Flight_214' }
    ]
  },

  // 35. ─── Malaysia Airlines 370 ───────────────────────────────
  {
    id: 'mh370',
    date: '2014-03-08',
    airline: 'Malaysia Airlines',
    flight: '370',
    aircraft: 'Boeing 777-2H6ER',
    registration: '9M-MRO',
    lat: -39.0,
    lon: 88.0,
    location: 'Indian Ocean, presumed (exact location unknown)',
    fatalities: { onboard: 239, ground: 0, total: 239, occupants: 239 },
    phase: 'cruise',
    category: 'unknown',
    summary_zh: '由吉隆坡飞往北京的 777-200ER 起飞约 38 分钟后，机组通过 ACARS 与 SATCOM 例行向 ATC 报告 "Good night Malaysian three seven zero" 之后即刻关闭应答机，飞机偏离原航线、向西回转穿越马来半岛、进入孟加拉湾、转向南下进入南印度洋。Inmarsat 卫星每小时与飞机进行的 "握手" 信号让事故调查者推断飞机在燃油耗尽前飞行了约 7 小时，落点在南印度洋远海未知区域。马来西亚、澳大利亚、中国主导的多次海上搜索（AUV、声纳扫描）覆盖约 12 万平方公里仍未找到主残骸。零星残骸（襟翼、副翼）数年后冲到非洲东海岸与留尼汪岛海滩。马来西亚最终调查报告（2018）未给出明确原因。事故催生 ICAO GADSS（全球航空遇险与安全系统）—要求所有商用客机每 15 分钟自动报告位置；此前每 30 分钟仅在指定区域。MH370 的下落至今未明，是民航史上最重大的未解之谜。',
    summary_en: 'A 777-200ER from Kuala Lumpur to Beijing, about 38 minutes after takeoff, signed off ATC with the routine "Good night Malaysian three seven zero" — and immediately afterwards the transponder went dark. The aircraft deviated from its planned route, turned west across the Malay Peninsula, entered the Bay of Bengal, then turned south into the deep southern Indian Ocean. Hourly Inmarsat satellite "handshakes" allowed investigators to infer about 7 hours of flight after the deviation, ending at fuel exhaustion somewhere in remote southern Indian Ocean. Malaysia-, Australia-, and China-led searches with AUVs and sonar covered about 120,000 km² without locating the main wreckage. Fragments — flaps, ailerons — have washed up on East African and Réunion beaches over subsequent years. Malaysia\'s 2018 final report did not state a cause. The accident drove ICAO\'s GADSS (Global Aeronautical Distress and Safety System), requiring all commercial aircraft to report position automatically every 15 minutes (previously every 30, in designated areas only). The fate of MH370 remains the great unresolved mystery of civil aviation.',
    links: [
      { label: 'Malaysian Investigation Final Report (2018)', url: 'https://reports.aviation-safety.net/2014/20140308-0_B772_9M-MRO.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Malaysia_Airlines_Flight_370' }
    ]
  },

  // 36. ─── Malaysia Airlines 17 ────────────────────────────────
  {
    id: 'mh17',
    date: '2014-07-17',
    airline: 'Malaysia Airlines',
    flight: '17',
    aircraft: 'Boeing 777-2H6ER',
    registration: '9M-MRD',
    lat: 48.1411,
    lon: 38.6519,
    location: 'Hrabove, Donetsk Oblast, Ukraine',
    fatalities: { onboard: 298, ground: 0, total: 298, occupants: 298 },
    phase: 'cruise',
    category: 'security',
    summary_zh: '由阿姆斯特丹飞往吉隆坡的 777-200ER 在乌克兰东部顿涅茨克州上空 33,000 英尺巡航时，被亲俄武装从地面发射的俄制 9K37 "山毛榉"（Buk）防空导弹击落，机头与左侧机身遭近接破片密集打击，飞机解体。机上 298 人全部罹难（其中 196 名荷兰公民）。荷兰主导的国际联合调查组（JIT）通过弹片化学分析、雷达数据、社交媒体记录追溯导弹发射车从俄罗斯第 53 防空旅运抵顿涅茨克再撤回的全过程，2022 年荷兰法院缺席判决三名俄罗斯及亲俄武装人员谋杀罪。事故催生 ICAO 关于冲突区飞越风险评估的修订指南，多国航司随后回避乌克兰、利比亚、叙利亚、伊拉克等冲突区上空。',
    summary_en: 'A 777-200ER from Amsterdam to Kuala Lumpur was at 33,000 feet over eastern Ukraine\'s Donetsk Oblast when a Russian-made 9K37 Buk surface-to-air missile, fired by pro-Russian forces from the ground, struck the cockpit and left fuselage with a dense pattern of pre-formed fragments; the aircraft broke up in flight. All 298 aboard died, including 196 Dutch citizens. The Dutch-led Joint Investigation Team traced the missile launcher\'s movement from Russia\'s 53rd Anti-Aircraft Missile Brigade into Donetsk and back via fragment chemistry, radar data, and social media; in 2022 a Dutch court convicted three Russian and pro-Russian personnel of murder in absentia. The accident drove ICAO guidance on conflict-zone overflight risk assessment; carriers worldwide subsequently avoided Ukrainian, Libyan, Syrian, and Iraqi airspace.',
    links: [
      { label: 'DSB Final Report', url: 'https://www.onderzoeksraad.nl/en/page/3546/crash-mh17-17-july-2014' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Malaysia_Airlines_Flight_17' }
    ]
  },

  // 37. ─── Germanwings 9525 ───────────────────────────────────
  {
    id: 'ger9525',
    date: '2015-03-24',
    airline: 'Germanwings',
    flight: '9525',
    aircraft: 'Airbus A320-211',
    registration: 'D-AIPX',
    lat: 44.2806,
    lon: 6.4392,
    location: 'Massif des Trois-Évêchés, French Alps, France',
    fatalities: { onboard: 150, ground: 0, total: 150, occupants: 150 },
    phase: 'cruise',
    category: 'security',
    summary_zh: '由巴塞罗那飞往杜塞尔多夫的 A320 在法国阿尔卑斯山上空巡航时，机长 Patrick Sondenheimer 离开驾驶舱去洗手间。副驾驶 Andreas Lubitz 关闭驾驶舱门并将自动驾驶高度设定从 38,000 英尺改为 100 英尺。机长返回时门已锁，紧急代码失效，他用斧头试图破门未成。飞机持续 8 分钟下降，撞入海拔 1,550 米山脊。机上 150 人全部罹难。Lubitz 长期患抑郁症并隐瞒病史；事发当日他已被一位医生开具不能飞行的诊断书但未上交雇主。事故催生 EASA 与各国航司"驾驶舱内任何时候至少两人在岗"规则（机长上洗手间时乘务员需进入），及对飞行员心理健康筛查程序的全面收紧——但"两人规则"在 2017 年后多家航司又放宽，理由是与心理健康无直接关联且增加运行复杂度。',
    summary_en: 'An A320 from Barcelona to Düsseldorf was cruising over the French Alps when Captain Patrick Sondenheimer left the cockpit for the lavatory. First Officer Andreas Lubitz locked the cockpit door and set the autopilot altitude from 38,000 feet to 100 feet. When the captain returned, the door was locked, the emergency override had been disabled, and his attempts to break in with an axe failed. The aircraft descended for 8 minutes and struck a 1,550 metre ridge. All 150 aboard died. Lubitz had a long-standing depressive illness which he had concealed; on the day of the flight, a doctor had given him a written certification that he was unfit to fly, which he did not submit to his employer. The accident drove the EASA "two persons in the cockpit at all times" rule (a flight attendant entering during a pilot\'s lavatory break) and a tightening of pilot mental-health screening — though several carriers relaxed the two-person rule after 2017, citing weak linkage to the underlying issue and operational cost.',
    links: [
      { label: 'BEA Final Report (English)', url: 'https://bea.aero/uploads/tx_elydbrapports/BEA2015-0125.en-LR.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Germanwings_Flight_9525' }
    ]
  },

  // 38. ─── Saratov Airlines 703 ────────────────────────────────
  {
    id: 'srt703',
    date: '2018-02-11',
    airline: 'Saratov Airlines',
    flight: '703',
    aircraft: 'Antonov An-148-100B',
    registration: 'RA-61704',
    lat: 55.4019,
    lon: 38.1431,
    location: 'Argunovo, Moscow Oblast, Russia',
    fatalities: { onboard: 71, ground: 0, total: 71, occupants: 71 },
    phase: 'climb',
    category: 'LOC-I',
    summary_zh: '由莫斯科多莫杰多沃机场飞往奥尔斯克的 An-148 起飞后，机长未启动皮托管加热——飞机在云中爬升期间，皮托管结冰使空速指示器读数错误。两个空速读数出现矛盾时机长断开自动驾驶手动操纵，根据错误的空速读数做出错误俯冲指令，飞机以 30 度俯角撞地。机上 71 人全部罹难。俄罗斯航空界长期存在将皮托加热视为可选程序的现象，事故催生俄罗斯民航局 ROSAVIATSIA 的强制性起飞前检查程序更新。',
    summary_en: 'An An-148 from Moscow Domodedovo to Orsk took off without pitot heat activated; in cloud during climb, the pitot tubes iced over and airspeed indications became erroneous. When the two airspeed readouts diverged, the captain disengaged the autopilot and acted on the false readings, pushing into a 30° dive. The aircraft struck the ground; all 71 aboard died. Russian aviation had long treated pitot heat as an optional procedure; the accident drove a mandatory pre-takeoff check requirement from Rosaviatsia.',
    links: [
      { label: 'IAC (MAK) Final Report', url: 'https://reports.aviation-safety.net/2018/20180211-0_AN48_RA-61704.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Saratov_Airlines_Flight_703' }
    ]
  },

  // 39. ─── Lion Air 610 ───────────────────────────────────────
  {
    id: 'jt610',
    date: '2018-10-29',
    airline: 'Lion Air',
    flight: '610',
    aircraft: 'Boeing 737 MAX 8',
    registration: 'PK-LQP',
    lat: -5.7958,
    lon: 107.1208,
    location: 'Java Sea, off Karawang, Indonesia',
    fatalities: { onboard: 189, ground: 0, total: 189, occupants: 189 },
    phase: 'climb',
    category: 'LOC-I',
    summary_zh: '由雅加达飞往邦加勿里洞的 737 MAX 8 起飞后，因左侧攻角传感器（AoA sensor）故障，MCAS（机动特性增强系统）反复将水平安定面配平至机头下俯。机组与 MCAS 之间发生持续配平抢夺约 11 分钟，机组未能识别问题源自 MCAS——因为波音并未在飞行手册或机型转换训练中告知机组该系统的存在。飞机最终俯冲撞入爪哇海，机上 189 人全部罹难。这是 737 MAX 系列首例致命事故。波音最初将事故归咎于机组培训不足，未停飞机型；五个月后埃塞俄比亚航空 ET302 以同样方式坠毁（见下条），全球停飞 MAX 长达 20 个月。',
    summary_en: 'A 737 MAX 8 from Jakarta to Pangkal Pinang experienced a left angle-of-attack (AoA) sensor failure shortly after takeoff. MCAS (Maneuvering Characteristics Augmentation System) repeatedly trimmed the stabilizer nose-down. A trim contest ensued between the crew and MCAS for about 11 minutes; the crew could not identify the source as MCAS because Boeing had not disclosed the system\'s existence in flight manuals or type conversion training. The aircraft eventually entered an unrecoverable dive into the Java Sea. All 189 aboard died. This was the first fatal accident of the 737 MAX. Boeing initially attributed the crash to inadequate crew training and did not ground the type; five months later Ethiopian 302 crashed in nearly identical circumstances (next entry), and the MAX was grounded worldwide for 20 months.',
    links: [
      { label: 'KNKT Final Report', url: 'http://knkt.dephub.go.id/knkt/ntsc_aviation/baru/2018%20-%20035%20-%20PK-LQP%20Final%20Report.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Lion_Air_Flight_610' }
    ]
  },

  // 40. ─── Ethiopian 302 ──────────────────────────────────────
  {
    id: 'et302',
    date: '2019-03-10',
    airline: 'Ethiopian Airlines',
    flight: '302',
    aircraft: 'Boeing 737 MAX 8',
    registration: 'ET-AVJ',
    lat: 8.8772,
    lon: 39.2517,
    location: 'Bishoftu, Ethiopia',
    fatalities: { onboard: 157, ground: 0, total: 157, occupants: 157 },
    phase: 'climb',
    category: 'LOC-I',
    summary_zh: '由亚的斯亚贝巴飞往内罗毕的 737 MAX 8 起飞后约 1 分钟，左侧攻角传感器（AoA）故障触发 MCAS——同 5 个月前 Lion Air 610 几乎一样的故障序列。机组识别了问题（受过 Lion Air 事故后波音补发的 emergency AD 训练），按程序断开电动配平、试图人工转动配平轮——但飞行高度低速度高，气动力使配平轮无法转动。机组在试图各种应急组合的 6 分钟后撞地，机上 157 人全部罹难。这次事故强迫了 737 MAX 全球停飞 20 个月，迫使波音公开 MCAS 的存在与设计、彻底重写 MCAS 软件、修订机型差异训练，并面临美国国会的多轮听证。波音 CEO Dennis Muilenburg 因此事故下台，公司支付 25 亿美元罚款。两次 MAX 事故是民航史上罕见的——同一型号在投入运行不到两年内两次以同一根本原因致命坠毁。',
    summary_en: 'A 737 MAX 8 from Addis Ababa to Nairobi suffered an AoA sensor failure about a minute after takeoff, triggering MCAS — almost the same fault sequence as Lion Air 610 five months earlier. This crew recognised the problem (they had received Boeing\'s post-Lion Air emergency AD training) and followed the procedure to cut electric trim and use the manual trim wheel — but at low altitude and high airspeed, aerodynamic loads on the stabilizer made the manual wheel impossible to turn. After six minutes of emergency configurations, the aircraft struck the ground. All 157 aboard died. This second crash forced the global 737 MAX grounding (20 months), public disclosure of MCAS\'s existence and design, a complete software rewrite, revised type-difference training, and multiple U.S. congressional hearings. Boeing CEO Dennis Muilenburg was forced out; the company paid $2.5 billion in penalties. The two MAX accidents are nearly unique in aviation history — the same model, killing nearly 350 people from the same root cause within months of entering service.',
    links: [
      { label: 'AIB Ethiopia Final Report', url: 'https://www.aib.gov.et/wp-content/uploads/2020/documents/Final%20Report%20ET-302.pdf' },
      { label: 'FAA Lessons Learned: 737 MAX', url: 'https://www.faa.gov/lessons_learned/transport_airplane/accidents/ET-AVJ' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Ethiopian_Airlines_Flight_302' }
    ]
  },

  // 41. ─── Ukraine International 752 ──────────────────────────
  {
    id: 'ps752',
    date: '2020-01-08',
    airline: 'Ukraine International Airlines',
    flight: '752',
    aircraft: 'Boeing 737-8KV',
    registration: 'UR-PSR',
    lat: 35.5611,
    lon: 51.1086,
    location: 'Parand, Tehran, Iran',
    fatalities: { onboard: 176, ground: 0, total: 176, occupants: 176 },
    phase: 'climb',
    category: 'security',
    summary_zh: '由德黑兰霍梅尼机场飞往基辅的 737-800 起飞后约 2 分钟，被伊朗革命卫队（IRGC）防空部队的两枚 Tor-M1 防空导弹击中。事发时正值美伊紧张升级期间——美军 Qasem Soleimani 将军被无人机击毙后六天，伊朗向伊拉克美军基地发射弹道导弹后数小时，IRGC 处于"高度战备"状态并开启防空雷达。导弹操作员将该航班误识为巡航导弹（疑因雷达校准未与机场坐标同步偏差所致）。机上 176 人全部罹难（其中 138 名加拿大-伊朗双国籍乘客，准备转乘多伦多航班）。伊朗最初否认击落，三天后承认；事故引发加拿大、乌克兰、瑞典等国对伊朗的国际索赔诉讼。',
    summary_en: 'A 737-800 from Tehran Imam Khomeini to Kyiv was about 2 minutes after takeoff when it was hit by two Tor-M1 surface-to-air missiles fired by the Iranian Revolutionary Guard Corps (IRGC) air-defence forces. The shoot-down occurred during the U.S.–Iran escalation: six days after the U.S. drone strike that killed General Qasem Soleimani, hours after Iranian ballistic-missile strikes on U.S. forces in Iraq, with IRGC air defences on a high state of alert. The missile crew misidentified the airliner as a cruise missile, reportedly due to a misalignment between the unit\'s radar bearing and the airport coordinates. All 176 aboard died, including 138 Canadian-Iranian dual nationals continuing to Toronto. Iran initially denied the shoot-down, then admitted it three days later. The accident led to international legal claims against Iran by Canada, Ukraine, Sweden, and the United Kingdom.',
    links: [
      { label: 'CAO Iran Final Report', url: 'https://www.cao.ir/documents/20124/152633/PS-752+Final+Report+EN.pdf' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Ukraine_International_Airlines_Flight_752' }
    ]
  },

  // 42. ─── China Eastern 5735 (Holmes case) ────────────────────
  {
    id: 'mu5735',
    date: '2022-03-21',
    airline: 'China Eastern Airlines',
    flight: '5735',
    aircraft: 'Boeing 737-89P',
    registration: 'B-1791',
    lat: 23.3257,
    lon: 110.8678,
    location: 'Mountainous terrain, Tengxian County, Wuzhou, Guangxi, China',
    fatalities: { onboard: 132, ground: 0, total: 132, occupants: 132 },
    phase: 'cruise',
    category: 'unknown',
    summary_zh: '由昆明飞往广州的 737-800 在巡航高度 8,900 米突然进入近垂直俯冲，约一分钟后撞入广西梧州藤县山区，机上 132 人全部罹难。中国民航局负责调查；2024 年 3 月发布的过渡性更新报告称机组、维护、管制员、设备、天气、危险品均"无异常"。2025 年三周年时未按 ICAO 附件 13 要求发布更新；同年 5 月民航局公开拒绝公布进一步信息，理由是"可能危及国家安全"。柯南·道尔笔下的福尔摩斯有一句格言：<em>"How often have I said to you that when you have eliminated the impossible, whatever remains, however improbable, must be the truth?"</em>（《四签名》，1890）。本案的所有"可能"已被官方排除，剩下的"不可能"则被封存。',
    summary_en: 'A 737-800 from Kunming to Guangzhou, cruising at 8,900 metres, entered a near-vertical descent and struck mountainous terrain in Tengxian County, Guangxi about a minute later. All 132 aboard died. The Civil Aviation Administration of China (CAAC) is the investigating authority. An interim update issued in March 2024 reported "no anomalies" in crew, maintenance, controller performance, aircraft systems, weather, or cargo. CAAC missed the third-anniversary update required by ICAO Annex 13 and, in May 2025, publicly declined to release further information on the grounds that doing so might "endanger national security." Conan Doyle\'s Sherlock Holmes is on record with a relevant precept: <em>"How often have I said to you that when you have eliminated the impossible, whatever remains, however improbable, must be the truth?"</em> (<em>The Sign of the Four</em>, 1890). In this case, every possibility has been officially eliminated; what remains is sealed.',
    links: [
      { label: 'CAAC Preliminary Report (April 2022)', url: 'http://www.caac.gov.cn/XXGK/XXGK/ZFXXGKML/202204/t20220420_212614.html' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/China_Eastern_Airlines_Flight_5735' }
    ]
  },

  // 43. ─── Jeju Air 2216 ──────────────────────────────────────
  {
    id: 'je2216',
    date: '2024-12-29',
    airline: 'Jeju Air',
    flight: '2216',
    aircraft: 'Boeing 737-8AS',
    registration: 'HL8088',
    lat: 34.9939,
    lon: 126.3833,
    location: 'Muan International Airport (MWX), South Korea',
    fatalities: { onboard: 179, ground: 0, total: 179, occupants: 181 },
    phase: 'landing',
    category: 'runway',
    summary_zh: '由曼谷飞往韩国务安的 737-800 在进近期间遭遇鸟击（推测两侧发动机均吸入鸽子或类似中等鸟类）。机组宣布 mayday 复飞后绕场，第二次进近选择反向 19 号跑道、不放起落架与襟翼，以高速腹部着陆。飞机沿跑道滑行至跑道末端，撞上一道长期争议的混凝土堤墙——该堤墙原为 ILS 定位天线提供支撑，但其结构高度与刚度被多位航空安全专家此前警告过分危险。机身完全解体起火，仅尾部两名乘务员幸存。机上 181 人中 179 人罹难。事故引发对务安机场基础设施安全标准的公开讨论；韩国国土交通部宣布全国机场内堤墙审计。',
    summary_en: 'A 737-800 from Bangkok to Muan in South Korea apparently suffered bird ingestion (likely doves or similar medium birds) into both engines on approach. The crew declared mayday and went around; on the second approach, they chose the opposite-direction runway 19, did not extend gear or flaps, and made a high-speed belly landing. The aircraft slid the length of the runway and struck a concrete embankment at the runway end — an embankment that had supported the ILS localiser antenna but whose structural height and rigidity had been criticised by aviation safety specialists for years. The fuselage broke up and burned; only two flight attendants in the tail section survived. Of 181 aboard, 179 died. The accident opened public debate on airport infrastructure safety standards in Korea; the Ministry of Land, Infrastructure and Transport announced a national audit of airport embankments and frangibility standards.',
    links: [
      { label: 'ARAIB Investigation Page', url: 'https://araib.molit.go.kr/' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Jeju_Air_Flight_2216' }
    ]
  },

  // 44. ─── Air India 171 ──────────────────────────────────────
  {
    id: 'ai171',
    date: '2025-06-12',
    airline: 'Air India',
    flight: '171',
    aircraft: 'Boeing 787-8',
    registration: 'VT-ANB',
    lat: 23.0772,
    lon: 72.6347,
    location: 'Meghaninagar, near Sardar Vallabhbhai Patel Airport, Ahmedabad, India',
    fatalities: { onboard: 241, ground: 19, total: 260, occupants: 242 },
    phase: 'takeoff',
    category: 'LOC-I',
    summary_zh: '由艾哈迈达巴德飞往伦敦盖特威克的 787-8 起飞后约 30 秒内失去推力坠毁，撞入机场附近的 BJ 医学院学生宿舍楼。机上 242 人中 241 人罹难（一名英国乘客 Vishwash Kumar Ramesh 从 11A 座位幸存），地面 19 人罹难（多为医学院学生）。这是 787 系列服役以来首次致命事故、印度国内自 1996 年 Charkhi Dadri 以来死亡人数最多的空难。印度民航事故调查局（AAIB）2025 年 7 月初步调查报告指出：起飞滚转后两台 GEnx 发动机的燃油控制开关在事发时被切至 cutoff 位（极短间隔内连续切断），驾驶舱话音记录显示一名机组成员问另一名 "为什么切断"，对方否认。最终调查仍在进行；具体原因（电气、软件、机组操作）尚未确定。事故对 787 与 GEnx 信誉产生重大影响。',
    summary_en: 'A 787-8 from Ahmedabad to London Gatwick lost thrust within about 30 seconds of takeoff and crashed into the BJ Medical College student hostel near the airport. Of 242 aboard, 241 died — sole survivor Vishwash Kumar Ramesh, a British passenger seated in 11A — plus 19 on the ground (many medical students). It was the first fatal accident of the 787 family and India\'s deadliest accident since Charkhi Dadri in 1996. The Indian AAIB\'s preliminary report (July 2025) found that the fuel control switches for both GEnx engines were moved to CUTOFF in rapid succession after rotation; the cockpit voice recorder captured one crew member asking the other "why did you cut off," with denial from the other. The full investigation remains underway; the cause (electrical, software, or crew action) is not yet determined. The accident has had a major impact on the 787 and GEnx reputation.',
    links: [
      { label: 'AAIB India Preliminary Report (July 2025)', url: 'https://aaib.gov.in/' },
      { label: 'Wikipedia', url: 'https://en.wikipedia.org/wiki/Air_India_Flight_171' }
    ]
  },

];
