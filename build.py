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
    .venv\\Scripts\\python.exe build.py                        solo l'exe (oppure doppio clic su build.bat)
    .venv\\Scripts\\python.exe build.py --release              + zip e note di rilascio in dist\\
    .venv\\Scripts\\python.exe build.py --release --no-build   rifà solo zip e note

--release produce dist\\PhotoExplorer-<versione>-windows-x64.zip (exe, LICENSE,
ADDITIONAL_TERMS.txt, THIRD_PARTY_LICENSES.txt, README.md) e dist\\release-notes-<versione>.md
con le novità della sezione più recente di CHANGELOG.md e l'impronta SHA-256 dello zip,
come per le altre app dell'autore. La pubblicazione su GitHub si fa a mano (git push, poi
una nuova Release con il tag della versione, le note e lo zip allegato).
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "PhotoExplorer"
ENTRY = ROOT / "main.py"
ICON = ROOT / "assets" / "photoexplorer.ico"
LOGO = ROOT / "assets" / "logo.png"
DIST = ROOT / "dist"
WORK = ROOT / "build"

REQUIRED_MODULES = ("customtkinter", "PIL", "smbclient", "spnego", "keyring", "pillow_heif")
RUNTIME_PACKAGES = ("customtkinter", "Pillow", "smbprotocol", "keyring", "pillow-heif")   # con le loro dipendenze
NOTICES = DIST / "THIRD_PARTY_LICENSES.txt"
CHANGELOG = ROOT / "CHANGELOG.md"
LEGAL_FILES = ("LICENSE", "ADDITIONAL_TERMS.txt")   # accanto all'exe e nello zip, con le note di terze parti

sys.path.insert(0, str(ROOT))
from photoexplorer import __author__, __email__, __url__, __version__  # noqa: E402

ZIP = DIST / f"{NAME}-{__version__}-windows-x64.zip"
RELEASE_NOTES_FILE = DIST / f"release-notes-{__version__}.md"
VERSION_FILE = WORK / "version_info.txt"

RELEASE_NOTES = """\
{intro}

## What's new in {version}

{changes}

## Download

**{zip}** is the standalone program for Windows 10/11 (64-bit). Python is
not needed: unzip it in any folder and run `{exe}`.

## First start

- Choose the interface language (Italian, English, Spanish, German, French; it can be
  changed later from the top bar), then read and accept the disclaimer.
- Connect to the NAS (SMB) or open a folder on the PC, a hard disk or a USB stick.
- Settings and the memory of viewed photos are stored in `%APPDATA%\\PhotoExplorer`.
  Photos are changed only when you rotate or delete them: keep a backup of the ones you care about.
- The executable is not signed, so Windows SmartScreen may show a warning the
  first time it runs.

## Verify the download

SHA-256 of `{zip}`:

```
{sha256}
```

## Bundled software

`{exe}` contains the Python interpreter, Tcl/Tk and these libraries, each under its
own license; their license texts are in `THIRD_PARTY_LICENSES.txt` in the zip (and in the
program's About window):

{bundled}

## License

{name} is free software under the GNU GPL version 3 with additional attribution
terms (see `LICENSE` and `ADDITIONAL_TERMS.txt`). It is not forensic software and comes
without any warranty. {author} - {email} - {url}
"""

VERSION_INFO = """\
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={numbers}, prodvers={numbers},
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0),
  ),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', {author!r}),
      StringStruct('FileDescription', {description!r}),
      StringStruct('FileVersion', {version!r}),
      StringStruct('InternalName', {name!r}),
      StringStruct('LegalCopyright', {copyright!r}),
      StringStruct('OriginalFilename', {exe!r}),
      StringStruct('ProductName', {name!r}),
      StringStruct('ProductVersion', {version!r}),
    ])]),
    VarFileInfo([VarStruct('Translation', [0x0409, 1200])]),
  ],
)
"""


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
        "--version-file", str(VERSION_FILE),          # versione e autore nelle proprietà del file
        "--add-data", f"{ICON}{os.pathsep}assets",   # icona della finestra
        "--add-data", f"{LOGO}{os.pathsep}assets",   # scritta PhotoExplorer nella barra in alto
        # testo della licenza e termini di attribuzione, mostrati nella finestra "Informazioni"
        "--add-data", f"{ROOT / 'LICENSE'}{os.pathsep}.",
        "--add-data", f"{ROOT / 'ADDITIONAL_TERMS.txt'}{os.pathsep}.",
        # licenze e copyright dei componenti di terze parti inclusi nell'exe (generato da build.py)
        "--add-data", f"{NOTICES}{os.pathsep}.",
        "--collect-data", "customtkinter",            # temi e font di customtkinter
        "--collect-binaries", "pillow_heif",          # libheif, per le foto HEIC degli iPhone
        "--collect-submodules", "spnego",             # autenticazione NTLM di smbprotocol
        "--collect-submodules", "keyring.backends",   # "Ricorda password" (Gestione credenziali)
        "--exclude-module", "PyInstaller",
    ]
    if windowed:
        args.append("--windowed")   # niente finestra nera del terminale
    return args


