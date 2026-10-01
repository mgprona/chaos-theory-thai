"""Validation script for the completed story missions (00, 01, 02 and 01_Panama)."""

from __future__ import annotations
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def validate_all():
    story_dir = PROJECT_ROOT / "data" / "translations" / "story"
    targets = {
        "00_Training.json": 594,
        "01_Lighthouse.json": 381,
        "01_Panama.json": 168,
        "02_CargoShip.json": 450,
    }
    
    forbidden = {"“", "”", "‘", "’", "…"}
    
    for filename, expected_count in targets.items():
        filepath = story_dir / filename
        assert filepath.exists(), f"File not found: {filepath}"
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        count = 0
        sections = data["sections"]
        for sec_name, sec_data in sections.items():
            for key, val in sec_data.items():
                if key == "_source":
                    continue
                count += 1
                assert isinstance(val, dict), f"Entry [{sec_name}][{key}] is not dict"
                th = val.get("th")
                assert th is not None, f"Missing th in [{sec_name}][{key}]"
                assert str(th).strip() != "", f"Empty th in [{sec_name}][{key}]"
                
                # Check forbidden characters
                for fc in forbidden:
                    assert fc not in th, f"Forbidden character {fc} in [{sec_name}][{key}]: {th}"
                    
                # Check CP874 encoding
                raw = th.encode("cp874")
                for b in raw:
                    assert b < 128 or (161 <= b <= 251), f"Invalid byte {b} in [{sec_name}][{key}]: {th}"
                    
        assert count == expected_count, f"{filename}: expected {expected_count}, got {count}"
        print(f"[VALIDATE] {filename}: {count}/{expected_count} strings valid & 100% CP874 clean.")

    # Verify compiled .int files exist and can be decoded with CP874
    int_dir = PROJECT_ROOT / "dist" / "loose" / "Data" / "System" / "Localization"
    int_files = [
        "00_Training.int",
        "P_00_Training.int",
        "01_Lighthouse.int",
        "P_01_Lighthouse.int",
        "01_Panama.int",
        "P_01_Panama.int",
        "02_CargoShip.int",
        "P_02_CargoShip.int",
    ]
    for int_file in int_files:
        p = int_dir / int_file
        assert p.exists(), f"Compiled file not found: {p}"
        raw = p.read_bytes()
        decoded = raw.decode("cp874")
        assert len(decoded) > 0
        print(f"[VALIDATE] Compiled {int_file}: {len(raw)} bytes, decoded CP874 successfully.")

if __name__ == "__main__":
    validate_all()
    print("[VALIDATE] ALL CHECKS PASSED PERFECTLY!")
