"""Unreal Engine INI / localization file codec.

Handles parsing, reading, editing, and serializing Unreal Engine INI localization
files (.int, .fra, .deu, .esp, .ita) while preserving section order, comments,
whitespace, repeated/dummy tokens, and proper encoding (CP1252, CP874, UTF-16LE).
"""

from __future__ import annotations
import os
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple, Union


@dataclass
class IniEntry:
    """A single line/entry in an INI file."""
    line_type: str  # 'key_value', 'comment', 'blank', 'header'
    raw_text: str
    key: Optional[str] = None
    value: Optional[str] = None

    @property
    def is_key_value(self) -> bool:
        return self.line_type == "key_value"

    @property
    def is_comment(self) -> bool:
        return self.line_type == "comment"

    @property
    def is_blank(self) -> bool:
        return self.line_type == "blank"


@dataclass
class IniSection:
    """A section in an INI file containing entries."""
    name: str
    entries: List[IniEntry] = field(default_factory=list)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get the last value for a given key in this section."""
        key_lower = key.lower()
        for entry in reversed(self.entries):
            if entry.is_key_value and entry.key and entry.key.lower() == key_lower:
                return entry.value
        return default

    def get_all(self, key: str) -> List[str]:
        """Get all values for a key (supports repeated keys)."""
        key_lower = key.lower()
        return [
            entry.value
            for entry in self.entries
            if entry.is_key_value and entry.key and entry.key.lower() == key_lower and entry.value is not None
        ]

    def set(self, key: str, value: str) -> None:
        """Set or update the value of a key. Updates existing entry or appends."""
        key_lower = key.lower()
        updated = False
        for entry in self.entries:
            if entry.is_key_value and entry.key and entry.key.lower() == key_lower:
                entry.value = value
                entry.raw_text = f"{entry.key}={value}"
                updated = True
                break

        if not updated:
            new_entry = IniEntry(
                line_type="key_value",
                raw_text=f"{key}={value}",
                key=key,
                value=value,
            )
            self.entries.append(new_entry)

    def items(self) -> List[Tuple[str, str]]:
        """Return list of (key, value) pairs."""
        res = []
        for entry in self.entries:
            if entry.is_key_value and entry.key is not None and entry.value is not None:
                res.append((entry.key, entry.value))
        return res

    def to_dict(self) -> Dict[str, str]:
        """Return dict of {key: value} (later occurrences overwrite earlier)."""
        d = {}
        for k, v in self.items():
            d[k] = v
        return d


class IniDocument:
    """Representation of an entire Unreal Engine INI localization file."""

    def __init__(self):
        self.sections: OrderedDict[str, IniSection] = OrderedDict()
        self.encoding: str = "cp1252"
        self.has_bom: bool = False
        self.newline: str = "\r\n"
        self.header_entries: List[IniEntry] = []  # Lines before first section

    @classmethod
    def from_bytes(cls, data: bytes, default_encoding: str = "cp1252") -> "IniDocument":
        """Parse an INI document from raw bytes with auto encoding detection."""
        doc = cls()
        has_bom = False

        if data.startswith(b"\xff\xfe"):
            encoding = "utf-16le"
            text = data[2:].decode("utf-16le", errors="replace")
            has_bom = True
        elif data.startswith(b"\xef\xbb\xbf"):
            encoding = "utf-8"
            text = data[3:].decode("utf-8", errors="replace")
            has_bom = True
        else:
            encoding = default_encoding
            try:
                text = data.decode(encoding)
            except UnicodeDecodeError:
                text = data.decode("latin-1", errors="replace")

        doc.encoding = encoding
        doc.has_bom = has_bom

        if "\r\n" in text:
            doc.newline = "\r\n"
        else:
            doc.newline = "\n"

        doc._parse_text(text)
        return doc

    @classmethod
    def from_file(
        cls, filepath: Union[str, Path], default_encoding: str = "cp1252"
    ) -> "IniDocument":
        """Load and parse an INI file from disk."""
        data = Path(filepath).read_bytes()
        return cls.from_bytes(data, default_encoding=default_encoding)

    def _parse_text(self, text: str) -> None:
        """Parse raw text into sections and entries."""
        current_section: Optional[IniSection] = None

        for line in text.splitlines():
            stripped = line.strip()

            if not stripped:
                entry = IniEntry(line_type="blank", raw_text=line)
                if current_section is not None:
                    current_section.entries.append(entry)
                else:
                    self.header_entries.append(entry)
            elif stripped.startswith(";") or stripped.startswith("#"):
                entry = IniEntry(line_type="comment", raw_text=line)
                if current_section is not None:
                    current_section.entries.append(entry)
                else:
                    self.header_entries.append(entry)
            elif stripped.startswith("[") and stripped.endswith("]"):
                sec_name = stripped[1:-1].strip()
                if sec_name in self.sections:
                    current_section = self.sections[sec_name]
                else:
                    current_section = IniSection(name=sec_name)
                    self.sections[sec_name] = current_section
            elif "=" in line:
                k, v = line.split("=", 1)
                key = k.strip()
                # Do not strip leading/trailing spaces from value if quotation marks or intentional
                val = v
                # Strip trailing \r if present
                if val.endswith("\r"):
                    val = val[:-1]
                entry = IniEntry(
                    line_type="key_value",
                    raw_text=line,
                    key=key,
                    value=val,
                )
                if current_section is not None:
                    current_section.entries.append(entry)
                else:
                    self.header_entries.append(entry)
            else:
                # Raw text / unknown line
                entry = IniEntry(line_type="comment", raw_text=line)
                if current_section is not None:
                    current_section.entries.append(entry)
                else:
                    self.header_entries.append(entry)

    def get_section(self, name: str) -> Optional[IniSection]:
        """Get section by name (case-insensitive)."""
        name_lower = name.lower()
        for s_name, sec in self.sections.items():
            if s_name.lower() == name_lower:
                return sec
        return None

    def get_or_create_section(self, name: str) -> IniSection:
        """Get existing section or create a new one."""
        sec = self.get_section(name)
        if sec is None:
            sec = IniSection(name=name)
            self.sections[name] = sec
        return sec

    def apply_translations(
        self,
        translations: Dict[str, Dict[str, str]],
        fallback_to_english: bool = True,
    ) -> int:
        """Apply a translation dictionary {section: {key: new_value}}.

        Returns the number of keys updated.
        """
        updated_count = 0
        trans_sections_lower = {s.lower(): (s, kvs) for s, kvs in translations.items()}

        for s_name, sec in self.sections.items():
            s_match = trans_sections_lower.get(s_name.lower())
            if not s_match:
                continue
            _, kvs = s_match
            kvs_lower = {k.lower(): (k, v) for k, v in kvs.items()}

            for entry in sec.entries:
                if entry.is_key_value and entry.key:
                    k_match = kvs_lower.get(entry.key.lower())
                    if k_match:
                        _, new_val = k_match
                        if new_val is not None:
                            new_val_str = str(new_val)
                            # If new_val is empty string and fallback is on, keep existing
                            if new_val_str.strip() == "" and fallback_to_english:
                                continue
                            if entry.value != new_val_str:
                                entry.value = new_val_str
                                entry.raw_text = f"{entry.key}={new_val_str}"
                                updated_count += 1

        return updated_count

    def serialize(
        self,
        encoding: Optional[str] = None,
        add_bom: Optional[bool] = None,
    ) -> bytes:
        """Serialize the document back to bytes with preserved formatting."""
        enc = encoding or self.encoding
        bom = add_bom if add_bom is not None else self.has_bom

        lines: List[str] = []

        # Header entries
        for entry in self.header_entries:
            lines.append(entry.raw_text)

        # Sections
        for sec in self.sections.values():
            lines.append(f"[{sec.name}]")
            for entry in sec.entries:
                if entry.is_key_value and entry.key is not None and entry.value is not None:
                    lines.append(f"{entry.key}={entry.value}")
                else:
                    lines.append(entry.raw_text)

        full_text = self.newline.join(lines)
        if full_text and not full_text.endswith(self.newline):
            full_text += self.newline

        if enc.lower() in ("utf-16", "utf-16le"):
            raw_bytes = full_text.encode("utf-16le")
            if bom:
                return b"\xff\xfe" + raw_bytes
            return raw_bytes
        elif enc.lower() in ("utf-8", "utf-8-sig"):
            raw_bytes = full_text.encode("utf-8")
            if bom:
                return b"\xef\xbb\xbf" + raw_bytes
            return raw_bytes
        else:
            return full_text.encode(enc, errors="replace")

    def save(
        self,
        filepath: Union[str, Path],
        encoding: Optional[str] = None,
        add_bom: Optional[bool] = None,
    ) -> None:
        """Save the document to disk."""
        data = self.serialize(encoding=encoding, add_bom=add_bom)
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Export as dictionary of {section: {key: value}}."""
        result = OrderedDict()
        for s_name, sec in self.sections.items():
            result[s_name] = sec.to_dict()
        return result
