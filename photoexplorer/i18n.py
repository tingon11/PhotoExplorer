# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Lingua dell'interfaccia e dei messaggi.

Nel codice i testi sono scritti in italiano dentro ``tr("…")``; le altre lingue stanno in
``translations.py``, che associa a ogni testo italiano la sua traduzione. Se una traduzione
manca si usa il testo italiano. I segnaposto ``{nome}`` vengono riempiti con ``str.format``.
"""
from __future__ import annotations

import locale
import sys

from .translations import TRANSLATIONS, WEEKDAYS

LANGUAGES = {          # codice -> nome mostrato nel selettore
    "it": "Italiano",
    "en": "English",
    "es": "Español",
    "de": "Deutsch",
    "fr": "Français",
}
DEFAULT_LANGUAGE = "en"   # se la lingua del sistema non è tra quelle disponibili

_current = "it"


def system_language() -> str:
    """Lingua di Windows (o del sistema), se è una di quelle disponibili."""
    code = ""
    try:
        if sys.platform == "win32":
            import ctypes
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            code = locale.windows_locale.get(lang_id, "")
        if not code:
            code = locale.getlocale()[0] or ""
    except Exception:
        code = ""
    code = code[:2].lower()
    return code if code in LANGUAGES else DEFAULT_LANGUAGE


def set_language(code: str | None) -> str:
    """Imposta la lingua corrente; con un codice vuoto o sconosciuto usa quella del sistema."""
    global _current
    _current = code if code in LANGUAGES else system_language()
    return _current


def get_language() -> str:
    return _current


def tr(text: str, /, **values) -> str:
    """Traduce un testo scritto in italiano nella lingua corrente e riempie i segnaposto."""
    if _current != "it":
        text = TRANSLATIONS.get(text, {}).get(_current, text)
    return text.format(**values) if values else text


def weekday_name(index: int) -> str:
    """Nome del giorno della settimana (0 = lunedì) nella lingua corrente."""
    return WEEKDAYS.get(_current, WEEKDAYS["it"])[index]
