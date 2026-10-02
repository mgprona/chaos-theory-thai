# Thai Localization QA — rev-02 (story files 02)

Reviewer: Thai localization QA (script-driven sampling: all `en` > 180 chars, all `Objective_*`/`Email*`/`Briefing_*` keys, then every 3rd remaining line → 190/450 strings for `02_CargoShip.json` and 74/140 for `02_Seoulthree.json`; 264 strings reviewed, plus a full-file compact sweep of the remaining 326 strings). No files under `data/`, `src/`, or `tools/` were modified. Scratch: `out/translation-review/scratch/`.

## Verdicts

**data/translations/story/02_CargoShip.json — 7/10.**
Meaning is faithfully carried across all 450 strings, the locked glossary is respected everywhere (`ฟิชเชอร์`, `แลมเบิร์ต`, `กริมส์ดอตเตียร์`, `ฮูโก ลาแซร์ดา`, `มาเรีย นาร์ซิสซา`, `เธิร์ดเอเชลอน`, `NKA`, `I-SDF`, `OPSAT`), and no string is left in English. The residual problems are register/word-choice issues — one wrong-word mistranslation ("พอสิ" for "Yeah"), a handful of calques (`ธนาคารนอกอาณาเขต`, `สัมภาระ` for "shipment", `เก็บกู้` for documents) and small grammar slips — none of which blocks comprehension.

**data/translations/story/02_Seoulthree.json — 6/10.**
The narrative and comms lines read well, but the sabotage verb is mistranslated as "ทำลาย" (destroy) in the player-facing objectives and in Lambert's confirmation line, collapsing an intentional gameplay distinction; the "cyber café" calque `ร้านอินเทอร์เน็ตคาเฟ่` is repeated in eight objectives, and a few calques (`จุดแทรกซึม`, `สัญญาณเรียก`) plus one name transliteration drift (`เซญอร์` vs `ซินญอร์`) remain.

## 02_CargoShip.json

