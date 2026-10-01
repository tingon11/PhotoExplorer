# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Persistenza su disco: impostazioni e memoria delle foto viste / scaricate."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

APP_NAME = "PhotoExplorer"
APP_DIR = Path(os.environ.get("APPDATA") or Path.home()) / APP_NAME
SETTINGS_FILE = APP_DIR / "settings.json"
HISTORY_FILE = APP_DIR / "history.json"


def default_print_dir() -> str:
    return str(Path.home() / "Pictures" / "Da stampare")


def _atomic_write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _read_json(path: Path) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


@dataclass
class Settings:
    server: str = ""
    port: int = 445
    share: str = ""
    start_folder: str = ""
    username: str = ""
    domain: str = ""
    remember_password: bool = False
    print_dir: str = ""
    skip_viewed: bool = False
    include_subfolders: bool = True
    stamp_date: bool = False
    sort_by: str = "name"      # "name" oppure "date"
    language: str = ""         # codice della lingua ("it", "en"…); vuoto = lingua del sistema
    last_folder: str = ""
    last_location: str = ""  # sorgente (NAS o cartella locale) a cui si riferisce last_folder
    last_source: str = "smb"  # "smb" = NAS, "local" = cartella del PC / disco / chiavetta
    local_root: str = ""     # ultima cartella locale aperta
    geometry: str = ""

    @classmethod
    def load(cls) -> "Settings":
        raw = _read_json(SETTINGS_FILE)
        known = {f.name for f in fields(cls)}
        s = cls(**{k: v for k, v in raw.items() if k in known})
        if not s.print_dir:
            s.print_dir = default_print_dir()
        s.sort_by = {"Data": "date", "date": "date"}.get(s.sort_by, "name")   # le vecchie versioni salvavano il testo
        return s

    def save(self) -> None:
        _atomic_write_json(SETTINGS_FILE, asdict(self))


def folder_key(share: str, folder: str) -> str:
    """Chiave della cartella indipendente dall'indirizzo del server (IP o nome)."""
    return f"{share}\\{folder}".strip("\\").lower()


