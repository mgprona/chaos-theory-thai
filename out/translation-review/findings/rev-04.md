# rev-04 — Thai localization QA review

**Targets:** `data/translations/story/04_GCS.json` (117), `data/translations/story/04_Penthouse.json` (548), `data/translations/story/05_NuclearPlant.json` (54)
**Method:** script-dumped every `(section, key, en, th)` triple; reviewed all of `04_GCS` and `05_NuclearPlant`, and in `04_Penthouse` every `en` > 180 chars, every `Objective_*` / `Email*` / `Briefing_*` key, plus every 3rd remaining line (334 script-selected + remainder skimmed ≈ 460 strings total). fr/de/es/it were used as second opinions on each candidate row; no source file was modified.
**Notes:** curly apostrophes ( ’ ) in `en` are original data, not defects. Machine sweeps (digits, placeholders, whitespace edges, Latin-in-Thai, TH/EN length ratio, duplicate `en` with differing `th`) returned **zero** hits for these three files, so every row below is a human-read semantic/tone call.

## Verdicts

**`data/translations/story/04_GCS.json` — 8/10.** The cleanest of the three: names, honorifics (ครับท่าน / แก), bomb mechanics and objective text all track the source, and the two digit-set differences are only spelled-out numerals, not dropped data. Remaining issues are low-severity idiom and word-choice polish.

**`data/translations/story/04_Penthouse.json` — 6/10.** Structure, names and objective text are sound, but there are two outright meaning errors in ambient dialogue and a recurring ungrammatical night-vision phrase across four keys. Register/tone slips (slang flattened, literal calques) are frequent enough to be a pattern rather than one-offs.

**`data/translations/story/05_NuclearPlant.json` — 8/10.** The flagged `GENERAL::Briefing_LAMBERT` suspicion is a **false alarm**: `en` "The 3 double-laser detonators" is rendered "ตัวจุดชนวนแบบเลเซอร์คู่**สาม**ตัว", i.e. the numeral 3 is spelled out in Thai rather than dropped — fr/de/es do the same, and the count, the Yongbyon link and the mission order are all intact (digit-set diff is only 3 → "สาม"; likewise 5th → "ฟิฟท์" in GCS). Remaining findings are deixis/word-choice at Low.

## Findings — 04_GCS.json

| sev | type | section::key | EN | TH | problem + suggested Thai fix |
|---|---|---|---|---|---|
| Low | UNNATURAL | P_04_GCS_Communications::Speech_0001L | LAMBERT - From what we can tell, Kim has men all over the area. | แลมเบิร์ต - เท่าที่เราบอกได้ คิมมีคนกระจายอยู่ทั่วพื้นที่ | "เท่าที่เราบอกได้" is a stiff calque of "from what we can tell" (de "wie es aussieht", it "a quanto ci risulta") → "เท่าที่เราพอจะบอกได้" |
| Low | MEANING GAIN | P_04_GCS_ConvCellPhoneChu::Speech_0003L | CHU - Well hurry up... and be careful. Those things are sensitive. | ชู - งั้นก็รีบๆ... และระวังด้วย ของพวกนั้นไวต่อการสั่นสะเทือน | Adds "ต่อการสั่นสะเทือน" (to vibration); fr/de/es/it all say only "sensitive" → "ของพวกนั้นไวมาก" |
| Low | TERM | P_04_GCS_Objectives::Objective_0010 | Chu, and agent of Kim's, will be receiving a telephone call on a payphone | ชู เจ้าหน้าที่ของคิม จะรับสายโทรศัพท์ที่ตู้สาธารณะในห้องโถงหลัก | "เจ้าหน้าที่ของคิม" reads as "Kim's official/staff", not a spy/operative → "ชู สายลับของคิม" (or "คนของคิม") |
| Low | MEANING LOSS | P_04_GCS_Email::EmailDiffusalBody | we don't want some lone wolf sneaking in here and disabling our bombs | เราไม่อยากให้ใครที่คิดจะเล่นคนเดียวแอบเข้ามาปลดระเบิดของเรา | "lone wolf" → "คิดจะเล่นคนเดียว" trivialises it (เล่น = play) → "คนที่ชอบทำอะไรคนเดียว" |

## Findings — 04_Penthouse.json

