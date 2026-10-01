# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Apre Google Maps sul punto in cui è stata scattata la foto.

Si usa solo un normale indirizzo di Google Maps aperto nel browser dell'utente (nessuna API,
nessuna chiave, nessuna mappa scaricata dal programma). Se c'è un browser basato su Chromium
(Edge, Chrome…) la pagina viene aperta in "modalità app": una finestrella senza barre.
"""
from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import webbrowser

MAP_URL = "https://www.google.com/maps/search/?api=1&query={lat:.6f},{lon:.6f}"
# Dimensione della finestrella, in pixel a scala 100%. Larga abbastanza perché il segnaposto,
# che Google Maps mette al centro, non resti coperto dal riquadro laterale (circa 430 pixel).
WINDOW_SIZE = (1200, 700)

_CHROMIUM_EXES = ("msedge.exe", "chrome.exe", "brave.exe", "vivaldi.exe", "chromium.exe")
_CHROMIUM_WINDOW_CLASS = "Chrome_WidgetWin_1"


def format_coords(lat: float, lon: float) -> str:
    return f"{abs(lat):.5f}° {'N' if lat >= 0 else 'S'},  {abs(lon):.5f}° {'E' if lon >= 0 else 'O'}"


def map_url(lat: float, lon: float) -> str:
    return MAP_URL.format(lat=lat, lon=lon)


# --- ricerca del browser ------------------------------------------------------
def _registry_value(root, key: str, name: str = "") -> str | None:
    import winreg
    try:
        with winreg.OpenKey(root, key) as handle:
            return str(winreg.QueryValueEx(handle, name)[0])
    except OSError:
        return None


def _default_browser_exe() -> str | None:
    import winreg
    prog_id = _registry_value(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice",
                              "ProgId")
    command = _registry_value(winreg.HKEY_CLASSES_ROOT, rf"{prog_id}\shell\open\command") if prog_id else None
    if not command:
        return None
    exe = command.split('"')[1] if command.startswith('"') else command.split(" ")[0]
    return exe if os.path.isfile(exe) else None


def _installed_exe(name: str) -> str | None:
    import winreg
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        exe = _registry_value(root, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{name}")
        if exe and os.path.isfile(exe):
            return exe
    return None


def chromium_browser() -> str | None:
    """Browser che sa aprire una finestra senza barre: quello predefinito se è basato su
    Chromium, altrimenti Edge o Chrome se sono installati. None se non ce n'è nessuno."""
    if sys.platform != "win32":
        return None
    default = _default_browser_exe()
    if default and os.path.basename(default).lower() in _CHROMIUM_EXES:
        return default
    for name in _CHROMIUM_EXES:
        exe = _installed_exe(name)
        if exe:
            return exe
    return None


# --- finestre del browser -------------------------------------------------------
def _browser_windows() -> dict[int, str]:
    """Finestre visibili dei browser Chromium: {handle: titolo}."""
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    found: dict[int, str] = {}

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visit(hwnd, _lparam):
        if user32.IsWindowVisible(hwnd):
            cls = ctypes.create_unicode_buffer(64)
            user32.GetClassNameW(hwnd, cls, 64)
            if cls.value == _CHROMIUM_WINDOW_CLASS:
                title = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, title, 256)
                found[hwnd] = title.value
        return True

    user32.EnumWindows(visit, 0)
    return found


def find_map_window(before: set[int]) -> int | None:
    """La finestra della mappa appena aperta: una finestra del browser che prima non c'era e
    il cui titolo parla di Google Maps (o è ancora l'indirizzo in caricamento)."""
    for hwnd, title in _browser_windows().items():
        if hwnd not in before and "maps" in title.lower():   # non una qualsiasi finestra "… - Google Chrome"
            return hwnd
    return None


def place_window(hwnd: int, x: int, y: int, width: int, height: int) -> None:
    """Sposta e ridimensiona la finestra della mappa (il browser, se è già aperto, ignora le
    dimensioni chieste all'avvio)."""
    user32 = ctypes.windll.user32
    user32.ShowWindow(hwnd, 9)                                   # se era ingrandita, torna normale
    user32.SetWindowPos(hwnd, 0, x, y, width, height, 0x0004)    # senza cambiare l'ordine delle finestre
    user32.SetForegroundWindow(hwnd)


def open_google_maps(lat: float, lon: float, x: int, y: int, width: int, height: int) -> set[int] | None:
    """Apre Google Maps sul punto indicato.

    Con un browser Chromium apre una finestrella senza barre e restituisce l'insieme delle
    finestre del browser che c'erano prima (serve a ``find_map_window`` per riconoscere quella
    nuova). Altrimenti apre una normale scheda del browser predefinito e restituisce None."""
    url = map_url(lat, lon)
    browser = chromium_browser()
    if browser is None:
        webbrowser.open(url)
        return None
    before = set(_browser_windows())
    frozen_dir = getattr(sys, "_MEIPASS", None)
    kernel32 = ctypes.windll.kernel32
    if frozen_dir:   # nell'exe: il browser non deve ereditare la cartella delle DLL del programma
        kernel32.SetDllDirectoryW(None)
    try:
        subprocess.Popen([browser, f"--app={url}", f"--window-size={width},{height}",
                          f"--window-position={x},{y}"],
                         close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
    except OSError:
        webbrowser.open(url)
        return None
    finally:
        if frozen_dir:
            kernel32.SetDllDirectoryW(frozen_dir)
    return before
