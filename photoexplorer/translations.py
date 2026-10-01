# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Traduzioni dell'interfaccia: testo italiano (com'è scritto nel codice) -> altre lingue.

Regole: gli stessi segnaposto ``{nome}`` dell'italiano, gli stessi spazi iniziali e finali
(servono all'impaginazione), le stesse lettere dei tasti (Q, W, D, C, F, H, L, P).
"""

WEEKDAYS = {
    "it": ("lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"),
    "en": ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
    "es": ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"),
    "de": ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"),
    "fr": ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"),
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    # --- barra in alto ---------------------------------------------------------------------
    "Connetti al NAS…": {
        "en": "Connect to NAS…", "es": "Conectar al NAS…", "de": "Mit NAS verbinden…", "fr": "Connexion au NAS…"},
    "Cartella PC / USB…": {
        "en": "PC / USB folder…", "es": "Carpeta PC / USB…", "de": "PC-/USB-Ordner…", "fr": "Dossier PC / USB…"},
    "Cartella stampa…": {
        "en": "Print folder…", "es": "Carpeta de impresión…", "de": "Druckordner…", "fr": "Dossier d'impression…"},
    "Apri cartella stampa": {
        "en": "Open print folder", "es": "Abrir carpeta impresión", "de": "Druckordner öffnen",
        "fr": "Ouvrir dossier impression"},
    "●  Nessuna sorgente aperta": {
        "en": "●  No source open", "es": "●  Ninguna fuente abierta", "de": "●  Keine Quelle geöffnet",
        "fr": "●  Aucune source ouverte"},
    "Connesso a  {root}": {
        "en": "Connected to  {root}", "es": "Conectado a  {root}", "de": "Verbunden mit  {root}",
        "fr": "Connecté à  {root}"},
    "Cartella locale  {root}": {
        "en": "Local folder  {root}", "es": "Carpeta local  {root}", "de": "Lokaler Ordner  {root}",
        "fr": "Dossier local  {root}"},

    # --- pannello laterale -----------------------------------------------------------------
    "Cartella superiore": {
        "en": "Parent folder", "es": "Carpeta superior", "de": "Übergeordneter Ordner", "fr": "Dossier parent"},
    "Aggiorna": {"en": "Refresh", "es": "Actualizar", "de": "Aktualisieren", "fr": "Actualiser"},
    "Cartelle  (doppio clic per aprire)": {
        "en": "Folders  (double-click to open)", "es": "Carpetas  (doble clic para abrir)",
        "de": "Ordner  (Doppelklick zum Öffnen)", "fr": "Dossiers  (double-clic pour ouvrir)"},
    "Foto": {"en": "Photos", "es": "Fotos", "de": "Fotos", "fr": "Photos"},
    "Foto  ({count}, {new} da vedere){searching}": {
        "en": "Photos  ({count}, {new} to view){searching}", "es": "Fotos  ({count}, {new} por ver){searching}",
        "de": "Fotos  ({count}, {new} ungesehen){searching}", "fr": "Photos  ({count}, {new} à voir){searching}"},
    "Preferite  ({count}){searching}": {
        "en": "Favorites  ({count}){searching}", "es": "Favoritas  ({count}){searching}",
        "de": "Favoriten  ({count}){searching}", "fr": "Favorites  ({count}){searching}"},
    "  · ricerca…": {"en": "  · searching…", "es": "  · buscando…", "de": "  · Suche…", "fr": "  · recherche…"},
    "   ✓ tutte viste": {
        "en": "   ✓ all viewed", "es": "   ✓ todas vistas", "de": "   ✓ alle angesehen", "fr": "   ✓ toutes vues"},
    "   {seen}/{total} viste": {
        "en": "   {seen}/{total} viewed", "es": "   {seen}/{total} vistas", "de": "   {seen}/{total} angesehen",
        "fr": "   {seen}/{total} vues"},
    "Includi le foto delle sottocartelle": {
        "en": "Include photos from subfolders", "es": "Incluir fotos de las subcarpetas",
        "de": "Fotos aus Unterordnern einbeziehen", "fr": "Inclure les photos des sous-dossiers"},
    "Salta le foto già viste": {
        "en": "Skip photos already viewed", "es": "Saltar las fotos ya vistas",
        "de": "Bereits angesehene Fotos überspringen", "fr": "Passer les photos déjà vues"},
    "Mostra solo le preferite": {
        "en": "Show favorites only", "es": "Mostrar solo las favoritas", "de": "Nur Favoriten anzeigen",
        "fr": "Afficher seulement les favorites"},
    "Ordina per": {"en": "Sort by", "es": "Ordenar por", "de": "Sortieren nach", "fr": "Trier par"},
    "Nome": {"en": "Name", "es": "Nombre", "de": "Name", "fr": "Nom"},
    "Data": {"en": "Date", "es": "Fecha", "de": "Datum", "fr": "Date"},
    "Segna tutta la cartella come “non vista”": {
        "en": "Mark the whole folder as “not viewed”", "es": "Marcar toda la carpeta como “no vista”",
        "de": "Ganzen Ordner als „ungesehen“ markieren", "fr": "Marquer tout le dossier comme « non vu »"},
    "Cartella dei dati": {"en": "Data folder", "es": "Carpeta de datos", "de": "Datenordner", "fr": "Dossier des données"},
    "Azzera tutto…": {"en": "Reset all…", "es": "Borrar todo…", "de": "Alles zurücksetzen…", "fr": "Tout réinitialiser…"},

    # --- barra dei comandi (le lettere finali sono i tasti) ---------------------------------
    "Ruota sx  Q": {"en": "Rotate L  Q", "es": "Girar izq.  Q", "de": "Drehen L  Q", "fr": "Tourner G  Q"},
    "Ruota dx  W": {"en": "Rotate R  W", "es": "Girar der.  W", "de": "Drehen R  W", "fr": "Tourner D  W"},
    "Elimina  D": {"en": "Delete  D", "es": "Eliminar  D", "de": "Löschen  D", "fr": "Supprimer  D"},
    "Conferma  C": {"en": "Confirm  C", "es": "Confirmar  C", "de": "Bestätigen  C", "fr": "Confirmer  C"},
    "Preferita  F": {"en": "Favorite  F", "es": "Favorita  F", "de": "Favorit  F", "fr": "Favorite  F"},
    "Stampa data": {"en": "Print date", "es": "Imprimir fecha", "de": "Datum drucken", "fr": "Imprimer date"},
    "Indietro  L": {"en": "Back  L", "es": "Atrás  L", "de": "Zurück  L", "fr": "Précédente  L"},
    "Stampa  H": {"en": "Print  H", "es": "Imprimir  H", "de": "Drucken  H", "fr": "Imprimer  H"},
    "Avanti  P": {"en": "Next  P", "es": "Siguiente  P", "de": "Weiter  P", "fr": "Suivante  P"},
    "L / P indietro / avanti   ·   rotella: zoom, trascina: sposta   ·   Q / W ruota   ·   D elimina, C conferma   ·   "
    "F preferita   ·   H stampa   ·   Esc annulla": {
        "en": "L / P back / next   ·   wheel: zoom, drag: move   ·   Q / W rotate   ·   D delete, C confirm   ·   "
              "F favorite   ·   H print   ·   Esc cancel",
        "es": "L / P atrás / siguiente   ·   rueda: zoom, arrastrar: mover   ·   Q / W girar   ·   D eliminar, "
              "C confirmar   ·   F favorita   ·   H imprimir   ·   Esc cancelar",
        "de": "L / P zurück / weiter   ·   Mausrad: Zoom, Ziehen: Verschieben   ·   Q / W drehen   ·   D löschen, "
              "C bestätigen   ·   F Favorit   ·   H drucken   ·   Esc abbrechen",
        "fr": "L / P précédente / suivante   ·   molette : zoom, glisser : déplacer   ·   Q / W tourner   ·   "
              "D supprimer, C confirmer   ·   F favorite   ·   H imprimer   ·   Échap annuler"},

    # --- informazioni sulla foto -----------------------------------------------------------
    "  GIÀ VISTA  ": {"en": "  VIEWED  ", "es": "  YA VISTA  ", "de": "  ANGESEHEN  ", "fr": "  DÉJÀ VUE  "},
    "  NUOVA  ": {"en": "  NEW  ", "es": "  NUEVA  ", "de": "  NEU  ", "fr": "  NOUVELLE  "},
    " PREFERITA  ": {"en": " FAVORITE  ", "es": " FAVORITA  ", "de": " FAVORIT  ", "fr": " FAVORITE  "},
    " IN STAMPA  ": {"en": " TO PRINT  ", "es": " PARA IMPRIMIR  ", "de": " ZUM DRUCK  ", "fr": " À IMPRIMER  "},
    " IN STAMPA · CON DATA  ": {
        "en": " TO PRINT · WITH DATE  ", "es": " PARA IMPRIMIR · CON FECHA  ", "de": " ZUM DRUCK · MIT DATUM  ",
        "fr": " À IMPRIMER · AVEC DATE  "},
    " GIÀ STAMPATA  ": {
        "en": " ALREADY PRINTED  ", "es": " YA IMPRESA  ", "de": " BEREITS GEDRUCKT  ", "fr": " DÉJÀ IMPRIMÉE  "},
    "cartella: {subfolder}": {
        "en": "folder: {subfolder}", "es": "carpeta: {subfolder}", "de": "Ordner: {subfolder}",
        "fr": "dossier : {subfolder}"},
    "file: ": {"en": "file: ", "es": "archivo: ", "de": "Datei: ", "fr": "fichier : "},
    "Scattata {weekday} {date} alle {time}": {
        "en": "Taken {weekday} {date} at {time}", "es": "Tomada el {weekday} {date} a las {time}",
        "de": "Aufgenommen {weekday} {date} um {time}", "fr": "Prise {weekday} {date} à {time}"},
    " Data di scatto non presente": {
        "en": " No capture date", "es": " Sin fecha de captura", "de": " Kein Aufnahmedatum",
        "fr": " Pas de date de prise de vue"},
    "Google Maps aperto sulla posizione della foto: {coords}": {
        "en": "Google Maps opened at the photo's location: {coords}",
        "es": "Google Maps abierto en la ubicación de la foto: {coords}",
        "de": "Google Maps am Aufnahmeort des Fotos geöffnet: {coords}",
        "fr": "Google Maps ouvert sur le lieu de la photo : {coords}"},

    # --- apertura di cartelle e ricerca ----------------------------------------------------
    "Connettiti al NAS o apri una cartella del PC per iniziare": {
        "en": "Connect to the NAS or open a folder on the PC to get started",
        "es": "Conéctate al NAS o abre una carpeta del PC para empezar",
        "de": "Verbinden Sie sich mit dem NAS oder öffnen Sie einen Ordner auf dem PC",
        "fr": "Connectez-vous au NAS ou ouvrez un dossier du PC pour commencer"},
    "Apertura di {root}…": {
        "en": "Opening {root}…", "es": "Abriendo {root}…", "de": "{root} wird geöffnet…", "fr": "Ouverture de {root}…"},
    "Apertura di {path}…": {
        "en": "Opening {path}…", "es": "Abriendo {path}…", "de": "{path} wird geöffnet…", "fr": "Ouverture de {path}…"},
    "Cartella con le foto (PC, hard disk o chiavetta USB)": {
        "en": "Folder with the photos (PC, hard disk or USB stick)",
        "es": "Carpeta con las fotos (PC, disco duro o memoria USB)",
        "de": "Ordner mit den Fotos (PC, Festplatte oder USB-Stick)",
        "fr": "Dossier contenant les photos (PC, disque dur ou clé USB)"},
    "Impossibile aprire {root}: {msg}": {
        "en": "Cannot open {root}: {msg}", "es": "No se puede abrir {root}: {msg}",
        "de": "{root} kann nicht geöffnet werden: {msg}", "fr": "Impossible d'ouvrir {root} : {msg}"},
    "Cartella non accessibile": {
        "en": "Folder not accessible", "es": "Carpeta no accesible", "de": "Ordner nicht zugänglich",
        "fr": "Dossier inaccessible"},
    "Impossibile aprire la cartella: {error}": {
        "en": "Cannot open the folder: {error}", "es": "No se puede abrir la carpeta: {error}",
        "de": "Der Ordner kann nicht geöffnet werden: {error}", "fr": "Impossible d'ouvrir le dossier : {error}"},
    "Cerco le foto nelle sottocartelle…": {
        "en": "Looking for photos in the subfolders…", "es": "Buscando fotos en las subcarpetas…",
        "de": "Fotos werden in den Unterordnern gesucht…", "fr": "Recherche des photos dans les sous-dossiers…"},
    "Cerco le foto preferite nelle sottocartelle…": {
        "en": "Looking for favorite photos in the subfolders…", "es": "Buscando fotos favoritas en las subcarpetas…",
        "de": "Favoriten werden in den Unterordnern gesucht…",
        "fr": "Recherche des photos favorites dans les sous-dossiers…"},
    "Cerco nelle sottocartelle…  {scan_dirs_read} cartelle lette, {count} foto trovate": {
        "en": "Searching subfolders…  {scan_dirs_read} folders read, {count} photos found",
        "es": "Buscando en las subcarpetas…  {scan_dirs_read} carpetas leídas, {count} fotos encontradas",
        "de": "Unterordner werden durchsucht…  {scan_dirs_read} Ordner gelesen, {count} Fotos gefunden",
        "fr": "Recherche dans les sous-dossiers…  {scan_dirs_read} dossiers lus, {count} photos trouvées"},
    "Cerco foto nuove nelle sottocartelle…\n\n{count} foto trovate finora, tutte già viste.\n"
    "Puoi comunque sceglierne una dall'elenco.": {
        "en": "Looking for new photos in the subfolders…\n\n{count} photos found so far, all already viewed.\n"
              "You can still pick one from the list.",
        "es": "Buscando fotos nuevas en las subcarpetas…\n\n{count} fotos encontradas hasta ahora, todas ya vistas.\n"
              "Puedes elegir una de la lista de todos modos.",
        "de": "Neue Fotos werden in den Unterordnern gesucht…\n\n{count} Fotos bisher gefunden, alle bereits "
              "angesehen.\nSie können trotzdem eines aus der Liste wählen.",
        "fr": "Recherche de nouvelles photos dans les sous-dossiers…\n\n{count} photos trouvées pour l'instant, "
              "toutes déjà vues.\nVous pouvez quand même en choisir une dans la liste."},
    " in {scan_dirs_read} cartelle": {
        "en": " in {scan_dirs_read} folders", "es": " en {scan_dirs_read} carpetas", "de": " in {scan_dirs_read} Ordnern",
        "fr": " dans {scan_dirs_read} dossiers"},
    "  ({scan_errors} cartelle non leggibili)": {
        "en": "  ({scan_errors} folders could not be read)", "es": "  ({scan_errors} carpetas no legibles)",
        "de": "  ({scan_errors} Ordner nicht lesbar)", "fr": "  ({scan_errors} dossiers illisibles)"},
    "{count} foto preferite.{errors}": {
        "en": "{count} favorite photos.{errors}", "es": "{count} fotos favoritas.{errors}",
        "de": "{count} Favoriten.{errors}", "fr": "{count} photos favorites.{errors}"},
    "Nessuna foto{where}.{errors}": {
        "en": "No photos{where}.{errors}", "es": "Ninguna foto{where}.{errors}", "de": "Keine Fotos{where}.{errors}",
        "fr": "Aucune photo{where}.{errors}"},
    "{count} foto{where}, {new_count} mai viste.{errors}": {
        "en": "{count} photos{where}, {new_count} never viewed.{errors}",
        "es": "{count} fotos{where}, {new_count} nunca vistas.{errors}",
        "de": "{count} Fotos{where}, {new_count} noch nie angesehen.{errors}",
        "fr": "{count} photos{where}, {new_count} jamais vues.{errors}"},
    "{count} foto{where}: le hai già viste tutte.{errors}": {
        "en": "{count} photos{where}: you have already viewed them all.{errors}",
        "es": "{count} fotos{where}: ya las has visto todas.{errors}",
        "de": "{count} Fotos{where}: Sie haben bereits alle angesehen.{errors}",
        "fr": "{count} photos{where} : vous les avez déjà toutes vues.{errors}"},
    "Nessuna foto in questa cartella": {
        "en": "No photos in this folder", "es": "Ninguna foto en esta carpeta", "de": "Keine Fotos in diesem Ordner",
        "fr": "Aucune photo dans ce dossier"},
    "Nessuna foto in questa cartella né nelle sue sottocartelle": {
        "en": "No photos in this folder or its subfolders", "es": "Ninguna foto en esta carpeta ni en sus subcarpetas",
        "de": "Keine Fotos in diesem Ordner und seinen Unterordnern",
        "fr": "Aucune photo dans ce dossier ni dans ses sous-dossiers"},
    "Nessuna altra foto in questa cartella": {
        "en": "No more photos in this folder", "es": "No hay más fotos en esta carpeta",
        "de": "Keine weiteren Fotos in diesem Ordner", "fr": "Plus aucune photo dans ce dossier"},
    "1 sottocartella a sinistra": {
        "en": "1 subfolder on the left", "es": "1 subcarpeta a la izquierda", "de": "1 Unterordner links",
        "fr": "1 sous-dossier à gauche"},
    "{n} sottocartelle a sinistra": {
        "en": "{n} subfolders on the left", "es": "{n} subcarpetas a la izquierda", "de": "{n} Unterordner links",
        "fr": "{n} sous-dossiers à gauche"},
    "Nessuna foto preferita in questa cartella": {
        "en": "No favorite photos in this folder", "es": "Ninguna foto favorita en esta carpeta",
        "de": "Keine Favoriten in diesem Ordner", "fr": "Aucune photo favorite dans ce dossier"},
    "Nessuna foto preferita in questa cartella né nelle sue sottocartelle": {
        "en": "No favorite photos in this folder or its subfolders",
        "es": "Ninguna foto favorita en esta carpeta ni en sus subcarpetas",
        "de": "Keine Favoriten in diesem Ordner und seinen Unterordnern",
        "fr": "Aucune photo favorite dans ce dossier ni dans ses sous-dossiers"},
    "Per aggiungerne una usa il pulsante Preferita (tasto F).": {
        "en": "To add one, use the Favorite button (F key).", "es": "Para añadir una usa el botón Favorita (tecla F).",
        "de": "Zum Hinzufügen die Schaltfläche „Favorit“ verwenden (Taste F).",
        "fr": "Pour en ajouter une, utilisez le bouton Favorite (touche F)."},
    "Azzera foto viste": {
        "en": "Reset viewed photos", "es": "Borrar fotos vistas", "de": "Angesehene Fotos zurücksetzen",
        "fr": "Réinitialiser les photos vues"},
    "Segnare tutte le foto di\n{path}\ne di tutte le sue sottocartelle come non ancora viste?": {
        "en": "Mark all photos in\n{path}\nand in all its subfolders as not yet viewed?",
        "es": "¿Marcar todas las fotos de\n{path}\ny de todas sus subcarpetas como aún no vistas?",
        "de": "Alle Fotos in\n{path}\nund in allen Unterordnern als noch nicht angesehen markieren?",
        "fr": "Marquer toutes les photos de\n{path}\net de tous ses sous-dossiers comme non encore vues ?"},
    "Segnare tutte le foto di\n{path}\ncome non ancora viste?": {
        "en": "Mark all photos in\n{path}\nas not yet viewed?", "es": "¿Marcar todas las fotos de\n{path}\ncomo aún no vistas?",
        "de": "Alle Fotos in\n{path}\nals noch nicht angesehen markieren?",
        "fr": "Marquer toutes les photos de\n{path}\ncomme non encore vues ?"},
    "Memoria delle foto viste azzerata.": {
        "en": "Viewed-photo memory reset.", "es": "Memoria de fotos vistas borrada.",
        "de": "Liste der angesehenen Fotos zurückgesetzt.", "fr": "Mémoire des photos vues réinitialisée."},

    # --- navigazione -----------------------------------------------------------------------
    "Caricamento…": {"en": "Loading…", "es": "Cargando…", "de": "Wird geladen…", "fr": "Chargement…"},
    "Impossibile aprire la foto\n\n{error}": {
        "en": "Cannot open the photo\n\n{error}", "es": "No se puede abrir la foto\n\n{error}",
        "de": "Das Foto kann nicht geöffnet werden\n\n{error}", "fr": "Impossible d'ouvrir la photo\n\n{error}"},
    "Attendi che la foto compaia, così non ne salti nessuna. Per saltarla apposta scegli un'altra foto dall'elenco.": {
        "en": "Wait for the photo to appear, so you don't skip any. To skip it on purpose, pick another photo from "
              "the list.",
        "es": "Espera a que aparezca la foto, así no te saltas ninguna. Para saltarla a propósito elige otra foto "
              "de la lista.",
        "de": "Warten Sie, bis das Foto erscheint, damit keines übersprungen wird. Zum absichtlichen Überspringen "
              "ein anderes Foto in der Liste wählen.",
        "fr": "Attendez que la photo s'affiche pour n'en sauter aucune. Pour la passer volontairement, choisissez "
              "une autre photo dans la liste."},
    "Sei già alla prima foto della cartella.": {
        "en": "You are already at the first photo of the folder.", "es": "Ya estás en la primera foto de la carpeta.",
        "de": "Sie sind bereits beim ersten Foto des Ordners.", "fr": "Vous êtes déjà à la première photo du dossier."},
    "Sei all'ultima foto della cartella.": {
        "en": "You are at the last photo of the folder.", "es": "Estás en la última foto de la carpeta.",
        "de": "Sie sind beim letzten Foto des Ordners.", "fr": "Vous êtes à la dernière photo du dossier."},
    "Sei all'ultima foto preferita.": {
        "en": "You are at the last favorite photo.", "es": "Estás en la última foto favorita.",
        "de": "Sie sind beim letzten Favoriten.", "fr": "Vous êtes à la dernière photo favorite."},
    "Non ci sono altre foto da vedere dopo questa.": {
        "en": "There are no more photos to view after this one.", "es": "No hay más fotos por ver después de esta.",
        "de": "Nach diesem Foto gibt es keine ungesehenen Fotos mehr.",
        "fr": "Il n'y a plus de photos à voir après celle-ci."},
    " La ricerca nelle sottocartelle è ancora in corso: riprova tra poco.": {
        "en": " The subfolder search is still running: try again shortly.",
        "es": " La búsqueda en las subcarpetas sigue en curso: inténtalo de nuevo en un momento.",
        "de": " Die Suche in den Unterordnern läuft noch: bitte gleich noch einmal versuchen.",
        "fr": " La recherche dans les sous-dossiers est encore en cours : réessayez dans un instant."},
    "  ·  carico i dettagli…": {
        "en": "  ·  loading details…", "es": "  ·  cargando detalles…", "de": "  ·  Details werden geladen…",
        "fr": "  ·  chargement des détails…"},

    # --- preferite -------------------------------------------------------------------------
    "Aggiunta alle preferite: {name}": {
        "en": "Added to favorites: {name}", "es": "Añadida a favoritas: {name}",
        "de": "Zu den Favoriten hinzugefügt: {name}", "fr": "Ajoutée aux favorites : {name}"},
    "Tolta dalle preferite: {name}": {
        "en": "Removed from favorites: {name}", "es": "Quitada de favoritas: {name}",
        "de": "Aus den Favoriten entfernt: {name}", "fr": "Retirée des favorites : {name}"},
    "  (resta nell'elenco fino al prossimo aggiornamento)": {
        "en": "  (stays in the list until the next refresh)", "es": "  (sigue en la lista hasta la próxima actualización)",
        "de": "  (bleibt bis zur nächsten Aktualisierung in der Liste)",
        "fr": "  (reste dans la liste jusqu'à la prochaine actualisation)"},

    # --- rotazione -------------------------------------------------------------------------
    "Rotazione {view_rotation}° — salvataggio tra poco…": {
        "en": "Rotation {view_rotation}° — saving shortly…", "es": "Rotación {view_rotation}° — se guardará en breve…",
        "de": "Drehung {view_rotation}° — wird gleich gespeichert…",
        "fr": "Rotation {view_rotation}° — enregistrement dans un instant…"},
    "Attendi che la foto sia caricata prima di ruotarla.": {
        "en": "Wait for the photo to load before rotating it.", "es": "Espera a que la foto se cargue antes de girarla.",
        "de": "Warten Sie, bis das Foto geladen ist, bevor Sie es drehen.",
        "fr": "Attendez que la photo soit chargée avant de la tourner."},
    "Le immagini animate o multipagina non possono essere ruotate.": {
        "en": "Animated or multi-page images cannot be rotated.",
        "es": "Las imágenes animadas o de varias páginas no se pueden girar.",
        "de": "Animierte oder mehrseitige Bilder können nicht gedreht werden.",
        "fr": "Les images animées ou multipages ne peuvent pas être tournées."},
    "Le immagini animate o multipagina non possono essere modificate.": {
        "en": "Animated or multi-page images cannot be modified.",
        "es": "Las imágenes animadas o de varias páginas no se pueden modificar.",
        "de": "Animierte oder mehrseitige Bilder können nicht verändert werden.",
        "fr": "Les images animées ou multipages ne peuvent pas être modifiées."},
    "Salvataggio della rotazione di {name}…": {
        "en": "Saving the rotation of {name}…", "es": "Guardando la rotación de {name}…",
        "de": "Drehung von {name} wird gespeichert…", "fr": "Enregistrement de la rotation de {name}…"},
    "Rotazione salvata: {name}{extra}": {
        "en": "Rotation saved: {name}{extra}", "es": "Rotación guardada: {name}{extra}",
        "de": "Drehung gespeichert: {name}{extra}", "fr": "Rotation enregistrée : {name}{extra}"},
    " (aggiornata anche la copia per la stampa)": {
        "en": " (print copy updated too)", "es": " (también se actualizó la copia para imprimir)",
        "de": " (Druckkopie ebenfalls aktualisiert)", "fr": " (copie pour l'impression mise à jour aussi)"},
    "Rotazione NON salvata: {msg}": {
        "en": "Rotation NOT saved: {msg}", "es": "Rotación NO guardada: {msg}", "de": "Drehung NICHT gespeichert: {msg}",
        "fr": "Rotation NON enregistrée : {msg}"},
    "Rotazione non salvata": {
        "en": "Rotation not saved", "es": "Rotación no guardada", "de": "Drehung nicht gespeichert",
        "fr": "Rotation non enregistrée"},

    # --- eliminazione ----------------------------------------------------------------------
    "Eliminare definitivamente questa foto dal NAS?": {
        "en": "Permanently delete this photo from the NAS?", "es": "¿Eliminar definitivamente esta foto del NAS?",
        "de": "Dieses Foto endgültig vom NAS löschen?", "fr": "Supprimer définitivement cette photo du NAS ?"},
    "Eliminare questa foto? (va nel Cestino; sulle chiavette è definitiva)": {
        "en": "Delete this photo? (goes to the Recycle Bin; permanent on USB sticks)",
        "es": "¿Eliminar esta foto? (va a la Papelera; en memorias USB es definitivo)",
        "de": "Dieses Foto löschen? (kommt in den Papierkorb; auf USB-Sticks endgültig)",
        "fr": "Supprimer cette photo ? (va dans la Corbeille ; définitif sur clé USB)"},
    "Eliminare questa foto?": {
        "en": "Delete this photo?", "es": "¿Eliminar esta foto?", "de": "Dieses Foto löschen?",
        "fr": "Supprimer cette photo ?"},
    "Premi  C  (o il pulsante Conferma) per eliminarla  ·  Esc per annullare": {
        "en": "Press  C  (or the Confirm button) to delete it  ·  Esc to cancel",
        "es": "Pulsa  C  (o el botón Confirmar) para eliminarla  ·  Esc para cancelar",
        "de": "C  drücken (oder „Bestätigen“) zum Löschen  ·  Esc zum Abbrechen",
        "fr": "Appuyez sur  C  (ou le bouton Confirmer) pour la supprimer  ·  Échap pour annuler"},
    "Eliminare {name}?  Premi C per confermare, Esc per annullare.": {
        "en": "Delete {name}?  Press C to confirm, Esc to cancel.",
        "es": "¿Eliminar {name}?  Pulsa C para confirmar, Esc para cancelar.",
        "de": "{name} löschen?  C zum Bestätigen, Esc zum Abbrechen.",
        "fr": "Supprimer {name} ?  Appuyez sur C pour confirmer, Échap pour annuler."},
    "Eliminazione annullata.": {
        "en": "Deletion cancelled.", "es": "Eliminación cancelada.", "de": "Löschen abgebrochen.",
        "fr": "Suppression annulée."},
    "Per eliminare premi prima D, poi C per confermare.": {
        "en": "To delete, press D first, then C to confirm.", "es": "Para eliminar pulsa primero D y luego C para confirmar.",
        "de": "Zum Löschen zuerst D, dann C zum Bestätigen drücken.",
        "fr": "Pour supprimer, appuyez d'abord sur D, puis sur C pour confirmer."},
    "Eliminazione di {name}…": {
        "en": "Deleting {name}…", "es": "Eliminando {name}…", "de": "{name} wird gelöscht…",
        "fr": "Suppression de {name}…"},
    "Eliminata: {name}": {"en": "Deleted: {name}", "es": "Eliminada: {name}", "de": "Gelöscht: {name}", "fr": "Supprimée : {name}"},
    "Eliminazione non riuscita: {msg}": {
        "en": "Deletion failed: {msg}", "es": "No se pudo eliminar: {msg}", "de": "Löschen fehlgeschlagen: {msg}",
        "fr": "Échec de la suppression : {msg}"},
    "Eliminazione non riuscita": {
        "en": "Deletion failed", "es": "No se pudo eliminar", "de": "Löschen fehlgeschlagen",
        "fr": "Échec de la suppression"},

    # --- stampa ----------------------------------------------------------------------------
    "Stampa data attiva: la data di scatto compare in rosso nell'anteprima e nelle copie salvate con H "
    "(la foto originale non cambia).": {
        "en": "Print date on: the capture date appears in red in the preview and in the copies saved with H "
              "(the original photo is not changed).",
        "es": "Imprimir fecha activado: la fecha de captura aparece en rojo en la vista previa y en las copias "
              "guardadas con H (la foto original no cambia).",
        "de": "Datum drucken aktiv: Das Aufnahmedatum erscheint rot in der Vorschau und in den mit H gespeicherten "
              "Kopien (das Originalfoto bleibt unverändert).",
        "fr": "Impression de la date activée : la date de prise de vue apparaît en rouge dans l'aperçu et dans les "
              "copies enregistrées avec H (la photo d'origine ne change pas)."},
    "Data disattivata: le copie salvate con H saranno senza data.": {
        "en": "Date off: copies saved with H will have no date.",
        "es": "Fecha desactivada: las copias guardadas con H no tendrán fecha.",
        "de": "Datum aus: Mit H gespeicherte Kopien haben kein Datum.",
        "fr": "Date désactivée : les copies enregistrées avec H n'auront pas de date."},
    "Copia di {name} nella cartella stampa…": {
        "en": "Copying {name} to the print folder…", "es": "Copiando {name} a la carpeta de impresión…",
        "de": "{name} wird in den Druckordner kopiert…", "fr": "Copie de {name} dans le dossier d'impression…"},
    "copia aggiornata": {"en": "copy updated", "es": "copia actualizada", "de": "Kopie aktualisiert", "fr": "copie mise à jour"},
    "copiata": {"en": "copied", "es": "copiada", "de": "kopiert", "fr": "copiée"},
    "  ·  aggiunta alle preferite": {
        "en": "  ·  added to favorites", "es": "  ·  añadida a favoritas", "de": "  ·  zu den Favoriten hinzugefügt",
        "fr": "  ·  ajoutée aux favorites"},
    "Stampa: {action} con la data {date} → {dest}{starred}": {
        "en": "Print: {action} with the date {date} → {dest}{starred}",
        "es": "Impresión: {action} con la fecha {date} → {dest}{starred}",
        "de": "Druck: {action} mit Datum {date} → {dest}{starred}",
        "fr": "Impression : {action} avec la date {date} → {dest}{starred}"},
    "Stampa: {action} SENZA data (la foto non ha la data di scatto EXIF) → {dest}{starred}": {
        "en": "Print: {action} WITHOUT date (the photo has no EXIF capture date) → {dest}{starred}",
        "es": "Impresión: {action} SIN fecha (la foto no tiene fecha de captura EXIF) → {dest}{starred}",
        "de": "Druck: {action} OHNE Datum (das Foto hat kein EXIF-Aufnahmedatum) → {dest}{starred}",
        "fr": "Impression : {action} SANS date (la photo n'a pas de date de prise de vue EXIF) → {dest}{starred}"},
    "Stampa: {action} → {dest}{starred}": {
        "en": "Print: {action} → {dest}{starred}", "es": "Impresión: {action} → {dest}{starred}",
        "de": "Druck: {action} → {dest}{starred}", "fr": "Impression : {action} → {dest}{starred}"},
    "Copia per la stampa non riuscita: {msg}": {
        "en": "Copy for printing failed: {msg}", "es": "No se pudo copiar para imprimir: {msg}",
        "de": "Kopie für den Druck fehlgeschlagen: {msg}", "fr": "Échec de la copie pour l'impression : {msg}"},
    "Copia non riuscita": {"en": "Copy failed", "es": "No se pudo copiar", "de": "Kopieren fehlgeschlagen", "fr": "Échec de la copie"},
    "Cartella in cui copiare le foto da stampare": {
        "en": "Folder where photos to print are copied", "es": "Carpeta donde copiar las fotos para imprimir",
        "de": "Ordner, in den die zu druckenden Fotos kopiert werden",
        "fr": "Dossier où copier les photos à imprimer"},
    "Cartella stampa: {print_dir}": {
        "en": "Print folder: {print_dir}", "es": "Carpeta de impresión: {print_dir}", "de": "Druckordner: {print_dir}",
        "fr": "Dossier d'impression : {print_dir}"},
    "Troppi file con lo stesso nome nella cartella di stampa": {
        "en": "Too many files with the same name in the print folder",
        "es": "Demasiados archivos con el mismo nombre en la carpeta de impresión",
        "de": "Zu viele Dateien mit demselben Namen im Druckordner",
        "fr": "Trop de fichiers portant le même nom dans le dossier d'impression"},

    # --- dati, azzeramento, chiusura -------------------------------------------------------
    "Dati dell'app: {app_dir}  (history.json = foto viste e copie per la stampa)": {
        "en": "App data: {app_dir}  (history.json = viewed photos and print copies)",
        "es": "Datos de la app: {app_dir}  (history.json = fotos vistas y copias para imprimir)",
        "de": "App-Daten: {app_dir}  (history.json = angesehene Fotos und Druckkopien)",
        "fr": "Données de l'application : {app_dir}  (history.json = photos vues et copies pour l'impression)"},
    "Impossibile aprire {app_dir}: {exc}": {
        "en": "Cannot open {app_dir}: {exc}", "es": "No se puede abrir {app_dir}: {exc}",
        "de": "{app_dir} kann nicht geöffnet werden: {exc}", "fr": "Impossible d'ouvrir {app_dir} : {exc}"},
    "Impossibile aprire {folder}: {exc}": {
        "en": "Cannot open {folder}: {exc}", "es": "No se puede abrir {folder}: {exc}",
        "de": "{folder} kann nicht geöffnet werden: {exc}", "fr": "Impossible d'ouvrir {folder} : {exc}"},
    "Impossibile salvare: {exc}": {
        "en": "Cannot save: {exc}", "es": "No se puede guardar: {exc}", "de": "Speichern nicht möglich: {exc}",
        "fr": "Impossible d'enregistrer : {exc}"},
    "Impossibile salvare le impostazioni: {exc}": {
        "en": "Cannot save the settings: {exc}", "es": "No se pueden guardar los ajustes: {exc}",
        "de": "Die Einstellungen können nicht gespeichert werden: {exc}",
        "fr": "Impossible d'enregistrer les paramètres : {exc}"},
    "Dati azzerati: foto viste, preferite e foto mandate in stampa.": {
        "en": "Data reset: viewed photos, favorites and photos sent to print.",
        "es": "Datos borrados: fotos vistas, favoritas y fotos enviadas a imprimir.",
        "de": "Daten zurückgesetzt: angesehene Fotos, Favoriten und zum Druck gesendete Fotos.",
        "fr": "Données réinitialisées : photos vues, favorites et photos envoyées à l'impression."},
    "Dati e impostazioni azzerati: il programma è tornato come al primo avvio.": {
        "en": "Data and settings reset: the program is back to its first-run state.",
        "es": "Datos y ajustes borrados: el programa ha vuelto al estado del primer inicio.",
        "de": "Daten und Einstellungen zurückgesetzt: Das Programm ist wieder wie beim ersten Start.",
        "fr": "Données et paramètres réinitialisés : le programme est revenu à son état du premier lancement."},
    "Attendo la fine dei salvataggi prima di chiudere…": {
        "en": "Waiting for saves to finish before closing…", "es": "Esperando a que terminen los guardados antes de cerrar…",
        "de": "Vor dem Schließen wird auf das Ende der Speichervorgänge gewartet…",
        "fr": "Attente de la fin des enregistrements avant de fermer…"},
    "Azzera tutti i dati": {
        "en": "Reset all data", "es": "Borrar todos los datos", "de": "Alle Daten zurücksetzen",
        "fr": "Réinitialiser toutes les données"},
    "Azzerare tutti i dati di PhotoExplorer?": {
        "en": "Reset all PhotoExplorer data?", "es": "¿Borrar todos los datos de PhotoExplorer?",
        "de": "Alle Daten von PhotoExplorer zurücksetzen?", "fr": "Réinitialiser toutes les données de PhotoExplorer ?"},
    "Verranno cancellati definitivamente:\n   •  l'elenco delle foto già viste\n   •  le foto preferite\n"
    "   •  l'elenco delle foto mandate in stampa\n\nLe foto e le copie nella cartella stampa non vengono toccate.": {
        "en": "The following will be permanently erased:\n   •  the list of photos already viewed\n"
              "   •  the favorite photos\n   •  the list of photos sent to print\n\n"
              "The photos and the copies in the print folder are not touched.",
        "es": "Se borrarán definitivamente:\n   •  la lista de fotos ya vistas\n   •  las fotos favoritas\n"
              "   •  la lista de fotos enviadas a imprimir\n\n"
              "Las fotos y las copias de la carpeta de impresión no se tocan.",
        "de": "Endgültig gelöscht werden:\n   •  die Liste der bereits angesehenen Fotos\n   •  die Favoriten\n"
              "   •  die Liste der zum Druck gesendeten Fotos\n\n"
              "Die Fotos und die Kopien im Druckordner bleiben unberührt.",
        "fr": "Seront définitivement effacés :\n   •  la liste des photos déjà vues\n   •  les photos favorites\n"
              "   •  la liste des photos envoyées à l'impression\n\n"
              "Les photos et les copies du dossier d'impression ne sont pas touchées."},
    "Azzera anche le impostazioni e i dati di connessione\n(indirizzo del NAS, utente, password salvata, cartelle)": {
        "en": "Also reset the settings and connection data\n(NAS address, user, saved password, folders)",
        "es": "Borrar también los ajustes y los datos de conexión\n(dirección del NAS, usuario, contraseña guardada, "
              "carpetas)",
        "de": "Auch Einstellungen und Verbindungsdaten zurücksetzen\n(NAS-Adresse, Benutzer, gespeichertes Passwort, "
              "Ordner)",
        "fr": "Réinitialiser aussi les paramètres et les données de connexion\n(adresse du NAS, utilisateur, "
              "mot de passe enregistré, dossiers)"},
    "Azzera tutto": {"en": "Reset all", "es": "Borrar todo", "de": "Alles zurücksetzen", "fr": "Tout réinitialiser"},
    "Annulla": {"en": "Cancel", "es": "Cancelar", "de": "Abbrechen", "fr": "Annuler"},
    "Chiudi": {"en": "Close", "es": "Cerrar", "de": "Schließen", "fr": "Fermer"},

    # --- finestra Informazioni -------------------------------------------------------------
    "Informazioni su PhotoExplorer": {
        "en": "About PhotoExplorer", "es": "Acerca de PhotoExplorer", "de": "Über PhotoExplorer",
        "fr": "À propos de PhotoExplorer"},
    "Questo programma è software libero: puoi usarlo, ridistribuirlo e modificarlo secondo i termini della GNU "
    "General Public License versione 3. È distribuito SENZA ALCUNA GARANZIA.\n\nOgni copia e ogni opera derivata deve "
    "restare sotto la stessa licenza e conservare in modo ben visibile l'attribuzione all'autore (termini aggiuntivi, "
    "GPLv3 art. 7(b)).": {
        "en": "This program is free software: you can use, redistribute and modify it under the terms of the GNU "
              "General Public License version 3. It is distributed WITHOUT ANY WARRANTY.\n\nEvery copy and every "
              "derivative work must remain under the same license and keep the author attribution clearly visible "
              "(additional terms, GPLv3 section 7(b)).",
        "es": "Este programa es software libre: puedes usarlo, redistribuirlo y modificarlo según los términos de la "
              "GNU General Public License versión 3. Se distribuye SIN NINGUNA GARANTÍA.\n\nToda copia y toda obra "
              "derivada debe mantener la misma licencia y conservar de forma bien visible la atribución al autor "
              "(términos adicionales, GPLv3 art. 7(b)).",
        "de": "Dieses Programm ist freie Software: Sie können es unter den Bedingungen der GNU General Public "
              "License Version 3 verwenden, weitergeben und verändern. Es wird OHNE JEDE GEWÄHRLEISTUNG verbreitet."
              "\n\nJede Kopie und jedes abgeleitete Werk muss unter derselben Lizenz bleiben und die Nennung des "
              "Autors gut sichtbar beibehalten (Zusatzbedingungen, GPLv3 Abschnitt 7(b)).",
        "fr": "Ce programme est un logiciel libre : vous pouvez l'utiliser, le redistribuer et le modifier selon les "
              "termes de la GNU General Public License version 3. Il est distribué SANS AUCUNE GARANTIE.\n\nToute "
              "copie et toute œuvre dérivée doit rester sous la même licence et conserver de façon bien visible "
              "l'attribution à l'auteur (conditions supplémentaires, GPLv3 art. 7(b))."},
    "Il testo della licenza non è stato trovato accanto al programma.\nPuoi leggerlo qui: {license_url}": {
        "en": "The license text was not found next to the program.\nYou can read it here: {license_url}",
        "es": "No se encontró el texto de la licencia junto al programa.\nPuedes leerlo aquí: {license_url}",
        "de": "Der Lizenztext wurde neben dem Programm nicht gefunden.\nSie können ihn hier lesen: {license_url}",
        "fr": "Le texte de la licence est introuvable à côté du programme.\nVous pouvez le lire ici : {license_url}"},

    # --- connessione -----------------------------------------------------------------------
    "Connessione al NAS": {"en": "NAS connection", "es": "Conexión al NAS", "de": "NAS-Verbindung", "fr": "Connexion au NAS"},
    "Connessione alla cartella condivisa (SMB)": {
        "en": "Connect to the shared folder (SMB)", "es": "Conexión a la carpeta compartida (SMB)",
        "de": "Verbindung zum freigegebenen Ordner (SMB)", "fr": "Connexion au dossier partagé (SMB)"},
    "Puoi anche incollare un percorso completo nel campo Server,\nes. \\\\192.168.1.10\\Multimedia\\Foto": {
        "en": "You can also paste a full path into the Server field,\ne.g. \\\\192.168.1.10\\Multimedia\\Photos",
        "es": "También puedes pegar una ruta completa en el campo Servidor,\np. ej. \\\\192.168.1.10\\Multimedia\\Fotos",
        "de": "Sie können auch einen vollständigen Pfad in das Feld „Server“ einfügen,\n"
              "z. B. \\\\192.168.1.10\\Multimedia\\Fotos",
        "fr": "Vous pouvez aussi coller un chemin complet dans le champ Serveur,\n"
              "p. ex. \\\\192.168.1.10\\Multimedia\\Photos"},
    "Server (IP o nome)": {
        "en": "Server (IP or name)", "es": "Servidor (IP o nombre)", "de": "Server (IP oder Name)",
        "fr": "Serveur (IP ou nom)"},
    "es. 192.168.1.10 o mionas.myqnapcloud.com": {
        "en": "e.g. 192.168.1.10 or mynas.myqnapcloud.com", "es": "p. ej. 192.168.1.10 o minas.myqnapcloud.com",
        "de": "z. B. 192.168.1.10 oder meinnas.myqnapcloud.com", "fr": "p. ex. 192.168.1.10 ou monnas.myqnapcloud.com"},
    "Porta": {"en": "Port", "es": "Puerto", "de": "Port", "fr": "Port"},
    "Cartella condivisa": {"en": "Shared folder", "es": "Carpeta compartida", "de": "Freigegebener Ordner", "fr": "Dossier partagé"},
    "es. Multimedia": {"en": "e.g. Multimedia", "es": "p. ej. Multimedia", "de": "z. B. Multimedia", "fr": "p. ex. Multimedia"},
    "Sottocartella iniziale": {
        "en": "Starting subfolder", "es": "Subcarpeta inicial", "de": "Start-Unterordner", "fr": "Sous-dossier initial"},
    "facoltativa, es. Foto\\2024": {
        "en": "optional, e.g. Photos\\2024", "es": "opcional, p. ej. Fotos\\2024", "de": "optional, z. B. Fotos\\2024",
        "fr": "facultatif, p. ex. Photos\\2024"},
    "Utente": {"en": "User", "es": "Usuario", "de": "Benutzer", "fr": "Utilisateur"},
    "Password": {"en": "Password", "es": "Contraseña", "de": "Passwort", "fr": "Mot de passe"},
    "Dominio": {"en": "Domain", "es": "Dominio", "de": "Domäne", "fr": "Domaine"},
    "di solito vuoto": {"en": "usually empty", "es": "normalmente vacío", "de": "meist leer", "fr": "généralement vide"},
    "Ricorda la password (Gestione credenziali di Windows)": {
        "en": "Remember the password (Windows Credential Manager)",
        "es": "Recordar la contraseña (Administrador de credenciales de Windows)",
        "de": "Passwort merken (Windows-Anmeldeinformationsverwaltung)",
        "fr": "Mémoriser le mot de passe (Gestionnaire d'identification Windows)"},
    "Cartella sul PC / USB…": {
        "en": "Folder on PC / USB…", "es": "Carpeta en PC / USB…", "de": "Ordner auf PC / USB…",
        "fr": "Dossier sur PC / USB…"},
    "Connetti": {"en": "Connect", "es": "Conectar", "de": "Verbinden", "fr": "Connecter"},
    "Connessione…": {"en": "Connecting…", "es": "Conectando…", "de": "Verbindung…", "fr": "Connexion…"},
    "Inserisci almeno il server e la cartella condivisa.": {
        "en": "Enter at least the server and the shared folder.", "es": "Introduce al menos el servidor y la carpeta compartida.",
        "de": "Geben Sie mindestens den Server und den freigegebenen Ordner ein.",
        "fr": "Indiquez au moins le serveur et le dossier partagé."},
    "La porta deve essere un numero (di solito 445).": {
        "en": "The port must be a number (usually 445).", "es": "El puerto debe ser un número (normalmente 445).",
        "de": "Der Port muss eine Zahl sein (meist 445).", "fr": "Le port doit être un nombre (généralement 445)."},
    "Connesso.": {"en": "Connected.", "es": "Conectado.", "de": "Verbunden.", "fr": "Connecté."},
    "Connessione a \\\\{server}\\{share}…": {
        "en": "Connecting to \\\\{server}\\{share}…", "es": "Conectando a \\\\{server}\\{share}…",
        "de": "Verbindung mit \\\\{server}\\{share}…", "fr": "Connexion à \\\\{server}\\{share}…"},
    "Connessione automatica a \\\\{server}\\{share}…": {
        "en": "Connecting automatically to \\\\{server}\\{share}…", "es": "Conexión automática a \\\\{server}\\{share}…",
        "de": "Automatische Verbindung mit \\\\{server}\\{share}…", "fr": "Connexion automatique à \\\\{server}\\{share}…"},
    "Connessione non riuscita: {msg}": {
        "en": "Connection failed: {msg}", "es": "No se pudo conectar: {msg}", "de": "Verbindung fehlgeschlagen: {msg}",
        "fr": "Échec de la connexion : {msg}"},

    # --- errori ----------------------------------------------------------------------------
    "Formato non riconosciuto o file danneggiato.": {
        "en": "Unrecognized format or damaged file.", "es": "Formato no reconocido o archivo dañado.",
        "de": "Unbekanntes Format oder beschädigte Datei.", "fr": "Format non reconnu ou fichier endommagé."},
    "Immagine troppo grande per la memoria disponibile.": {
        "en": "Image too large for the available memory.", "es": "Imagen demasiado grande para la memoria disponible.",
        "de": "Bild zu groß für den verfügbaren Speicher.", "fr": "Image trop grande pour la mémoire disponible."},
    "Nome utente o password non validi.": {
        "en": "Invalid user name or password.", "es": "Nombre de usuario o contraseña no válidos.",
        "de": "Benutzername oder Passwort ungültig.", "fr": "Nom d'utilisateur ou mot de passe incorrect."},
    "La condivisione indicata non esiste sul NAS.": {
        "en": "The specified share does not exist on the NAS.", "es": "La carpeta compartida indicada no existe en el NAS.",
        "de": "Die angegebene Freigabe existiert auf dem NAS nicht.", "fr": "Le partage indiqué n'existe pas sur le NAS."},
    "Accesso negato: l'utente non ha i permessi necessari.": {
        "en": "Access denied: the user does not have the required permissions.",
        "es": "Acceso denegado: el usuario no tiene los permisos necesarios.",
        "de": "Zugriff verweigert: Der Benutzer hat nicht die nötigen Rechte.",
        "fr": "Accès refusé : l'utilisateur n'a pas les autorisations nécessaires."},
    "File o cartella non trovati (forse sono stati spostati o eliminati).": {
        "en": "File or folder not found (it may have been moved or deleted).",
        "es": "Archivo o carpeta no encontrados (quizá se movieron o eliminaron).",
        "de": "Datei oder Ordner nicht gefunden (vielleicht verschoben oder gelöscht).",
        "fr": "Fichier ou dossier introuvable (peut-être déplacé ou supprimé)."},
    "Nome del server non risolto: controlla l'indirizzo del NAS.": {
        "en": "Server name not resolved: check the NAS address.",
        "es": "No se pudo resolver el nombre del servidor: comprueba la dirección del NAS.",
        "de": "Servername nicht auflösbar: Bitte die NAS-Adresse prüfen.",
        "fr": "Nom du serveur introuvable : vérifiez l'adresse du NAS."},
    "Il NAS non risponde: controlla indirizzo, porta, VPN o firewall.": {
        "en": "The NAS is not responding: check address, port, VPN or firewall.",
        "es": "El NAS no responde: comprueba dirección, puerto, VPN o cortafuegos.",
        "de": "Das NAS antwortet nicht: Adresse, Port, VPN oder Firewall prüfen.",
        "fr": "Le NAS ne répond pas : vérifiez l'adresse, le port, le VPN ou le pare-feu."},
    "Connessione con il NAS interrotta.": {
        "en": "Connection to the NAS lost.", "es": "Conexión con el NAS interrumpida.",
        "de": "Verbindung zum NAS unterbrochen.", "fr": "Connexion au NAS interrompue."},
    "Errore SMB: {exc}": {"en": "SMB error: {exc}", "es": "Error SMB: {exc}", "de": "SMB-Fehler: {exc}", "fr": "Erreur SMB : {exc}"},
}
