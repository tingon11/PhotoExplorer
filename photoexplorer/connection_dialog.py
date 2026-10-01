# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Finestra di connessione al NAS."""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from .i18n import tr
from .icons import app_icon_path
from .smb import SmbConfig, normalize
from .storage import Settings

try:
    import keyring
except ImportError:  # keyring è facoltativo
    keyring = None

KEYRING_SERVICE = "PhotoExplorer-SMB"


def _keyring_user(server: str, username: str) -> str:
    return f"{username}@{server}".lower()


def load_saved_password(server: str, username: str) -> str | None:
    if keyring is None or not server or not username:
        return None
    try:
        return keyring.get_password(KEYRING_SERVICE, _keyring_user(server, username))
    except Exception:
        return None


def store_password(server: str, username: str, password: str | None) -> None:
    if keyring is None or not server or not username:
        return
    try:
        if password:
            keyring.set_password(KEYRING_SERVICE, _keyring_user(server, username), password)
        else:
            keyring.delete_password(KEYRING_SERVICE, _keyring_user(server, username))
    except Exception:
        pass


def parse_unc(text: str) -> tuple[str, str, str] | None:
    """'\\\\nas\\Foto\\2024' o 'smb://nas/Foto/2024' -> (server, share, cartella)."""
    t = text.strip()
    if t.lower().startswith("smb://"):
        t = t[6:]
    t = t.replace("/", "\\").strip("\\")
    parts = [p for p in t.split("\\") if p]
    if len(parts) < 2:
        return None
    return parts[0], parts[1], "\\".join(parts[2:])


class ConnectionDialog(ctk.CTkToplevel):
    def __init__(self, master, settings: Settings,
                 on_connect: Callable[[SmbConfig, str, bool], None],
                 on_local: Callable[[], None] | None = None) -> None:
        super().__init__(master)
        self._on_local = on_local
        self.title(tr("Connessione al NAS"))
        if app_icon_path():
            self.iconbitmap(app_icon_path())
        self.resizable(False, False)
        self.transient(master)
        self._on_connect = on_connect

        frm = ctk.CTkFrame(self)
        frm.pack(fill="both", expand=True, padx=16, pady=16)
        frm.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frm, text=tr("Connessione alla cartella condivisa (SMB)"),
                     font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 4))
        ctk.CTkLabel(frm, text=tr("Puoi anche incollare un percorso completo nel campo "
                                  "Server,\nes. \\\\192.168.1.10\\Multimedia\\Foto"),
                     text_color="gray60", justify="left").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10))

        self.e_server = self._row(frm, 2, tr("Server (IP o nome)"), settings.server, tr("es. 192.168.1.10 o mionas.myqnapcloud.com"))
        self.e_port = self._row(frm, 3, tr("Porta"), str(settings.port or 445))
        self.e_share = self._row(frm, 4, tr("Cartella condivisa"), settings.share, tr("es. Multimedia"))
        self.e_folder = self._row(frm, 5, tr("Sottocartella iniziale"), settings.start_folder, tr("facoltativa, es. Foto\\2024"))
        self.e_user = self._row(frm, 6, tr("Utente"), settings.username)
        self.e_pass = self._row(frm, 7, tr("Password"), "", show="•")
        self.e_domain = self._row(frm, 8, tr("Dominio"), settings.domain, tr("di solito vuoto"))

        saved = load_saved_password(settings.server, settings.username) if settings.remember_password else None
        if saved:
            self.e_pass.insert(0, saved)

        self.remember = ctk.BooleanVar(value=settings.remember_password and keyring is not None)
        cb = ctk.CTkCheckBox(frm, text=tr("Ricorda la password (Gestione credenziali di Windows)"),
                             variable=self.remember)
        cb.grid(row=9, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 4))
        if keyring is None:
            cb.configure(state="disabled")

        self.error_label = ctk.CTkLabel(frm, text="", text_color="#ff6b6b", wraplength=420, justify="left")
        self.error_label.grid(row=10, column=0, columnspan=2, sticky="w", padx=12)

        btns = ctk.CTkFrame(frm, fg_color="transparent")
        btns.grid(row=11, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 12))
        if on_local is not None:   # in alternativa al NAS: foto su PC, hard disk o chiavetta
            ctk.CTkButton(btns, text=tr("Cartella sul PC / USB…"), width=170, fg_color="gray30", hover_color="gray25",
                          command=self._choose_local).pack(side="left")
        self.btn_ok = ctk.CTkButton(btns, text=tr("Connetti"), width=130, command=self._submit)
        self.btn_ok.pack(side="right")
        ctk.CTkButton(btns, text=tr("Annulla"), width=110, fg_color="gray30", hover_color="gray25",
                      command=self.destroy).pack(side="right", padx=(0, 8))

        self.bind("<Return>", lambda _e: self._submit())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # su Windows il CTkToplevel va portato davanti dopo che è stato disegnato
        self.after(150, self._focus)

    def _choose_local(self) -> None:
        on_local = self._on_local
        self.destroy()          # il dialogo è modale: va chiuso prima di aprire la scelta della cartella
        if on_local is not None:
            on_local()

    def _focus(self) -> None:
        self.lift()
        self.focus_force()
        try:
            self.grab_set()
        except Exception:
            pass
        first_empty = next((e for e in (self.e_server, self.e_share, self.e_user, self.e_pass) if not e.get()),
                           self.e_pass)
        first_empty.focus_set()

    @staticmethod
    def _row(frm, row: int, label: str, value: str = "", placeholder: str = "", show: str = "") -> ctk.CTkEntry:
        ctk.CTkLabel(frm, text=label, anchor="w").grid(row=row, column=0, sticky="w", padx=(12, 10), pady=4)
        entry = ctk.CTkEntry(frm, width=300, placeholder_text=placeholder or None, show=show or None)
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 12), pady=4)
        if value:
            entry.insert(0, value)
        return entry

    def set_busy(self, busy: bool, error: str = "") -> None:
        if not self.winfo_exists():
            return
        self.btn_ok.configure(state="disabled" if busy else "normal",
                              text=tr("Connessione…") if busy else tr("Connetti"))
        self.error_label.configure(text=error)

    def _submit(self) -> None:
        if self.btn_ok.cget("state") == "disabled":   # connessione già in corso
            return
        server = self.e_server.get().strip()
        share = self.e_share.get().strip().strip("\\/")
        folder = self.e_folder.get()
        parsed = parse_unc(server) if ("\\" in server or "/" in server) else None
        if parsed:
            server, share, sub = parsed
            folder = sub or folder
        try:
            port = int(self.e_port.get().strip() or 445)
        except ValueError:
            self.set_busy(False, tr("La porta deve essere un numero (di solito 445)."))
            return
        if not server or not share:
            self.set_busy(False, tr("Inserisci almeno il server e la cartella condivisa."))
            return

        cfg = SmbConfig(server=server, share=share, username=self.e_user.get().strip(),
                        password=self.e_pass.get(), port=port, domain=self.e_domain.get().strip())
        self.set_busy(True)
        self._on_connect(cfg, normalize(folder), bool(self.remember.get()))
