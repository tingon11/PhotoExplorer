# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Thread di lavoro unico per tutte le operazioni di rete.

Tutte le operazioni SMB passano da qui, in ordine: così una rotazione salvata è sempre
completata prima di una successiva lettura/copia dello stesso file. I risultati vengono
consegnati al thread della GUI tramite una coda letta con ``after()``.
"""
from __future__ import annotations

import itertools
import queue
import threading
from typing import Any, Callable

HIGH = 0      # azioni dell'utente e foto corrente
LOW = 1       # precaricamento

Callback = Callable[[Any], None] | None


class Worker:
    def __init__(self) -> None:
        self._tasks: queue.PriorityQueue = queue.PriorityQueue()
        self._results: queue.Queue = queue.Queue()
        self._seq = itertools.count()
        self._busy_writes = 0
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run, name="smb-worker", daemon=True)
        self._thread.start()

    def submit(self, fn: Callable[[], Any], on_done: Callback = None, on_error: Callback = None,
               priority: int = HIGH, is_write: bool = False) -> None:
        if is_write:
            with self._lock:
                self._busy_writes += 1
        self._tasks.put((priority, next(self._seq), fn, on_done, on_error, is_write))

    @property
    def writes_pending(self) -> int:
        with self._lock:
            return self._busy_writes

    def _run(self) -> None:
        while True:
            _, _, fn, on_done, on_error, is_write = self._tasks.get()
            if fn is None:
                return
            try:
                result = fn()
            except BaseException as exc:  # noqa: BLE001 - l'errore va mostrato nella GUI
                self._results.put((on_error, exc))
            else:
                self._results.put((on_done, result))
            finally:
                if is_write:
                    with self._lock:
                        self._busy_writes -= 1

    def process_results(self, limit: int = 20) -> None:
        """Da chiamare dal thread della GUI."""
        for _ in range(limit):
            try:
                callback, value = self._results.get_nowait()
            except queue.Empty:
                return
            if callback is not None:
                callback(value)

    def stop(self) -> None:
        self._tasks.put((-1, -1, None, None, None, False))
