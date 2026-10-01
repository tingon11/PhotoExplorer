# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
import sys

import customtkinter as ctk

from photoexplorer.app import PhotoExplorerApp


def main() -> None:
    if sys.platform == "win32":
        # icona propria nella barra delle applicazioni invece di quella di Python
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PhotoExplorer")
        except Exception:
            pass
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    PhotoExplorerApp().mainloop()


if __name__ == "__main__":
    main()
