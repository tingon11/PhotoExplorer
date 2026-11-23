# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Primo avvio: scelta della lingua e avvertenze da accettare prima di usare il programma."""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from .i18n import LANGUAGES, system_language, tr
from .icons import app_icon_path, logo_label

# Se il testo delle avvertenze cambia in modo sostanziale, aumentare il numero: verranno
# mostrate di nuovo a tutti, anche a chi le aveva già accettate.
DISCLAIMER_VERSION = "2"


def disclaimer_text() -> str:
    return tr("PhotoExplorer è un programma gratuito, sviluppato per uso personale e condiviso così com'è.\n\n"
              "•  È fornito SENZA ALCUNA GARANZIA, espressa o implicita, come previsto dalla licenza GNU GPL "
              "versione 3 (articoli 15 e 16).\n"
              "•  Il programma modifica e cancella file: la rotazione riscrive le foto e l'eliminazione le "
              "rimuove, dal NAS in modo definitivo. Fai sempre una copia di sicurezza delle foto a cui tieni.\n"
              "•  Nei limiti massimi consentiti dalla legge, l'autore non risponde di perdite o danni a dati, foto, "
              "dispositivi o sistemi, né di qualsiasi altro danno, diretto o indiretto, derivante dall'uso o "
              "dall'impossibilità di usare il programma.\n"
              "•  Non è un software forense: non garantisce l'integrità di dati e metadati e non va usato per "
              "acquisire, analizzare o conservare prove.\n"
              "•  Chi lo usa è il solo responsabile del rispetto delle leggi, della privacy e dei diritti sulle "
              "foto che gestisce.")


class _Modal(ctk.CTkToplevel):
    def __init__(self, master, title: str) -> None:
        super().__init__(master)
        self.title(title)
        if app_icon_path():
            self.iconbitmap(app_icon_path())
        self.resizable(False, False)
        self.transient(master)
        self.after(150, self._focus)

    def _focus(self) -> None:
        self.lift()
        self.focus_force()
        try:
            self.grab_set()
        except Exception:
            pass


class LanguageDialog(_Modal):
    """Scelta della lingua: è la prima cosa che si vede, quindi i testi sono in tutte le lingue."""

    def __init__(self, master, on_choose: Callable[[str], None]) -> None:
        super().__init__(master, "PhotoExplorer")
        self._on_choose = on_choose
        suggested = system_language()

        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=16, pady=16)
        logo_label(frm, 20, 22).pack(padx=30, pady=(22, 8))
        ctk.CTkLabel(frm, justify="center", text_color="gray70",
                     text="Scegli la lingua  ·  Choose your language  ·  Elige el idioma\n"
                          "Sprache wählen  ·  Choisissez la langue").pack(padx=30, pady=(0, 14))
        for code, name in LANGUAGES.items():
            highlight = code == suggested
            ctk.CTkButton(frm, text=name, width=240, height=38, font=ctk.CTkFont(size=15, weight="bold"),
                          fg_color=None if highlight else "gray30", hover_color=None if highlight else "gray25",
                          command=lambda c=code: self._choose(c)).pack(padx=30, pady=4)
        ctk.CTkLabel(frm, text="").pack(pady=4)
        # chiudere la finestra senza scegliere = lingua del sistema
        self.protocol("WM_DELETE_WINDOW", lambda: self._choose(suggested))

    def _choose(self, code: str) -> None:
        self.destroy()
        self._on_choose(code)


class DisclaimerDialog(_Modal):
    """Avvertenze e limitazione di responsabilità. Al primo avvio vanno accettate per proseguire;
    dalla finestra "Informazioni" si possono rileggere (solo il pulsante Chiudi)."""

    def __init__(self, master, on_accept: Callable[[], None] | None = None,
                 on_decline: Callable[[], None] | None = None) -> None:
        super().__init__(master, tr("Avvertenze"))
        self._on_accept, self._on_decline = on_accept, on_decline
        must_accept = on_accept is not None

        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(frm, text=tr("Avvertenze e limitazione di responsabilità"),
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=16, pady=(14, 8))
        ctk.CTkLabel(frm, text=disclaimer_text(), justify="left", wraplength=600, anchor="w").pack(
            anchor="w", padx=16)

        btns = ctk.CTkFrame(frm, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(16, 14))
        if must_accept:
            ctk.CTkLabel(frm, text=tr("Proseguendo dichiari di aver letto e accettato queste condizioni."),
                         text_color="gray70").pack(anchor="w", padx=16, before=btns)
            ctk.CTkButton(btns, text=tr("Accetto"), width=140, command=self._accept).pack(side="right")
            ctk.CTkButton(btns, text=tr("Non accetto ed esco"), width=170, fg_color="gray30",
                          hover_color="gray25", command=self._decline).pack(side="right", padx=(0, 8))
            self.protocol("WM_DELETE_WINDOW", self._decline)   # chiudere = non accettare
        else:
            ctk.CTkButton(btns, text=tr("Chiudi"), width=120, command=self.destroy).pack(side="right")
            self.bind("<Escape>", lambda _e: self.destroy())

    def _accept(self) -> None:
        self.destroy()
        if self._on_accept:
            self._on_accept()

    def _decline(self) -> None:
        self.destroy()
        if self._on_decline:
            self._on_decline()