| sev | type | section::key | EN | TH | problem + suggested Thai fix |
|---|---|---|---|---|---|
| Medium | MISTRANSLATION | P_04_Penthouse_Conversation_Park::Speech_0005L | So where does that leave us? | งั้นเราจะเหลืออะไรล่ะ? | Idiom read as "what will be left for us"; fr "on fait quoi ?", de "was heißt das für uns ?" → the next line ("In the dark...as usual") depends on it → "แล้วเราจะทำยังไงต่อ" |
| Medium | MISTRANSLATION | P_04_Penthouse_Conversation_Patio::Speech_0001L | Hey... I don't recognize you. How long have you been with Displace? | เฮ้... ฉันจำคุณไม่ได้ อยู่กับดิสเพลสมาบ่อยแค่ไหน? | "how long" (fr "depuis longtemps ?", de "wie lange") mistranslated as "บ่อยแค่ไหน" (how often) → "คุณอยู่กับดิสเพลสมานานแค่ไหนแล้ว?" |
| Medium | MISTRANSLATION | P_04_Penthouse_AlarmState::Speech_0002L | I'm serious Sam... too many alarms these mercenaries will be after you. | ฉันพูดจริงนะแซม... สัญญาณเตือนภัยดังมากเกินไป พวกทหารรับจ้างจะตามล่าคุณ | "too many alarms" → "alarm too loud"; fr "trop d'alertes", de "wenn der Alarm zu oft losgeht", es "demasiadas alarmas" → "สัญญาณเตือนภัยดังบ่อยเกินไป" |
| Medium | GRAMMAR | P_04_Penthouse_Objectives::Note_0041L | You can see the infrared light projected by IR cameras with Night Vision. | คุณเห็นแสงอินฟราเรดที่กล้อง IR ฉายได้ด้วยมองกลางคืน | "ด้วยมองกลางคืน" is ungrammatical (verb phrase used as an instrument); same flaw in Lambert_Comm Speech_0007L / Speech_0112L / Speech_0162L → "ด้วยโหมดมองกลางคืน" |
| Medium | UNNATURAL | P_04_Penthouse_Interro_Construction::Speech_0004L | we need to secure it because we can't lock it off from the penthouse. | เราดูแลคุ้มกันบุคคลสำคัญ... เราต้องรักษาความปลอดภัยเพราะเราล็อกไม่ให้แยกจากเพนต์เฮาส์ไม่ได้ | Double negative garbles "lock it off from the penthouse" (de "weil wir sie vom Penthouse aus nicht abriegeln können") → "เราต้องรักษาความปลอดภัยชั้นนี้ เพราะปิดกั้นมันแยกจากเพนต์เฮาส์ไม่ได้" |
| Medium | UNNATURAL | P_04_Penthouse_Interro_Construction::Speech_0010L | You're messing with the wrong company pal. | คุณกำลังยุ่งกับบริษัทผิดคนแล้วเพื่อน | "บริษัทผิดคน" is not Thai; fr/de/es all say "wrong people" → "คุณกำลังไปยุ่งกับพวกผิดคนแล้วเพื่อน" |
| Medium | NAME | P_04_Penthouse_Lambert_Comm::Speech_0164L | That's Doug Shetland's company. | นั่นคือบริษัทของดั๊ก เชตแลนด์ | Locked glossary is Douglas Shetland = ดักลาส เชตแลนด์; file writes ดั๊ก เชตแลนด์ (also Speech_0099L, Speech_0102L) → "ดักลาส เชตแลนด์" |
| Low | TERM | P_04_Penthouse_Lambert_Comm::Speech_0003L | He's no night watchman either...he's a merc. | เขาก็ไม่ใช่นายทหารยามกลางคืน... เขาเป็นทหารรับจ้าง | "นายทหารยาม" = military officer of the guard; EN/IT mean a plain watchman → "เขาก็ไม่ใช่ยามเฝ้ากลางคืนเหมือนกัน" |
| Low | UNNATURAL | P_04_Penthouse_Lambert_Comm::Speech_0002L | Fisher, that's a hired gun if I've ever seen one. | ฟิชเชอร์ นั่นคือมือปืนรับจ้างชัดๆ ถ้าเคยมี | Dangling "ถ้าเคยมี" (no object) → drop it or "นั่นคือมือปืนรับจ้างชัดๆ ถ้าเคยมีสักคน" |
| Low | UNNATURAL | P_04_Penthouse_Lambert_Comm::Speech_0101L | Maybe you can dig up some blueprints. | บางทีคุณอาจขุดแบบแปลนได้ | Literal "ขุด" for "dig up"; cf. Speech_0035L "ขุดหาแผน" which works → "บางทีคุณอาจหาแบบแปลนได้" |
| Low | TONE/REGISTER | P_04_Penthouse_Lambert_Comm::Speech_0077L | Always happy to keep the donut dippers busy. | ยินดีเสมอที่ได้ทำให้พวกตำรวจต้องทำงาน | Mocking cop slang flattened (fr "gratte-papier", de "Sesselfurzer", it "culi di pietra") → "ยินดีเสมอที่ได้ทำให้พวกตำรวจหัวหมุน" |
| Low | UNNATURAL | P_04_Penthouse_SamIsAKiller::Speech_0003L | We don't have room for accidents. Watch your fire. | เราไม่มีที่ให้กับอุบัติเหตุ ระวังการยิงของตัวเอง | Word-for-word "room for" → "เราไม่อาจมีอุบัติเหตุได้ ระวังการยิงของตัวเอง" |
| Low | MEANING LOSS | P_04_Penthouse_SRC_NG1::Speech_0006L | a Chinese knock-off of a wrought-iron Soviet-era Russian missile | จรวดโซเวียตสมัยเก่าที่จีนก๊อปมา | "wrought-iron" (เหล็กดัด) dropped although de/it keep the junk-metal image → "จรวดเหล็กดัดโซเวียตยุคเก่าที่จีนก๊อปมา" |
| Low | TERM | P_04_Penthouse_Lambert_Comm::Speech_0020L | Hmm... work permits, architectural plans... interesting... | หืม... ใบอนุญาตทำงาน แบบแปลนสถาปัตยกรรม... น่าสนใจ... | "ใบอนุญาตทำงาน" = (alien) work permit; context is construction filings, cf. Speech_0014L "ใบอนุญาตก่อสร้าง" → "ใบอนุญาตก่อสร้าง" |
| Low | MEANING LOSS | P_04_Penthouse_Gnome_help::Speech_0029L | but let's have it for the record anyway. | แต่เล่ามาให้ครบเป็นทางการหน่อย | "for the record" ≠ "ให้ครบ/เป็นทางการ" → "แต่เล่าให้ฟังเพื่อบันทึกไว้หน่อยก็แล้วกัน" |
| Low | TONE/REGISTER | P_04_Penthouse_Gnome_Lambert::Speech_0030L | weird academic sixties era university basement crap. | ของเก่าๆ สไตล์มหาวิทยาลัยยุคหกสิบที่น่าประหลาด | "crap" and "basement" lost, register softened (also Speech_0053L) → "ของเก่าๆ น่าประหลาดจากห้องใต้ดินมหาวิทยาลัยยุคหกสิบ" |

