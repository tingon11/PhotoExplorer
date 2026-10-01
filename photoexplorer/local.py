# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Foto in una cartella del PC, di un hard disk esterno o di una chiavetta USB.

Ha la stessa interfaccia di ``SmbBrowser`` (elenco, lettura, scrittura, eliminazione), così il
resto del programma funziona allo stesso modo con il NAS e con i dischi locali.
"""
from __future__ import annotations

import ctypes
import os
import stat
import sys
from pathlib import Path

from .i18n import tr
from .imaging import is_image
from .smb import HIDDEN_DIRS, RemoteFile, join

_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def volume_id(path: str) -> str:
    """Identificativo del disco che non dipende dalla lettera di unità: una chiavetta resta
    riconoscibile (e ricorda le foto già viste) anche se un giorno è E: e un altro F:."""
    drive = os.path.splitdrive(os.path.abspath(path))[0]
    if sys.platform == "win32" and len(drive) == 2 and drive[1] == ":":
        serial = ctypes.c_ulong(0)
        if ctypes.windll.kernel32.GetVolumeInformationW(drive + "\\", None, 0, ctypes.byref(serial),
                                                        None, None, None, 0):
            return f"disk-{serial.value:08x}"
    return drive.strip("\\/").lower() or "local"


def move_to_recycle_bin(path: str) -> bool:
    """Sposta un file nel Cestino di Windows. Restituisce False se non è stato possibile."""
    if sys.platform != "win32":
        return False
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        if ctypes.sizeof(ctypes.c_void_p) == 4:
            _pack_ = 1
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT), ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR), ("fFlags", ctypes.c_uint16),
                    ("fAnyOperationsAborted", wintypes.BOOL), ("hNameMappings", ctypes.c_void_p),
                    ("lpszProgressTitle", wintypes.LPCWSTR)]

    fo_delete, silent, no_confirm, allow_undo, no_error_ui = 3, 0x4, 0x10, 0x40, 0x400
    source = ctypes.create_unicode_buffer(os.path.abspath(path) + "\0")   # elenco terminato da doppio zero
    op = SHFILEOPSTRUCTW(None, fo_delete, ctypes.cast(source, wintypes.LPCWSTR), None,
                         allow_undo | no_confirm | silent | no_error_ui, False, None, None)
    result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    return result == 0 and not op.fAnyOperationsAborted and not os.path.exists(path)


class LocalBrowser:
    kind = "local"
    connection_key = "local"

    @property
    def delete_question(self) -> str:
        return tr("Eliminare questa foto? (va nel Cestino; sulle chiavette è definitiva)")

    def __init__(self, root: str) -> None:
        self.root = os.path.abspath(root)

    # --- identità ---------------------------------------------------------
    @property
    def root_name(self) -> str:
        return os.path.basename(self.root.rstrip("\\/")) or self.root.rstrip("\\/")

    @property
    def location(self) -> str:
        return f"local|{self.root.lower()}"

    @property
    def history_root(self) -> str:
        """Radice delle chiavi per la memoria delle foto viste: disco + percorso senza lettera di unità."""
        tail = os.path.splitdrive(self.root)[1].replace("/", "\\").strip("\\")
        return f"{volume_id(self.root)}\\{tail}".strip("\\")

    def parent_root(self) -> str | None:
        """Cartella superiore alla radice scelta (None se si è già in cima al disco)."""
        up = os.path.dirname(self.root.rstrip("\\/"))
        return up if up and os.path.normcase(up) != os.path.normcase(self.root.rstrip("\\/")) and os.path.isdir(up) \
            else None

    def unc(self, rel: str) -> str:
        return os.path.join(self.root, *rel.split("\\")) if rel else self.root

    # --- operazioni -------------------------------------------------------
    def connect(self) -> None:
        if not os.path.isdir(self.root):
            raise FileNotFoundError(self.root)

    def close(self) -> None:
        pass

    def list_dir(self, rel: str) -> tuple[list[str], list[RemoteFile]]:
        dirs: list[str] = []
        files: list[RemoteFile] = []
        with os.scandir(self.unc(rel)) as entries:
            for entry in entries:
                name = entry.name
                if name.startswith(".") or name.lower() in HIDDEN_DIRS:
                    continue
                try:
                    info = entry.stat(follow_symlinks=False)
                    if entry.is_dir(follow_symlinks=False):
                        # niente collegamenti/giunzioni: potrebbero creare giri infiniti
                        if not name.startswith("@") and not entry.is_symlink() \
                                and not getattr(info, "st_file_attributes", 0) & _REPARSE_POINT:
                            dirs.append(name)
                    elif is_image(name):
                        files.append(RemoteFile(name, join(rel, name), info.st_size, info.st_mtime))
                except OSError:
                    continue   # file sparito o illeggibile mentre si leggeva la cartella
        return dirs, files

    def read_bytes(self, rel: str) -> bytes:
        return Path(self.unc(rel)).read_bytes()

    def write_bytes(self, rel: str, data: bytes) -> None:
        """Scrive su un file temporaneo e poi sostituisce l'originale, così un'interruzione
        (es. chiavetta staccata) non lascia mai una foto troncata."""
        target = Path(self.unc(rel))
        tmp = target.with_name(f".{target.name}.photoexplorer.tmp")
        try:
            tmp.write_bytes(data)
            os.replace(tmp, target)
        except BaseException:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    def remove(self, rel: str) -> None:
        path = self.unc(rel)
        if not move_to_recycle_bin(path) and os.path.exists(path):
            os.remove(path)   # dischi senza Cestino