| sev | type | section::key | EN (<=90) | TH (<=90) | problem + suggested Thai fix |
|---|---|---|---|---|---|
| Med | MISTRANSLATION | P_02_CargoShip_TeleportSoldiers::Speech_0006L | PrGeu_D - Yeah... but I'm not sure that I even trust the life rafts... | กองโจร D - พอสิ... แต่ฉันไม่แน่ใจว่าจะไว้ใจแพชูชีพ... | "พอสิ" = "enough/stop it", not agreement (fr "Oui", de "Ja", it "Sì"). → "เออ... แต่ฉันไม่แน่ใจว่า..." |
| Med | TERM | P_02_CargoShip_LambertComms::Speech_0031L | ...search them for the bill of lading attached to Lacerda's shipment. | ...ค้นหาใบตราส่งสินค้าที่ติดอยู่กับสัมภาระของลาแซร์ดา... | "shipment" = สัมภาระ (personal luggage); wrong term. → "...ที่ติดอยู่กับสินค้าที่จัดส่งให้ลาแซร์ดา" |
| Med | UNNATURAL | Email::EmailLacerdaBody | Please keep your smelly hooligans out of my way. | ช่วยกันไอ้พวกอันธพาลตัวเหม็นของพวกคุณไปให้พ้นทางผมด้วย | "ช่วยกัน" + object is ungrammatical (reads "help each other"). → "ช่วยเอาไอ้พวกอันธพาลตัวเหม็นของพวกคุณไปให้พ้นทางผมด้วย" |
| Med | MISTRANSLATION | P_02_CargoShip_LambertComms::Speech_0041L | ...judging by the numbering on the crates, that's about half of them. | ...ดูจากหมายเลขบนลัง นั่นน่าจะผ่านมาครึ่งหนึ่งแล้ว | "ผ่านมาครึ่งหนึ่ง" reads as "half went past"; wrong sense of "half of them". → "นั่นก็ประมาณครึ่งหนึ่งของทั้งหมดแล้ว" |
| Med | TERM | P_02_CargoShip_LambertComms::Speech_0061L | FISHER - Off shore bankers? | ฟิชเชอร์ - พวกนายธนาคารนอกอาณาเขตเหรอ? | "นอกอาณาเขต" = extraterritorial; offshore bank ≠ this. Same error at Speech_0076L/Speech_0106L. → "ธนาคารนอกชายฝั่ง" |
| Med | GRAMMAR/TYPO | P_02_CargoShip_InteroQuartCrowSold::Speech_0003L | FISHER - So you're an officer? | ฟิชเชอร์ - งั้นนายก็เป็นนายทหารงั้นสิ? | duplicated "งั้น" is ungrammatical. → "งั้นนายก็เป็นนายทหารสินะ?" |
| Med | MEANING LOSS | P_02_CargoShip_InterogCoffeeSoldier::Speech_0001L | FISHER - Tell me something useful, or I'll have to hurt you. | ฟิชเชอร์ - บอกอะไรที่เป็นประโยชน์มา ไม่งั้นฉันคงต้องสั่งสอนนายหน่อยแล้ว | "hurt you" → "สั่งสอน" removes the physical threat. → "ไม่งั้นฉันคงต้องทำให้นายเจ็บตัวแน่" |
| Low | LEFT-ENGLISH | GENERAL::Briefing_LAMBERT | ...make sure he doesn't have an opportunity to spread what he knows. Fifth Freedom. | ...จัดการให้แน่ใจว่าเขาจะไม่มีโอกาสเผยแพร่สิ่งที่เขารู้ สิทธิเสรีภาพขั้นที่ 5 (Fifth Freedom) | redundant English gloss inside a subtitle; glossary term already locked. Duplicated at LambertComms::Speech_0114L. → drop "(Fifth Freedom)" |
| Low | MEANING GAIN | Email::EmailInfoBody | The body of American Bruce Morgenholt was recovered in Peru today. | มีการกู้ร่างของ บรูซ มอร์เกนโฮลต์ วิศวกรชาวอเมริกันในเปรูวันนี้ | adds "วิศวกร" (not in source) and a stray space. → "...ร่างของบรูซ มอร์เกนโฮลต์ ชาวอเมริกันในเปรูวันนี้" |
| Low | TONE/REGISTER | P_02_CargoShip_InterogMShopSailor::Speech_0001L | FISHER - Boo. | ฟิชเชอร์ - จ๊ะเอ๋ | "จ๊ะเอ๋" is playful peekaboo; the beat is a startle. → "ตุ๊!" or "โห!" |
| Low | TERM | P_02_CargoShip_Objectives::Objective_0001 | Retrieve the bill of lading for Lacerda's arms shipment. | เก็บกู้ใบตราส่งสินค้าสำหรับการขนส่งอาวุธของลาแซร์ดา | "เก็บกู้" = salvage (wrecks/bodies/UXO); odd for a document. Same at POPUPMESSAGE_0101/0103/0061, Speech_0079L. → "เก็บ/นำใบตราส่งสินค้ามา" |
| Low | TERM | P_02_CargoShip_Objectives::Note_0055L | Sliding doors roll in wheeled tracks. The Optic Cable can't be used. | ...จึงไม่สามารถใช้กล้องสายเคเบิลสอดใต้ประตูได้ | gadget name must match HUD (`hud.json` Interaction::DoorOptic = "กล้องสายเคเบิล"); the added gloss breaks term consistency. → "...จึงใช้กล้องสายเคเบิลไม่ได้" |
| Low | TERM | P_02_CargoShip_Objectives::Note_0038L | There is a gas leak in the engine room. | มีแก๊สรั่วในห้องเครื่องยนต์ | same location is "ห้องเครื่อง" in the comms (Speech_0006L/0017L/0105L); unify the term. Also Note_0039L, Email::EmailEngineRoomSubject. → "ห้องเครื่อง" |
| Low | UNNATURAL | P_02_CargoShip_InterogLacerda::Speech_0019L | FISHER - Shh... let's not make a scene. | ฟิชเชอร์ - ชู่ว... อย่าทำเรื่องให้เอิกเกริกไปหน่อยเลย | "ไปหน่อยเลย" is misplaced word order. → "อย่าทำเรื่องให้เอิกเกริกเลย" |
| Low | MEANING LOSS | P_02_CargoShip_LambertComms::Speech_0047L | That's their alarm system Fisher... I'm warning you... be careful | ...ฟิชเชอร์... ผมเตือนคุณแล้ว... ระวังตัวด้วย | "แล้ว" turns "I'm warning you" into a past event ("I warned you"). → "ผมเตือนคุณนะ" |
| Low | MEANING GAIN | P_02_CargoShip_InterogEngineFenceS::Speech_0008L | Iago - Uh...the men bunk up portside... | อิอาโก - เอ่อ... พวกคนงานพักอยู่ฝั่งกราบซ้าย... | "the men" → "พวกคนงาน" (the workers) adds a detail not in source. → "พวกมันพักอยู่ฝั่งกราบซ้าย" |
| Low | GRAMMAR/TYPO | P_02_CargoShip_LambertComms::Speech_0053L | ...If you set off too many alarms, they'll know you're there... | ...ถ้าคุณทำสัญญาณดังบ่อยเกินไป พวกมันจะรู้ว่าคุณอยู่ที่นั่น... | missing causative "ให้". Same pattern at Objectives::Note_0053L ("การทำสัญญาณเตือนภัยดัง"). → "ถ้าคุณทำให้สัญญาณดังบ่อยเกินไป" / "การทำให้สัญญาณเตือนภัยดัง" |

## 02_Seoulthree.json

