# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Finestra principale di PhotoExplorer."""
from __future__ import annotations

import gc
import os
import re
import shutil
import threading
import time
import tkinter as tk
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import ImageTk

from . import __author__, __url__
from .about import AboutDialog, ResetDialog
from .connection_dialog import ConnectionDialog, load_saved_password, store_password
from .i18n import LANGUAGES, get_language, set_language, tr, weekday_name
from .icons import app_icon_path, icon
from .mapview import WINDOW_SIZE, find_map_window, format_coords, open_google_maps, place_window
from .local import LocalBrowser
from .imaging import (LoadedImage, RotationNotSupported, View, decode_for_display, decode_full, format_stamp,
                      read_meta_from_bytes, render_image_bytes, render_view, rotate_cw, rotate_image_bytes,
                      stamp_date)
from .smb import RemoteFile, SmbBrowser, SmbConfig, describe_error, join, normalize, parent
from .storage import APP_DIR, History, Settings, default_print_dir, folder_key
from .worker import HIGH, LOW, Worker

# --- colori -----------------------------------------------------------------
BG_VIEWER = "#141414"
BG_INFO = "#1c1c1c"
LIST_BG = "#232323"
LIST_FG = "#e6e6e6"
LIST_FG_VIEWED = "#7d7d7d"
LIST_SEL = "#1f6aa5"
GREEN = "#2fa36b"
RED = "#d64545"
RED_DARK = "#8a2c2c"
RED_HOVER = "#b33a3a"
GOLD = "#f5c518"
GRAY_BTN = "#3a3a3a"
GRAY_HOVER = "#4a4a4a"
STATUS_COLORS = {"info": "#c8c8c8", "ok": "#5fd08f", "warn": "#f0b85a", "error": "#ff6b6b"}

ROTATION_SAVE_DELAY_MS = 1200
CACHE_SIZE = 10
PREFETCH_AHEAD = 3
ZOOM_STEP = 1.25        # ingrandimento per ogni scatto della rotella
DRAG_THRESHOLD = 5      # pixel di movimento oltre i quali un clic diventa un trascinamento


def natural_key(name: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name.casefold())]


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


def print_copy_path(dest_dir: Path, name: str, source_folder: str) -> Path:
    """Nome libero per una nuova copia nella cartella stampa. Se il nome originale è già
    occupato (da un'altra foto con lo stesso nome) si aggiunge la cartella di provenienza,
    es. "IMG_0001 (Estate).JPG", e se serve un numero: non si sovrascrive mai un file esistente."""
    path = dest_dir / name
    if not path.exists():
        return path
    tag = f" ({source_folder})" if source_folder else ""
    candidate = dest_dir / f"{path.stem}{tag}{path.suffix}"
    if tag and not candidate.exists():
        return candidate
    for i in range(2, 10_000):
        candidate = dest_dir / f"{path.stem}{tag} {i}{path.suffix}"
        if not candidate.exists():
            return candidate
    raise OSError(tr("Troppi file con lo stesso nome nella cartella di stampa"))


