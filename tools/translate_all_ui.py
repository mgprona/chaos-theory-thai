"""Comprehensive Thai translation injector for all remaining UI strings in pregame_pc.json and pregame_menus.json."""

from __future__ import annotations
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dictionary mapping English text to Thai translation across UI
ENG_TO_TH = {
    # General UI / Buttons
    "BACK": "ย้อนกลับ",
    "EXIT": "ออกจากเกม",
    "QUIT": "ออกจากเกม",
    "QUIT GAME": "ออกจากเกม",
    "ARE YOU SURE YOU WANT TO EXIT ?": "คุณแน่ใจหรือไม่ว่าต้องการออกจากเกม?",
    "DEFAULT": "ค่าเริ่มต้น",
    "RESOLUTION": "ความละเอียด",
    "FULLSCREEN": "เต็มหน้าจอ",
    "REFRESH RATE": "อัตรารีเฟรช",
    "LOW": "ต่ำ",
    "MEDIUM": "ปานกลาง",
    "HIGH": "สูง",
    "VERY HIGH": "สูงมาก",
    "NONE": "ไม่มี",
    "ENABLED": "เปิดใช้งาน",
    "DISABLED": "ปิดใช้งาน",
    "OFF": "ปิด",
    "ON": "เปิด",
    "YES": "ใช่",
    "NO": "ไม่",
    "CANCEL": "ยกเลิก",
    "OK": "ตกลง",
    "ACCEPT": "ยืนยัน",
    "CONTINUE": "เล่นต่อ",
    "RESUME": "เล่นต่อ",
    "PAUSE": "หยุดชั่วคราว",
    "RESTART": "เริ่มใหม่",
    "RELOAD": "รีโหลด",
    "SELECT": "เลือก",
    "DELETE": "ลบ",
    "CREATE": "สร้าง",
    "RENAME": "เปลี่ยนชื่อ",
    "MODIFY": "แก้ไข",
    "SAVE": "บันทึก",
    "LOAD": "โหลด",
    "REFRESH": "รีเฟรช",
    "APPLY": "นำไปใช้",
    "CLOSE": "ปิด",
    "DONE": "เสร็จสิ้น",
    "HELP": "ช่วยเหลือ",
    "CURRENT PROFILE": "โปรไฟล์ปัจจุบัน",
    "LEVEL": "ด่าน",
    "NAME": "ชื่อ",
    "DATE / TIME": "วัน / เวลา",
    "TIME": "เวลา",
    "STATUS": "สถานะ",
    "RATING": "คะแนนประเมิน",
    "TIME PLAYED": "เวลาที่เล่น",
    "DIFFICULTY": "ระดับความยาก",
    "MISSION": "ภารกิจ",
    "MISSIONS": "ภารกิจ",
    "SAVES": "เซฟเกม",
    "SETTINGS": "การตั้งค่า",
    "OPTIONS": "ตัวเลือก",
    "CONTROLS": "การควบคุม",
    "DISPLAY": "การแสดงผล",
    "SOUND": "ระบบเสียง",
    "SOUNDS": "ระบบเสียง",
    "AUDIO": "ระบบเสียง",
    "VIDEO": "การแสดงผล",
    "ONLINE": "ออนไลน์",
    "GENERAL": "ทั่วไป",
    "SOLO": "เล่นคนเดียว",
    "COOP": "ร่วมมือกัน",
    "VERSUS": "ประจันหน้า",
    "LAN": "LAN",
    "SPLIT SCREEN": "แบ่งหน้าจอ",
    "NORMAL": "ปกติ",
    "HARD": "ยาก",
    "EXPERT": "ผู้เชี่ยวชาญ",
    "UNKNOWN": "ไม่ระบุ",
    "HOST": "เจ้าของห้อง",
    "CLIENT": "ผู้เข้าร่วม",
    "READY": "พร้อม",
    "LAUNCH": "เริ่มเกม",
    "START": "เริ่ม",
    "WAITING...": "กำลังรอ...",
    "LOADING...": "กำลังโหลด...",
    "SEARCHING...": "กำลังค้นหา...",
    "PRESS ANY KEY TO CONTINUE": "กดปุ่มใดๆ เพื่อเล่นต่อ",
    "PRESS SPACE TO CONTINUE": "กด SPACE เพื่อเล่นต่อ",

    # Pause & Confirmation
    "RESTART MISSION": "เริ่มภารกิจใหม่",
    "QUIT TO LOBBY": "กลับสู่ล็อบบี้",
    "DO YOU WANT TO RETURN TO THE MAIN MENU? YOUR CURRENT PROGRESS WILL BE LOST.": "คุณต้องการกลับสู่เมนูหลักหรือไม่? ความคืบหน้าปัจจุบันจะสูญหาย",
    "DO YOU WANT TO RETURN TO THE LOBBY ? YOUR CURRENT PROGRESS WILL BE LOST.": "คุณต้องการกลับสู่ล็อบบี้หรือไม่? ความคืบหน้าปัจจุบันจะสูญหาย",
    "DO YOU WANT TO RESTART THE CURRENT MISSION ? YOUR PROGRESS WILL BE LOST.": "คุณต้องการเริ่มภารกิจปัจจุบันใหม่หรือไม่? ความคืบหน้าของคุณจะสูญหาย",
    "PRESS READY BEFORE RETURNING TO THE GAME": "กดพร้อมก่อนกลับเข้าสู่เกม",
    "SORRY, NO SAVEGAME NAME ENTERED.": "ขออภัย ยังไม่ได้ป้อนชื่อเซฟเกม",
    "WARNING: YOU ARE ABOUT TO OVERWRITE A PREVIOUS SAVEGAME. DO YOU WANT TO CONTINUE ?": "คำเตือน: คุณกำลังจะบันทึกทับเซฟเกมเดิม คุณต้องการดำเนินการต่อหรือไม่?",
    "YOU CANNOT DELETE YOUR ONLY PROFILE": "คุณไม่สามารถลบโปรไฟล์เดียวที่มีอยู่ได้",
    "YOU CANNOT DELETE THE DEFAULT PROFILE": "คุณไม่สามารถลบโปรไฟล์เริ่มต้นได้",
    "FAILED TO DELETE THE PROFILE": "ลบโปรไฟล์ไม่สำเร็จ",
    "ARE YOU SURE YOU WANT TO DELETE YOUR PROFILE AND ALL ITS PROGRESS ?": "คุณแน่ใจหรือไม่ว่าต้องการลบโปรไฟล์และความคืบหน้าทั้งหมด?",
    "THIS PROFILE APPEARS TO BE DAMAGED AND CANNOT BE USED. DO YOU WANT TO DELETE IT ?": "โปรไฟล์นี้เสียหายและไม่สามารถใช้งานได้ คุณต้องการลบหรือไม่?",
    "ARE YOU SURE YOU WANT TO DELETE THIS SAVE ?": "คุณแน่ใจหรือไม่ว่าต้องการลบเซฟเกมนี้?",
    "ARE YOU SURE YOU WANT TO LOAD THIS SAVEGAME ? YOUR CURRENT PROGRESS WILL BE LOST.": "คุณแน่ใจหรือไม่ว่าต้องการโหลดเซฟเกมนี้? ความคืบหน้าปัจจุบันจะสูญหาย",
    "ARE YOU SURE YOU WANT TO REPLAY THIS LEVEL IN MISSION MODE ?": "คุณแน่ใจหรือไม่ว่าต้องการเล่นด่านนี้ใหม่ในโหมดภารกิจ?",

    # Audio & Controls Settings
    "INVERT LOOK UP/DOWN": "กลับทิศทางการมอง ขึ้น/ลง",
    "INVERT LOOK LEFT/RIGHT": "กลับทิศทางการมอง ซ้าย/ขวา",
    "VIBRATION": "การสั่นของจอย",
    "AIMING SENSITIVITY": "ความไวในการเล็ง",
    "BRIGHTNESS": "ความสว่าง",
    "CONTRAST": "ความคมชัด",
    "VOICE MASKING": "การแปลงเสียง",
    "VOICE THROUGH SPEAKERS": "เสียงพูดออกลำโพง",
    "VOICE DETECTION": "การตรวจจับเสียง",
    "VOICE DETECTION SENSITIVITY": "ความไวในการตรวจจับเสียง",
    "MUSIC VOLUME": "ระดับเสียงดนตรี",
    "AMBIENT / INTERFACE VOLUME": "ระดับเสียงบรรยากาศ / อินเทอร์เฟซ",
    "SOUND EFFECTS / VOICE VOLUME ": "ระดับเสียงเอฟเฟกต์ / เสียงพูด",
    "SOUND EFFECTS VOLUME": "ระดับเสียงเอฟเฟกต์",
    "VOICE VOLUME": "ระดับเสียงพูด",
    "SHOW COMMUNICATIONS BOX": "แสดงกล่องการสื่อสาร",
    "LANGUAGE": "ภาษา",
    "MODE": "โหมด",
    "MATCH NAME": "ชื่อห้องแข่งขัน",
    "MAXIMUM PLAYERS": "จำนวนผู้เล่นสูงสุด",
    "FRIENDS ONLY": "เฉพาะเพื่อนเท่านั้น",
    "VOICE ONLY": "เฉพาะเสียงพูด",
    "SKILLS RANGE": "ระดับฝีมือ",
    "SPEED": "ความเร็ว",
    "FRIENDLY FIRE": "ยิงพวกเดียวกันเอง",
    "VERSION ORIGINALE": "ภาษาต้นฉบับ",

    # Loadout & Gear
    "LOAD OUT": "เลือกอุปกรณ์",
    "EQUIPED GEAR": "อุปกรณ์ที่ติดตั้ง",
    "EQUIPMENT SELECTION": "เลือกอุปกรณ์",
    "ATTACHMENT SELECTION ": "เลือกอุปกรณ์เสริม",
    "EQUIPMENT INFO": "ข้อมูลอุปกรณ์",
    "[EMPTY]": "[ว่างเปล่า]",
    "[LOCKED]": "[ล็อกอยู่]",
    "REDDING'S RECOMMENDATION": "คำแนะนำของเรดดิง",
    "STEALTH": "สายลอบเร้น",
    "ASSAULT": "สายจู่โจม",

    # Briefing & Characters
    "BRIEFING": "สรุปภารกิจ",
    "COLONEL IRVING LAMBERT": "พันเอก เออร์วิง แลมเบิร์ต",
    "ANNA GRIMSDOTTIR": "แอนนา กริมสดอตตีร์",
    "WILLIAM REDDING": "วิลเลียม เรดดิง",
    "DOUGLAS SHETLAND": "ดักลาส เชตแลนด์",
    "ADMIRAL TOSHIRO OTOMO": "พลเรือเอก โทชิโร โอโตโมะ",
    "CAPTAIN ARTHUR PARTRIDGE": "กัปตัน อาร์เธอร์ พาร์ทริดจ์",
    "SECRETARY FRANK MASSON": "รัฐมนตรี แฟรงก์ แมสสัน",
    'THOMAS "THE TURTLE" STANDISH': 'โธมัส "เดอะ เทอร์เทิล" สแตนดิช',

    # Extras & Menu
    "AMON TOBIN BIOGRAPHY": "ประวัติ AMON TOBIN",
    "MUSIC LIST": "รายการเพลง",
    "OVERALL": "ภาพรวม",
    "STATISTICS": "สถิติ",
    "PLAY": "เล่น",
    "STOP": "หยุด",
    "GAMES LIST": "รายการเกม",
    "FILTER": "ตัวกรอง",
    "MODIFY GAME": "แก้ไขเกม",
    "AGENTS": "สายลับ",
    "INFOS": "ข้อมูล",
    "QUICKMATCH FILTER": "ตัวกรองการจับคู่ด่วน",
    "SELECT LOBBY": "เลือกล็อบบี้",
    "LOBBY NAME": "ชื่อล็อบบี้",
    "FRIENDS MANAGEMENT": "จัดการเพื่อน",
    "IGNORE": "เพิกเฉย",
    "REPLY": "ตอบกลับ",
    "RETURN": "กลับ",
    "CD-KEY": "CD-KEY",
    "PLEASE ENTER YOUR CD-KEY": "โปรดป้อน CD-KEY ของคุณ",
    "ESRB NOTICE": "ประกาศ ESRB",
    "GAME EXPERIENCE MAY CHANGE DURING ONLINE PLAY": "ประสบการณ์การเล่นเกมอาจเปลี่ยนแปลงระหว่างการเล่นออนไลน์",

    # Friends & Messages
    "ENTER FRIEND NAME": "ป้อนชื่อเพื่อน",
    "FRIENDS": "เพื่อน",
    "RECENT PLAYERS": "ผู้เล่นล่าสุด",
    "PLAYER OPTIONS ": "ตัวเลือกผู้เล่น",
    "PLAYER OPTIONS": "ตัวเลือกผู้เล่น",
    "SELECT MISSION": "เลือกภารกิจ",
    "QUICKMATCH": "จับคู่ด่วน",
    "OPTIMATCH": "ค้นหาห้องแข่งขัน",
    "MESSAGES": "ข้อความ",
    "COMPOSE": "เขียนข้อความ",
    "COMPOSE MESSAGE": "เขียนข้อความ",
    "SEND TO": "ส่งถึง",
    "[NO TITLE]": "[ไม่มีหัวข้อ]",
    "[NO TEXT]": "[ไม่มีข้อความ]",
    "[NO RECIPIENT]": "[ไม่มีผู้รับ]",
    "GOING BACK AT THIS TIME WILL DISCARD THE CONTENT OF YOUR CURRENT MESSAGE.": "การย้อนกลับตอนนี้จะละทิ้งเนื้อหาข้อความปัจจุบันของคุณ",
    "SEND": "ส่ง",
    "ADD VOICE MESSAGE": "เพิ่มข้อความเสียง",
    "MESSAGE": "ข้อความ",
    "MESSAGE TITLE": "หัวข้อข้อความ",
    "INBOX": "กล่องข้อความเข้า",
    "YOU HAVE NO MESSAGES": "คุณไม่มีข้อความ",
    "READ MESSAGE": "อ่านข้อความ",
    "SENT BY:": "ส่งโดย:",
    "BLOCK THIS PLAYER": "บล็อกผู้เล่นนี้",
    "FEEDBACK": "ผลตอบรับ",
    "EXPIRATION : ": "หมดอายุ : ",
    "DELETE MESSAGE": "ลบข้อความ",
    "DO YOU WANT TO DELETE THIS MESSAGE?": "คุณต้องการลบข้อความนี้หรือไม่?",
    "AN EMPTY MESSAGE CANNOT BE SENT.": "ไม่สามารถส่งข้อความว่างเปล่าได้",
    "COMPLAINTS": "รายงานปัญหา",
    "OFFENSIVE MESSAGE": "ข้อความไม่เหมาะสม",
    "SPAM": "สแปม",
    "VOICE MESSAGE": "ข้อความเสียง",
    "RECORD": "บันทึกเสียง",

    # Training
    "TRAINING VIDEOS": "วิดีโอฝึกสอน",
    "THE FOLLOWING TUTORIALS WERE CREATED WITH THE DEFAULT KEYBOARD CONFIGURATION.": "บทฝึกสอนต่อไปนี้สร้างขึ้นด้วยการกำหนดค่าคีย์บอร์ดเริ่มต้น",
}


def translate_file(path: Path) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    sections = data.get("sections", {})
    for sec_name, sec_dict in sections.items():
        if sec_name in ["OnlineTermsOfUse", "Interactions"]:
            continue
        for k, v in sec_dict.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict):
                th_current = v.get("th", "").strip()
                if th_current:
                    continue  # already has translation
                en_val = v.get("en", "").strip()
                if en_val in ENG_TO_TH:
                    v["th"] = ENG_TO_TH[en_val]
                    updated += 1
                elif en_val.upper() in ENG_TO_TH:
                    v["th"] = ENG_TO_TH[en_val.upper()]
                    updated += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return updated


def main():
    pc_path = PROJECT_ROOT / "data" / "translations" / "ui" / "pregame_pc.json"
    menus_path = PROJECT_ROOT / "data" / "translations" / "ui" / "pregame_menus.json"

    u1 = translate_file(pc_path)
    u2 = translate_file(menus_path)
    print(f"Updated {u1} additional strings in {pc_path.name}")
    print(f"Updated {u2} additional strings in {menus_path.name}")


if __name__ == "__main__":
    main()
