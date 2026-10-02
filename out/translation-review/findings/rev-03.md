# rev-03 — Thai QA review: `03_Bank.json` + `03_ChemBunker.json`

Reviewer: Thai localization QA (script-driven sample).
Sources: `data/translations/story/03_Bank.json` (514 strings), `data/translations/story/03_ChemBunker.json` (152 strings).
Method: dumped all `(section, key, en, th)` triples in the requested priority order — every `en` > 180 chars, every
`Objective_*` / `Email*` / `Briefing_*` key, every interrogation section/key (`Interro`), then every 3rd remaining
line. **Reviewed 393 strings (300 Bank + 93 ChemBunker)**, well over the 220 minimum; `fr/de/es/it` used as second
opinions on every reported item. No file under `data/`, `src/`, `tools/` was modified. Scratch: `out/translation-review/scratch/`.

## Special checks

- **`P_03_Chemical_Objectives.Objective_0034` blank template — PASS.** `en` = `'   '` (U+0020 ×3, 3 bytes) and
  `th` = `'   '` (identical, 3 bytes); no NBSP/tab drift. It matches `fr/de/es/it` and kept its whitespace.
- **Interrogation register.** ChemBunker's 5 interrogation lines (`InterroGuard`/`InterroTech`) keep the surrender
  cadence and the trailing `...` beats faithfully; Bank's Q→A threat rhythm is largely intact, but Fisher's second-person
  pronoun flips between `นาย` and `คุณ` inside the same mission (row 6), and his opening greeting is mistranslated (row 4).
- **Automated sweeps:** no empty `th`, no placeholder (`%s`/`{}`) mismatches, no forbidden curly quotes/ellipsis in
  either file. Only untranslated token is the source-side `TODO` marker (Bank row 12).

## Verdicts

**`03_Bank.json` — 7/10.** Dialogue and OPSAT objectives read naturally and keep the heist-movie tone; the interrogation
set as a whole is the strongest part of the file. Deductions come from a false-fact mistranslation in a news line, one
visible subtitle typo, and a bank-vs-head-of-state term flip that recurs in four keys.

**`03_ChemBunker.json` — 7.5/10.** Long briefing/email paragraphs are accurate and complete, and the interrogation lines
land well. The main defects are a garbled "because it does" punchline, a protocol term that drifts away from the rest of
the file, and an outlier rendering of "primary extraction point" used nowhere else in the project.

## Findings — `03_Bank.json`

