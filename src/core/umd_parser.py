"""UMD archive parser and builder for Splinter Cell Chaos Theory.

Handles reading, extracting, and repacking of .umd package archives,
specifically dynamic-pc.umd (Unreal Engine 2 package format with
CompactIndex table of contents and footer).
"""

from __future__ import annotations
import os
import struct
import time
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Callable, Dict, List, Optional, Union

UMD_MAGIC = 0x9FE3C5A3
ALIGNMENT = 16  # Unreal Engine file offset alignment in UMD


def read_compact_index(stream: BinaryIO) -> int:
    """Read an Unreal Engine CompactIndex integer from a binary stream."""
    b0 = stream.read(1)
    if not b0:
        raise EOFError("Unexpected end of stream while reading CompactIndex")
    byte0 = b0[0]
    sign = byte0 & 0x80
    has_more = byte0 & 0x40
    val = byte0 & 0x3F
    shift = 6
    while has_more:
        b = stream.read(1)
        if not b:
            raise EOFError("Unexpected end of stream in multi-byte CompactIndex")
        byte_val = b[0]
        has_more = byte_val & 0x80
        val |= (byte_val & 0x7F) << shift
        shift += 7
    if sign:
        val = -val
    return val


def write_compact_index(val: int) -> bytes:
    """Encode an integer as Unreal Engine CompactIndex bytes."""
    sign = 0x80 if val < 0 else 0
    abs_val = abs(val)
    b0 = (abs_val & 0x3F) | sign
    abs_val >>= 6
    if abs_val > 0:
        b0 |= 0x40
        out = bytearray([b0])
        while abs_val > 0:
            b = abs_val & 0x7F
            abs_val >>= 7
            if abs_val > 0:
                b |= 0x80
            out.append(b)
        return bytes(out)
    return bytes([b0])


@dataclass
class UMDEntry:
    """Represents a single file entry in the UMD archive."""
    name: str
    offset: int
    size: int
    flags: int
    is_unicode: bool = False

    @property
    def extension(self) -> str:
        """Return the lowercase extension without leading dot."""
        if "." in self.name:
            return self.name.rsplit(".", 1)[-1].lower()
        return ""


