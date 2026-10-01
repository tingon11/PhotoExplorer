# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Icone dei pulsanti disegnate dal font di sistema Segoe MDL2 Assets / Segoe Fluent Icons.

I simboli Unicode nei testi dei pulsanti in grassetto non sono affidabili su Windows
(il fallback dei font di Tk a volte mostra dei quadratini), le immagini sì.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageOps

_FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
_FONT_FILES = [_FONTS_DIR / "segmdl2.ttf", _FONTS_DIR / "SegoeIcons.ttf"]

# nome -> (codice del glifo, specchiato orizzontalmente)
_GLYPHS = {
    "prev": (0xE76B, False),
    "next": (0xE76C, False),
    "rotate_left": (0xE72C, True),
    "rotate_right": (0xE72C, False),
    "delete": (0xE74D, False),
    "confirm": (0xE8FB, False),
    "print": (0xE749, False),
    "up": (0xE74A, False),
    "refresh": (0xE895, False),
    "folder": (0xE8B7, False),
    "open_folder": (0xE8DA, False),
    "connect": (0xE8CE, False),
    "calendar": (0xE787, False),
    "pin": (0xE707, False),
    "star": (0xE734, False),
    "star_fill": (0xE735, False),
}

_SUPERSAMPLE = 3


def resource_path(*parts: str) -> Path:
    """File distribuito con il programma: nella cartella del progetto o dentro l'exe (PyInstaller)."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base.joinpath(*parts)


def app_icon_path() -> str | None:
    path = resource_path("assets", "photoexplorer.ico")
    return str(path) if path.exists() else None


@lru_cache(maxsize=None)
def _font_path() -> str | None:
    return next((str(p) for p in _FONT_FILES if p.exists()), None)


@lru_cache(maxsize=None)
def icon(name: str, size: int = 18, color: str = "#ffffff") -> ctk.CTkImage | None:
    font_path = _font_path()
    if font_path is None or name not in _GLYPHS:
        return None
    code, mirror = _GLYPHS[name]
    px = size * _SUPERSAMPLE
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((px / 2, px / 2), chr(code), fill=color,
                             font=ImageFont.truetype(font_path, int(px * 0.9)), anchor="mm")
    if mirror:
        img = ImageOps.mirror(img)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
