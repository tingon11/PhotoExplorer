# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
# SPDX-License-Identifier: GPL-3.0-only
"""Controlla che le traduzioni siano complete e coerenti.

Si può lanciare direttamente:  .venv\\Scripts\\python.exe tests\\test_translations.py
oppure con pytest.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from photoexplorer.i18n import LANGUAGES  # noqa: E402
from photoexplorer.translations import TRANSLATIONS, WEEKDAYS  # noqa: E402

OTHER_LANGUAGES = [code for code in LANGUAGES if code != "it"]


def texts_in_code() -> dict[str, str]:
    """Tutti i testi passati a tr("…") nel codice: {testo: file:riga}."""
    found: dict[str, str] = {}
    for path in sorted((ROOT / "photoexplorer").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "tr":
                first = node.args[0]
                assert isinstance(first, ast.Constant) and isinstance(first.value, str), \
                    f"{path.name}:{node.lineno}: tr() deve ricevere un testo scritto per esteso"
                found.setdefault(first.value, f"{path.name}:{node.lineno}")
    return found


def placeholders(text: str) -> list[str]:
    return sorted(re.findall(r"\{([a-z_0-9]+)[^}]*\}", text))


def edge_spaces(text: str) -> tuple[int, int]:
    return len(text) - len(text.lstrip(" ")), len(text) - len(text.rstrip(" "))


def problems() -> list[str]:
    found = []
    code = texts_in_code()
    for text, where in code.items():
        entry = TRANSLATIONS.get(text)
        if entry is None:
            found.append(f"manca la traduzione di {text!r} ({where})")
            continue
        for lang in OTHER_LANGUAGES:
            translated = entry.get(lang)
            if not translated:
                found.append(f"manca la lingua {lang} per {text!r}")
            elif placeholders(translated) != placeholders(text):
                found.append(f"segnaposto diversi in {lang} per {text!r}: {placeholders(translated)}")
            elif edge_spaces(translated) != edge_spaces(text):
                found.append(f"spazi iniziali/finali diversi in {lang} per {text!r}")
            elif translated.count("\n") != text.count("\n"):
                found.append(f"numero di righe diverso in {lang} per {text!r}")
    for text in TRANSLATIONS:
        if text not in code:
            found.append(f"traduzione non più usata nel codice: {text!r}")
    for lang in LANGUAGES:
        if len(WEEKDAYS.get(lang, ())) != 7:
            found.append(f"giorni della settimana mancanti per {lang}")
    return found


def test_translations_are_complete():
    assert not problems(), "\n".join(problems())


if __name__ == "__main__":
    issues = problems()
    for issue in issues:
        print("-", issue)
    print(f"{len(texts_in_code())} testi, {len(OTHER_LANGUAGES)} lingue oltre l'italiano: "
          + ("tutto a posto" if not issues else f"{len(issues)} problemi"))
    sys.exit(1 if issues else 0)
