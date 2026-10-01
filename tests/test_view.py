# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
# SPDX-License-Identifier: GPL-3.0-only
"""La vista della foto deve potersi disegnare per qualsiasi dimensione, zoom e posizione.

Nasce da un difetto reale: per foto come 3872x2592 o 2500x1667 l'anteprima ha un'altezza
arrotondata (1920x1285, 1920x1280) e il ritaglio usciva di una frazione di pixel dai bordi,
lasciando la foto bloccata su "Caricamento…".

Si può lanciare direttamente:  .venv\\Scripts\\python.exe tests\\test_view.py
"""
from __future__ import annotations

import itertools
import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image  # noqa: E402

from photoexplorer.imaging import decode_for_display, render_view, rotate_cw  # noqa: E402

SIZES = [(1984, 1488), (2500, 1667), (1667, 2500), (3872, 2592), (4288, 2848), (3008, 2000), (2848, 4288),
         (5184, 3456), (4928, 3264), (640, 427), (100, 37), (37, 100), (8000, 1200), (3, 5000), (1, 1)]
SCREENS = (1366, 1920, 2560, 3200)
BOXES = ((1170, 690), (1590, 760), (300, 200), (60, 40))
ZOOMS = (1.0, 1.3, 2.5, 7.0, 40.0)


def failures() -> list[str]:
    found = []
    for max_side, (w, h) in itertools.product(SCREENS, SIZES):
        data = BytesIO()
        Image.new("RGB", (w, h), "teal").save(data, "PNG" if max(w, h) <= 64 else "JPEG")
        item = decode_for_display(data.getvalue(), max_side)
        for turn in (0, 90):
            src = rotate_cw(item.base, turn)
            full = item.full_size if turn == 0 else item.full_size[::-1]
            centers = (None, (0, 0), full, (full[0] / 3, full[1] * 0.9))
            for box, zoom, center, fast in itertools.product(BOXES, ZOOMS, centers, (False, True)):
                try:
                    view = render_view(src, full, box, zoom, center, fast)
                    assert view.image.width >= 1 and view.image.height >= 1
                except Exception as exc:  # noqa: BLE001 - qualsiasi errore qui è un difetto
                    found.append(f"schermo {max_side}, foto {w}x{h}, anteprima {item.base.size}, riquadro {box}, "
                                 f"zoom {zoom}: {type(exc).__name__}: {exc}")
    return found


def test_view_never_fails():
    assert not failures()


if __name__ == "__main__":
    problems = failures()
    for problem in problems[:10]:
        print("-", problem)
    print("vista: tutto a posto" if not problems else f"vista: {len(problems)} casi falliti")
    sys.exit(1 if problems else 0)
