# PhotoExplorer

**English** · [Italiano](README.it.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md)

A photo viewer for NAS devices (QNAP and similar, over SMB) and for folders on a PC, hard disks
and USB sticks, with a dark customtkinter interface.
Built for going through large photo archives: it remembers which photos you have already viewed
and lets you rotate them, delete them and copy them to a local folder for printing.

**Author: Andrea Cumini — [www.osintinfo.net](https://www.osintinfo.net) — andrea@osintinfo.net**

> **Note.** PhotoExplorer is not forensic software. I developed it for my own use, to manage my
> private photos, and decided to share it. It modifies files (rotation rewrites the photo,
> deletion removes it) and does not guarantee the integrity of data or metadata: do not use it
> to acquire, analyze or preserve evidence.

## Features

- Connects to an SMB shared folder (user and password; the password can be remembered in the
  Windows Credential Manager).
- Alternatively, browses photos in a folder on the PC, an external hard disk or a USB stick.
- Lists the photos of the selected folder and of all its subfolders.
- Remembers the photos already viewed, with a "Skip photos already viewed" option (for local
  disks the memory is tied to the disk, not to the drive letter).
- Rotation is saved to the file (EXIF data is preserved).
- Deletion with double confirmation (on local disks the file goes to the Recycle Bin).
- Copies photos to the print folder (the original is never moved), optionally stamping the
  capture date in red in the bottom-right corner.
- Shows the capture date and GPS position from the EXIF data; one click opens the location in
  Google Maps in the browser.
- Favorite photos: flag them with a button (or the F key) and view only those. Photos sent to
  print become favorites automatically and are marked with an icon in the list.
- Interface in Italian, English, Spanish, German and French, selectable from the top bar.
- Full data reset (viewed photos, favorites, print records) with confirmation.
- Zoom with the mouse wheel and pan by dragging.
- Formats: JPG, PNG, WEBP, TIFF, BMP, GIF and HEIC (with `pillow-heif`).

## Keys

| Key | Action |
|---|---|
| P / L | next / previous photo |
| W / Q | rotate right / left |
| D, then C | delete (D arms, C confirms; Esc cancels) |
| H | copy the photo to the print folder |
| F | add the photo to, or remove it from, the favorites |
| Wheel / drag | zoom / move the enlarged photo |

Every command also has its own button in the interface.

## Installation

Requires Python 3.11 or later on Windows.

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

To build a single executable (`dist\PhotoExplorer.exe`) with PyInstaller:

```
.venv\Scripts\python.exe build.py
```

Settings and the memory of viewed photos are stored in `%APPDATA%\PhotoExplorer`.

## Translations

In the code, texts are written in Italian inside `tr("…")`; the other languages are in
`photoexplorer/translations.py`. To check that nothing is missing after a change:

```
.venv\Scripts\python.exe tests\test_translations.py
```

To add a language, add its code to `LANGUAGES` (`photoexplorer/i18n.py`) and its translations to
`translations.py`.

## License and attribution

Copyright (C) 2026 Andrea Cumini. Free software released under the
[GNU GPL version 3](LICENSE), with the [additional terms](ADDITIONAL_TERMS.txt) allowed by
section 7(b) of the license. No warranty.

In practice: you may use, copy, modify and redistribute it, but every copy and every derivative
work must

- remain under GPLv3, with the source code available;
- keep the attribution **Andrea Cumini — https://www.osintinfo.net — andrea@osintinfo.net**
  clearly visible, in the source files and in the program's interface;
- clearly state that it is a modified version.

## Third-party libraries

The source uses, without including them, these libraries (each under its own license):
customtkinter (MIT), Pillow (MIT-CMU), smbprotocol and pyspnego (MIT), keyring (MIT),
pillow-heif (BSD-3-Clause).

The binary packages of `pillow-heif` bundle libheif and libde265 (LGPLv3) and x265 (GPLv2 or
later), all compatible with this program's GPLv3. Anyone distributing the executable must
therefore distribute it under GPLv3 and make the source code available.

The GPS position is opened through an ordinary Google Maps address in the user's browser: the
program does not download or embed maps.