class ImageCache:
    """Cache LRU delle foto decodificate. Il campo ``raw`` è letto/aggiornato anche
    dal thread di rete, quindi passa sempre dal lock."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._items: OrderedDict[str, LoadedImage] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> LoadedImage | None:
        with self._lock:
            item = self._items.get(key)
            if item is not None:
                self._items.move_to_end(key)
            return item

    def put(self, key: str, item: LoadedImage) -> None:
        with self._lock:
            if key in self._items:
                return
            self._items[key] = item
            while len(self._items) > self.capacity:
                self._items.popitem(last=False)

    def pop(self, key: str) -> None:
        with self._lock:
            self._items.pop(key, None)

    def get_raw(self, key: str) -> bytes | None:
        with self._lock:
            item = self._items.get(key)
            return item.raw if item else None

    def set_raw(self, key: str, raw: bytes) -> None:
        with self._lock:
            item = self._items.get(key)
            if item:
                item.raw = raw

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


class PhotoExplorerApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        # Gli oggetti Tk (font, immagini, variabili) vanno distrutti solo nel thread della GUI:
        # se il garbage collector partisse nel thread di rete, Tk resterebbe bloccato.
        # Per questo la raccolta automatica è disattivata e viene eseguita qui periodicamente.
        gc.disable()
        self._gc_job = self.after(2000, self._collect_garbage)
        self.settings = Settings.load()
        set_language(self.settings.language)   # vuota = lingua del sistema
        self.history = History()
        self.worker = Worker()
        self.decoder = Worker()        # decodifica a piena risoluzione per lo zoom, senza occupare il thread di rete
        self.cache = ImageCache(CACHE_SIZE)

        self.source: SmbBrowser | LocalBrowser | None = None   # NAS oppure cartella locale
        self.session = 0               # cambia a ogni nuova connessione
        self.folder = ""               # cartella corrente, relativa alla condivisione
        self.dirs: list[str] = []
        self.photos: list[RemoteFile] = []
        self.index = -1

        # ricerca delle foto nelle sottocartelle
        self.listing = 0               # cambia a ogni apertura di cartella
        self._scanning = False
        self._scan_stack: list[str] = []
        self._scan_pending: list[RemoteFile] = []
        self._scan_dirs_read = 0
        self._scan_errors = 0
        self._flush_job = None
        self._keep_photo: str | None = None

        self.loading: set[str] = set()
        self.saving: dict[str, int] = {}
        self.deleting: set[str] = set()
        self.wanted: frozenset[str] = frozenset()   # letto dal thread di rete

        # vista della foto: zoom con la rotella e spostamento trascinando
        self.zoom = 1.0                              # 1 = foto intera adattata alla finestra
        self._view_center: tuple[float, float] | None = None
        self._view: View | None = None               # ultima vista disegnata
        self._full = None                            # (percorso, foto a piena risoluzione) della foto corrente
        self._full_requested: str | None = None
        self._src_cache = None
        self._press = None                           # trascinamento in corso sul riquadro della foto
        self._hq_job = None

        self._seen_before = False      # la foto corrente era già stata vista prima di aprirla ora?
        self.view_rotation = 0         # rotazione mostrata ma non ancora salvata (gradi orari)
        self._rotation_job = None
        self.delete_armed = False
        self._canvas_message: tuple[str, bool] | None = None
        self._photo_ref = None
        self._resize_job = None
        self._dir_targets: list[str] = []
        self._has_up_entry = False
        self._closing = False
        self.dialog: ConnectionDialog | None = None
        self.about: AboutDialog | None = None
        self.max_side = min(max(self.winfo_screenwidth(), self.winfo_screenheight()), 3200)

        self.title("PhotoExplorer")
        if app_icon_path():
            self.iconbitmap(app_icon_path())
        self.minsize(1360, 680)
        if self.settings.geometry and self.settings.geometry != "zoomed":
            self.geometry(self.settings.geometry)
        else:   # primo avvio o ultima chiusura a schermo intero: finestra massimizzata
            self.geometry("1400x880")
            self.after(50, lambda: self.state("zoomed"))

        self._build_ui()
        self._bind_keys()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._poll_job = self.after(30, self._poll_worker)
        self._autosave_job = self.after(5000, self._autosave)
        self.after(300, self._startup)

    # =====================================================================
    # Interfaccia
    # =====================================================================
    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        bold = ctk.CTkFont(size=14, weight="bold")

        # --- barra superiore ---------------------------------------------
        top = ctk.CTkFrame(self, corner_radius=0, height=52)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        title = ctk.CTkFrame(top, fg_color="transparent")
        title.pack(side="left", padx=(16, 18), pady=(6, 4))
        ctk.CTkLabel(title, text="PhotoExplorer", font=ctk.CTkFont(size=20, weight="bold"), height=24).pack(anchor="w")
        # Attribuzione dell'autore: va conservata, ben visibile, anche nelle versioni modificate
        # (termini aggiuntivi della licenza, GPLv3 art. 7(b): vedi ADDITIONAL_TERMS.txt).
        # Un clic apre la finestra "Informazioni" con copyright, licenza e assenza di garanzia.
        credit = ctk.CTkLabel(title, text=f"{__author__}  ·  {__url__.split('//')[-1]}", height=14, cursor="hand2",
                              text_color="gray60", font=ctk.CTkFont(size=11))
        credit.pack(anchor="w")
        credit.bind("<Button-1>", lambda _e: self.open_about())
        self.language_menu = ctk.CTkOptionMenu(top, values=list(LANGUAGES.values()), width=112, fg_color=GRAY_BTN,
                                               button_color=GRAY_BTN, button_hover_color=GRAY_HOVER,
                                               command=self._on_language_change)
        self.language_menu.set(LANGUAGES[get_language()])
        self.language_menu.pack(side="right", padx=(6, 16))
        ctk.CTkButton(top, text=tr("Apri cartella stampa"), image=icon("open_folder", 16), width=170,
                      fg_color=GRAY_BTN, hover_color=GRAY_HOVER,
                      command=self.open_print_folder).pack(side="right", padx=6)
        ctk.CTkButton(top, text=tr("Cartella stampa…"), image=icon("folder", 16), width=160,
                      fg_color=GRAY_BTN, hover_color=GRAY_HOVER,
                      command=self.choose_print_folder).pack(side="right", padx=6)
        ctk.CTkButton(top, text=tr("Cartella PC / USB…"), image=icon("folder", 16), width=160,
                      command=self.choose_local_folder).pack(side="right", padx=6)
        ctk.CTkButton(top, text=tr("Connetti al NAS…"), image=icon("connect", 16), width=160,
                      command=self.open_connection_dialog).pack(side="right", padx=6)
        # per ultima, così se la finestra è stretta si accorcia questa scritta e non spariscono i pulsanti
        self.conn_label = ctk.CTkLabel(top, text="")
        self.conn_label.pack(side="left")
        self._show_source_label()

        # --- barra laterale ----------------------------------------------
        side = ctk.CTkFrame(self, corner_radius=0, width=330)
        side.grid(row=1, column=0, sticky="ns")
        side.grid_propagate(False)
        side.grid_columnconfigure(0, weight=1)
        side.grid_rowconfigure(3, weight=2)
        side.grid_rowconfigure(5, weight=3)

        self.path_label = ctk.CTkLabel(side, text="—", anchor="w", justify="left", wraplength=300,
                                       text_color="gray70")
        self.path_label.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        nav = ctk.CTkFrame(side, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="ew", padx=12)
        nav.grid_columnconfigure((0, 1), weight=1)
        self.btn_up = ctk.CTkButton(nav, text=tr("Cartella superiore"), image=icon("up", 14), fg_color=GRAY_BTN,
                                    hover_color=GRAY_HOVER, command=self.go_up)
        self.btn_up.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(nav, text=tr("Aggiorna"), image=icon("refresh", 14), fg_color=GRAY_BTN, hover_color=GRAY_HOVER,
                      command=self.refresh_folder).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        ctk.CTkLabel(side, text=tr("Cartelle  (doppio clic per aprire)"), font=bold, anchor="w").grid(
            row=2, column=0, sticky="ew", padx=12, pady=(12, 2))
        self.dir_list = self._make_listbox(side, row=3)
        self.dir_list.bind("<Double-Button-1>", lambda _e: self.open_selected_dir())
        self.dir_list.bind("<Return>", lambda _e: self.open_selected_dir())

        self.photo_header = ctk.CTkLabel(side, text=tr("Foto"), font=bold, anchor="w")
        self.photo_header.grid(row=4, column=0, sticky="ew", padx=12, pady=(12, 2))
        self.photo_list = self._make_listbox(side, row=5)
        self.photo_list.bind("<<ListboxSelect>>", self._on_photo_list_select)

        opts = ctk.CTkFrame(side, fg_color="transparent")
        opts.grid(row=6, column=0, sticky="ew", padx=12, pady=(10, 12))
        opts.grid_columnconfigure(1, weight=1)
        self.recursive_var = ctk.BooleanVar(value=self.settings.include_subfolders)
        ctk.CTkSwitch(opts, text=tr("Includi le foto delle sottocartelle"), variable=self.recursive_var,
                      command=self._on_recursive_toggle).grid(row=0, column=0, columnspan=2, sticky="w")
        self.skip_var = ctk.BooleanVar(value=self.settings.skip_viewed)
        ctk.CTkSwitch(opts, text=tr("Salta le foto già viste"), variable=self.skip_var,
                      command=self._on_skip_toggle).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.fav_only_var = ctk.BooleanVar(value=False)   # all'avvio sempre spento: si vedono tutte le foto
        ctk.CTkSwitch(opts, text=tr("Mostra solo le preferite"), variable=self.fav_only_var, progress_color=GOLD,
                      command=self._on_fav_only_toggle).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ctk.CTkLabel(opts, text=tr("Ordina per")).grid(row=6, column=0, sticky="w", pady=(10, 0))
        self._sort_codes = {tr("Nome"): "name", tr("Data"): "date"}   # testo mostrato -> codice salvato
        self.sort_button = ctk.CTkSegmentedButton(opts, values=list(self._sort_codes), command=self._on_sort_change)
        self.sort_button.set(tr("Data") if self.settings.sort_by == "date" else tr("Nome"))
        self.sort_button.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=(10, 0))
        ctk.CTkButton(opts, text=tr("Segna tutta la cartella come “non vista”"), fg_color="transparent",
                      border_width=1, border_color=GRAY_HOVER, hover_color=GRAY_BTN,
                      command=self.reset_viewed).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        data_row = ctk.CTkFrame(opts, fg_color="transparent")
        data_row.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        data_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(data_row, text=tr("Cartella dei dati"), image=icon("open_folder", 14),
                      fg_color="transparent", hover_color=GRAY_BTN, text_color="gray65", height=26,
                      command=self.open_data_folder).grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(data_row, text=tr("Azzera tutto…"), image=icon("delete", 14, "#e08a8a"),
                      fg_color="transparent", hover_color=RED_DARK, text_color="#e08a8a", height=26,
                      command=self.open_reset_dialog).grid(row=0, column=1, sticky="ew")

        # --- visualizzatore ----------------------------------------------
        viewer = ctk.CTkFrame(self, corner_radius=0, fg_color=BG_VIEWER)
        viewer.grid(row=1, column=1, sticky="nsew")
        viewer.grid_rowconfigure(1, weight=1)
        viewer.grid_columnconfigure(0, weight=1)

        info = ctk.CTkFrame(viewer, corner_radius=0, fg_color=BG_INFO, height=56)
        info.grid(row=0, column=0, sticky="ew")
        info.grid_columnconfigure(1, weight=1)
        self.name_label = ctk.CTkLabel(info, text="", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        self.name_label.grid(row=0, column=0, sticky="w", padx=(16, 10), pady=(8, 0))
        badges = ctk.CTkFrame(info, fg_color="transparent")
        badges.grid(row=0, column=1, sticky="w", pady=(8, 0))
        self.badge_seen = ctk.CTkLabel(badges, text="", corner_radius=6, height=22, font=ctk.CTkFont(size=12, weight="bold"))
        self.badge_fav = ctk.CTkLabel(badges, text=tr(" PREFERITA  "), image=icon("star_fill", 12, "#1c1c1c"),
                                      compound="left", corner_radius=6, height=22, fg_color=GOLD,
                                      text_color="#1c1c1c", font=ctk.CTkFont(size=12, weight="bold"))
        self.badge_print = ctk.CTkLabel(badges, text="", image=icon("print", 12), compound="left",
                                        corner_radius=6, height=22, fg_color="#2b5c8a",
                                        font=ctk.CTkFont(size=12, weight="bold"))
        self.counter_label = ctk.CTkLabel(info, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.counter_label.grid(row=0, column=2, rowspan=2, sticky="e", padx=16)
        meta_row = ctk.CTkFrame(info, fg_color="transparent")
        meta_row.grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 6))
        self.details_label = ctk.CTkLabel(meta_row, text="", text_color="gray60", anchor="w")
        self.details_label.pack(side="left")
        # dati EXIF: data di scatto e posizione GPS
        self.taken_label = ctk.CTkLabel(meta_row, text="", image=icon("calendar", 15), compound="left",
                                        text_color="#e6e6e6", anchor="w")
        # piccola icona accanto alla data: si vede solo se la foto ha la posizione GPS, apre la mappa
        self.gps_button = ctk.CTkButton(meta_row, text="", image=icon("pin", 15), width=30, height=24,
                                        fg_color=LIST_SEL, hover_color="#2a7fc0", command=self.open_map)

        self.canvas = tk.Canvas(viewer, bg=BG_VIEWER, highlightthickness=0, bd=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        # --- barra dei comandi -------------------------------------------
        bar = ctk.CTkFrame(self, corner_radius=0)
        bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        left_group = ctk.CTkFrame(bar, fg_color="transparent")     # modifica della foto
        left_group.pack(side="left", padx=(12, 0), pady=10)
        right_group = ctk.CTkFrame(bar, fg_color="transparent")    # Indietro · Stampa · Avanti, vicini a destra
        right_group.pack(side="right", padx=(0, 12), pady=10)
        big = ctk.CTkFont(size=14, weight="bold")

        def button(group, text, cmd, icon_name, **kw):
            b = ctk.CTkButton(group, text=text, command=cmd, height=42, width=140, font=big,
                              image=icon(icon_name, 20), **kw)
            b.pack(side="left", padx=4)
            return b

        button(left_group, tr("Ruota sx  Q"), lambda: self.rotate(-90), "rotate_left",
               fg_color=GRAY_BTN, hover_color=GRAY_HOVER)
        button(left_group, tr("Ruota dx  W"), lambda: self.rotate(90), "rotate_right",
               fg_color=GRAY_BTN, hover_color=GRAY_HOVER)
        self.btn_delete = button(left_group, tr("Elimina  D"), self.arm_delete, "delete",
                                 fg_color=RED_DARK, hover_color=RED_HOVER)
        self.btn_confirm = button(left_group, tr("Conferma  C"), self.confirm_delete, "confirm", fg_color=GRAY_BTN,
                                  hover_color=RED_HOVER, state="disabled", text_color_disabled="gray50")
        self.btn_confirm.configure(image=icon("confirm", 20, "#808080"))
        self.btn_fav = button(left_group, tr("Preferita  F"), self.toggle_favorite, "star",
                              fg_color=GRAY_BTN, hover_color=GRAY_HOVER)

        # data di scatto in rosso sulla copia per la stampa (e nell'anteprima)
        self.stamp_var = ctk.BooleanVar(value=self.settings.stamp_date)
        ctk.CTkCheckBox(right_group, text=tr("Stampa data"), variable=self.stamp_var, command=self._on_stamp_toggle,
                        font=big, fg_color=GREEN, hover_color="#258556", width=130).pack(side="left", padx=(0, 10))
        button(right_group, tr("Indietro  L"), lambda: self.navigate(-1), "prev")
        button(right_group, tr("Stampa  H"), self.send_to_print, "print", fg_color=GREEN, hover_color="#258556")
        self.btn_next = button(right_group, tr("Avanti  P"), lambda: self.navigate(1), "next", compound="right")

        # --- barra di stato ----------------------------------------------
        status = ctk.CTkFrame(self, corner_radius=0, height=30, fg_color=BG_INFO)
        status.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.status_label = ctk.CTkLabel(status, text="", anchor="w")
        self.status_label.pack(side="left", padx=12, pady=2)
        ctk.CTkLabel(status, text=tr("L / P indietro / avanti   ·   rotella: zoom, "
                                     "trascina: sposta   ·   Q / W ruota   ·   D elimina, C "
                                     "conferma   ·   F preferita   ·   H stampa   ·   Esc "
                                     "annulla"), text_color="gray55").pack(side="right", padx=12)

        self.show_message(tr("Connettiti al NAS o apri una cartella del PC per iniziare"))
        self.update_info()

    def _make_listbox(self, parent_widget, row: int) -> tk.Listbox:
        frame = ctk.CTkFrame(parent_widget, fg_color=LIST_BG, corner_radius=8)
        frame.grid(row=row, column=0, sticky="nsew", padx=12)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        lb = tk.Listbox(frame, bg=LIST_BG, fg=LIST_FG, selectbackground=LIST_SEL, selectforeground="white",
                        highlightthickness=0, borderwidth=0, activestyle="none", exportselection=False,
                        font=("Segoe UI", 10), width=1)
        lb.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=6)
        sb = ctk.CTkScrollbar(frame, command=lb.yview)
        sb.grid(row=0, column=1, sticky="ns", padx=2, pady=4)
        lb.configure(yscrollcommand=sb.set)
        return lb

    def _bind_keys(self) -> None:
        keys = {
            "p": lambda: self.navigate(1),
            "l": lambda: self.navigate(-1),
            "d": self.arm_delete,
            "c": self.confirm_delete,
            "w": lambda: self.rotate(90),
            "q": lambda: self.rotate(-90),
            "h": self.send_to_print,
            "f": self.toggle_favorite,
            "<Escape>": self.cancel_delete,
        }
        for seq, fn in keys.items():
            handler = (lambda f: (lambda _e: (f(), "break")[1]))(fn)
            self.bind(seq, handler)
            if len(seq) == 1:
                self.bind(seq.upper(), handler)  # anche con Bloc Maiusc attivo
        self.bind("<MouseWheel>", self._on_root_wheel, add="+")

    # =====================================================================
    # Utilità GUI
    # =====================================================================
    def set_status(self, text: str, kind: str = "info") -> None:
        self.status_label.configure(text=text, text_color=STATUS_COLORS.get(kind, STATUS_COLORS["info"]))

    def current_photo(self) -> RemoteFile | None:
        return self.photos[self.index] if 0 <= self.index < len(self.photos) else None

    def current_item(self) -> LoadedImage | None:
        photo = self.current_photo()
        return self.cache.get(photo.path) if photo else None

    def fkey(self) -> str:
        return folder_key(self.source.history_root if self.source else "", self.folder)

    def _poll_worker(self) -> None:
        try:
            self.worker.process_results()
            self.decoder.process_results()
        finally:
            self._poll_job = self.after(30, self._poll_worker)

    def _collect_garbage(self) -> None:
        gc.collect()
        self._gc_job = self.after(2000, self._collect_garbage)

    def _autosave(self) -> None:
        try:
            self.history.save()
        except OSError:
            pass
        self._autosave_job = self.after(5000, self._autosave)

    # =====================================================================
    # Connessione
    # =====================================================================
    def _startup(self) -> None:
        """All'avvio riapre l'ultima sorgente usata: cartella locale oppure NAS."""
        s = self.settings
        if s.last_source == "local" and s.local_root and os.path.isdir(s.local_root):
            self.open_local(s.local_root, resume=True)
            return
        if s.server and s.share and s.remember_password:
            password = load_saved_password(s.server, s.username)
            if password is not None:
                cfg = SmbConfig(s.server, s.share, s.username, password, s.port, s.domain)
                self.set_status(tr("Connessione automatica a \\\\{server}\\{share}…",
                                   server=s.server, share=s.share))
                self.connect(cfg, normalize(s.start_folder), True, auto=True)
                return
        self.open_connection_dialog()

    def open_connection_dialog(self) -> None:
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.lift()
            self.dialog.focus_force()
            return
        self.dialog = ConnectionDialog(self, self.settings, self.connect, self.choose_local_folder)

    def _show_source_label(self) -> None:
        if self.source is None:
            self.conn_label.configure(text=tr("●  Nessuna sorgente aperta"), text_color=STATUS_COLORS["error"])
            return
        if self.source.kind == "local":
            label = tr("Cartella locale  {root}", root=self.source.root)
        else:
            label = tr("Connesso a  {root}", root=self.source.root)
        if len(label) > 70:
            label = label[:30] + "…" + label[-38:]
        self.conn_label.configure(text=f"●  {label}", text_color=STATUS_COLORS["ok"])

    def _activate(self, browser) -> None:
        """Passa a una nuova sorgente di foto (NAS o cartella locale)."""
        self.cancel_delete(redraw=False)
        self.commit_rotation()
        old = self.source
        self.source = browser
        self.session += 1
        self.cache.clear()
        self.loading.clear()
        if old is not None and old.connection_key != browser.connection_key:
            self.worker.submit(old.close, priority=LOW)
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.destroy()
        self.dialog = None
        self._show_source_label()

    def connect(self, cfg: SmbConfig, start_folder: str, remember: bool, auto: bool = False) -> None:
        browser = SmbBrowser(cfg)
        s = self.settings
        folder = start_folder
        if s.last_location == cfg.location and s.last_folder.lower().startswith(start_folder.lower()):
            folder = s.last_folder

        def task():
            browser.connect()
            try:
                browser.list_dir(folder)
                return folder
            except Exception:
                if folder == start_folder:
                    raise
                browser.list_dir(start_folder)  # l'ultima cartella non esiste più
                return start_folder

        def done(opened_folder: str):
            self._activate(browser)
            s.server, s.port, s.share = cfg.server, cfg.port, cfg.share
            s.username, s.domain = cfg.username, cfg.domain
            s.start_folder, s.remember_password = start_folder, remember
            s.last_source = "smb"
            store_password(cfg.server, cfg.username, cfg.password if remember else None)
            self._save_settings()
            self.set_status(tr("Connesso."), "ok")
            self.open_folder(opened_folder)

        def error(exc: BaseException):
            msg = describe_error(exc)
            self.set_status(tr("Connessione non riuscita: {msg}", msg=msg), "error")
            if self.dialog is None or not self.dialog.winfo_exists():
                self.open_connection_dialog()
                self.after(200, lambda: self.dialog and self.dialog.set_busy(False, msg))
            else:
                self.dialog.set_busy(False, msg)

        if not auto:
            self.set_status(tr("Connessione a \\\\{server}\\{share}…", server=cfg.server, share=cfg.share))
        self.worker.submit(task, done, error, HIGH)

    # --- cartelle sul PC, su hard disk o su chiavette USB ------------------
    def choose_local_folder(self) -> None:
        start = self.settings.local_root if os.path.isdir(self.settings.local_root) else str(Path.home())
        folder = filedialog.askdirectory(parent=self, title=tr("Cartella con le foto (PC, hard disk o chiavetta USB)"),
                                         initialdir=start, mustexist=True)
        if folder:
            self.open_local(folder)

    def open_local(self, root: str, highlight_dir: str | None = None, resume: bool = False) -> None:
        browser = LocalBrowser(root)
        s = self.settings
        # all'avvio si riprende dall'ultima sottocartella in cui si era
        folder = s.last_folder if resume and s.last_location == browser.location else ""

        def task():
            browser.connect()
            try:
                browser.list_dir(folder)
                return folder
            except OSError:
                if not folder:
                    raise
                return ""

        def done(opened_folder: str):
            self._activate(browser)
            s.last_source, s.local_root = "local", browser.root
            self._save_settings()
            self.open_folder(opened_folder, highlight_dir=highlight_dir)

        def error(exc: BaseException):
            msg = describe_error(exc)
            self.set_status(tr("Impossibile aprire {root}: {msg}", root=browser.root, msg=msg), "error")
            messagebox.showerror(tr("Cartella non accessibile"), f"{browser.root}\n\n{msg}", parent=self)

        self.set_status(tr("Apertura di {root}…", root=browser.root))
        self.worker.submit(task, done, error, HIGH)

    # =====================================================================
    # Cartelle
    # =====================================================================
    def open_folder(self, rel: str, highlight_dir: str | None = None, keep_photo: str | None = None) -> None:
        """Apre una cartella. Con "Includi sottocartelle" attivo, dopo le foto della cartella
        vengono cercate (in background, una cartella alla volta) quelle di tutte le sottocartelle."""
        if self.source is None:
            self.open_connection_dialog()
            return
        self.cancel_delete(redraw=False)
        self.commit_rotation()
        browser, session = self.source, self.session
        self.listing += 1
        listing = self.listing
        self.set_status(tr("Apertura di {path}…", path=browser.unc(rel)))

        def done(result):
            if session != self.session or listing != self.listing:
                return
            dirs, files = result
            self.folder = rel
            self.dirs = sorted(dirs, key=natural_key)
            self.photos = []
            self.index = -1
            self.view_rotation = 0
            self.wanted = frozenset()
            self._keep_photo = keep_photo
            self.history.set_total(self.fkey(), len(files))
            self.settings.last_folder = rel
            self.settings.last_location = browser.location
            self._save_settings()

            self.path_label.configure(text=browser.unc(rel))
            self.btn_up.configure(state="normal" if rel or browser.parent_root() else "disabled")
            self._fill_dir_list(highlight_dir)
            self.photo_list.delete(0, "end")

            self._scan_stack = self._folders_to_scan(rel, self.dirs) if self.recursive_var.get() else []
            self._scan_pending = []
            self._scan_dirs_read = 1
            self._scan_errors = 0
            self._scanning = bool(self._scan_stack)
            self._add_photos(files)
            if self._scanning:
                if not self.photos:
                    self.show_message(tr("Cerco le foto nelle sottocartelle…"))
                self._scan_next(listing)
            else:
                self._scan_finished()

        def error(exc: BaseException):
            if session == self.session and listing == self.listing:
                self.set_status(tr("Impossibile aprire la cartella: {error}", error=describe_error(exc)), "error")

        self.worker.submit(lambda: browser.list_dir(rel), done, error, HIGH)

    # --- scansione delle sottocartelle -----------------------------------
    def _scan_next(self, listing: int) -> None:
        """Legge la prossima sottocartella (visita in profondità, nello stesso ordine dell'elenco)."""
        if listing != self.listing:
            return
        if not self._scan_stack:
            self._scan_finished()
            return
        rel = self._scan_stack.pop()
        browser, session = self.source, self.session
        share = browser.history_root

        def done(result):
            if session != self.session or listing != self.listing:
                return
            dirs, files = result
            self.history.set_total(folder_key(share, rel), len(files))
            self._scan_dirs_read += 1
            self._scan_stack.extend(self._folders_to_scan(rel, dirs))
            self._scan_pending.extend(files)
            if self._flush_job is None:
                self._flush_job = self.after(250, self._flush_scan)
            self._scan_next(listing)

        def error(_exc: BaseException):
            if session != self.session or listing != self.listing:
                return
            self._scan_errors += 1
            self._scan_next(listing)

        # priorità bassa: la foto che stai guardando viene sempre caricata prima
        self.worker.submit(lambda: browser.list_dir(rel), done, error, LOW)

    def _folders_to_scan(self, rel: str, dirs: list[str]) -> list[str]:
        """Sottocartelle da leggere, in ordine inverso (è una pila). In modalità "solo preferite"
        si saltano quelle che non ne contengono: su archivi grandi la ricerca è molto più rapida."""
        paths = [join(rel, d) for d in sorted(dirs, key=natural_key, reverse=True)]
        if self.fav_only_var.get():
            root = self.source.history_root
            paths = [path for path in paths if self.history.has_favorites_under(folder_key(root, path))]
        return paths

    def _flush_scan(self) -> None:
        self._flush_job = None
        pending, self._scan_pending = self._scan_pending, []
        self._add_photos(pending)
        if self._scanning:
            self.set_status(tr("Cerco nelle sottocartelle…  {scan_dirs_read} cartelle "
                               "lette, {count} foto trovate",
                               scan_dirs_read=self._scan_dirs_read, count=len(self.photos)))

    def _scan_finished(self) -> None:
        if self._flush_job is not None:
            self.after_cancel(self._flush_job)
            self._flush_job = None
        self._scanning = False
        pending, self._scan_pending = self._scan_pending, []
        self._add_photos(pending)
        self._update_photo_header()
        sel = self.dir_list.curselection()
        self._fill_dir_list()              # aggiorna il conteggio delle viste delle sottocartelle
        if sel:
            self.dir_list.selection_set(sel[0])
        if self.index == -1:
            self._start_viewing()
        new_count = sum(not self.is_viewed(p) for p in self.photos)
        where = tr(" in {scan_dirs_read} cartelle", scan_dirs_read=self._scan_dirs_read) if self._scan_dirs_read > 1 else ""
        errors = tr("  ({scan_errors} cartelle non leggibili)", scan_errors=self._scan_errors) if self._scan_errors else ""
        if self.fav_only_var.get():
            self.set_status(tr("{count} foto preferite.{errors}", count=len(self.photos), errors=errors), "ok" if self.photos else "info")
        elif not self.photos:
            self.set_status(tr("Nessuna foto{where}.{errors}", where=where, errors=errors), "warn" if errors else "info")
        elif new_count:
            self.set_status(tr("{count} foto{where}, {new_count} mai viste.{errors}",
                               count=len(self.photos), where=where, new_count=new_count, errors=errors), "ok")
        else:
            self.set_status(tr("{count} foto{where}: le hai già viste tutte.{errors}",
                               count=len(self.photos), where=where, errors=errors), "info")

    def _add_photos(self, files: list[RemoteFile]) -> None:
        """Aggiunge foto all'elenco mantenendo l'ordinamento e la foto corrente."""
        if self.fav_only_var.get():
            files = [f for f in files if self.is_favorite(f)]
        if files:
            files.sort(key=self._photo_sort_key)
            by_name = self.settings.sort_by != "date"
            if by_name and (not self.photos or
                            self._photo_sort_key(files[0]) >= self._photo_sort_key(self.photos[-1])):
                start = len(self.photos)       # caso normale: le nuove foto vanno in fondo
                self.photos.extend(files)
                for i in range(start, len(self.photos)):
                    self._insert_photo_row(i)
            else:
                current = self.current_photo()
                self.photos.extend(files)
                self._sort_photos()
                self._fill_photo_list()
                if current is not None:
                    self.index = next(i for i, p in enumerate(self.photos) if p is current)
                    self._select_in_list(self.index)
                    self.update_info()
        self._update_photo_header()
        if self.index == -1 and self.photos:
            self._start_viewing()

    def _start_viewing(self) -> None:
        """Sceglie la prima foto da mostrare: quella da ritrovare dopo "Aggiorna",
        altrimenti la prima mai vista. Se per ora sono tutte viste aspetta la fine della ricerca."""
        if self._keep_photo:
            i = next((i for i, p in enumerate(self.photos) if p.path == self._keep_photo), None)
            if i is not None:
                self._keep_photo = None
                self.show_index(i)
                return
            if self._scanning:
                return
            self._keep_photo = None
        if self.fav_only_var.get():   # tra le preferite si parte dalla prima, viste o no
            if self.photos:
                self.show_index(0)
            elif self._scanning:
                self.show_message(tr("Cerco le foto preferite nelle sottocartelle…"))
            else:
                if self.recursive_var.get() and self.dirs:
                    text = tr("Nessuna foto preferita in questa cartella né nelle sue sottocartelle")
                else:
                    text = tr("Nessuna foto preferita in questa cartella")
                self.show_message(text + "\n\n" + tr("Per aggiungerne una usa il pulsante Preferita (tasto F)."))
                self.update_info()
            return
        i = next((i for i, p in enumerate(self.photos) if not self.is_viewed(p)), None)
        if i is not None:
            self.show_index(i)
        elif self._scanning:
            self.show_message(tr("Cerco foto nuove nelle sottocartelle…\n\n{count} foto "
                                 "trovate finora, tutte già viste.\nPuoi comunque "
                                 "sceglierne una dall'elenco.", count=len(self.photos)))
        elif self.photos:
            self.show_index(0)
        else:
            n = len(self.dirs)
            if self.recursive_var.get() and n:
                self.show_message(tr("Nessuna foto in questa cartella né nelle sue sottocartelle"))
            else:
                text = tr("Nessuna foto in questa cartella")
                if n == 1:
                    text += "\n\n" + tr("1 sottocartella a sinistra")
                elif n:
                    text += "\n\n" + tr("{n} sottocartelle a sinistra", n=n)
                self.show_message(text)
            self.update_info()

    def _photo_sort_key(self, p: RemoteFile):
        # prima le foto della cartella, poi quelle delle sottocartelle (in ordine naturale)
        parts = self.relative_path(p).split("\\")
        name_key = [(1, natural_key(d)) for d in parts[:-1]] + [(0, natural_key(parts[-1]))]
        return (p.mtime, name_key) if self.settings.sort_by == "date" else name_key

    def _sort_photos(self) -> None:
        self.photos.sort(key=self._photo_sort_key)

    def relative_path(self, p: RemoteFile) -> str:
        """Percorso della foto rispetto alla cartella selezionata, es. "Estate\\mare.jpg"."""
        if self.folder and p.path.lower().startswith(self.folder.lower() + "\\"):
            return p.path[len(self.folder) + 1:]
        return p.path

    def pkey(self, p: RemoteFile) -> str:
        """Chiave della cartella in cui si trova la foto (per la memoria delle viste/stampe)."""
        return folder_key(self.source.history_root if self.source else "", parent(p.path))

    def is_viewed(self, p: RemoteFile) -> bool:
        return self.history.is_viewed(self.pkey(p), p.name)

    def is_favorite(self, p: RemoteFile) -> bool:
        return self.history.is_favorite(self.pkey(p), p.name)

    # --- elenchi -----------------------------------------------------------
    def _fill_dir_list(self, highlight: str | None = None) -> None:
        lb = self.dir_list
        lb.delete(0, "end")
        self._dir_targets: list[str] = []
        self._has_up_entry = bool(self.folder or (self.source is not None and self.source.parent_root()))
        if self._has_up_entry:
            lb.insert("end", "⬆  ..")
            self._dir_targets.append(parent(self.folder))
        share = self.source.history_root if self.source else ""
        recursive = bool(self.recursive_var.get())
        for name in self.dirs:
            rel = join(self.folder, name)
            fk = folder_key(share, rel)
            progress = self.history.tree_progress(fk) if recursive else self.history.folder_progress(fk)
            label = f"▸  {name}"
            if progress and progress[1]:
                seen, total = progress
                label += tr("   ✓ tutte viste") if seen >= total else tr("   {seen}/{total} viste",
                                                                     seen=seen, total=total)
            lb.insert("end", label)
            if progress and progress[1] and progress[0] >= progress[1]:
                lb.itemconfig("end", fg=LIST_FG_VIEWED)
            self._dir_targets.append(rel)
            if highlight and name == highlight:
                lb.selection_set("end")
                lb.see("end")

    def _photo_label(self, photo: RemoteFile) -> str:
        # ✓ = già vista, ★ = preferita, 🖨 = già mandata in stampa
        star = "★ " if self.is_favorite(photo) else ""
        printed = "🖨 " if self.history.was_printed(self.pkey(photo), photo.name) else ""
        return f"{'✓' if self.is_viewed(photo) else '•'}   {star}{printed}{self.relative_path(photo)}"

    def _insert_photo_row(self, i: int) -> None:
        self.photo_list.insert(i, self._photo_label(self.photos[i]))
        if self.is_viewed(self.photos[i]):
            self.photo_list.itemconfig(i, fg=LIST_FG_VIEWED)

    def _fill_photo_list(self) -> None:
        self.photo_list.delete(0, "end")
        for i in range(len(self.photos)):
            self._insert_photo_row(i)
        self._update_photo_header()

    def _refresh_photo_row(self, i: int) -> None:
        if not 0 <= i < len(self.photos):
            return
        lb = self.photo_list
        selected = i in lb.curselection()
        lb.delete(i)
        self._insert_photo_row(i)
        if selected:
            lb.selection_set(i)

    def _update_photo_header(self) -> None:
        searching = tr("  · ricerca…") if self._scanning else ""
        if self.fav_only_var.get():
            self.photo_header.configure(text=tr("Preferite  ({count}){searching}",
                                                count=len(self.photos), searching=searching))
            return
        new = sum(not self.is_viewed(p) for p in self.photos)
        self.photo_header.configure(text=tr("Foto  ({count}, {new} da vedere){searching}",
                                            count=len(self.photos), new=new, searching=searching))

    def open_selected_dir(self) -> None:
        sel = self.dir_list.curselection()
        if not sel:
            return
        target = self._dir_targets[sel[0]]
        if self._has_up_entry and sel[0] == 0:
            self.go_up()
        else:
            self.open_folder(target)

    def go_up(self) -> None:
        if self.folder:
            self.open_folder(parent(self.folder), highlight_dir=self.folder.rsplit("\\", 1)[-1])
        elif self.source is not None and self.source.parent_root():
            # cartella locale: si sale anche sopra la cartella scelta all'inizio
            self.open_local(self.source.parent_root(), highlight_dir=self.source.root_name)

    def refresh_folder(self) -> None:
        photo = self.current_photo()
        self.cache.clear()
        self.open_folder(self.folder, keep_photo=photo.path if photo else None)

    def _on_photo_list_select(self, _event=None) -> None:
        sel = self.photo_list.curselection()
        if sel and sel[0] != self.index:
            self.show_index(sel[0])

    def toggle_favorite(self) -> None:
        """Mette o toglie la foto corrente dalle preferite (pulsante Preferita, tasto F)."""
        self.cancel_delete()
        photo = self.current_photo()
        if photo is None:
            return
        favorite = not self.is_favorite(photo)
        self.history.set_favorite(self.pkey(photo), photo.name, favorite)
        self._refresh_photo_row(self.index)
        self.update_info()
        if favorite:
            self.set_status(tr("Aggiunta alle preferite: {name}", name=photo.name), "ok")
        else:
            self.set_status(tr("Tolta dalle preferite: {name}", name=photo.name)
                            + (tr("  (resta nell'elenco fino al prossimo aggiornamento)") if self.fav_only_var.get() else ""))

    def _on_fav_only_toggle(self) -> None:
        # si rilegge la cartella: con "solo preferite" si cercano soltanto le cartelle che ne contengono
        if self.source is not None:
            photo = self.current_photo()
            self.open_folder(self.folder, keep_photo=photo.path if photo else None)
        self.canvas.focus_set()

    def _on_skip_toggle(self) -> None:
        self.settings.skip_viewed = bool(self.skip_var.get())
        self._save_settings()
        self.canvas.focus_set()

    def _on_recursive_toggle(self) -> None:
        self.settings.include_subfolders = bool(self.recursive_var.get())
        self._save_settings()
        if self.source is not None:
            photo = self.current_photo()
            self.open_folder(self.folder, keep_photo=photo.path if photo else None)
        self.canvas.focus_set()

    def _on_sort_change(self, value: str) -> None:
        self.settings.sort_by = self._sort_codes.get(value, "name")
        self._save_settings()
        if not self.photos:
            return
        current = self.current_photo()
        self._sort_photos()
        self._fill_photo_list()
        if current:
            self.index = next(i for i, p in enumerate(self.photos) if p is current)
            self._select_in_list(self.index)
            self.update_info()
        self.canvas.focus_set()

    def reset_viewed(self) -> None:
        if not self.source:
            return
        recursive = bool(self.recursive_var.get())
        if recursive:
            question = tr("Segnare tutte le foto di\n{path}\ne di tutte le sue sottocartelle come non ancora viste?",
                          path=self.source.unc(self.folder))
        else:
            question = tr("Segnare tutte le foto di\n{path}\ncome non ancora viste?", path=self.source.unc(self.folder))
        if not messagebox.askyesno(tr("Azzera foto viste"), question, parent=self):
            return
        if recursive:
            self.history.reset_tree(self.fkey())
        else:
            self.history.reset_folder(self.fkey())
        self._fill_photo_list()
        self._select_in_list(self.index)
        self._fill_dir_list()
        self.update_info()
        self.set_status(tr("Memoria delle foto viste azzerata."), "ok")

    # =====================================================================
    # Navigazione e visualizzazione
    # =====================================================================
    def _step_from(self, i: int, step: int) -> int:
        """Indice della foto successiva/precedente. Con "Salta le foto già viste" l'avanti salta
        tutte quelle con la ✓ (anche viste in questa sessione); l'indietro va sempre alla
        precedente, così si può ricontrollare la foto appena vista."""
        n = len(self.photos)
        i += step
        if self.settings.skip_viewed and step > 0 and not self.fav_only_var.get():
            while 0 <= i < n and self.is_viewed(self.photos[i]):
                i += step
        return i

    def _current_not_shown_yet(self) -> bool:
        """La foto corrente è ancora in caricamento e non è mai comparsa sullo schermo?"""
        photo = self.current_photo()
        if photo is None or photo.path in self.deleting or self.cache.get(photo.path) is not None:
            return False
        failed = self._canvas_message is not None and self._canvas_message[1]
        return not failed   # se il file non si apre si può comunque andare avanti

    def navigate(self, step: int) -> None:
        if not self.photos:
            return
        if step > 0 and self._current_not_shown_yet():
            # evita di passare oltre una foto mai vista premendo Avanti mentre si sta caricando
            self.set_status(tr("Attendi che la foto compaia, così non ne salti nessuna. "
                               "Per saltarla apposta scegli un'altra foto dall'elenco."), "warn")
            return
        n = len(self.photos)
        i = self._step_from(self.index, step)
        if i < 0:
            self.set_status(tr("Sei già alla prima foto della cartella."), "warn")
        elif i >= n:
            if self.fav_only_var.get():
                msg = tr("Sei all'ultima foto preferita.")
            elif self.settings.skip_viewed:
                msg = tr("Non ci sono altre foto da vedere dopo questa.")
            else:
                msg = tr("Sei all'ultima foto della cartella.")
            if self._scanning:
                msg += tr(" La ricerca nelle sottocartelle è ancora in corso: riprova tra poco.")
            self.set_status(msg, "warn")
        else:
            self.show_index(i, direction=step)

    def show_index(self, i: int, direction: int = 1) -> None:
        if not 0 <= i < len(self.photos):
            return
        self.cancel_delete(redraw=False)
        if i != self.index:
            self.commit_rotation()
            self._reset_view()         # ogni foto parte intera, senza zoom
        self.index = i
        photo = self.photos[i]
        self._seen_before = self.is_viewed(photo)
        self._select_in_list(i)

        # precarica le prossime foto nella direzione di scorrimento (e una all'indietro)
        neighbours = []
        j = i
        for _ in range(PREFETCH_AHEAD):
            j = self._step_from(j, direction)
            neighbours.append(j)
        neighbours.append(self._step_from(i, -direction))
        prefetch = [self.photos[j] for j in neighbours if 0 <= j < len(self.photos)]
        self.wanted = frozenset([photo.path] + [p.path for p in prefetch])

        item = self.cache.get(photo.path)
        if item is not None:
            self._canvas_message = None
            self.render()
            self._mark_viewed(i)
        else:
            self.show_message(tr("Caricamento…"))
            self.load(photo, HIGH)
        self.update_info()
        for p in prefetch:
            if self.cache.get(p.path) is None:
                self.load(p, LOW)

    def _select_in_list(self, i: int) -> None:
        lb = self.photo_list
        lb.selection_clear(0, "end")
        if 0 <= i < lb.size():
            lb.selection_set(i)
            lb.see(i)

    def load(self, photo: RemoteFile, priority: int) -> None:
        path = photo.path
        if path in self.loading or self.source is None:
            return
        self.loading.add(path)
        browser, session, max_side = self.source, self.session, self.max_side

        def task():
            if path not in self.wanted:   # l'utente è già andato oltre
                return None
            return decode_for_display(browser.read_bytes(path), max_side)

        def done(item: LoadedImage | None):
            self.loading.discard(path)
            if session != self.session:
                return
            current = self.current_photo()
            if item is None:
                if current is not None and current.path == path:
                    self.load(current, HIGH)
                return
            if path in self.saving or path in self.deleting:
                return
            self.cache.put(path, item)
            if current is not None and current.path == path:
                self._canvas_message = None
                self.render()
                self._mark_viewed(self.index)
                self.update_info()

        def error(exc: BaseException):
            self.loading.discard(path)
            current = self.current_photo()
            if session == self.session and current is not None and current.path == path:
                self.show_message(tr("Impossibile aprire la foto\n\n{error}", error=describe_error(exc)), error=True)

        self.worker.submit(task, done, error, priority)

    def _mark_viewed(self, i: int) -> None:
        photo = self.photos[i]
        if self.history.mark_viewed(self.pkey(photo), photo.name):
            self._refresh_photo_row(i)
            self._update_photo_header()

    def update_info(self) -> None:
        photo = self.current_photo()
        if photo is None:
            self.name_label.configure(text="")
            self.counter_label.configure(text="")
            self.details_label.configure(text="")
            self._update_exif_info(None)
            for badge in (self.badge_seen, self.badge_fav, self.badge_print):
                badge.pack_forget()
            self.btn_fav.configure(image=icon("star", 20))
            return
        self.name_label.configure(text=photo.name)
        self.counter_label.configure(text=f"{self.index + 1} / {len(self.photos)}")
        parts = []
        subfolder = parent(self.relative_path(photo))
        if subfolder:
            parts.append(tr("cartella: {subfolder}", subfolder=subfolder))
        item = self.cache.get(photo.path)
        if item is not None:
            w, h = item.full_size
            if self.view_rotation in (90, 270):
                w, h = h, w
            parts.append(f"{w} × {h}")
        parts.append(human_size(photo.size))
        parts.append(tr("file: ") + datetime.fromtimestamp(photo.mtime).strftime("%d/%m/%Y %H:%M"))
        self.details_label.configure(text="   ·   ".join(parts))
        self._update_exif_info(item)

        for badge in (self.badge_seen, self.badge_fav, self.badge_print):
            badge.pack_forget()
        if self._seen_before:
            self.badge_seen.configure(text=tr("  GIÀ VISTA  "), fg_color="#4a4a4a", text_color="#dddddd")
        else:
            self.badge_seen.configure(text=tr("  NUOVA  "), fg_color=GREEN, text_color="white")
        self.badge_seen.pack(side="left", padx=(0, 6))
        favorite = self.is_favorite(photo)
        if favorite:
            self.badge_fav.pack(side="left", padx=(0, 6))
        self.btn_fav.configure(image=icon("star_fill", 20, GOLD) if favorite else icon("star", 20))
        printed = self.history.printed_copy(self.pkey(photo), photo.name)
        if printed:   # già mandata in stampa: la copia è ancora nella cartella stampa oppure è già stata tolta
            if not os.path.exists(printed[0]):
                text = tr(" GIÀ STAMPATA  ")
            else:
                text = tr(" IN STAMPA · CON DATA  ") if printed[1] else tr(" IN STAMPA  ")
            self.badge_print.configure(text=text)
            self.badge_print.pack(side="left")

    def _update_exif_info(self, item: LoadedImage | None) -> None:
        for w in (self.taken_label, self.gps_button):
            w.pack_forget()
        if item is None:
            return
        taken, gps = item.meta.taken, item.meta.gps
        if taken:
            text = tr("Scattata {weekday} {date} alle {time}", weekday=weekday_name(taken.weekday()),
                      date=f"{taken:%d/%m/%Y}", time=f"{taken:%H:%M}")
            self.taken_label.configure(text=f" {text}", text_color="#e6e6e6")
        else:
            self.taken_label.configure(text=tr(" Data di scatto non presente"), text_color="gray50")
        self.taken_label.pack(side="left", padx=(24, 0))
        if gps:
            self.gps_button.pack(side="left", padx=(10, 0))

    # --- mappa della posizione GPS -----------------------------------------
    def open_map(self) -> None:
        """Apre Google Maps nel browser sul punto in cui è stata scattata la foto: se possibile
        in una finestrella senza barre, sistemata sotto l'icona."""
        item = self.current_item()
        if item is None or not item.meta.gps:
            return
        lat, lon = item.meta.gps
        scale = ctk.ScalingTracker.get_window_scaling(self)
        width, height = round(WINDOW_SIZE[0] * scale), round(WINDOW_SIZE[1] * scale)
        x = self.gps_button.winfo_rootx()
        y = self.gps_button.winfo_rooty() + self.gps_button.winfo_height() + round(8 * scale)
        x = max(0, min(x, self.winfo_screenwidth() - width - 10))
        y = max(0, min(y, self.winfo_screenheight() - height - 60))
        before = open_google_maps(lat, lon, x, y, width, height)
        self.set_status(tr("Google Maps aperto sulla posizione della foto: {coords}",
                           coords=format_coords(lat, lon)))
        if before is not None:
            self._place_map_window(before, (x, y, width, height), attempts=40)

    def _place_map_window(self, before: set[int], rect: tuple[int, int, int, int], attempts: int) -> None:
        # il browser, se è già aperto, ignora dimensione e posizione chieste all'avvio:
        # appena la finestrella compare la si sistema da qui
        hwnd = find_map_window(before)
        if hwnd is not None:
            place_window(hwnd, *rect)
        elif attempts > 0 and not self._closing:
            self.after(150, lambda: self._place_map_window(before, rect, attempts - 1))

    def _on_root_wheel(self, event) -> None:
        # Su Windows la rotella arriva alla finestra attiva, non a quella sotto il puntatore:
        # lo zoom si applica solo se il puntatore è sopra la foto.
        cx, cy = event.x_root - self.canvas.winfo_rootx(), event.y_root - self.canvas.winfo_rooty()
        if 0 <= cx < self.canvas.winfo_width() and 0 <= cy < self.canvas.winfo_height():
            self.zoom_at(cx, cy, 1 if event.delta > 0 else -1)

    def _on_stamp_toggle(self) -> None:
        self.settings.stamp_date = bool(self.stamp_var.get())
        self._save_settings()
        self.redraw()
        if self.settings.stamp_date:
            self.set_status(tr("Stampa data attiva: la data di scatto compare in rosso "
                               "nell'anteprima e nelle copie salvate con H (la foto "
                               "originale non cambia)."), "ok")
        else:
            self.set_status(tr("Data disattivata: le copie salvate con H saranno senza data."))
        self.canvas.focus_set()

    def _on_canvas_resize(self, _event=None) -> None:
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(80, self.redraw)

    def redraw(self) -> None:
        self._resize_job = None
        if self._canvas_message is not None:
            text, is_error = self._canvas_message
            self.show_message(text, is_error)
        else:
            self.render()

    def render(self, fast: bool = False) -> None:
        """Disegna la foto corrente: intera (zoom 1) oppure la zona ingrandita attorno a _view_center.
        ``fast`` usa un ridimensionamento veloce, per rotella e trascinamento."""
        photo, item = self.current_photo(), self.current_item()
        if photo is None or item is None:
            return
        full_size = item.full_size if self.view_rotation in (0, 180) else item.full_size[::-1]
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        view = render_view(self._view_source(photo, item), full_size, (cw, ch), self.zoom, self._view_center, fast)
        self._view = view
        self.zoom = view.zoom
        self._view_center = view.center if view.zoom > 1 else None

        self._photo_ref = ImageTk.PhotoImage(view.image)
        self.canvas.delete("all")
        self.canvas.create_image(round(view.offset[0]), round(view.offset[1]), image=self._photo_ref, anchor="nw")
        if view.zoom > 1:
            needs_full = item.base.size != item.full_size and not self._has_full(photo)
            if needs_full:   # l'anteprima è ridotta: per vedere i dettagli serve la foto a piena risoluzione
                self._request_full(photo)
            self.canvas.create_text(14, ch - 12, anchor="sw", fill="#e6e6e6", font=("Segoe UI", 11, "bold"),
                                    text=f"{view.scale * 100:.0f}%" + (tr("  ·  carico i dettagli…") if needs_full else ""))
        if self.view_rotation:
            self.canvas.create_text(cw - 16, ch - 14, anchor="se", fill="#f0b85a", font=("Segoe UI", 11),
                                    text=tr("Rotazione {view_rotation}° — salvataggio tra poco…",
                                            view_rotation=self.view_rotation))
        if self.delete_armed:
            self._draw_delete_overlay()

    # --- zoom (rotella) e spostamento (trascinamento) ------------------------
    def _has_full(self, photo: RemoteFile) -> bool:
        return self._full is not None and self._full[0] == photo.path

    def _view_source(self, photo: RemoteFile, item: LoadedImage):
        """Immagine da cui ritagliare la vista: l'anteprima oppure, con lo zoom, la foto a piena
        risoluzione; già ruotata (rotazione in sospeso) e con la data se "Stampa data" è attivo."""
        full = self._full[1] if self.zoom > 1 and self._has_full(photo) else None
        stamp = item.meta.taken if self.stamp_var.get() else None
        c = self._src_cache   # (anteprima, piena risoluzione, rotazione, data, risultato)
        if c is None or c[0] is not item.base or c[1] is not full or c[2] != self.view_rotation or c[3] != stamp:
            img = rotate_cw(full if full is not None else item.base, self.view_rotation)
            if stamp is not None:
                img = stamp_date(img, stamp)   # anteprima di come verrà la copia per la stampa
            self._src_cache = c = (item.base, full, self.view_rotation, stamp, img)
        return c[4]

    def _request_full(self, photo: RemoteFile) -> None:
        path = photo.path
        if self._full_requested == path or path in self.saving:
            return   # durante il salvataggio di una rotazione il file sta cambiando: si chiede dopo
        raw = self.cache.get_raw(path)
        if raw is None:
            return
        self._full_requested = path

        def done(image):
            if self._full_requested == path:
                self._full_requested = None
            current = self.current_photo()
            if current is None or current.path != path or path in self.saving \
                    or self.cache.get_raw(path) is not raw:
                return   # nel frattempo si è cambiata foto, o il file è stato ruotato
            self._full = (path, image)
            if self.zoom > 1 and self._canvas_message is None:
                self.render()

        def error(_exc: BaseException):
            if self._full_requested == path:
                self._full_requested = None

        self.decoder.submit(lambda: decode_full(raw), done, error)

    def _reset_view(self, forget_full: bool = True) -> None:
        self.zoom = 1.0
        self._view_center = None
        self._press = None
        if self._hq_job is not None:
            self.after_cancel(self._hq_job)
            self._hq_job = None
        if forget_full:
            self._full = None
            self._src_cache = None
            self._view = None

    def zoom_at(self, x: float, y: float, direction: int) -> None:
        """Ingrandisce (direction > 0) o riduce tenendo fermo il punto della foto sotto il puntatore."""
        view = self._view
        if view is None or self._canvas_message is not None or self.current_item() is None:
            return
        zoom = min(max(view.zoom * ZOOM_STEP ** direction, 1.0), view.max_zoom)
        if zoom < 1.02:
            zoom = 1.0
        if abs(zoom - view.zoom) < 1e-6:
            return
        px, py = view.to_photo(x, y)
        scale = view.scale / view.zoom * zoom
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.zoom = zoom
        self._view_center = (px - (x - cw / 2) / scale, py - (y - ch / 2) / scale)
        self.render(fast=True)
        if self._hq_job is not None:
            self.after_cancel(self._hq_job)
        self._hq_job = self.after(150, self._render_hq)

    def _render_hq(self) -> None:
        self._hq_job = None
        if self._canvas_message is None:
            self.render()

    def _on_canvas_press(self, event) -> None:
        self.canvas.focus_set()
        self._press = {"x": event.x, "y": event.y, "moved": False,
                       "center": self._view.center if self._view is not None else None}

    def _on_canvas_drag(self, event) -> None:
        press = self._press
        if press is None:
            return
        dx, dy = event.x - press["x"], event.y - press["y"]
        if not press["moved"] and abs(dx) + abs(dy) < DRAG_THRESHOLD:
            return   # piccolo tremolio durante un clic: non è un trascinamento
        press["moved"] = True
        if self.zoom > 1 and self._view is not None and press["center"] is not None:
            self.canvas.configure(cursor="fleur")
            cx, cy = press["center"]
            self._view_center = (cx - dx / self._view.scale, cy - dy / self._view.scale)
            self.render(fast=True)

    def _on_canvas_release(self, _event) -> None:
        press, self._press = self._press, None
        if press is None:
            return
        # un clic senza movimento non fa nulla: le foto si cambiano solo con tastiera e pulsanti
        if press["moved"]:
            self.canvas.configure(cursor="")
            if self.zoom > 1:
                self._render_hq()   # a trascinamento finito si ridisegna in alta qualità

    def show_message(self, text: str, error: bool = False) -> None:
        self._canvas_message = (text, error)
        self._photo_ref = None
        c = self.canvas
        c.delete("all")
        cw, ch = max(c.winfo_width(), 200), max(c.winfo_height(), 200)
        c.create_text(cw // 2, ch // 2, text=text, justify="center", width=cw - 80,
                      fill=STATUS_COLORS["error"] if error else "#8a8a8a", font=("Segoe UI", 16))
        if self.delete_armed:
            self._draw_delete_overlay()

    def _draw_delete_overlay(self) -> None:
        c = self.canvas
        cw, ch = c.winfo_width(), c.winfo_height()
        c.create_rectangle(3, 3, cw - 3, ch - 3, outline=RED, width=6)
        top = max(ch - 170, ch // 2)
        c.create_rectangle(40, top, cw - 40, top + 110, fill="#3d1414", outline=RED, width=2)
        c.create_text(cw // 2, top + 38, fill="white", font=("Segoe UI", 18, "bold"),
                      text=self.source.delete_question if self.source else tr("Eliminare questa foto?"))
        c.create_text(cw // 2, top + 78, fill="#ffcccc", font=("Segoe UI", 12),
                      text=tr("Premi  C  (o il pulsante Conferma) per eliminarla  ·  Esc per annullare"))

    # =====================================================================
    # Rotazione
    # =====================================================================
    def rotate(self, degrees: int) -> None:
        self.cancel_delete()
        photo, item = self.current_photo(), self.current_item()
        if photo is None:
            return
        if item is None:
            self.set_status(tr("Attendi che la foto sia caricata prima di ruotarla."), "warn")
            return
        if not item.rotatable:
            self.set_status(tr("Le immagini animate o multipagina non possono essere ruotate."), "error")
            return
        if photo.path in self.deleting:
            return
        self.view_rotation = (self.view_rotation + degrees) % 360
        self._reset_view(forget_full=False)
        self.render()
        self.update_info()
        if self._rotation_job is not None:
            self.after_cancel(self._rotation_job)
        self._rotation_job = self.after(ROTATION_SAVE_DELAY_MS, self.commit_rotation)

    def _discard_rotation(self) -> None:
        if self._rotation_job is not None:
            self.after_cancel(self._rotation_job)
            self._rotation_job = None
        self.view_rotation = 0

    def commit_rotation(self) -> None:
        """Salva sul file (NAS o disco) la rotazione in sospeso della foto corrente."""
        angle = self.view_rotation
        self._discard_rotation()
        photo, item = self.current_photo(), self.current_item()
        if angle == 0 or photo is None or item is None or self.source is None:
            return

        # l'anteprima in cache viene aggiornata subito; in caso di errore si torna indietro
        item.base = rotate_cw(item.base, angle)
        if angle in (90, 270):
            item.full_size = item.full_size[::-1]
        if self._has_full(photo):   # anche la versione a piena risoluzione usata dallo zoom
            self._full = (photo.path, rotate_cw(self._full[1], angle))
        path, browser, cache = photo.path, self.source, self.cache
        printed = self.history.printed_copy(self.pkey(photo), photo.name)
        self.saving[path] = self.saving.get(path, 0) + 1

        def task():
            raw = cache.get_raw(path) or browser.read_bytes(path)
            new = rotate_image_bytes(raw, angle)
            browser.write_bytes(path, new)
            cache.set_raw(path, new)
            updated_copy = False
            if printed and os.path.exists(printed[0]):   # tiene allineata anche la copia per la stampa
                copy_path, with_date = printed
                when = read_meta_from_bytes(new).taken if with_date else None
                _write_local(Path(copy_path), render_image_bytes(new, stamp=when) if when else new)
                updated_copy = True
            return new, updated_copy

        def finished():
            left = self.saving.get(path, 1) - 1
            if left:
                self.saving[path] = left
            else:
                self.saving.pop(path, None)

        def done(result):
            finished()
            new, updated_copy = result
            photo.size, photo.mtime = len(new), time.time()
            extra = tr(" (aggiornata anche la copia per la stampa)") if updated_copy else ""
            self.set_status(tr("Rotazione salvata: {name}{extra}", name=photo.name, extra=extra), "ok")
            if self.current_photo() is photo:
                self.update_info()
                if self.zoom > 1 and self._canvas_message is None:
                    self.render()   # ora si può caricare la piena risoluzione del file ruotato

        def error(exc: BaseException):
            finished()
            if self.cache.get(path) is item:
                item.base = rotate_cw(item.base, -angle)
                if angle in (90, 270):
                    item.full_size = item.full_size[::-1]
                if self.current_photo() is photo:
                    self._reset_view()
                    self.render()
                    self.update_info()
            msg = str(exc) if exc.__class__.__name__ == "RotationNotSupported" else describe_error(exc)
            self.set_status(tr("Rotazione NON salvata: {msg}", msg=msg), "error")
            messagebox.showerror(tr("Rotazione non salvata"), f"{photo.name}\n\n{msg}", parent=self)

        self.set_status(tr("Salvataggio della rotazione di {name}…", name=photo.name))
        self.worker.submit(task, done, error, HIGH, is_write=True)

    # =====================================================================
    # Eliminazione (D = prepara, C = conferma)
    # =====================================================================
    def arm_delete(self) -> None:
        photo = self.current_photo()
        if photo is None or photo.path in self.deleting:
            return
        if self._rotation_job is not None:          # la rotazione aspetta la decisione
            self.after_cancel(self._rotation_job)
            self._rotation_job = None
        self.delete_armed = True
        self._set_confirm_enabled(True)
        self.redraw()
        self.set_status(tr("Eliminare {name}?  Premi C per confermare, Esc per annullare.", name=photo.name), "warn")

    def _set_confirm_enabled(self, enabled: bool) -> None:
        self.btn_confirm.configure(state="normal" if enabled else "disabled",
                                   fg_color=RED if enabled else GRAY_BTN,
                                   image=icon("confirm", 20) if enabled else icon("confirm", 20, "#808080"))

    def cancel_delete(self, redraw: bool = True) -> None:
        if not self.delete_armed:
            return
        self.delete_armed = False
        self._set_confirm_enabled(False)
        if self.view_rotation and self._rotation_job is None:
            self._rotation_job = self.after(ROTATION_SAVE_DELAY_MS, self.commit_rotation)
        if redraw:
            self.redraw()
            self.set_status(tr("Eliminazione annullata."))

    def confirm_delete(self) -> None:
        photo = self.current_photo()
        if photo is None:
            return
        if not self.delete_armed:
            self.set_status(tr("Per eliminare premi prima D, poi C per confermare."), "warn")
            return
        self.delete_armed = False
        self._set_confirm_enabled(False)
        self._discard_rotation()
        self.redraw()

        path, name, browser, session, listing = photo.path, photo.name, self.source, self.session, self.listing
        fk = self.pkey(photo)
        self.deleting.add(path)
        self.set_status(tr("Eliminazione di {name}…", name=name))

        def done(_):
            self.deleting.discard(path)
            self.cache.pop(path)
            self.history.forget(fk, name)
            self.history.set_total(fk, max(0, self.history.totals.get(fk, 1) - 1))
            self.set_status(tr("Eliminata: {name}", name=name), "ok")
            idx = next((i for i, p in enumerate(self.photos) if p is photo), None)
            if session != self.session or listing != self.listing or idx is None:
                return
            del self.photos[idx]
            self.photo_list.delete(idx)
            self._update_photo_header()
            if idx < self.index:
                self.index -= 1
                self._select_in_list(self.index)
                self.update_info()
            elif idx == self.index:
                if not self.photos:
                    self.index = -1
                    self.wanted = frozenset()
                    self.show_message(tr("Nessuna altra foto in questa cartella"))
                    self.update_info()
                else:
                    self.index = -1
                    self.show_index(min(idx, len(self.photos) - 1))
            else:
                self.update_info()

        def error(exc: BaseException):
            self.deleting.discard(path)
            msg = describe_error(exc)
            self.set_status(tr("Eliminazione non riuscita: {msg}", msg=msg), "error")
            messagebox.showerror(tr("Eliminazione non riuscita"), f"{name}\n\n{msg}", parent=self)

        self.worker.submit(lambda: browser.remove(path), done, error, HIGH, is_write=True)

    # =====================================================================
    # Copia nella cartella per la stampa (H)
    # =====================================================================
    def send_to_print(self) -> None:
        self.cancel_delete()
        photo = self.current_photo()
        if photo is None or self.source is None or photo.path in self.deleting:
            return
        self.commit_rotation()   # la copia deve già essere ruotata

        dest_dir = Path(self.settings.print_dir)
        folder = parent(photo.path)
        source_folder = folder.rsplit("\\", 1)[-1] if folder else self.source.root_name
        fk = self.pkey(photo)
        existing = self.history.printed_copy(fk, photo.name)
        with_date = bool(self.stamp_var.get())
        path, browser, cache = photo.path, self.source, self.cache

        def task():
            raw = cache.get_raw(path) or browser.read_bytes(path)
            when = read_meta_from_bytes(raw).taken if with_date else None
            data = raw
            if when is not None:
                try:
                    data = render_image_bytes(raw, stamp=when)
                except RotationNotSupported:   # GIF animate: copia senza data
                    when = None
            dest_dir.mkdir(parents=True, exist_ok=True)
            if existing and Path(existing[0]).exists() and Path(existing[0]).parent == dest_dir:
                dest, updated = Path(existing[0]), True
            else:
                dest, updated = print_copy_path(dest_dir, photo.name, source_folder), False
            _write_local(dest, data)
            return dest, updated, when

        def done(result):
            dest, updated, when = result
            self.history.set_printed(fk, photo.name, str(dest), when is not None)
            # le foto mandate in stampa diventano automaticamente preferite
            newly_favorite = not self.history.is_favorite(fk, photo.name)
            self.history.set_favorite(fk, photo.name, True)
            row = next((i for i, p in enumerate(self.photos) if p is photo), None)
            if newly_favorite and row is not None:
                self._refresh_photo_row(row)
            action = tr("copia aggiornata") if updated else tr("copiata")
            starred = tr("  ·  aggiunta alle preferite") if newly_favorite else ""
            if when is not None:
                self.set_status(tr("Stampa: {action} con la data {date} → {dest}{starred}",
                                   action=action, date=format_stamp(when), dest=dest, starred=starred), "ok")
            elif with_date:
                self.set_status(tr("Stampa: {action} SENZA data (la foto non ha la data "
                                   "di scatto EXIF) → {dest}{starred}",
                                   action=action, dest=dest, starred=starred), "warn")
            else:
                self.set_status(tr("Stampa: {action} → {dest}{starred}",
                                   action=action, dest=dest, starred=starred), "ok")
            if self.current_photo() is photo:
                self.update_info()

        def error(exc: BaseException):
            msg = describe_error(exc)
            self.set_status(tr("Copia per la stampa non riuscita: {msg}", msg=msg), "error")
            messagebox.showerror(tr("Copia non riuscita"), f"{photo.name}\n\n{msg}", parent=self)

        self.set_status(tr("Copia di {name} nella cartella stampa…", name=photo.name))
        self.worker.submit(task, done, error, HIGH, is_write=True)

    def choose_print_folder(self) -> None:
        folder = filedialog.askdirectory(parent=self, title=tr("Cartella in cui copiare le foto da stampare"),
                                         initialdir=self.settings.print_dir, mustexist=False)
        if folder:
            self.settings.print_dir = str(Path(folder))
            self._save_settings()
            self.set_status(tr("Cartella stampa: {print_dir}", print_dir=self.settings.print_dir), "ok")
            self.update_info()

    def open_about(self) -> None:
        if self.about is not None and self.about.winfo_exists():
            self.about.lift()
            self.about.focus_force()
            return
        self.about = AboutDialog(self)

    # --- azzeramento completo ----------------------------------------------
    def open_reset_dialog(self) -> None:
        ResetDialog(self, self.reset_all)

    def reset_all(self, also_settings: bool) -> None:
        """Cancella foto viste, preferite e foto mandate in stampa; a richiesta anche le
        impostazioni e i dati di connessione. Le foto e le copie per la stampa non si toccano."""
        self.cancel_delete(redraw=False)
        self.commit_rotation()
        self.history.clear_all()
        try:
            self.history.save()
            shutil.rmtree(APP_DIR / "map_cache", ignore_errors=True)   # residuo delle vecchie versioni
        except OSError as exc:
            self.set_status(tr("Impossibile salvare: {exc}", exc=exc), "error")
        if not also_settings:
            if self.source is not None:
                photo = self.current_photo()
                self.open_folder(self.folder, keep_photo=photo.path if photo else None)
            self.set_status(tr("Dati azzerati: foto viste, preferite e foto mandate in stampa."), "ok")
            return

        # anche le impostazioni: si torna allo stato del primo avvio (la lingua scelta resta)
        store_password(self.settings.server, self.settings.username, None)
        old = self.source
        self.source = None
        self.session += 1
        self.listing += 1
        self.cache.clear()
        self.loading.clear()
        if old is not None:
            self.worker.submit(old.close, priority=LOW)
        self.settings = Settings(print_dir=default_print_dir(), geometry=self.settings.geometry,
                                 language=self.settings.language)
        self._save_settings()
        self.folder, self.dirs, self.photos, self.index = "", [], [], -1
        self._scanning = False
        self._reset_view()
        self._rebuild_ui()
        self.set_status(tr("Dati e impostazioni azzerati: il programma è tornato come al primo avvio."), "ok")
        self.open_connection_dialog()

    def _rebuild_ui(self) -> None:
        """Ricostruisce l'interfaccia da zero (dopo un azzeramento o un cambio di lingua)."""
        for job_name in ("_resize_job", "_hq_job"):
            job = getattr(self, job_name)
            if job is not None:
                self.after_cancel(job)
                setattr(self, job_name, None)
        favorites_only = bool(self.fav_only_var.get()) and self.source is not None
        for child in list(self.winfo_children()):
            child.destroy()            # anche eventuali finestre di dialogo aperte
        self.dialog = self.about = None
        self.delete_armed = False
        self._photo_ref = None
        self._view = None
        self._build_ui()
        self.fav_only_var.set(favorites_only)

    def _on_language_change(self, name: str) -> None:
        code = next((c for c, shown in LANGUAGES.items() if shown == name), get_language())
        if code == get_language():
            return
        self.settings.language = code
        self._save_settings()
        set_language(code)
        self.change_language()

    def change_language(self) -> None:
        """Ridisegna tutta l'interfaccia nella lingua corrente e rilegge la cartella aperta
        (così anche i messaggi sulla foto e nella barra di stato sono nella nuova lingua)."""
        photo = self.current_photo()
        dialog_was_open = self.dialog is not None and self.dialog.winfo_exists()
        self.cancel_delete(redraw=False)
        self.commit_rotation()
        self._rebuild_ui()
        if self.source is not None:
            self.open_folder(self.folder, keep_photo=photo.path if photo else None)
        elif dialog_was_open:
            self.open_connection_dialog()

    def open_data_folder(self) -> None:
        """Apre in Esplora file la cartella con history.json (foto viste) e settings.json."""
        try:
            self.history.save()        # così il file mostra lo stato aggiornato
            self.settings.save()
            os.startfile(APP_DIR)  # type: ignore[attr-defined]
            self.set_status(tr("Dati dell'app: {app_dir}  (history.json = foto viste e "
                               "copie per la stampa)", app_dir=APP_DIR))
        except OSError as exc:
            self.set_status(tr("Impossibile aprire {app_dir}: {exc}", app_dir=APP_DIR, exc=exc), "error")

    def open_print_folder(self) -> None:
        folder = Path(self.settings.print_dir)
        try:
            folder.mkdir(parents=True, exist_ok=True)
            os.startfile(folder)  # type: ignore[attr-defined]
        except OSError as exc:
            self.set_status(tr("Impossibile aprire {folder}: {exc}", folder=folder, exc=exc), "error")

    # =====================================================================
    # Chiusura
    # =====================================================================
    def _save_settings(self) -> None:
        try:
            self.settings.save()
        except OSError as exc:
            self.set_status(tr("Impossibile salvare le impostazioni: {exc}", exc=exc), "error")

    def on_close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.cancel_delete(redraw=False)
        self.commit_rotation()
        self.settings.geometry = "zoomed" if self.state() == "zoomed" else self.geometry()
        self._finish_close(0)

    def _finish_close(self, waited_ms: int) -> None:
        if self.worker.writes_pending and waited_ms < 60_000:
            self.set_status(tr("Attendo la fine dei salvataggi prima di chiudere…"), "warn")
            self.after(200, lambda: self._finish_close(waited_ms + 200))
            return
        self.worker.process_results(limit=1000)
        try:
            self.history.save()
        except OSError:
            pass
        self._save_settings()
        self.worker.stop()
        self.decoder.stop()
        for job in (self._poll_job, self._autosave_job, self._gc_job, self._rotation_job, self._resize_job,
                    self._flush_job, self._hq_job):
            if job is not None:
                self.after_cancel(job)
        self.destroy()


def _write_local(dest: Path, data: bytes) -> None:
    tmp = dest.with_name(dest.name + ".part")
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, dest)