| sev | type | section::key | EN (<=90) | TH (<=90) | problem + suggested Thai fix |
|---|---|---|---|---|---|
| High | MISTRANSLATION | P_02_Seoulthree_goals_activ::Objective_0010 | Sabotage Jong's escape boat. | ทำลายเรือหลบหนีของจง | "sabotage" is rendered as "ทำลาย" (destroy), the same verb used for Objective_0006 "Destroy the Chun-Ma…"; the player is only asked to disable the boat, which still exists afterwards. → "ทำให้เรือหลบหนีของจงใช้การไม่ได้" |
| Med | MISTRANSLATION | P_02_Seoulthree_goals_activ::Objective_0022 | Sabotage the engine on Jong's boat | ทำลายเครื่องยนต์บนเรือของจง | same sabotage/destroy collapse; fr "Sabotez", de "Sabotieren". → "ทำให้เครื่องยนต์บนเรือของจงใช้การไม่ได้" |
| Med | MEANING LOSS | P_02_Seoulthree_Lambertcomms::Speech_0036L | ...Good thing you disabled it. Go grab him from the docks... | ...ดีที่คุณทำลายมันไว้แล้ว ไปจับเขาที่ท่าเรือ... | line states the boat was destroyed, contradicting "Jong is trying to get to his boat"; fr/de/es/it all say disabled/out of use. → "ดีที่คุณทำให้มันใช้การไม่ได้" |
| Med | UNNATURAL | P_02_Seoulthree_goals_activ::Objective_0008 | Get to the cyber café where Jong is being protected. | ไปให้ถึงร้านอินเทอร์เน็ตคาเฟ่ที่จงถูกคุ้มกันอยู่ | calque compound "อินเทอร์เน็ตคาเฟ่"; repeated in Objective_0018/0045/0057/0058/POPUPMESSAGE_0045/Speech_0024L/Speech_0032L. → "ร้านอินเทอร์เน็ต" or "ร้านไซเบอร์คาเฟ่" |
| Low | UNNATURAL | P_02_Seoulthree_cybercafe_conv::Speech_0003L | NKSol_Jin- How long are we supposed to baby sit him for? | พลทหารจิน - เราต้องคอยเฝ้าเลี้ยงดูเขาไปอีกนานแค่ไหน? | "เลี้ยงดู" = raise/nurture a child. → "เราต้องคอยเฝ้าดูแลเขาไปอีกนานแค่ไหน?" |
| Low | TERM | P_02_Seoulthree_goals_activ::Objective_0013 | ...not far from the insertion point. Jong must be captured alive. | ...ไม่ไกลจากจุดแทรกซึม ต้องจับตัวจงให้ได้ทั้งเป็น | literal calque of "insertion point"; reads as an infiltration point. → "ไม่ไกลจากจุดส่งตัว/จุดเริ่มปฏิบัติการ" |
| Low | NAME | GENERAL::Briefing_LAMBERT | ...Jong has been bribing Senor de Medeiros... | ...จงติดสินบนท่านเซญอร์ เด เมเดรอส... | "Senor" transliterated เซญอร์ here but ซินญอร์ in 02_CargoShip MemorableM::Speech_0003L; pick one. → "ท่านเซญอร์" consistently |
| Low | TERM | P_02_Seoulthree_Lambertcomms::Speech_0029L | AgentTwo- Must be his call-sign... | สายลับสอง - คงเป็นสัญญาณเรียกของเขา... | "call-sign" term incomplete. → "รหัสเรียกขานของเขา" |
| Low | GRAMMAR/TYPO | P_02_Seoulthree_goals_activ::Note_0039L | Disable the tanks by climbing on one another's shoulders | ปีนไต่บ่าของอีกคนเพื่อขึ้นไปทำให้รถถังใช้การไม่ได้ | "ไต่บ่า" is not idiomatic. → "ปีนขึ้นไปบนบ่าของอีกคนเพื่อ..." |

## Three highest-impact fixes

1. **`02_Seoulthree` sabotage ≠ destroy (High).** Change `Objective_0010`, `Objective_0022` and Lambert's confirmation (`Lambertcomms::Speech_0036L`) from "ทำลาย" to "ทำให้…ใช้การไม่ได้" so the objective matches what the player actually does (the translator already uses this phrasing in `goals_activ::Note_0039L`/`templefront_interro::Speech_0002L`).
2. **`02_CargoShip::TeleportSoldiers::Speech_0006L` wrong word (Med).** "พอสิ" ("enough!") reverses the speaker's agreement; replace with "เออ…" so the line matches fr/de/es/it.
3. **Cross-file term/name consistency (Med).** Unify `ธนาคารนอกชายฝั่ง` (offshore bank, currently "นอกอาณาเขต"), `ห้องเครื่อง` (engine room, currently also "ห้องเครื่องยนต์"), and the `เซญอร์`/`ซินญอร์` transliteration of "Senor" so HUD/objective/comms text reads as one glossary.
