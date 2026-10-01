"""Expand and complete UI translations for pregame_pc.json and pregame_menus.json."""

from __future__ import annotations
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ADDITIONAL_PC_TRANSLATIONS = {
    "Keys": {
        "K_Duck": "หมอบ / ลุกขึ้น",
        "K_DuckJoystick": "หมอบ / ลุกขึ้น / ออกจากการปฏิสัมพันธ์",
        "K_Accel": "ซูมเข้า / เร่งความเร็ว",
        "K_Decell": "ซูมออก / ลดความเร็ว",
        "k_BackToWall": "พิงกำแพง / สลับมือ",
        "K_SwitchHandZoom": "พิงกำแพง / สลับมือ / ซูมเข้า-ออก",
        "K_Fire": "ยิง",
        "K_AltFire": "ยิงโหมดพิเศษ",
        "K_Scope": "ใช้งาน / สวมใส่อุปกรณ์",
        "K_Interaction": "ปฏิสัมพันธ์",
        "K_SwitchROF": "ปรับอัตราการยิง",
        "K_ResetCamera": "รีเซ็ตมุมกล้อง",
        "K_SwitchAttach": "สลับอุปกรณ์เสริม",
        "K_InteractionReload": "ปฏิสัมพันธ์ / เติมกระสุน",
        "K_CoopWhistle": "ผิวปาก / ปฏิบัติการร่วม",
        "Title_Visions": "โหมดการมองเห็น",
        "K_Opsat": "Opsat",
        "K_ZoomToggle": "กล้อง EEV / ซูม / สไนเปอร์",
        "K_HeatVision": "กล้องตรวจจับความร้อน",
        "K_EEVVision": "กล้องตรวจจับคลื่นแม่เหล็กไฟฟ้า",
        "Title_Inventory": "ช่องเก็บของ",
        "K_FullInventory": "ช่องเก็บของทั้งหมด",
        "K_NextGadget": "อาวุธถัดไป",
        "K_PrevGadget": "อาวุธก่อนหน้า",
        "K_QuickInventoryJoystick": "ช่องเก็บของด่วน / สลับอุปกรณ์เสริม",
        "K_ShowChatIngame": "แสดงหน้าต่างแชทในเกม",
        "K_CoopAction": "ปฏิบัติการร่วม",
        "Title_System": "ระบบ",
        "K_PauseMenu": "เมนูหยุดเกม",
        "MENU": "เมนู",
        "CTRLOpsat": "Opsat",
        "CTRLPauseMenu": "เมนูหยุดเกม",
    },
    "Interactions": {
        "IK_None": "ไม่มี",
        "IK_LeftMouse": "คลิกซ้าย",
        "IK_RightMouse": "คลิกขวา",
        "IK_MiddleMouse": "คลิกกลาง",
        "IK_Enter": "Enter",
        "IK_Shift": "Shift",
        "IK_Ctrl": "Ctrl",
        "IK_Alt": "Alt",
        "IK_Space": "Spacebar",
        "IK_Backspace": "Backspace",
        "IK_Tab": "Tab",
        "IK_Escape": "Esc",
        "IK_Up": "ลูกศรขึ้น",
        "IK_Down": "ลูกศรลง",
        "IK_Left": "ลูกศรซ้าย",
        "IK_Right": "ลูกศรขวา",
        "IK_MouseWheelUp": "ลูกกลิ้งเมาส์ขึ้น",
        "IK_MouseWheelDown": "ลูกกลิ้งเมาส์ลง",
    },
}

