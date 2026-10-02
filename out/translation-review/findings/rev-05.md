# Thai Localization QA — rev-05

Reviewer: rev-05 (Thai localization QA). Scope: `data/translations/story/05_Displace01.json`, `data/translations/story/07_UNhq.json`.
Method: script dump of all `(section, key, en, th)` triples + fr/de/es/it second opinions (`scratch/rev-05/`); automated digit/placeholder/glossary/left-English/length passes, then manual review of every string in both files (603 strings: 346 sampled as required + remaining 196 of 05 skimmed in full + all 61 of 07).
Known suspicions: (1) `EmailWNMLotteryBody` digit set — **CLEARED**: the extra `3` in Thai is `III` → `ที่ 3`; `1.1` and `68.4` are correct. (2) `InterroRoof::Speech_0013L` — speaker prefix `-DisSol_Walter-` → `พลทหารดิสเพลสวอลเตอร์ -` is correct; `twenty-seven B stroke six` → `27 บี สโตรก 6` matches DE "27B-Strich-6"/IT "27B barra 6" (raw transliteration, low style issue only). (3) E-mail register — the two WNM wire bodies do read as news copy; only `EmailWNMMasonBody` slips into redundant spoken-style reporting.

## data/translations/story/05_Displace01.json — verdict 5.5/10

Broad, mostly natural translation with correct glossary names and good handling of the long conference/briefing monologues, but it carries several high-confidence idiom mistranslations, one garbled sentence, and a 14-string block where raw English speaker tags were never localized. Factual/unit detail is also wrong in at least one place (weapon spec), which a player can hear in voiced dialogue.

