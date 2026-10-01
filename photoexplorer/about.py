# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Finestra "Informazioni": gli avvisi legali del programma (Appropriate Legal Notices della GPL).

L'attribuzione all'autore mostrata qui e sotto il titolo della finestra principale deve essere
conservata nelle versioni modificate: vedi ADDITIONAL_TERMS.txt.
"""
from __future__ import annotations

import webbrowser
from typing import Callable

import customtkinter as ctk

from . import __author__, __email__, __url__, __version__
from .i18n import tr
from .icons import app_icon_path, resource_path

COPYRIGHT = f"Copyright © 2026 {__author__}"
LICENSE_URL = "https://www.gnu.org/licenses/gpl-3.0.html"


def _summary() -> str:
    """Riassunto della licenza nella lingua corrente (per questo non è una costante)."""
    return tr("Questo programma è software libero: puoi usarlo, ridistribuirlo e modificarlo "
              "secondo i termini della GNU General Public License versione 3. È distribuito "
              "SENZA ALCUNA GARANZIA.\n\nOgni copia e ogni opera derivata deve restare sotto la "
              "stessa licenza e conservare in modo ben visibile l'attribuzione all'autore "
              "(termini aggiuntivi, GPLv3 art. 7(b)).")


def _license_text() -> str:
    parts = []
    for name in ("ADDITIONAL_TERMS.txt", "LICENSE"):
        try:
            parts.append(resource_path(name).read_text(encoding="utf-8"))
        except OSError:
            pass
    if not parts:
        return tr("Il testo della licenza non è stato trovato accanto al "
                  "programma.\nPuoi leggerlo qui: {license_url}", license_url=LICENSE_URL)
    return ("\n\n" + "=" * 80 + "\n\n").join(parts)


class AboutDialog(ctk.CTkToplevel):
    def __init__(self, master) -> None:
        super().__init__(master)
        self.title(tr("Informazioni su PhotoExplorer"))
        if app_icon_path():
            self.iconbitmap(app_icon_path())
        self.resizable(False, False)
        self.transient(master)

        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frm, text=f"PhotoExplorer  {__version__}", font=ctk.CTkFont(size=20, weight="bold")).pack(
            anchor="w", padx=14, pady=(12, 0))
        ctk.CTkLabel(frm, text=COPYRIGHT, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=14)

        links = ctk.CTkFrame(frm, fg_color="transparent")
        links.pack(anchor="w", padx=14, pady=(2, 8))
        site = ctk.CTkLabel(links, text=__url__.split("//")[-1], text_color="#5aa9e6", cursor="hand2")
        site.pack(side="left")
        site.bind("<Button-1>", lambda _e: webbrowser.open(__url__))
        ctk.CTkLabel(links, text=f"   ·   {__email__}", text_color="gray75").pack(side="left")

        ctk.CTkLabel(frm, text=_summary(), wraplength=560, justify="left").pack(anchor="w", padx=14, pady=(0, 8))

        box = ctk.CTkTextbox(frm, width=590, height=250, font=ctk.CTkFont(family="Consolas", size=11), wrap="none")
        box.pack(padx=14, pady=(4, 8))
        box.insert("1.0", _license_text())
        box.configure(state="disabled")

        ctk.CTkButton(frm, text=tr("Chiudi"), width=120, command=self.destroy).pack(anchor="e", padx=14, pady=(0, 12))

        self.bind("<Escape>", lambda _e: self.destroy())
        self.after(150, self._focus)

    def _focus(self) -> None:
        self.lift()
        self.focus_force()


class ResetDialog(ctk.CTkToplevel):
    """Conferma dell'azzeramento completo dei dati del programma."""

    def __init__(self, master, on_confirm: Callable[[bool], None]) -> None:
        super().__init__(master)
        self.title(tr("Azzera tutti i dati"))
        if app_icon_path():
            self.iconbitmap(app_icon_path())
        self.resizable(False, False)
        self.transient(master)
        self._on_confirm = on_confirm

        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(frm, text=tr("Azzerare tutti i dati di PhotoExplorer?"),
                     font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w", padx=14, pady=(12, 6))
        ctk.CTkLabel(frm, justify="left", wraplength=470, text=(
            tr("Verranno cancellati definitivamente:\n   •  l'elenco delle foto già "
               "viste\n   •  le foto preferite\n   •  l'elenco delle foto mandate in "
               "stampa\n\nLe foto e le copie nella cartella stampa non vengono toccate."))).pack(anchor="w", padx=14)
        self.also_settings = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(frm, variable=self.also_settings, checkbox_width=20, checkbox_height=20,
                        text=tr("Azzera anche le impostazioni e i dati di "
                                "connessione\n(indirizzo del NAS, utente, password "
                                "salvata, cartelle)")).pack(
            anchor="w", padx=14, pady=(14, 6))

        btns = ctk.CTkFrame(frm, fg_color="transparent")
        btns.pack(fill="x", padx=14, pady=(10, 12))
        ctk.CTkButton(btns, text=tr("Azzera tutto"), width=130, fg_color="#d64545", hover_color="#b33a3a",
                      command=self._confirm).pack(side="right")
        ctk.CTkButton(btns, text=tr("Annulla"), width=110, fg_color="gray30", hover_color="gray25",
                      command=self.destroy).pack(side="right", padx=(0, 8))

        self.bind("<Escape>", lambda _e: self.destroy())
        self.after(150, self._focus)

    def _focus(self) -> None:
        self.lift()
        self.focus_force()
        try:
            self.grab_set()
        except Exception:
            pass

    def _confirm(self) -> None:
        also_settings = bool(self.also_settings.get())
        self.destroy()
        self._on_confirm(also_settings)