## Findings — 05_NuclearPlant.json

| sev | type | section::key | EN | TH | problem + suggested Thai fix |
|---|---|---|---|---|---|
| Low | UNNATURAL | P_05_NuclearPlant_LambertConv::Speech_0005L | LAMBERT - Good. Now cross the turbine room and you'll be on the way to the control room. | แลมเบิร์ต - ดี ตอนนี้ข้ามห้องกังหันมา แล้วคุณจะอยู่บนเส้นทางไปห้องควบคุม | Wrong direction particle "มา" (Lambert is not there; fr "traversez", de "durchquere") + literal "จะอยู่บนเส้นทาง" → "ข้ามห้องกังหันไป แล้วคุณจะเข้าสู่เส้นทางไปห้องควบคุม" |
| Low | GRAMMAR | Email::EmailLabBody | Deliver as many detonators as you can to Colonel Kim Pak-tu for a test mission. | ส่งตัวจุดชนวนมาให้พันเอกคิม พักทูให้มากที่สุดเท่าที่จะทำได้เพื่อภารกิจทดสอบ | "มาให้" is wrong deixis (Jin Soo is writing to Wen, not receiving); sentence-final "มาก" in the preceding clause also misreads → "ส่งตัวจุดชนวนให้พันเอกคิม พักทูให้มากที่สุดเท่าที่จะทำได้" + "...ที่ฉันไปยงบยอนครั้งล่าสุดเป็นอย่างมาก" |
| Low | MISTRANSLATION | P_05_NuclearPlant_OBJ::Objective_0021 | Colonel Kim cannot have organized everything by himself. | พันเอกคิมไม่สามารถจัดฉากทุกอย่างได้ด้วยตัวเอง | "จัดฉาก" = to stage/fake a scene, not to organise; same wording in GENERAL::Briefing_LAMBERT → "พันเอกคิมไม่สามารถจัดการทุกอย่างได้ด้วยตัวเอง" |
| Low | UNNATURAL | P_05_NuclearPlant_LambertConv::Speech_0011L | LAMBERT - Today is not your lucky day. | แลมเบิร์ต - วันนี้ไม่ใช่วันดีของคุณ | Literal calque of "not your lucky day" → "วันนี้โชคไม่เข้าข้างคุณ" |
| Low | SUBTITLE-LENGTH | P_05_NuclearPlant_AlarmCheck::POPUPMESSAGE_0004 | Alarm Stage Four - Full Alert - Enemies Fortifying Positions | ระดับสัญญาณเตือนภัยขั้นที่สี่ - เตรียมพร้อมเต็มอัตรา - ศัตรูเสริมกำลังที่มั่น | 77 chars vs 60 EN (1.28x) on a short on-screen popup, with redundant "ระดับ"+"ขั้นที่" → "สัญญาณเตือนภัยขั้นที่สี่ - เตรียมพร้อมเต็มอัตรา - ศัตรูเสริมกำลังที่มั่น" (same in Penthouse AlarmState::POPUPMESSAGE_0009) |

## Three highest-impact fixes

1. **`04_Penthouse` `Conversation_Park::Speech_0005L`** — "So where does that leave us?" is read as "what will be left for us"; fix to "แล้วเราจะทำยังไงต่อ" so the "In the dark…as usual" punchline lands.
2. **`04_Penthouse` night-vision wording (4 keys: `Objectives::Note_0041L`, `Lambert_Comm::Speech_0007L` / `Speech_0112L` / `Speech_0162L`)** — "ด้วยมองกลางคืน" is broken Thai on a repeated tutorial hint; change to "ด้วยโหมดมองกลางคืน".
3. **`04_Penthouse::AlarmState::Speech_0002L` + `Conversation_Patio::Speech_0001L`** — two meaning inversions in ambient dialogue ("alarm too loud" for "too many alarms"; "how often" for "how long") that misinform the player about the stealth/alarm system.
