# PhotoExplorer

[English](README.md) · [Italiano](README.it.md) · [Español](README.es.md) · [Deutsch](README.de.md) · **Français**

Visionneuse de photos pour NAS (QNAP et similaires, via SMB) et pour les dossiers du PC, les
disques durs et les clés USB, avec une interface sombre en customtkinter.
Conçue pour passer en revue de grandes archives de photos : elle se souvient de celles que vous
avez déjà vues et permet de les faire pivoter, de les supprimer et de les copier dans un dossier
local pour l'impression.

**Auteur : Andrea Cumini — [www.osintinfo.net](https://www.osintinfo.net) — andrea@osintinfo.net**

> **Remarque.** PhotoExplorer n'est pas un logiciel forensique. Je l'ai développé pour mon usage
> personnel, pour gérer mes photos privées, et j'ai décidé de le partager. Il modifie les
> fichiers (la rotation réécrit la photo, la suppression l'efface) et ne garantit pas
> l'intégrité des données ni des métadonnées : il ne doit pas être utilisé pour acquérir,
> analyser ou conserver des preuves.

## Fonctions

- Connexion à un dossier partagé SMB (utilisateur et mot de passe ; le mot de passe peut être
  mémorisé dans le Gestionnaire d'identification Windows).
- Sinon, photos d'un dossier du PC, d'un disque dur externe ou d'une clé USB.
- Liste des photos du dossier sélectionné et de tous ses sous-dossiers.
- Mémoire des photos déjà vues, avec l'option « Passer les photos déjà vues » (pour les disques
  locaux, elle est liée au disque et non à la lettre de lecteur).
- La rotation est enregistrée dans le fichier (les données EXIF sont conservées).
- Suppression avec double confirmation (sur les disques locaux, le fichier va dans la Corbeille).
- Copie dans le dossier d'impression (l'original n'est jamais déplacé), avec en option la date
  de prise de vue en rouge en bas à droite.
- Date de prise de vue et position GPS tirées des données EXIF ; un clic ouvre le lieu dans
  Google Maps dans le navigateur.
- Photos favorites : on les marque avec un bouton (ou la touche F) et on peut n'afficher
  qu'elles. Les photos envoyées à l'impression deviennent automatiquement favorites et sont
  signalées par une icône dans la liste.
- Interface en italien, anglais, espagnol, allemand et français, à choisir dans la barre du haut.
- Réinitialisation complète des données (photos vues, favorites, impressions) avec confirmation.
- Zoom avec la molette de la souris et déplacement par glisser.
- Formats : JPG, PNG, WEBP, TIFF, BMP, GIF et HEIC (avec `pillow-heif`).

## Touches

| Touche | Action |
|---|---|
| P / L | photo suivante / précédente |
| W / Q | tourner à droite / à gauche |
| D, puis C | supprimer (D prépare, C confirme ; Échap annule) |
| H | copier la photo dans le dossier d'impression |
| F | ajouter la photo aux favorites ou l'en retirer |
| Molette / glisser | zoom / déplacer la photo agrandie |

Chaque commande a aussi son bouton dans l'interface.

## Installation

Nécessite Python 3.11 ou plus récent sous Windows.

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Pour créer un exécutable unique (`dist\PhotoExplorer.exe`) avec PyInstaller :

```
.venv\Scripts\python.exe build.py
```

Les paramètres et la mémoire des photos vues sont enregistrés dans `%APPDATA%\PhotoExplorer`.

## Traductions

Dans le code, les textes sont en italien dans `tr("…")` ; les autres langues se trouvent dans
`photoexplorer/translations.py`. Pour vérifier qu'il ne manque rien après une modification :

```
.venv\Scripts\python.exe tests\test_translations.py
```

Pour ajouter une langue, il suffit d'ajouter son code dans `LANGUAGES` (`photoexplorer/i18n.py`)
et ses traductions dans `translations.py`.

## Licence et attribution

Copyright (C) 2026 Andrea Cumini. Logiciel libre distribué sous la
[GNU GPL version 3](LICENSE), avec les [conditions supplémentaires](ADDITIONAL_TERMS.txt) prévues
à l'article 7(b) de la licence. Sans aucune garantie.

En pratique : vous pouvez l'utiliser, le copier, le modifier et le redistribuer, mais toute copie
et toute œuvre dérivée doit

- rester sous GPLv3, avec le code source disponible ;
- conserver de façon bien visible, dans les fichiers source et dans l'interface du programme,
  l'attribution **Andrea Cumini — https://www.osintinfo.net — andrea@osintinfo.net** ;
- indiquer clairement qu'il s'agit d'une version modifiée.

## Bibliothèques tierces

Le code source utilise, sans les inclure, ces bibliothèques (chacune sous sa propre licence) :
customtkinter (MIT), Pillow (MIT-CMU), smbprotocol et pyspnego (MIT), keyring (MIT),
pillow-heif (BSD-3-Clause).

Les paquets binaires de `pillow-heif` intègrent libheif et libde265 (LGPLv3) ainsi que x265
(GPLv2 ou ultérieure), toutes des licences compatibles avec la GPLv3 de ce programme. Quiconque
distribue l'exécutable doit donc le distribuer sous GPLv3 et rendre le code source disponible.

La position GPS est ouverte au moyen d'une adresse Google Maps ordinaire dans le navigateur de
l'utilisateur : le programme ne télécharge ni n'intègre de cartes.