| sev | type | section::key | EN (<=90) | TH (<=90) | problem + suggested Thai fix |
|---|---|---|---|---|---|
| Medium | MISTRANSLATION | P_03_Bank_Communications::Speech_0253L | ...head pitching coach Mathieu Ferland stated that Watanabe was... | ...โค้ชพิชเชอร์คนแรกมาธิเยอ แฟร์ล็องด์ กล่าวว่า... | "head" read as "คนแรก"; fr/de/es/it all say the team's pitching coach. Fix: โค้ชหัวหน้าฝ่ายขว้างมาธิเยอ แฟร์ล็องด์ |
| Medium | TERM | P_03_Bank_Objectives::Objective_0023 | ...authorized from the President's Office, the Main Security Office... | ...จากห้องทำงานประธานาธิบดี ห้องรักษาความปลอดภัยหลัก... | Bank President rendered as head of state; de uses "Direktor", same file uses ประธานธนาคาร at Speech_0257L. Fix: ห้องทำงานประธานธนาคาร |
| Medium | TERM | P_03_Bank_PresOffLaserMic::Note_0024L | The door code to the President's office is 3490. | รหัสประตูห้องทำงานประธานาธิบดีคือ 3490 | Same flip; also Speech_0005L and Speech_0017L in this section. Fix: รหัสประตูห้องทำงานประธานธนาคารคือ 3490 |
| Medium | GRAMMAR/TYPO | P_03_Bank_InterroCamera::Speech_0012L | ...I can hear birds nesting in them... | ...ผมได้ยินเสียนกทำรังอยู่ในนั้น... | Missing ง: เสียนก → เสียงนก (fr/de/es/it all "birds"). Fix: ผมได้ยินเสียงนกทำรังอยู่ในนั้น |
| Medium | MISTRANSLATION | P_03_Bank_InterroBalcony::Speech_0001L | FISHER - Evenin' | ฟิชเชอร์ - ราตรีสวัสดิ์ | ราตรีสวัสดิ์ is a farewell; EN/fr/de/es are a casual evening hello. Fix: ฟิชเชอร์ - สวัสดีตอนค่ำ / มาเย็นเลยนะ |
| Medium | TONE/REGISTER | P_03_Bank_InterroBalcony::Speech_0003L (+5) | FISHER - I'll ask the questions... | ฟิชเชอร์ - ฉันจะเป็นคนถาม... | Fisher alternates นาย (Balcony/Camera/MainDesk) and คุณ (Lobby/Outside/Reception) when interrogating. Fix: standardise on นาย |
| Medium | MISTRANSLATION | P_03_Bank_PresOffLaserMic::Speech_0021L | SOLDIER - Tell me about it... well... anyway... | ทหาร - บอกมาเลย... เอาเถอะ... ยังไง... | Idiom of agreement reversed ("บอกมาเลย" = tell me); fr "Tu parles !", es "Dímelo a mí". Fix: ไม่ต้องบอกก็รู้... |
| Medium | MISTRANSLATION | P_03_Bank_InterroKeypad::Speech_0023L | Paco doesn't give his numbers out to just anyone... | ปาโกไม่ให้เบอร์ใครง่ายๆ หรอก... | "numbers" = the door codes discussed two lines earlier; fr/es say "le code". Fix: ปาโกไม่ให้รหัสใครง่ายๆ หรอก |
| Low | MISTRANSLATION | P_03_Bank_InterroReception::Speech_0001L | That's a neat trick you do with those lasers... | ท่าไม้ตายกับเลเซอร์พวกนั้นเก๋ดีนะ... | ท่าไม้ตาย = finishing move; fr "Joli", es "Bonito truco". Fix: กลเม็ดกับเลเซอร์พวกนั้นเก๋ดีนะ |
| Low | MISTRANSLATION | GENERAL::Briefing_REDDING | ...the bad news is that we have a lot of physical security. | ...ข่าวร้ายคือเรามีระบบรักษาความปลอดภัยทางกายภาพเต็มไปหมด | The bank has the security, not the team. Fix: ข่าวร้ายคือที่นั่นมีระบบรักษาความปลอดภัยทางกายภาพเต็มไปหมด |
| Low | UNNATURAL | P_03_Bank_Objectives::Objective_0053 | Exfiltrate over the outer wall from the front of the Bank where you entered. | ถอนกำลังข้ามกำแพงชั้นนอกทางด้านหน้าธนาคารจุดที่คุณเข้ามา | Run-on, missing จาก. Fix: ถอนกำลังข้ามกำแพงชั้นนอกตรงด้านหน้าธนาคาร จุดที่คุณเข้ามา (also 0042/0044) |
| Low | LEFT-ENGLISH | GENERAL::Briefing | TODO | TODO | Source-side placeholder never replaced (fr "A FAIRE", de "AUFGABE"). Fix: translate or blank it like Objective_0034 |
| Low | MEANING LOSS | P_03_Bank_Communications::Speech_0090L | ...the other do-hickey is a telemetric lock pick. | ...ส่วนอีกอย่างคือตัวสะเดาะกลอนทางไกล | Turtle's slang flattened to a neutral noun. Fix: ...ส่วนไอ้ตัวแปลก ๆ อีกอันคือตัวสะเดาะกลอนทางไกล |
| Low | UNNATURAL | P_03_Bank_SecurityPostB::Speech_0013L | ...I think that vent connects to this side... | ...ฉันว่ามันท่อนั้นเชื่อมมาฝั่งนี้... | Redundant มัน + ท่อนั้น. Fix: ฉันว่าท่อนั้นเชื่อมมาฝั่งนี้ |
| Low | MISTRANSLATION | P_03_Bank_InterroReception::Speech_0002L | ...the grids... they detect some kind of signal... | ...ตาข่ายพวกนั้น... มันตรวจจับสัญญาณบางอย่าง... | Laser grid is not a net; de says "Lasernetz", es "la rejilla". Fix: แนวเลเซอร์พวกนั้น |
| Low | NAME | P_03_Bank_InterroMainDesk::Speech_0006L | SOLDIER - Madre de Dios... | ทหาร - พระแม่มารี... | Spanish oath localized as a name; keep it as an exclamation. Fix: ทหาร - พระเจ้า... |

## Findings — `03_ChemBunker.json`