class UMDArchive:
    """Parser and repacker for Splinter Cell Chaos Theory UMD files."""

    def __init__(self, filepath: Union[str, Path]):
        self.filepath = Path(filepath)
        self.magic: int = 0
        self.toc_offset: int = 0
        self.archive_size: int = 0
        self.version: int = 1
        self.timestamp: int = 0
        self.entries: List[UMDEntry] = []
        self._entry_map: Dict[str, UMDEntry] = {}
        self._load()

    def _load(self) -> None:
        """Parse footer and TOC from the UMD file."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"UMD archive not found: {self.filepath}")

        with open(self.filepath, "rb") as f:
            f.seek(0, os.SEEK_END)
            actual_size = f.tell()
            if actual_size < 20:
                raise ValueError(f"File too small to be a valid UMD: {self.filepath}")

            # Read 20-byte footer
            f.seek(actual_size - 20)
            footer_data = f.read(20)
            self.magic, self.toc_offset, self.archive_size, self.version, self.timestamp = (
                struct.unpack("<5I", footer_data)
            )

            if self.magic != UMD_MAGIC:
                raise ValueError(
                    f"Invalid UMD magic: expected 0x{UMD_MAGIC:08x}, got 0x{self.magic:08x}"
                )

            # Read TOC
            f.seek(self.toc_offset)
            count = read_compact_index(f)
            self.entries = []
            self._entry_map = {}

            for _ in range(count):
                slen = read_compact_index(f)
                if slen > 0:
                    raw_name = f.read(slen)
                    name = raw_name.rstrip(b"\x00").decode("latin-1", errors="replace")
                    is_unicode = False
                elif slen < 0:
                    raw_name = f.read(-slen * 2)
                    name = raw_name.decode("utf-16le", errors="replace").rstrip("\x00")
                    is_unicode = True
                else:
                    name = ""
                    is_unicode = False

                offset, size, flags = struct.unpack("<3I", f.read(12))
                entry = UMDEntry(
                    name=name,
                    offset=offset,
                    size=size,
                    flags=flags,
                    is_unicode=is_unicode,
                )
                self.entries.append(entry)
                self._entry_map[name.lower().replace("/", "\\")] = entry

    def find_entry(self, name: str) -> Optional[UMDEntry]:
        """Find an entry by name (case-insensitive, slash-insensitive)."""
        normalized = name.lower().replace("/", "\\")
        return self._entry_map.get(normalized)

    def read_entry(self, entry_or_name: Union[UMDEntry, str]) -> bytes:
        """Read the raw data bytes for a given entry."""
        if isinstance(entry_or_name, str):
            entry = self.find_entry(entry_or_name)
            if not entry:
                raise KeyError(f"Entry '{entry_or_name}' not found in archive")
        else:
            entry = entry_or_name

        with open(self.filepath, "rb") as f:
            f.seek(entry.offset)
            return f.read(entry.size)

    def extract_entry(
        self, entry_or_name: Union[UMDEntry, str], dest_path: Union[str, Path]
    ) -> Path:
        """Extract a single entry to disk."""
        data = self.read_entry(entry_or_name)
        dest = Path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return dest

    def extract_filtered(
        self,
        dest_dir: Union[str, Path],
        predicate: Callable[[UMDEntry], bool],
        preserve_subdirs: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[Path]:
        """Extract all entries matching a filter predicate."""
        dest_root = Path(dest_dir)
        matched = [e for e in self.entries if predicate(e)]
        extracted = []

        with open(self.filepath, "rb") as f:
            for idx, entry in enumerate(matched):
                f.seek(entry.offset)
                data = f.read(entry.size)
                if preserve_subdirs:
                    target_file = dest_root / entry.name.replace("/", os.sep).replace("\\", os.sep)
                else:
                    target_file = dest_root / Path(entry.name).name

                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_bytes(data)
                extracted.append(target_file)

                if progress_callback:
                    progress_callback(idx + 1, len(matched), entry.name)

        return extracted

    def repack(
        self,
        output_path: Union[str, Path],
        replacements: Optional[Dict[str, Union[bytes, str, Path]]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> int:
        """Rebuild the UMD archive with file replacements.

        Args:
            output_path: Destination path for the new .umd file.
            replacements: Dict mapping entry names to replacement bytes or file paths.
            progress_callback: Callback(current, total, current_file_name) for progress.

        Returns:
            The total byte size of the new UMD archive.
        """
        replacements = replacements or {}
        # Normalize replacement keys (lowercase, backslashes)
        normalized_replacements: Dict[str, Union[bytes, Path]] = {}
        for k, v in replacements.items():
            norm_k = k.lower().replace("/", "\\")
            if isinstance(v, (str, Path)):
                p = Path(v)
                if not p.is_file():
                    raise FileNotFoundError(f"Replacement file not found: {p}")
                normalized_replacements[norm_k] = p
            elif isinstance(v, (bytes, bytearray)):
                normalized_replacements[norm_k] = bytes(v)
            else:
                raise TypeError(f"Invalid replacement type for {k}: {type(v)}")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        new_entries: List[UMDEntry] = []
        chunk_size = 4 * 1024 * 1024  # 4MB streaming buffer

        with open(self.filepath, "rb") as src_f, open(output_file, "wb") as dst_f:
            total_entries = len(self.entries)

            for idx, entry in enumerate(self.entries):
                norm_key = entry.name.lower().replace("/", "\\")
                current_offset = dst_f.tell()

                # Align offset to 16 bytes
                pad_bytes = (ALIGNMENT - (current_offset % ALIGNMENT)) % ALIGNMENT
                if pad_bytes > 0:
                    dst_f.write(b"\x00" * pad_bytes)
                    current_offset = dst_f.tell()

                if norm_key in normalized_replacements:
                    rep = normalized_replacements[norm_key]
                    if isinstance(rep, bytes):
                        rep_data = rep
                    else:
                        rep_data = rep.read_bytes()

                    dst_f.write(rep_data)
                    new_size = len(rep_data)
                else:
                    # Stream copy from source
                    src_f.seek(entry.offset)
                    remaining = entry.size
                    while remaining > 0:
                        to_read = min(remaining, chunk_size)
                        block = src_f.read(to_read)
                        if not block:
                            raise EOFError(f"Unexpected EOF reading entry {entry.name}")
                        dst_f.write(block)
                        remaining -= len(block)
                    new_size = entry.size

                new_entry = UMDEntry(
                    name=entry.name,
                    offset=current_offset,
                    size=new_size,
                    flags=entry.flags,
                    is_unicode=entry.is_unicode,
                )
                new_entries.append(new_entry)

                if progress_callback and (idx % 200 == 0 or idx == total_entries - 1):
                    progress_callback(idx + 1, total_entries, entry.name)

            # Write TOC
            new_toc_offset = dst_f.tell()
            dst_f.write(write_compact_index(len(new_entries)))

            for entry in new_entries:
                if not entry.is_unicode:
                    name_bytes = entry.name.encode("latin-1", errors="replace") + b"\x00"
                    dst_f.write(write_compact_index(len(name_bytes)))
                    dst_f.write(name_bytes)
                else:
                    name_bytes = entry.name.encode("utf-16le") + b"\x00\x00"
                    dst_f.write(write_compact_index(-len(entry.name) - 1))
                    dst_f.write(name_bytes)

                dst_f.write(struct.pack("<3I", entry.offset, entry.size, entry.flags))

            # Write 20-byte footer
            final_size = dst_f.tell() + 20
            new_timestamp = int(time.time())
            footer = struct.pack(
                "<5I",
                UMD_MAGIC,
                new_toc_offset,
                final_size,
                self.version,
                new_timestamp,
            )
            dst_f.write(footer)

        return final_size
