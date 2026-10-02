# Thai Localization QA — Story Missions rev-01

Targets: `data/translations/story/01_Lighthouse.json` (381 strings) and
`data/translations/story/01_Panama.json` (168 strings).
Source of truth: `en`; fr/de/es/it used as second opinions for ambiguous English.

Method: script-dumped `(section, key, en, th)` triples
(`out/translation-review/scratch/select.py`, read-only), reviewing **all 20** EN>180-char
strings in Lighthouse, **all 28** Objective_*/Email*/Briefing_* keys, every 3rd line of the
remainder (113), **plus a full complement pass over the other 220** strings — i.e. 381/381
Lighthouse strings and 168/168 Panama strings were read. Raw JSON was re-inspected directly
for every flagged pair (`out/translation-review/scratch/xcheck.py`). No file under `data/`,
`src/` or `tools/` was modified.

Structural pre-checks (run, no defects found): 0 empty `th`, 0 `th == en` except the
legitimate `EmailJimboSubject` = "PP", 0 Latin-heavy (LEFT-ENGLISH) strings, 0 leftover
English tokens other than locked/proper nouns (`People's Voice`, `Photobacterium Phosphorium`),
0 dialog-number mismatches.

Severity scale used: **High** = wrong meaning or an inverted/contradicted instruction the
player acts on. **Medium** = consistent register/term error a player would notice, or a
meaning nuance lost/gained on a story beat. **Low** = polish.

---

## 01_Lighthouse.json — verdict 8/10

The Lighthouse script is consistently voiced and reads like natural game Thai: soldier banter, threats and objectives all land, and locked glossary terms (ฟิชเชอร์, แซม, แลมเบิร์ต, กริมส์ดอตเตียร์, มาสส์เคอร์เนล, เธิร์ดเอเชลอน, มาเรีย นาร์ซิสซา, เซอร์เคซี absent) are all correct.
Deductions are for a handful of real defects — one inverted meaning ("Si" → ปลอดภัย, "ไม่ได้" → "ไม่ต้อง"), an out-of-character polite register for Quinton, and inconsistent Thai for recurring terms (butchers / come in / comm logs).