| sev | type | section::key | EN (<=90) | TH (<=90) | problem + suggested Thai fix |
|---|---|---|---|---|---|
| High | MISTRANSLATION | Email::EmailWarheadBody | Guard this code as though your life depends on it... because it does. | หวงรหัสนี้ไว้ให้เหมือนชีวิตคุณขึ้นอยู่กับมัน... เพราะมันขึ้นอยู่กับมันจริงๆ | "because it does" = your life depends on it; TH makes an object depend on itself. fr "ta vie en dépend". Fix: ...เพราะชีวิตคุณขึ้นอยู่กับมันจริง ๆ |
| Medium | TERM | P_03_Chemical_LocalizationTemp::Note_0009L | Anti-viral protocol Component One = Blood Serum Type O. | โพรโทคอลต้านไวรัส ส่วนประกอบที่หนึ่ง = เซรั่มเลือดกลุ่ม O | Protocol drifts to โพรโทคอล (= network protocol); file otherwise uses สูตรแอนติไวรัส. Fix: สูตรแอนติไวรัส ส่วนประกอบที่หนึ่ง = เซรั่มเลือดกรุ๊ป O |
| Medium | TERM | P_03_Chemical_Objectives::Objective_0021 | Exfiltrate to the primary extraction point | ถอนกำลังไปยังจุดรับตัวหลัก | Outlier: 03_Bank and 10 other story files use จุดถอนกำลังหลัก (26 vs 4). Fix: ถอนกำลังไปยังจุดถอนกำลังหลัก (also 0029, POPUPMESSAGE_0021) |
| Medium | MISTRANSLATION | P_03_Chemical_MissileRoomChat01::Speech_0044L | ...at the expense of five thousand loyal troops. | ...โดยเอาทหารที่จงรักภักดีห้าพันนายเป็นเดิมพัน | "at the expense of" = sacrifice; fr "en sacrifiant", it "tradendo". Fix: โดยสังเวยทหารที่จงรักภักดีห้าพันนาย |
| Low | UNNATURAL | Email::EmailVirusProtocolBody | The correct protocol ingredients are attached to this mail as Notes. | ส่วนผสมที่ถูกต้องของสูตรแนบมากับเมลฉบับนี้ ในส่วนบันทึก | Dangling "ในส่วนบันทึก"; "Notes" is a mail section label. Fix: ...แนบมากับอีเมลฉบับนี้ในหัวข้อ Notes |
| Low | MEANING GAIN | P_03_Chemical_WarehouseChat::Speech_0012L | Really? I heard they were pretty humane. | จริงเหรอ? ฉันได้ยินว่ามันค่อนข้างเมตตาคนนะ | "คน" added although the subject is a weapon (it "benigne"). Fix: จริงเหรอ? ฉันได้ยินว่ามันค่อนข้างเมตตานะ |
| Low | TERM | P_03_Chemical_Objectives::Objective_0025 | Infiltrate the bunker down one of the silos. | แทรกซึมเข้าบังเกอร์ทางปล่องยิงขีปนาวุธ | "silo" and "launch tube" (Objective_0026) collapse to one term. Fix: ...ทางปล่องเก็บขีปนาวุธ (silo) |
| Low | TONE/REGISTER | GENERAL::Briefing_LAMBERT | ...which he smuggled through Panama on their behalf. | ...ซึ่งเขาลักลอบขนผ่านปานามาในนามของพวกมัน | พวกมัน is derogatory for CGIB officers in a formal briefing. Fix: ในนามของพวกเขา |
| Low | UNNATURAL | P_03_Chemical_Objectives::Objective_0018 | A sample of the anti-virus must be manufactured from the protocol... | ต้องผลิตตัวอย่างแอนติไวรัสตามสูตรและเก็บกู้มันออกมาจากห้องแช่แข็ง | Redundant มัน. Fix: ต้องผลิตตัวอย่างแอนติไวรัสตามสูตรและเก็บกู้ออกมาจากห้องแช่แข็ง |

## 3 highest-impact fixes

1. **`03_Bank` — bank `President` is the head of state in Thai.** `Objective_0023`, `PresOffLaserMic::Note_0024L`,
   `Speech_0005L`, `Speech_0017L` all say `ประธานาธิบดี` while `Speech_0257L/0072L` correctly say `ประธานธนาคาร`.
   Unify on `ประธานธนาคาร`; it is the mission-critical vault-authorisation actor.
2. **`03_ChemBunker` — `EmailWarheadBody` garbled punchline.** `เพราะมันขึ้นอยู่กับมันจริงๆ` destroys the threat that
   closes the email. Replace with `เพราะชีวิตคุณขึ้นอยู่กับมันจริง ๆ`.
3. **`03_Bank` — two player-visible defects.** Fix the `เสียนก` → `เสียงนก` typo (`InterroCamera::Speech_0012L`) and
   retranslate `head pitching coach` (`Speech_0253L`) as `โค้ชหัวหน้าฝ่ายขว้าง`, which currently invents a "first coach".