| sev | type | section::key | EN | TH | problem + suggested Thai fix |
|---|---|---|---|---|---|
| High | MISTRANSLATION | SecurityEvents::Speech_0022L | `I'm gonna sort you out if you don't open the damn door.` | `ฉันจะจัดเรียงแกเองถ้าแกไม่เปิดประตูบ้าๆ นี่` | "sort out" = deal with/punish; `จัดเรียง` = to arrange/tidy. → `ถ้าแกไม่เปิดประตูบ้าๆ นี่ ฉันจะจัดการแกเอง` |
| High | MISTRANSLATION | RDEvents::Speech_0021L / SRC::Speech_0005L | `The guy isn't there anymore. He's outta town.` | `หมอนั่นไม่อยู่แล้ว เข้าออกตัวเมืองไปแล้ว` | garbled ("enter-exit the city"); `outta town` = out of town. → `เขาออกจากเมืองไปแล้ว` |
| High | MISTRANSLATION | InterroRDLounge::Speech_0010L | `...the prototype is individual...40 mill launchable...` | `...แต่ต้นแบบเป็นแบบพกพา... ยิงได้ไกล 40 เมตร...` | unit wrong: FR "40 mm", DE "40 Millimeter"; `individual` ≠ portable. → `...ต้นแบบเป็นแบบใช้คนเดียว... ยิงได้ 40 มม.` |
| High | MISTRANSLATION | InterroOfficeExec::Speech_0011L / Email::EmailLobbyCodeBody | `I was going to the operations room` / `between the ops room and the main lobby` | `ผมจะไปห้องปฏิบัติการ` / `ระหว่างห้องปฏิบัติการกับล็อบบี้หลัก` | `ops room` rendered as `ห้องปฏิบัติการ` (laboratory; DE "Betriebsraum"). → `ห้องควบคุมปฏิบัติการ` |
| Medium | MISTRANSLATION | NoKill::Speech_0001L | `I'm pulling the plug. Mission over.` | `ฉันจะตัดไฟ ภารกิจจบ` | "pull the plug" = abort, not cut power. → `ฉันจะยุติภารกิจ ภารกิจจบ` |
| Medium | GRAMMAR/TYPO | OfficeOpsConvo::Speech_0007L | `Heya, Mike. Brought Tom to see you.` | `เฮ้ ไมก์ พาฉันทอมมาหาคุณ` | garbled `พาฉันทอม` ("brought me Tom"). → `พาทอมมาหาคุณ` |
| Medium | MISTRANSLATION | InterroNYC::Speech_0007L | `...an army of sociopathic snake-eaters...` | `...กองทัพของพวกโรคจิตชอบกินงู...` | "snake-eater" = US spec-ops slang, not snake eating. → `...กองทัพหน่วยรบพิเศษโรคจิต...` |
| Medium | LEFT-ENGLISH | LobbyGFConvo::Speech_0002L-0008L, LobbyMezzConvo::Speech_0002L-0008L (14 strings) | `-DisExc_Julian- In the lobby of the Empire State Building...` | `-DisExc_Julian- ในล็อบบี้ของตึกเอ็มไพร์สเตต...` | raw English speaker tags survive; 280 sibling lines converted to `ฟิชเชอร์ -`/`กริมส์ดอตเตียร์ -` style (fr/de/es/it drop the tag). → replace with `ผู้บริหารดิสเพลสจูเลียน -` / `สมาชิกสภาเทศบาลทอม -` |
| Medium | TONE/REGISTER | Email::EmailWNMMasonBody | `Defense Secretary Frank Mason was quoted as saying the National Guard...` | `รัฐมนตรีกลาโหมแฟรงก์ เมสันถูกอ้างคำพูดว่ากล่าวว่าเนชันนัลการ์ด...` | redundant, un-newswire-like (`ถูกอ้างคำพูดว่ากล่าวว่า`). → `แฟรงก์ เมสัน รัฐมนตรีกลาโหม ให้สัมภาษณ์ว่า...` |
| Medium | TERM | VIPLaserMic::Speech_0007L | `...as though there is a package on site.` | `...เสมือนมีสิ่งของอยู่ในพื้นที่` | "package" = the protected principal (FR "le client", DE "jemanden zu bewachen"), not an object. → `เสมือนมีบุคคลที่ต้องคุ้มกันอยู่ในพื้นที่` |
| Medium | NAME | Objectives::Speech_0119L / Speech_0109L | `...moved to the terminal of Mnedich...` | `...ย้ายไปที่เครื่องปลายทางของ Mnedich...` | Latin name kept although the same file uses `เอ็ม เนดิช` (Speech_0054L, Speech_0058L). → `ของเอ็ม เนดิช` |
| Medium | TERM | Objectives::Speech_0061L | `Echelon has nothing on him. Looks like he's been zeroed.` | `อีเชลอนไม่มีข้อมูลของเขาเลย...` | third spelling of the agency (glossary: `เธิร์ดเอเชลอน`, elsewhere `เอเชลอน`). → `เธิร์ดเอเชลอนไม่มีข้อมูลของเขาเลย` |
| Medium | MEANING LOSS/GAIN | InterroLobbyGuardA::Speech_0004L | `Fancy Nancy in the third at Belmont tomorrow...` | `แฟนซี แนนซี ในการแข่งที่เบลมอนต์พรุ่งนี้...` | "in the third" (race 3) dropped. → `...ในการแข่งม้าลำดับที่ 3 ที่เบลมอนต์พรุ่งนี้` |
| Low | MEANING LOSS/GAIN | OfficeEvents::Speech_0020L | `...but they don't want to see protection. It frightens them.` | `...แต่พวกเขาไม่อยากเห็นการคุ้มกัน มันทำให้กลัว` | missing object. → `มันทำให้พวกเขากลัว` |
| Low | UNNATURAL | SecurityEvents::Speech_0019L | `Hot, neutral, ground... got it all sorted out.` | `สายมีไฟ สายกลาง สายดิน... จัดเรียงครบแล้ว` | `จัดเรียง` does not collocate with wiring. → `...ต่อสายครบแล้ว` |
| Low | NAME | BGuardConvo::Speech_0009L/0011L/0013L/0015L | `-DisSol_Leif- Hey... NASA just reported...` | `พลทหารดิสเพลสไลฟ์ - เฮ้... NASA...` | Leif ≠ `ไลฟ์` (live). → `พลทหารดิสเพลสลีฟ` |
| Low | TONE/REGISTER | InterroVIPSol::Speech_0004L | `-DisSol_Paul- Forget it...I won't tell you anything.` | `ฝันไปเถอะ... ฉันไม่บอกอะไรแกทั้งนั้น` | same speaker uses `ผม/คุณ` in Speech_0013L; `ฉัน…แก` breaks register. → `ผมไม่บอกอะไรคุณทั้งนั้น` |
| Low | UNNATURAL | Objectives::Speech_0049L | `I would appreciate it.` | `ฉันจะขอบคุณมาก` | elliptical; reads unfinished. → `ถ้าอย่างนั้นฉันจะขอบคุณมากเลย` |
| Low | TONE/REGISTER | RoofEvents::Speech_0010L | `...I don't even know him.` | `...ฉันไม่รู้จักมันด้วยซ้ำ` | `มัน` for a person. → `ฉันไม่รู้จักเขาเลยด้วยซ้ำ` |
| Low | TERM | Objectives::Objective_0092 / Objective_0093 | `Recover technical specifications/reports...` | `เก็บกู้ข้อมูลจำเพาะทางเทคนิค...` | `เก็บกู้` = salvage (wreckage/bodies); for data use `กู้คืน`/`เก็บรวบรวม`. |
| Low | MEANING LOSS/GAIN | AlarmCheck::Speech_0003L | `One more alarm and you'll be in big trouble.` | `อีกครั้งเดียวคุณจะเจ็บตัวหนัก` | "in big trouble" ≠ physical injury. → `อีกครั้งเดียวคุณงานเข้าแน่` |
| Low | GRAMMAR/TYPO | Objectives::Speech_0088L | `...Displace's laundry basket` | `...ตะกร้าผ้าซักของดิสเพลส` | `ผ้าซัก` is not a Thai collocation. → `ตะกร้าใส่ผ้าของดิสเพลส` |
| Low | LEFT-ENGLISH | GENERAL::Briefing | `TODO` | `TODO` | placeholder in *both* en and th (source is untranslated); if the key ships, "TODO" is displayed. Translate or exclude from the build. |
| Low | UNNATURAL | InterroRoof::Speech_0013L | `...fill out your twenty-seven B stroke six.` | `...กรอกแบบฟอร์ม 27 บี สโตรก 6 ด้วย` | prefix/number OK (suspicion 2 cleared); `สโตรก` is a bare transliteration. Consider `แบบฟอร์ม 27 บี/6` for readability. |