def runtime_distributions() -> list:
    """Pacchetti Python che finiscono nell'exe: quelli del programma e, a cascata, le loro dipendenze."""
    import importlib.metadata as metadata
    from packaging.requirements import Requirement

    found, todo = {}, list(RUNTIME_PACKAGES)
    while todo:
        try:
            dist = metadata.distribution(todo.pop())
        except metadata.PackageNotFoundError:
            continue
        key = dist.metadata["Name"].lower()
        if key in found:
            continue
        found[key] = dist
        for requirement in dist.requires or []:
            req = Requirement(requirement)
            if req.marker is None or req.marker.evaluate({"extra": ""}):
                todo.append(req.name)
    return sorted(found.values(), key=lambda d: d.metadata["Name"].lower())


def licence_name(dist) -> str:
    """Licenza dichiarata da un pacchetto installato (espressione SPDX, campo License o classificatori)."""
    meta = dist.metadata
    licence = meta.get("License-Expression") or " ".join((meta.get("License") or "").split())
    if not licence or len(licence) > 80:
        licence = "; ".join(c.split("::")[-1].strip() for c in meta.get_all("Classifier", [])
                            if c.startswith("License")) or "see THIRD_PARTY_LICENSES.txt"
    return licence


def write_third_party_notices(path: Path = NOTICES) -> None:
    """Raccoglie licenze e copyright di tutti i componenti di terze parti inclusi nell'exe.
    Le licenze MIT, BSD e Apache chiedono di allegarli a ogni copia distribuita."""
    def section(title: str, licence: str, *texts: str) -> str:
        body = "\n\n".join(t.strip() for t in texts if t and t.strip())
        return f"{'=' * 78}\n{title}\nLicense: {licence}\n{'=' * 78}\n\n{body}\n"

    parts = ["PhotoExplorer - third-party software notices\n\n"
             "The PhotoExplorer executable includes the following third-party components. Each one is\n"
             "distributed under its own license, reproduced below. PhotoExplorer itself is licensed under\n"
             "the GNU GPL version 3 with additional terms (see LICENSE and ADDITIONAL_TERMS.txt); its source\n"
             "code is available at https://github.com/tingon11/PhotoExplorer\n"]
    apache_text = ""
    for dist in runtime_distributions():
        meta = dist.metadata
        licence = licence_name(dist)
        texts = []
        for file in dist.files or []:
            if ".dist-info" in str(file) and any(k in file.name.upper() for k in ("LICENSE", "COPYING", "NOTICE")):
                text = Path(dist.locate_file(file)).read_text(encoding="utf-8", errors="replace")
                texts.append(text)
                if file.name.upper() == "LICENSE.APACHE":
                    apache_text = text
        parts.append(section(f"{meta['Name']} {dist.version}", licence, *texts))

    base = Path(sys.base_prefix)
    parts.append(section(f"Python {sys.version.split()[0]} (interpreter and standard library, includes OpenSSL, "
                         "libffi and other components listed below)", "PSF License",
                         (base / "LICENSE.txt").read_text(encoding="utf-8", errors="replace")))
    tk_terms = base / "tcl" / "tk8.6" / "license.terms"
    if tk_terms.exists():
        parts.append(section("Tcl/Tk 8.6 (user interface toolkit; Tcl and Tk share these terms)", "Tcl/Tk License",
                             tk_terms.read_text(encoding="utf-8", errors="replace")))
    parts.append(section("Roboto font (bundled with customtkinter), Copyright Google", "Apache License 2.0",
                         apache_text))
    parts.append(section("libheif and libde265 (bundled in pillow-heif, HEIC support)",
                         "GNU LGPL version 3 - source code: see the pillow_heif section above (LICENSES_bundled.txt)",
                         (ROOT / "licenses" / "LGPL-3.0.txt").read_text(encoding="utf-8")))
    parts.append(section("x265 (bundled in pillow-heif)",
                         "GNU GPL version 2 or later, distributed here under GPL version 3 (see LICENSE) - "
                         "source code: see the pillow_heif section above (LICENSES_bundled.txt)"))
    parts.append(section("Panchang typeface, Indian Type Foundry (Fontshare)",
                         "ITF Free Font License - used only to draw the program logo and icon (tools/make_logo.py); "
                         "the font files are not included"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


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


def write_version_file() -> None:
    numbers = tuple(([int(n) for n in __version__.split(".") if n.isdigit()] + [0, 0, 0, 0])[:4])
    VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    VERSION_FILE.write_text(VERSION_INFO.format(
        numbers=numbers, author=__author__, description=f"{NAME} - photo viewer for NAS and local folders",
        version=__version__, name=NAME, copyright=f"Copyright (C) 2026 {__author__}", exe=f"{NAME}.exe"),
        encoding="utf-8")


def changelog_section() -> tuple[str, str]:
    """Introduzione e novità della versione corrente da CHANGELOG.md (sezione «## <versione>»)."""
    if not CHANGELOG.is_file():
        sys.exit(f"Manca {CHANGELOG.name}: scrivi la sezione «## {__version__}» con le novità.")
    text = CHANGELOG.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(__version__)}\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if match is None:
        sys.exit(f"{CHANGELOG.name} non ha la sezione «## {__version__}».")
    lines = [line.rstrip() for line in match.group(1).strip().splitlines()]
    first = next((n for n, line in enumerate(lines) if line.startswith(("- ", "* ", "### "))), len(lines))
    intro = "\n".join(lines[:first]).strip() or f"{NAME} {__version__}."
    changes = "\n".join(lines[first:]).strip() or "- Maintenance release."
    return intro, changes


def package() -> None:
    """Zip di rilascio (exe, licenze, README) e note di rilascio con l'impronta SHA-256."""
    exe = DIST / f"{NAME}.exe"
    if not exe.is_file() or not NOTICES.is_file():
        sys.exit(f"Manca {exe} o {NOTICES.name}: esegui prima la build.")
    intro, changes = changelog_section()      # prima dello zip: se manca la sezione non si crea nulla
    ZIP.unlink(missing_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe, exe.name)
        for name in LEGAL_FILES:
            zf.write(ROOT / name, name)
        zf.write(NOTICES, NOTICES.name)
        zf.write(ROOT / "README.md", "README.md")
    sha256 = hashlib.sha256(ZIP.read_bytes()).hexdigest()
    bundled = [f"- {d.metadata['Name']} {d.version}: {licence_name(d)}" for d in runtime_distributions()]
    bundled.append(f"- Python {platform.python_version()}: PSF-2.0")
    RELEASE_NOTES_FILE.write_text(RELEASE_NOTES.format(
        intro=intro, version=__version__, changes=changes, zip=ZIP.name, exe=exe.name, sha256=sha256,
        bundled="\n".join(bundled), name=NAME, author=__author__, email=__email__, url=__url__),
        encoding="utf-8")
    print(f"\n{ZIP}  ({ZIP.stat().st_size / 1e6:.1f} MB)\n{RELEASE_NOTES_FILE}\nSHA-256 {sha256}")


def main() -> None:
    args = set(sys.argv[1:])
    unknown = args - {"--release", "--no-build"}
    if unknown:
        sys.exit(f"Opzioni sconosciute: {' '.join(sorted(unknown))}")
    if "--no-build" in args:
        if "--release" in args:
            package()
        return
    build()
    if "--release" in args:
        package()


def build() -> None:
    check_environment()
    if not (ICON.exists() and LOGO.exists()):
        sys.exit("Mancano icona o logo in assets: rigenerali con  .venv\\Scripts\\python.exe tools\\make_logo.py")

    exe = DIST / f"{NAME}.exe"
    try:
        exe.unlink(missing_ok=True)
    except PermissionError:
        sys.exit(f"{exe} è in uso: chiudi PhotoExplorer e riprova.")
    shutil.rmtree(WORK, ignore_errors=True)
    write_third_party_notices()
    write_version_file()

    import PyInstaller.__main__

    started = time.time()
    PyInstaller.__main__.run(pyinstaller_args())
    shutil.rmtree(WORK, ignore_errors=True)
    for name in LEGAL_FILES:   # da allegare all'exe se lo si distribuisce
        shutil.copy2(ROOT / name, DIST / name)

    size_mb = exe.stat().st_size / 1024 / 1024
    print(f"\nFatto in {time.time() - started:.0f} s:  {exe}  ({size_mb:.0f} MB, versione {__version__})")
    print(f"Accanto all'exe: LICENSE, ADDITIONAL_TERMS.txt e {NOTICES.name} (da allegare se lo distribuisci)")


if __name__ == "__main__":
    main()