ADDITIONAL_MENUS_TRANSLATIONS = {
    "OPTIONSTITLE": {
        "SoundEffectsVolume": "ระดับเสียงเอฟเฟกต์ / เสียงพูด",
        "AppearOffline": "แสดงสถานะออฟไลน์",
        "QuickMatchVoice": "ค้นหาด่วนเฉพาะห้องที่มีเสียง",
        "QuickMatchMode": "โหมดค้นหาด่วน",
    },
    "OPTIONSVALUE": {
        "OptionAll": "ทั้งหมด",
        "Language[1]": "อังกฤษ",
        "Language[2]": "ญี่ปุ่น",
        "Language[3]": "เยอรมัน",
        "Language[4]": "ฝรั่งเศส",
        "Language[5]": "สเปน",
        "Language[6]": "อิตาลี",
        "Language[7]": "เกาหลี",
        "Language[8]": "จีน",
        "Language[9]": "โปรตุเกส",
        "Skills[1]": "ต่ำกว่า 500",
        "Skills[2]": "500-700",
        "Skills[3]": "700-1000",
        "Skills[4]": "1000-1500",
        "Skills[5]": "1500-2000",
        "Skills[6]": "2000 ขึ้นไป",
        "Mode[1]": "เนื้อเรื่อง",
        "Mode[3]": "อีลีท",
    },
    "COMMON": {
        "MainTitleOnline": "ออนไลน์",
        "MainTitleLan": "แลน (LAN)",
        "JoiningMsg": "กำลังเข้าร่วมห้องแข่งขัน...",
        "JoiningLobbyMsg": "กำลังเข้าร่วมล็อบบี้... ( %i )",
        "JoinFailedMsg": "ไม่สามารถเข้าร่วมห้องแข่งขันนี้ได้",
        "VerifyString": "กำลังตรวจสอบ %s ของคุณ...",
        "Sending": "กำลังส่งข้อมูล...",
        "Pausing": "กำลังหยุดชั่วคราว...",
        "LaunchingMsg": "กำลังเริ่มเกม...",
        "NetworkInitFail": "ไม่พบการเชื่อมต่อเครือข่าย",
        "Unavailable": "ไม่พร้อมใช้งาน",
        "SessionDisconnectMsg": "คุณถูกตัดการเชื่อมต่อจากเซสชัน",
        "SessionKickMsg": "คุณถูกเตะออกจากเซสชัน",
        "SessionDisconnectingMsg": "กำลังตัดการเชื่อมต่อจากเซสชัน...",
        "QuitDemo": "ออกจากเกม",
    },
    "LOADSAVE": {
        "ErrorSavingTitle": "พื้นที่จัดเก็บไม่เพียงพอ",
        "ErrorSavingMsg": 'พื้นที่จัดเก็บไม่เพียงพอสำหรับบันทึกจุดเช็คพอยต์ เลือก "ตกลง" เพื่อเพิ่มพื้นที่ว่าง %i บล็อก หรือ "ยกเลิก" เพื่อลองลบความคืบหน้าอื่นในรายการของคุณ',
        "LoadSavedGameWrongMode": "ไม่สามารถโหลดไฟล์เซฟนี้จากโหมดเกมอื่นได้",
        "LoadSavedGameWrongRole": "ไม่สามารถโหลดไฟล์เซฟนี้ในฐานะโฮสต์ได้ เนื่องจากคุณเล่นในฐานะลูกข่าย",
        "LoadSavedGameNotFriend": "ไม่สามารถโหลดเซฟได้เนื่องจากผู้เล่นไม่ได้อยู่ในรายชื่อเพื่อนของคุณ",
        "LoadSavedGameInviteFriend": 'ในการโหลดเซฟนี้ คุณต้องเชิญเพื่อนของคุณ เลือก "ตกลง" เพื่อส่งคำเชิญไปยัง %s และเล่นต่อ',
        "SavedMissingSpaceMsg": 'พื้นที่ว่างไม่เพียงพอสำหรับการบันทึก %i จุดเช็คพอยต์ เลือก "ตกลง" เพื่อเพิ่มพื้นที่ว่าง %i บล็อก หรือ "ยกเลิก"',
        "SavedMissingSpaceDontCareMsg": 'หากคุณยังต้องการเล่นต่อ เลือก "ตกลง" เพื่อดำเนินการต่อ หรือ "ยกเลิก"',
        "SaveGameErrorLoadTitle": "ไฟล์เซฟเสียหาย",
        "SaveGameErrorLoadMsg": "ไฟล์เซฟนี้ดูเหมือนจะเสียหายและไม่สามารถโหลดได้",
        "SaveGameErrorSaveTitle": "บันทึกเกม",
        "SaveGameErrorSaveMsg": "ไม่สามารถบันทึกเกมนี้ได้",
        "SaveGameNewFriend": "เพื่อให้สามารถเล่นไฟล์เซฟนี้กับผู้เล่นเดิมได้ คุณต้องเพิ่มเขาในรายชื่อเพื่อน คุณต้องการเพิ่มเขาเป็นเพื่อนหรือไม่?",
        "HostWantSave": "เพื่อนร่วมทีมต้องการบันทึกเกมนี้ถาวร คุณต้องการบันทึกด้วยหรือไม่? ",
        "ClientRefuseSave": "เพื่อนร่วมทีมปฏิเสธการบันทึกเกมถาวร ",
    },
    "PROFILES": {
        "ProfileErrorCreateTitle": "พื้นที่จัดเก็บไม่เพียงพอ",
        "ProfileErrorCreateMsg": 'พื้นที่จัดเก็บไม่เพียงพอสำหรับสร้างโปรไฟล์ใหม่ เลือก "ตกลง" เพื่อเพิ่มพื้นที่ว่าง %i บล็อก หรือ "ยกเลิก"',
    },
}


def apply_additional_translations():
    # 1. Update pregame_pc.json
    pc_path = PROJECT_ROOT / "data" / "translations" / "ui" / "pregame_pc.json"
    with open(pc_path, "r", encoding="utf-8") as f:
        pc_data = json.load(f)

    pc_count = 0
    for sec_name, kv in ADDITIONAL_PC_TRANSLATIONS.items():
        if sec_name in pc_data.get("sections", {}):
            sec = pc_data["sections"][sec_name]
            for k, th_val in kv.items():
                if k in sec and isinstance(sec[k], dict):
                    sec[k]["th"] = th_val
                    pc_count += 1
                elif k not in sec:
                    sec[k] = {"en": k, "th": th_val}
                    pc_count += 1

    with open(pc_path, "w", encoding="utf-8") as f:
        json.dump(pc_data, f, ensure_ascii=False, indent=2)
    print(f"Applied {pc_count} additional translations to {pc_path.name}")

    # 2. Update pregame_menus.json
    menus_path = PROJECT_ROOT / "data" / "translations" / "ui" / "pregame_menus.json"
    with open(menus_path, "r", encoding="utf-8") as f:
        menus_data = json.load(f)

    menus_count = 0
    for sec_name, kv in ADDITIONAL_MENUS_TRANSLATIONS.items():
        if sec_name in menus_data.get("sections", {}):
            sec = menus_data["sections"][sec_name]
            for k, th_val in kv.items():
                if k in sec and isinstance(sec[k], dict):
                    sec[k]["th"] = th_val
                    menus_count += 1
                elif k not in sec:
                    sec[k] = {"en": k, "th": th_val}
                    menus_count += 1

    with open(menus_path, "w", encoding="utf-8") as f:
        json.dump(menus_data, f, ensure_ascii=False, indent=2)
    print(f"Applied {menus_count} additional translations to {menus_path.name}")


if __name__ == "__main__":
    apply_additional_translations()