| sev | type | section::key | EN (<=90) | TH (<=90) | problem + suggested Thai fix |
|---|---|---|---|---|---|
| High | MISTRANSLATION | P_01_Lighthouse_CnvNoLacerda::Speech_0002L | IAGO: Si.  They've been gone for a while. | อิอาโก: ปลอดภัย พวกนั้นออกไปได้สักพักใหญ่แล้ว | **"ปลอดภัย" (safe) is wrong for Spanish "Si" (yes).** The identical "Si." is correctly "ใช่" in CnvMorgenholt::Speech_0006L, and fr/de/it all read "yes". Fix: "อิอาโก: ใช่ พวกนั้นออกไปได้สักพักใหญ่แล้ว" |
| High | MISTRANSLATION | P_01_Lighthouse_Communications::Speech_0064L | FISHER - Won't they wonder what happened to it? | ฟิชเชอร์ - พวกมันจะไม่สงสัยเหรอว่าเกิดอะไรขึ้นกับข้อมูลน่ะ? | **Negation reversed: missing "ไม่" before "สงสัย".** Fisher asks whether they *will* suspect; the Thai says they will not. Fix: "พวกมันจะไม่สงสัยหรือว่าเกิดอะไรขึ้นกับข้อมูลน่ะ?" |
| Medium | TONE/REGISTER | P_01_Lighthouse_Communications::Speech_0067L | FISHER - You're not trying to set me up on another blind date I hope... | ฟิชเชอร์ - หวังว่าเธอคงไม่ได้พยายามจะนัดบอดให้ฉันอีกหรอกนะ... | Fisher's next beat about the same woman is "หล่อน", so "เธอ" here reads as addressing Grim politely instead of talking *about* the woman. Fix: "หวังว่าเธอคงไม่ได้จะนัดบอดให้ฉันอีกนะ หมายถึงผู้หญิงคนนั้นน่ะ..." → better: "ฟิชเชอร์ - หวังว่าหล่อนคงไม่ใช่การนัดบอดอีกครั้งที่เธอจัดให้นะ..." |
| Medium | TONE/REGISTER | P_01_Lighthouse_CnvCaveGuards::Speech_0025L | QUINTON: Don't be a fool. | กินตัน: อย่าทำเป็นขี้ขลาดไปหน่อยเลยน่า | Quintons's clipped dismissal becomes a nagging, folksy sentence, and the register clashes with Stefano's formal "ระวังตัวด้วย" two lines later. Fix: "กินตัน: อย่ามาโง่เลยน่า" |
| Medium | TONE/REGISTER | GENERAL::Briefing_LAMBERT | LAMBERT - Fisher, an American engineer named Bruce Morgenholt has been kidnapped... | แลมเบิร์ต - ฟิชเชอร์ วิศวกรชาวอเมริกันชื่อ บรูซ มอร์เกนโฮลต์ ถูกกลุ่มแบ่งแยกดินแดนเปรู... | Lambert's whole briefing uses "คุณ" (and "ผม" in Panama), but in-mission he addresses Fisher as "นาย". A briefing from the same speaker should not switch pronoun class. Fix: use "นาย" (Lighthouse) / "นาย/พวกเธอ" (Panama) consistently for Lambert |
| Medium | TERM | P_01_Lighthouse_Objectives::Objective_0013 / Objective_0014 | Disable the guerilla's communications equipment. | ทำลายอุปกรณ์สื่อสารของพวกกองโจร | "Disable" is rendered "ทำลาย" (destroy), which contradicts "recover or destroy" used elsewhere for a different objective and misstates the mission action. Fix: "ปิดการใช้งานอุปกรณ์สื่อสารของพวกกองโจร" |
| Medium | TERM | P_01_Lighthouse_CnvWeather::Speech_0010L / Speech_0012L | IGNACIO: the Americans are not butchers... | พวกอเมริกันไม่ใช่พวกบ้าเลือดที่เที่ยวฆ่าฟันไม่เลือกหน้า / พวกมันไม่ใช่พวกกระหายเลือด | The same keyword "butchers" is translated two different ways two lines apart, weakening Ignacio's deliberate repetition. Fix: pick one, e.g. "พวกมันไม่ใช่พวกฆ่าคนเป็นผักเป็นปลา" in both |
| Medium | TERM | P_01_Lighthouse_CnvMariaNarcissa::Speech_0001L / Speech_0007L | THOMAS: Evening Star to Maria Narcissa, come in. | โทมัส: อีฟนิงสตาร์ เรียก มาเรีย นาร์ซิสซา ได้ยินแล้วตอบด้วย | Radio procedural "come in" is translated as if it were "come back" ("ได้ยินแล้วตอบด้วย") in Maria Narcissa but as "เชิญพูด" in Comm Speech_0008L — same procedure, two renderings. Fix: standardize on "เรียก มาเรีย นาร์ซิสซา เปลี่ยน" or "ได้ยินไหม ตอบด้วย" for all radio calls |
| Medium | TONE/REGISTER | P_01_Lighthouse_Communications::Speech_0103L / Speech_0128L | LAMBERT - These guerillas have some high-tech gear Sam. | แลมเบิร์ต - พวกกองโจรพวกนี้มีอุปกรณ์ไฮเทคอยู่ด้วยนะ แซม | "พวกกองโจรพวกนี้" doubles the classifier ("พวก...พวกนี้"); natural Thai is "พวกกองโจรนี้". Fix: "กองโจรพวกนี้มีอุปกรณ์ไฮเทคอยู่ด้วยนะ แซม" |
| Low | MEANING LOSS/GAIN | P_01_Lighthouse_CnvWeather::Speech_0012L | but since that night... I have always been afraid of the thunder... | แต่ตั้งแต่คืนนั้นเป็นต้นมา... ฉันก็กลัวเสียงฟ้าร้องมาโดยตลอด... | The self-correction "no... " is dropped, and "but since that night" is rendered "แต่ตั้งแต่คืนนั้น" — acceptable, but the dropped "no..." removes Ignacio's hesitation beat. Optional: "เปล่าหรอก... แต่ตั้งแต่คืนนั้น..." |
| Low | MEANING LOSS/GAIN | P_01_Lighthouse_Communications::Speech_0030L | FISHER - You can spare thirty seconds for some simple dignity. | ฟิชเชอร์ - สละเวลาแค่สามสิบวินาทีเพื่อให้เขาได้มีศักดิ์ศรีบ้างก็ไม่เสียงานหรอก | Added clause "มันคงไม่ทำให้เสียงานหรอก" and "ศักดิ์ศรีความเป็นมนุษย์" over-explain Fisher's terse line. Fix: "ฟิชเชอร์ - แค่สามสิบวินาทีเพื่อให้เขาได้มีศักดิ์ศรีบ้างก็ไม่เสียหายนี่" |
| Low | MEANING LOSS/GAIN | P_01_Lighthouse_Communications::Speech_0041L | LAMBERT - We'll see if we can track him through Echelon... | แลมเบิร์ต - เราจะดูว่าสามารถติดตามร่องรอยมันผ่านระบบเอเชิลอนได้ไหม... | "Echelon" is rendered "ระบบเอเชิลอน" here but "เธิร์ดเอเชลอน" is the locked form for the organization; "ระบบ" also shifts it to a system rather than the agency. Fix: "ติดตามร่องรอยมันผ่านเอเชลอน" |
| Low | TONE/REGISTER | P_01_Lighthouse_Communications::Speech_0069L | FISHER - So was the last girl you set me up with... | ฟิชเชอร์ - ผู้หญิงคนล่าสุดที่เธอนัดบอดให้ฉันก็หุ่นเหมือนเรือเป๊ะเลย... | The boat joke is spelled out ("หุ่นเหมือนเรือเป๊ะ") where the English is elliptical; also "นัดบอด" vs "นัดเดต" in Speech_0074L. Fix: "ผู้หญิงคนล่าสุดที่เธอนัดบอดให้ฉันก็เป็นเรือเหมือนกันนี่นา..." and use "นัดบอด" in both |
| Low | TONE/REGISTER | P_01_Lighthouse_IntCaveGuard::Speech_0007L / Speech_0008L | GUARD: You're the American oppressor...you're the bad guy... | ยาม: แกต่างหากคือผู้กดขี่ชาวอเมริกัน... แกนั่นแหละคือคนเลว... | "ผู้กดขี่ชาวอเมริกัน" parses as "oppressor **of** Americans"; the guard means Fisher *is* the American oppressor. Fix: "แกนั่นแหละคือไอ้พวกอเมริกันผู้กดขี่... แกคือคนเลว..." |
| Low | GRAMMAR/TYPO | P_01_Lighthouse_Communications::Speech_0138L | GRIMSDOTTIR - Their radio and operator are down... | กริมส์ดอตเตียร์ - ทั้งวิทยุและคนส่งสัญญาณเดี้ยงไปหมดแล้ว... | Same entity is "พลวิทยุ" in four other strings and "คนส่งสัญญาณ" here, and "เดี้ยง" is very colloquial for Grim. Fix: "ทั้งวิทยุและพลวิทยุของพวกมันใช้การไม่ได้แล้ว" |
| Low | TONE/REGISTER | P_01_Lighthouse_IntThunder::Speech_0011L / Speech_0012L | HECTOR: I'm coming father... / I'm coming mother... | เฮกตอร์: ลูกกำลังจะไปหาแล้วครับพ่อ... / ลูกกำลังจะไปหาแล้วครับแม่... | Hector uses "ฉัน" for himself everywhere else; switching to 1st-person "ลูก" plus "ครับ" in his dying words changes his voice. Fix: "เฮกตอร์: ฉันกำลังจะไปแล้ว พ่อ..." |

