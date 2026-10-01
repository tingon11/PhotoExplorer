# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Accesso alla condivisione SMB del NAS tramite smbprotocol."""
from __future__ import annotations

import ntpath
import socket
from dataclasses import dataclass

import smbclient
from smbprotocol.exceptions import SMBConnectionClosed, SMBException

from .i18n import tr
from .imaging import is_image

FILE_ATTRIBUTE_DIRECTORY = 0x10
FILE_ATTRIBUTE_HIDDEN = 0x2

# Cartelle di sistema QNAP / Synology / Windows da non mostrare
HIDDEN_DIRS = {"@recycle", "@recently-snapshot", "@__thumb", ".@__thumb", "@eadir",
                "#recycle", "$recycle.bin", "system volume information", ".streams"}

_RETRYABLE = (SMBConnectionClosed, ConnectionError, TimeoutError, socket.timeout)


@dataclass
class RemoteFile:
    name: str
    path: str       # percorso relativo alla condivisione, es. "Foto\\2024\\IMG_1.jpg"
    size: int
    mtime: float


@dataclass
class SmbConfig:
    server: str
    share: str
    username: str
    password: str
    port: int = 445
    domain: str = ""

    @property
    def location(self) -> str:
        return f"{self.server.lower()}|{self.share.lower()}"


def join(folder: str, name: str) -> str:
    return f"{folder}\\{name}" if folder else name


def parent(folder: str) -> str:
    return folder.rsplit("\\", 1)[0] if "\\" in folder else ""


def normalize(folder: str) -> str:
    folder = folder.replace("/", "\\").strip("\\ ")
    return "" if folder in ("", ".") else ntpath.normpath(folder)


class SmbBrowser:
    def __init__(self, cfg: SmbConfig) -> None:
        self.cfg = cfg
        user = f"{cfg.domain}\\{cfg.username}" if cfg.domain else cfg.username
        self._kw = dict(username=user or None, password=cfg.password or None,
                        port=int(cfg.port), connection_timeout=15)

    kind = "smb"

    @property
    def delete_question(self) -> str:
        return tr("Eliminare definitivamente questa foto dal NAS?")

    @property
    def root(self) -> str:
        return rf"\\{self.cfg.server}\{self.cfg.share}"

    @property
    def root_name(self) -> str:
        return self.cfg.share

    @property
    def location(self) -> str:
        return self.cfg.location

    @property
    def history_root(self) -> str:
        """Radice delle chiavi per la memoria delle foto viste: il nome della condivisione
        (non l'indirizzo del server, che può cambiare tra IP e nome)."""
        return self.cfg.share

    @property
    def connection_key(self) -> str:
        return f"{self.cfg.server.lower()}:{self.cfg.port}"

    def parent_root(self) -> None:
        return None   # sopra la condivisione non si sale

    def unc(self, rel: str) -> str:
        return f"{self.root}\\{rel}" if rel else self.root


    # --- connessione -----------------------------------------------------
    def connect(self) -> None:
        smbclient.register_session(self.cfg.server, **self._kw)

    def close(self) -> None:
        try:
            smbclient.delete_session(self.cfg.server, port=int(self.cfg.port))
        except Exception:
            pass

    def _call(self, fn, *args, **kwargs):
        """Esegue un'operazione; se la connessione è caduta la riapre e riprova una volta."""
        try:
            return fn(*args, **kwargs, **self._kw)
        except _RETRYABLE:
            self.close()
            return fn(*args, **kwargs, **self._kw)

    # --- operazioni ------------------------------------------------------
    def list_dir(self, rel: str) -> tuple[list[str], list[RemoteFile]]:
        def work(path, **kw):
            dirs: list[str] = []
            files: list[RemoteFile] = []
            for entry in smbclient.scandir(path, **kw):
                name = entry.name
                info = entry.smb_info
                if name.startswith(".") or name.lower() in HIDDEN_DIRS:
                    continue
                if info.file_attributes & FILE_ATTRIBUTE_DIRECTORY:
                    if not name.startswith("@"):
                        dirs.append(name)
                elif is_image(name):
                    try:
                        mtime = info.last_write_time.timestamp()
                    except (OverflowError, OSError, ValueError):
                        mtime = 0.0
                    files.append(RemoteFile(name, join(rel, name), info.end_of_file, mtime))
            return dirs, files

        return self._call(work, self.unc(rel))

    def read_bytes(self, rel: str) -> bytes:
        def work(path, **kw):
            with smbclient.open_file(path, mode="rb", share_access="rw", **kw) as f:
                return f.read()

        return self._call(work, self.unc(rel))

    def write_bytes(self, rel: str, data: bytes) -> None:
        """Scrive su un file temporaneo nella stessa cartella e poi sostituisce l'originale,
        così un'interruzione di rete non lascia mai una foto troncata."""
        folder, name = parent(rel), rel.rsplit("\\", 1)[-1]
        tmp = self.unc(join(folder, f".{name}.photoexplorer.tmp"))
        target = self.unc(rel)

        def work(**kw):
            try:
                with smbclient.open_file(tmp, mode="wb", **kw) as f:
                    f.write(data)
                smbclient.replace(tmp, target, **kw)
            except BaseException:
                try:
                    smbclient.remove(tmp, **kw)
                except Exception:
                    pass
                raise

        self._call(work)

    def remove(self, rel: str) -> None:
        self._call(smbclient.remove, self.unc(rel))


def describe_error(exc: BaseException) -> str:
    """Messaggio d'errore comprensibile per l'utente."""
    from PIL import UnidentifiedImageError
    from smbprotocol import exceptions as ex

    if isinstance(exc, UnidentifiedImageError):
        return tr("Formato non riconosciuto o file danneggiato.")
    if isinstance(exc, MemoryError):
        return tr("Immagine troppo grande per la memoria disponibile.")
    if isinstance(exc, ex.LogonFailure):
        return tr("Nome utente o password non validi.")
    if isinstance(exc, ex.BadNetworkName):
        return tr("La condivisione indicata non esiste sul NAS.")
    if isinstance(exc, ex.AccessDenied) or isinstance(exc, PermissionError):
        return tr("Accesso negato: l'utente non ha i permessi necessari.")
    if isinstance(exc, (ex.ObjectNameNotFound, ex.ObjectPathNotFound, FileNotFoundError)):
        return tr("File o cartella non trovati (forse sono stati spostati o eliminati).")
    if isinstance(exc, socket.gaierror) or "getaddrinfo" in str(exc):
        return tr("Nome del server non risolto: controlla l'indirizzo del NAS.")
    if isinstance(exc, (TimeoutError, socket.timeout, ConnectionRefusedError)) or \
            "timed out" in str(exc).lower() or "failed to connect" in str(exc).lower():
        return tr("Il NAS non risponde: controlla indirizzo, porta, VPN o firewall.")
    if isinstance(exc, (SMBConnectionClosed, ConnectionError)):
        return tr("Connessione con il NAS interrotta.")
    if isinstance(exc, SMBException):
        return tr("Errore SMB: {exc}", exc=exc)
    return f"{type(exc).__name__}: {exc}"