class History:
    """Memoria delle foto già viste, delle preferite e di quelle copiate nella cartella stampa.

    viewed:    chiave cartella -> set di nomi file (minuscoli)
    favorites: chiave cartella -> set di nomi file (minuscoli) segnati come preferiti
    totals:    chiave cartella -> numero di foto contate all'ultima apertura
    printed:   chiave cartella\\nome -> {"path": copia locale, "date": copia con la data stampata}
    """

    def __init__(self) -> None:
        raw = _read_json(HISTORY_FILE)
        self.viewed: dict[str, set[str]] = {k: set(v) for k, v in raw.get("viewed", {}).items()}
        self.favorites: dict[str, set[str]] = {k: set(v) for k, v in raw.get("favorites", {}).items()}
        self.totals: dict[str, int] = dict(raw.get("totals", {}))
        self.printed: dict[str, dict] = {
            k: v if isinstance(v, dict) else {"path": v, "date": False}
            for k, v in raw.get("printed", {}).items()
        }
        self.dirty = False

    # --- viste -------------------------------------------------------------
    def is_viewed(self, fkey: str, name: str) -> bool:
        return name.lower() in self.viewed.get(fkey, ())

    def viewed_names(self, fkey: str) -> set[str]:
        return set(self.viewed.get(fkey, ()))

    def mark_viewed(self, fkey: str, name: str) -> bool:
        names = self.viewed.setdefault(fkey, set())
        if name.lower() in names:
            return False
        names.add(name.lower())
        self.dirty = True
        return True

    def forget(self, fkey: str, name: str) -> None:
        """Da chiamare quando un file viene eliminato."""
        self.viewed.get(fkey, set()).discard(name.lower())
        self.favorites.get(fkey, set()).discard(name.lower())
        self.printed.pop(f"{fkey}\\{name.lower()}", None)
        self.dirty = True

    # --- preferite ---------------------------------------------------------
    def is_favorite(self, fkey: str, name: str) -> bool:
        return name.lower() in self.favorites.get(fkey, ())

    def set_favorite(self, fkey: str, name: str, favorite: bool) -> None:
        names = self.favorites.setdefault(fkey, set())
        if favorite:
            names.add(name.lower())
        else:
            names.discard(name.lower())
        self.dirty = True

    def has_favorites_under(self, fkey: str) -> bool:
        """C'è almeno una preferita in questa cartella o in una sua sottocartella?"""
        return any(names and self._in_tree(key, fkey) for key, names in self.favorites.items())

    # --- azzeramento delle viste (le preferite non vengono toccate) --------
    def reset_folder(self, fkey: str) -> None:
        self.viewed.pop(fkey, None)
        self.dirty = True

    def _in_tree(self, key: str, fkey: str) -> bool:
        return key == fkey or key.startswith(fkey + "\\")

    def reset_tree(self, fkey: str) -> None:
        """Azzera le viste della cartella e di tutte le sue sottocartelle."""
        for key in [k for k in self.viewed if self._in_tree(k, fkey)]:
            del self.viewed[key]
        self.dirty = True

    def set_total(self, fkey: str, total: int) -> None:
        if self.totals.get(fkey) != total:
            self.totals[fkey] = total
            self.dirty = True

    def folder_progress(self, fkey: str) -> tuple[int, int] | None:
        """(viste, totali) se la cartella è già stata aperta almeno una volta."""
        if fkey not in self.totals:
            return None
        total = self.totals[fkey]
        return min(len(self.viewed.get(fkey, ())), total), total

    def tree_progress(self, fkey: str) -> tuple[int, int] | None:
        """Come folder_progress, ma sommando anche tutte le sottocartelle già esplorate."""
        seen = total = 0
        found = False
        for key, count in self.totals.items():
            if self._in_tree(key, fkey):
                found = True
                total += count
                seen += min(len(self.viewed.get(key, ())), count)
        return (seen, total) if found else None

    # --- stampa ------------------------------------------------------------
    def printed_copy(self, fkey: str, name: str) -> tuple[str, bool] | None:
        """(percorso della copia locale, copia con la data stampata) se la foto è già stata copiata."""
        entry = self.printed.get(f"{fkey}\\{name.lower()}")
        return (entry["path"], bool(entry.get("date"))) if entry else None

    def was_printed(self, fkey: str, name: str) -> bool:
        """La foto è già stata mandata in stampa almeno una volta (anche se la copia non c'è più)?"""
        return f"{fkey}\\{name.lower()}" in self.printed

    def set_printed(self, fkey: str, name: str, local_path: str, with_date: bool) -> None:
        key = f"{fkey}\\{name.lower()}"
        # ogni file della cartella stampa appartiene a una sola foto: se prima quel nome era
        # di un'altra foto (la cui copia è stata cancellata a mano), quel collegamento non vale più
        target = os.path.normcase(os.path.abspath(local_path))
        for other in [k for k, v in self.printed.items()
                      if k != key and os.path.normcase(os.path.abspath(v["path"])) == target]:
            del self.printed[other]
        self.printed[key] = {"path": local_path, "date": with_date}
        self.dirty = True

    def clear_all(self) -> None:
        """Azzeramento completo: foto viste, preferite, foto mandate in stampa e conteggi."""
        self.viewed.clear()
        self.favorites.clear()
        self.totals.clear()
        self.printed.clear()
        self.dirty = True

    def save(self) -> None:
        if not self.dirty:
            return
        _atomic_write_json(HISTORY_FILE, {
            "viewed": {k: sorted(v) for k, v in self.viewed.items() if v},
            "favorites": {k: sorted(v) for k, v in self.favorites.items() if v},
            "totals": self.totals,
            "printed": self.printed,
        })
        self.dirty = False