## data/translations/story/07_UNhq.json — verdict 8/10

All 61 strings are translated, speaker prefixes are consistent (`แลมเบิร์ต - …`), numbers/dates/codes match English, and the long briefing plus the legal disclaimer read cleanly. Remaining issues are register/collocation level (a rude pronoun for Colonel Kim, `มัน` for rooms, `เก็บกู้` for data), with no mistranslation that changes mission meaning.

| sev | type | section::key | EN | TH | problem + suggested Thai fix |
|---|---|---|---|---|---|
| Medium | TERM | Objectives::Objective_0024 / Objective_0025 | `Recover the encrypted data sent by Jin Soo` | `เก็บกู้ข้อมูลที่เข้ารหัสซึ่งจิน ซูส่งมา` | `เก็บกู้` = salvage of wreckage; for data use `กู้คืนข้อมูล`. |
| Medium | TONE/REGISTER | BloodMessage::Speech_0001L | `It must be Kim. Stop him at any cost.` | `ต้องเป็นคิมแน่ หยุดมันให้ได้ไม่ว่าด้วยวิธีใด` | `มัน` for Colonel Kim is abusive; Lambert stays formal (`พันเอกคิม`). → `หยุดเขาให้ได้ไม่ว่าด้วยวิธีใด` |
| Low | UNNATURAL | ElevatorMessage::Speech_0001L | `...follow the main corridor and you ll find it.` | `...เดินตามทางเดินหลัก แล้วคุณจะเจอมัน` | `มัน` for a room. → `แล้วคุณจะเจอห้องนั้น` |
| Low | UNNATURAL | Ventilationroomsg::Speech_0001L | `There's a passage but you must go back downstairs to find it.` | `...แต่คุณต้องย้อนลงไปชั้นล่างเพื่อหามัน` | same: `มัน` for a passage. → `เพื่อหาทางนั้น` |
| Low | MISTRANSLATION | NOalarm::Speech_0001L | `They called a general alarm. The mission is over.` | `พวกเขาเปิดสัญญาณเตือนภัยทั่วไป ภารกิจจบแล้ว` | "called" = ประกาศ/แจ้ง, not switched on. → `พวกเขาประกาศสัญญาณเตือนภัยทั่วไป` (same fix at 05 AlarmCheck::Speech_0007L) |
| Low | TONE/REGISTER | Email::EmailJinBody | `...be sure that the bomb blows during tonight's assembly.` | `...ระเบิดทำงานระหว่างการประชุมคืนนี้` | same event is `สมัชชาใหญ่` in Note_0034L/Objective_0033; news-body copy should match. → `ระหว่างการประชุมสมัชชาคืนนี้` |
| Low | UNNATURAL | EleserviceMessage::Speech_0001L | `Be invisible and silent like only a Splinter Cell can.` | `จงเป็นผู้ที่มองไม่เห็นและเงียบกริบอย่างที่สปลินเตอร์เซลทำได้เท่านั้น` | `อย่างที่…ทำได้เท่านั้น` is tangled. → `จงล่องหนและเงียบกริบอย่างที่สปลินเตอร์เซลทำได้` |

Verified clean (no defect): `EmailJinDate`/`EmailNewsDate` = `31/10/2005` (date format, correctly identical); all alarm timers (`5`, `10`, `20`, `60`); door codes `2346`/`2109`/`350` family; `Briefing_LAMBERT` legal disclaimer; `MapName`; full interpolations — no placeholder or brace mismatch in either file.

## 3 highest-impact fixes

1. **Localize the 14 leaked English speaker tags** in `P_05_Displace01_LobbyGFConvo` / `LobbyMezzConvo` (`-DisExc_Julian-`, `-NYCCiv_Tom-`) to `ผู้บริหารดิสเพลสจูเลียน -` / `สมาชิกสภาเทศบาลทอม -` — the only raw-English visible in Thai subtitles, and the only block that breaks the file's own `ฟิชเชอร์ -` convention.
2. **Fix the two garbled/idiom lines**: `เข้าออกตัวเมืองไปแล้ว` → `เขาออกจากเมืองไปแล้ว` (RDEvents::Speech_0021L, SRC::Speech_0005L) and `พาฉันทอมมาหาคุณ` → `พาทอมมาหาคุณ` (OfficeOpsConvo::Speech_0007L) — both are unreadable to a Thai player.
3. **Correct the voice-track mistranslations that contradict what is spoken**: `ฉันจะจัดเรียงแกเอง` → `ฉันจะจัดการแกเอง` (SecurityEvents::Speech_0022L), `ฉันจะตัดไฟ` → `ฉันจะยุติภารกิจ` (NoKill::Speech_0001L), and `ยิงได้ไกล 40 เมตร` → `ยิงได้ 40 มม.` (InterroRDLounge::Speech_0010L, confirmed by FR/DE).
