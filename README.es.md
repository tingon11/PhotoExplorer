# PhotoExplorer

[English](README.md) · [Italiano](README.it.md) · **Español** · [Deutsch](README.de.md) · [Français](README.fr.md)

Visor de fotos para NAS (QNAP y similares, por SMB) y para carpetas del PC, discos duros y
memorias USB, con interfaz oscura en customtkinter.
Pensado para revisar grandes archivos de fotos: recuerda las que ya has visto y permite
girarlas, eliminarlas y copiarlas a una carpeta local para imprimirlas.

**Autor: Andrea Cumini — [www.osintinfo.net](https://www.osintinfo.net) — andrea@osintinfo.net**

## Funciones

- Conexión a una carpeta compartida SMB (usuario y contraseña; la contraseña se puede recordar
  en el Administrador de credenciales de Windows).
- Como alternativa, fotos de una carpeta del PC, de un disco duro externo o de una memoria USB.
- Lista de las fotos de la carpeta seleccionada y de todas sus subcarpetas.
- Memoria de las fotos ya vistas, con la opción «Saltar las fotos ya vistas» (en los discos
  locales va ligada al disco, no a la letra de unidad).
- La rotación se guarda en el archivo (los datos EXIF se conservan).
- Eliminación con doble confirmación (en los discos locales el archivo va a la Papelera).
- Copia a la carpeta de impresión (el original nunca se mueve), con la fecha de captura opcional
  en rojo en la esquina inferior derecha.
- Fecha de captura y posición GPS de los datos EXIF; un clic abre el lugar en Google Maps en el
  navegador.
- Fotos favoritas: se marcan con un botón (o la tecla F) y se pueden ver solas. Las fotos
  enviadas a imprimir pasan a ser favoritas automáticamente y llevan un icono en la lista.
- Interfaz en italiano, inglés, español, alemán y francés, seleccionable en la barra superior.
- Borrado completo de los datos (fotos vistas, favoritas, impresiones) con confirmación.
- Zoom con la rueda del ratón y desplazamiento arrastrando.
- Formatos: JPG, PNG, WEBP, TIFF, BMP, GIF y HEIC (con `pillow-heif`).

## Teclas

| Tecla | Acción |
|---|---|
| P / L | foto siguiente / anterior |
| W / Q | girar a la derecha / a la izquierda |
| D, luego C | eliminar (D prepara, C confirma; Esc cancela) |
| H | copiar la foto a la carpeta de impresión |
| F | añadir la foto a las favoritas o quitarla |
| Rueda / arrastrar | zoom / mover la foto ampliada |

Cada comando tiene también su botón en la interfaz.

## Instalación

Requiere Python 3.11 o posterior en Windows.

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Para crear un único ejecutable (`dist\PhotoExplorer.exe`) con PyInstaller:

```
.venv\Scripts\python.exe build.py
```

Los ajustes y la memoria de las fotos vistas se guardan en `%APPDATA%\PhotoExplorer`.

## Traducciones

En el código los textos están en italiano dentro de `tr("…")`; los demás idiomas están en
`photoexplorer/translations.py`. Para comprobar que no falta nada después de un cambio:

```
.venv\Scripts\python.exe tests\test_translations.py
```

Para añadir un idioma basta con añadir su código en `LANGUAGES` (`photoexplorer/i18n.py`) y sus
traducciones en `translations.py`.

## Licencia y atribución

Copyright (C) 2026 Andrea Cumini. Software libre distribuido bajo la
[GNU GPL versión 3](LICENSE), con los [términos adicionales](ADDITIONAL_TERMS.txt) previstos en
el artículo 7(b) de la licencia. Sin ninguna garantía.

En la práctica: puedes usarlo, copiarlo, modificarlo y redistribuirlo, pero toda copia y toda
obra derivada debe

- permanecer bajo GPLv3, con el código fuente disponible;
- conservar de forma bien visible, en los archivos fuente y en la interfaz del programa, la
  atribución **Andrea Cumini — https://www.osintinfo.net — andrea@osintinfo.net**;
- indicar claramente que es una versión modificada.

## Bibliotecas de terceros

El código fuente usa, sin incluirlas, estas bibliotecas (cada una con su propia licencia):
customtkinter (MIT), Pillow (MIT-CMU), smbprotocol y pyspnego (MIT), keyring (MIT),
pillow-heif (BSD-3-Clause).

Los paquetes binarios de `pillow-heif` incorporan libheif y libde265 (LGPLv3) y x265 (GPLv2 o
posterior), licencias todas compatibles con la GPLv3 de este programa. Quien distribuya el
ejecutable debe por tanto distribuirlo bajo GPLv3 y poner a disposición el código fuente.

La posición GPS se abre con una dirección normal de Google Maps en el navegador del usuario: el
programa no descarga ni incorpora mapas.
