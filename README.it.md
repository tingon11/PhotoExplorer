# PhotoExplorer

*[English version](README.md)*

Visualizzatore di foto per NAS (QNAP e simili, via SMB) e per cartelle del PC, hard disk e
chiavette USB, con interfaccia scura in customtkinter.
Pensato per passare in rassegna grandi archivi di foto: ricorda quelle già viste, permette di
ruotarle, eliminarle e copiarle in una cartella locale per la stampa.

**Autore: Andrea Cumini — [www.osintinfo.net](https://www.osintinfo.net) — andrea@osintinfo.net**

## Funzioni

- Connessione a una cartella condivisa SMB (utente e password; la password può essere ricordata
  in Gestione credenziali di Windows).
- In alternativa, foto in una cartella del PC, di un hard disk esterno o di una chiavetta USB.
- Elenco delle foto della cartella selezionata e di tutte le sue sottocartelle.
- Memoria delle foto già viste, con l'opzione "Salta le foto già viste" (per i dischi locali è
  legata al disco, non alla lettera di unità).
- Rotazione salvata sul file (i dati EXIF vengono conservati).
- Eliminazione con doppia conferma (sui dischi locali il file va nel Cestino).
- Copia nella cartella per la stampa (l'originale non viene mai spostato), con data di scatto
  opzionale in rosso in basso a destra.
- Data di scatto e posizione GPS dai dati EXIF; un clic apre il punto su Google Maps nel browser.
- Foto preferite: si segnano con un pulsante (o il tasto F) e si possono vedere da sole. Le foto
  mandate in stampa diventano preferite automaticamente e sono segnate da un'icona nell'elenco.
- Interfaccia in italiano, inglese, spagnolo, tedesco e francese, selezionabile dalla barra in alto.
- Azzeramento completo dei dati (foto viste, preferite, stampe) con conferma.
- Zoom con la rotella del mouse e spostamento trascinando.
- Formati: JPG, PNG, WEBP, TIFF, BMP, GIF e HEIC (con `pillow-heif`).

## Tasti

| Tasto | Azione |
|---|---|
| P / L | foto successiva / precedente |
| W / Q | ruota a destra / a sinistra |
| D, poi C | elimina (D prepara, C conferma; Esc annulla) |
| H | copia la foto nella cartella per la stampa |
| F | aggiunge o toglie la foto dalle preferite |
| Rotella / trascinamento | zoom / sposta la foto ingrandita |

Ogni comando ha anche il suo pulsante nell'interfaccia.

## Installazione

Serve Python 3.11 o successivo su Windows.

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Per creare un unico eseguibile (`dist\PhotoExplorer.exe`) con PyInstaller:

```
.venv\Scripts\python.exe build.py
```

Impostazioni e memoria delle foto viste sono salvate in `%APPDATA%\PhotoExplorer`.

## Traduzioni

Nel codice i testi sono in italiano dentro `tr("…")`; le altre lingue sono in
`photoexplorer/translations.py`. Per controllare che non manchi nulla dopo una modifica:

```
.venv\Scripts\python.exe tests\test_translations.py
```

Per aggiungere una lingua basta aggiungerne il codice in `LANGUAGES` (`photoexplorer/i18n.py`) e le
relative traduzioni in `translations.py`.

## Licenza e attribuzione

Copyright (C) 2026 Andrea Cumini. Software libero distribuito con licenza
[GNU GPL versione 3](LICENSE), con i [termini aggiuntivi](ADDITIONAL_TERMS.txt) previsti
dall'art. 7(b) della licenza. Nessuna garanzia.

In pratica: puoi usarlo, copiarlo, modificarlo e ridistribuirlo, ma ogni copia e ogni opera
derivata deve

- restare sotto GPLv3, con il codice sorgente disponibile;
- conservare in modo ben visibile, nei file sorgente e nell'interfaccia del programma,
  l'attribuzione **Andrea Cumini — https://www.osintinfo.net — andrea@osintinfo.net**;
- indicare chiaramente di essere una versione modificata.

## Librerie di terze parti

Il sorgente usa, senza includerle, queste librerie (ognuna con la propria licenza):
customtkinter (MIT), Pillow (MIT-CMU), smbprotocol e pyspnego (MIT), keyring (MIT),
pillow-heif (BSD-3-Clause).

I pacchetti binari di `pillow-heif` incorporano libheif e libde265 (LGPLv3) e x265 (GPLv2 o
successiva), tutte licenze compatibili con la GPLv3 di questo programma. Chi distribuisce
l'eseguibile deve quindi distribuirlo sotto GPLv3, rendendo disponibile il codice sorgente.

La posizione GPS viene aperta con un normale indirizzo di Google Maps nel browser dell'utente:
il programma non scarica né incorpora mappe.
