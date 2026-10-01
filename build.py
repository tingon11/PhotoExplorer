# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Crea dist\\PhotoExplorer.exe: un unico file eseguibile, senza bisogno di installare Python.

Uso (dalla cartella del progetto):
    .venv\\Scripts\\python.exe build.py
oppure doppio clic su build.bat.
"""
from __future__ import annotations

import importlib
import importlib.util
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "PhotoExplorer"
ENTRY = ROOT / "main.py"
ICON = ROOT / "assets" / "photoexplorer.ico"
DIST = ROOT / "dist"
WORK = ROOT / "build"

REQUIRED_MODULES = ("customtkinter", "PIL", "smbclient", "spnego", "keyring", "pillow_heif")


def make_icon(path: Path = ICON) -> None:
    """Disegna l'icona dell'app: un disegno originale (cornice con montagne e sole su quadrato blu),
    fatto solo di forme geometriche, senza usare simboli di font di terze parti."""
    from PIL import Image, ImageDraw

    s = 1024   # si disegna in grande e poi si riduce, per avere bordi morbidi
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([30, 30, s - 30, s - 30], radius=205, fill="#1f6aa5")
    left, top, right, bottom, border = 190, 280, 834, 744, 46
    d.rounded_rectangle([left, top, right, bottom], radius=40, outline="white", width=border)   # cornice
    floor = bottom - border
    d.polygon([(left + border, floor), (430, 455), (640, floor)], fill="white")                 # montagna grande
    d.polygon([(540, floor), (668, 545), (right - border, floor)], fill="white")                # montagna piccola
    d.ellipse([655, 370, 745, 460], fill="white")                                               # sole

    sizes = [256, 128, 64, 48, 32, 24, 16]
    images = [img.resize((size, size), Image.Resampling.LANCZOS) for size in sizes]
    path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(path, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])


def pyinstaller_args(entry: Path = ENTRY, name: str = NAME, dist: Path = DIST, work: Path = WORK,
                     windowed: bool = True) -> list[str]:
    args = [
        str(entry),
        "--name", name,
        "--onefile",
        "--noconfirm",
        "--clean",
        "--distpath", str(dist),
        "--workpath", str(work),
        "--specpath", str(work),
        "--paths", str(ROOT),
        "--icon", str(ICON),
        "--add-data", f"{ICON}{os.pathsep}assets",   # icona della finestra
        # testo della licenza e termini di attribuzione, mostrati nella finestra "Informazioni"
        "--add-data", f"{ROOT / 'LICENSE'}{os.pathsep}.",
        "--add-data", f"{ROOT / 'ADDITIONAL_TERMS.txt'}{os.pathsep}.",
        "--collect-data", "customtkinter",            # temi e font di customtkinter
        "--collect-binaries", "pillow_heif",          # libheif, per le foto HEIC degli iPhone
        "--collect-submodules", "spnego",             # autenticazione NTLM di smbprotocol
        "--collect-submodules", "keyring.backends",   # "Ricorda password" (Gestione credenziali)
        "--exclude-module", "PyInstaller",
    ]
    if windowed:
        args.append("--windowed")   # niente finestra nera del terminale
    return args


def check_environment() -> None:
    missing = []
    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(module)
    if missing:
        sys.exit(f"Mancano delle librerie ({', '.join(missing)}).\n"
                 f"Esegui la build con il Python del progetto:  .venv\\Scripts\\python.exe build.py\n"
                 f"oppure installale con:  {sys.executable} -m pip install -r requirements.txt")
    if importlib.util.find_spec("PyInstaller") is None:
        print("Installo PyInstaller…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def main() -> None:
    check_environment()
    if not ICON.exists():
        make_icon()

    exe = DIST / f"{NAME}.exe"
    try:
        exe.unlink(missing_ok=True)
    except PermissionError:
        sys.exit(f"{exe} è in uso: chiudi PhotoExplorer e riprova.")
    shutil.rmtree(WORK, ignore_errors=True)

    import PyInstaller.__main__

    started = time.time()
    PyInstaller.__main__.run(pyinstaller_args())
    shutil.rmtree(WORK, ignore_errors=True)

    size_mb = exe.stat().st_size / 1024 / 1024
    print(f"\nFatto in {time.time() - started:.0f} s:  {exe}  ({size_mb:.0f} MB)")


if __name__ == "__main__":
    main()