---

## 01_Panama.json — verdict 7.5/10

Panama is a well-localized file: the two trainee-voice radio exchanges, the locker-room guard gossip and the soccer commentary all read naturally and keep the source's casual register.
It loses points for a speaker-identity slip on the VP (missing "Señor" title in a name/NPC-address string), a Lambert pronoun/particle inconsistency against the Lighthouse file, and two mistranslations that bend intent ("You'll have to kill me" → "must", and "cut down" → "ลดลง").

| sev | type | section::key | EN (<=90) | TH (<=90) | problem + suggested Thai fix |
|---|---|---|---|---|---|
| Medium | NAME | P_01_Panama_SecurityRoom01::Speech_0002L | So what do you think is going on with Senor de Medeiros these days? | แล้วนายคิดว่าคุณเด เมเดรอส ช่วงนี้เป็นอะไรไป? | **"Senor" is dropped and "คุณ" is inserted**, so the guard addresses the VP as if talking to him, and the honorific is lost. Everywhere else the file uses "ท่านเซญอร์ เด เมเดรอส". Fix: "แล้วนายคิดว่าท่านเซญอร์ เด เมเดรอส ช่วงนี้เป็นอะไรไป?" |
| Medium | UNNATURAL | P_01_Panama_LockerRoom::Speech_0004L | Good to know. Where is he? | ดีที่บอก ท่านอยู่ไหน? | "Good to know" becomes an unidiomatic "ดีที่บอก". Fix: "ดีนะที่บอก / รู้ไว้ก็ดี" |
| Medium | MISTRANSLATION | P_01_Panama_VPOffice::Speech_0002L | I swear, that's all I know. You'll have to kill me. | ฉันสาบาน นั่นคือทั้งหมดที่ฉันรู้ คุณต้องฆ่าฉันแล้วล่ะ | "You'll have to kill me" is despair ("คงต้องฆ่าฉันแล้วสินะ"), not an instruction ("คุณต้องฆ่าฉัน"). Fix: "ฉันสาบาน นั่นคือทั้งหมดที่ฉันรู้... งั้นคงต้องฆ่าฉันแล้วล่ะ" |
| Medium | MISTRANSLATION | P_01_Panama_TheVP::Speech_0011L | God I need a drink... but the doctor says I have to cut down. | พระเจ้า ฉันอยากดื่มสักแก้ว... แต่หมอบอกว่าฉันต้องลดลง | "ต้องลดลง" needs its object; in Thai this is simply "ต้องดื่มน้อยลง". Fix: "แต่หมอบอกว่าฉันต้องดื่มให้น้อยลง" |
| Medium | TONE/REGISTER | P_01_Panama_Communications::Speech_0024L | Listen up. To make the grade as an official (unofficial) Splinter Cell... | ฟังให้ดี การจะได้เป็นสปลินเตอร์เซลเต็มตัว (ซึ่งก็ไม่เป็น… | Lambert mixes "คุณ" with the Lighthouse file's "นาย", and "สปลินเตอร์เซล" diverges from the series' locked "สปลินเตอร์เซลล์". Fix: "การจะได้เป็นสปลินเตอร์เซลล์เต็มตัว... นายต้องเก็บตัวให้เงียบ" |
| Medium | TERM | P_01_Panama_Communications::Speech_0015L | Neither one of you will ever qualify as full-fledged Splinter Cells. | พวกคุณทั้งคู่ไม่มีวันได้เป็นสปลินเตอร์เซลเต็มตัวอย่างแน่นอน | Same term as above; also "สปลินเตอร์เซลล์" should match the UI glossary. Fix: "สปลินเตอร์เซลล์เต็มตัว" |
| Medium | TONE/REGISTER | P_01_Panama_Communications::Speech_0024L / Speech_0015L | ...you're going to need to hack through those scanners. | ...คุณจะต้องแฮกเครื่องสแกนพวกนั้นแทน | Lambert switches between "คุณ" (radio briefings) and "นาย" (Speech_0015L, Speech_0030L) when addressing the same two trainees in the same mission. Fix: standardize on "พวกนาย/เธอ" for the trainees throughout |
| Medium | MEANING LOSS/GAIN | P_01_Panama_Communications::Speech_0022L | ...in other news, Director Liu of the Chinese National Space Administration... | ...ในข่าวอื่น ผู้อำนวยการหลิวแห่งองค์การอวกาศแห่งชาติจีน (CNSA)... | Wrong news idiom: "ในข่าวอื่น" means "in other [pieces of] news"; the anchor formula is "ต่อไปเป็นข่าว..." Fix: "ต่อไปเป็นข่าวต่างประเทศ..." |
| Medium | MEANING LOSS/GAIN | P_01_Panama_Communications::Speech_0023L | MCAS Banco de Panama filed an insurance claim today against the theft of... | ธนาคาร MCAS บังโกเดปานามา ยื่นเคลมประกันวันนี้ กรณีพันธบัตรรัฐบาล... | The theft happened *last night*; "เมื่อคืนที่ผ่านมา" is buried after the bond phrase, so the timeline reads as "today". Fix: "หลังพันธบัตร... ถูกโจรกรรมไปจากตู้เซฟเมื่อคืน" |
| Medium | MISTRANSLATION | P_01_Panama_TheVP::Speech_0004L | Oh, god! I knew you were coming! | โอ้ พระเจ้า! ฉันรู้ว่าคุณต้องมา! | Same "must" error as above, minor. Fix: "ฉันรู้ว่าคุณจะต้องมา!" |
| Low | MEANING LOSS/GAIN | P_01_Panama_Communications::Speech_0024L / Speech_0021L | Welcome to the big leagues. I know you're both still in training... | ยินดีต้อนรับสู่ลีกใหญ่ ผมรู้ว่าคุณทั้งคู่ยังฝึกอยู่... | "สล็อตใหญ่" would be ambiguous; "ลีกใหญ่" is fine, but the sentence is left unpunctuated after "มีเรื่องด่วนเข้ามา" (no comma). Optional polish |
| Low | UNNATURAL | P_01_Panama_Outside::Speech_0010L | I like everything gets a kind of reflective sheen. | ฉันชอบที่ทุกอย่างดูมีความเงาสะท้อนแบบนั้น | "มีความเงาสะท้อน" is redundant (เงา + สะท้อน). Fix: "ฉันชอบที่ทุกอย่างดูเป็นเงาวับแบบนั้น" |
| Low | TONE/REGISTER | P_01_Panama_ThirdFloorSecurity::Speech_0006L | Think we should report it? | เราควรจะรายงานไหม? | "เราควรจะ" is stiff for two bored night guards; "ว่าไง ควรรายงานไหม" fits better |
| Low | GRAMMAR/TYPO | P_01_Panama_SoccerGame::Speech_0011L / 01_Lighthouse_SRCSoccerPlayer::Speech_0012L | I'm going to kill myself. | ฉันอยากจะฆ่าตัวตายจริงๆ ให้ตายเถอะ | The 2007-era game reads this as a hyperbolic groan; "อยากจะ" makes it literal suicidal intent. Fix: "ให้ตายเถอะ ฉันจะบ้าตายอยู่แล้ว" |
| Low | SUBTITLE-LENGTH | P_01_Panama_LockerRoom::Speech_0011L | Ah... the VP went and installed a bunch of them... meeting room next to... | อ่า... รองประธานไปติดมันมาชุดใหญ่... ห้องประชุมข้างห้องทำงานท่าน... | Thai runs ~15% longer than EN, and this string has no pause after "ชุดใหญ่"; trim to keep the subtitle on one line: "อ่า... รองประธานติดตั้งมันชุดใหญ่..." |

---

## Top 3 highest-impact fixes

1. **`01_Lighthouse` CnvNoLacerda::Speech_0002L — "Si." → "ปลอดภัย".** A Spanish "yes" is translated as "safe", so Iago appears to confirm safety instead of agreeing that Lacerda's group left. It contradicts the identical line in CnvMorgenholt::Speech_0006L ("ใช่") and all four second-opinion languages. Fix to "ใช่".
2. **`01_Lighthouse` Communications::Speech_0064L — dropped "ไม่".** "Won't they wonder what happened to it?" is rendered as a bare statement ("พวกมันจะไม่สงสัยเหรอว่า..." missing the negative), inverting Fisher's question at a story beat about covering up the data wipe.
3. **Speaker-pronoun consistency across both files (Lambert: นาย vs คุณ vs ผม).** Lambert addresses Fisher as "นาย" in-mission, uses "ผม" in Panama briefings and "คุณ" in Panama radio lines, and Fisher addresses Grim as "เธอ" while her line two beats later treats the same woman as "หล่อน". This is the most visible systemic issue for a player and is cheap to fix by fixing one pronoun set per speaker pairing (Lambert→Fisher "นาย", Lambert→trainees "พวกนาย", Grim→Fisher "นาย", and in Fisher's blind-date joke keep the woman as "หล่อน" once introduced).
