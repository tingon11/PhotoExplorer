# PhotoExplorer - Copyright (C) 2026 Andrea Cumini
# https://www.osintinfo.net - andrea@osintinfo.net
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License version 3 as published by the Free Software Foundation, with the
# additional terms in ADDITIONAL_TERMS.txt (author attribution, GPLv3 section 7(b)).
# It is distributed WITHOUT ANY WARRANTY. See the LICENSE file for details.
# SPDX-License-Identifier: GPL-3.0-only
"""Decodifica delle immagini, dati EXIF, rotazione con salvataggio e data stampata sulla foto."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from io import BytesIO

from .i18n import tr
from PIL import Image, ImageDraw, ImageFont, ImageOps, JpegImagePlugin

try:  # foto HEIC degli iPhone
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIF_SUPPORTED = True
except ImportError:
    HEIF_SUPPORTED = False

Image.MAX_IMAGE_PIXELS = 400_000_000  # panorami molto grandi

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".jpe", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}
if HEIF_SUPPORTED:
    IMAGE_EXTENSIONS |= {".heic", ".heif"}

FULL_MAX_PIXELS = 80_000_000   # limite per la foto a piena risoluzione tenuta in memoria per lo zoom
MAX_PIXEL_SCALE = 4.0          # zoom massimo: 1 pixel della foto = 4 pixel dello schermo

ORIENTATION_TAG = 0x0112
_EXIF_IFD = 0x8769
_GPS_IFD = 0x8825
_DATETIME_ORIGINAL = 0x9003
_DATETIME_DIGITIZED = 0x9004
_DATETIME = 0x0132

# rotazione oraria in gradi -> trasposizione PIL
_TRANSPOSE = {
    90: Image.Transpose.ROTATE_270,
    180: Image.Transpose.ROTATE_180,
    270: Image.Transpose.ROTATE_90,
}

_XMP_ORIENTATION = re.compile(rb'(tiff:Orientation\s*=\s*["\']|<tiff:Orientation>)\s*\d')

# data stampata sulla foto
STAMP_COLOR = (235, 20, 20)
STAMP_OUTLINE = (70, 0, 0)
# misure in millimetri riferite a una stampa 10x15: il lato corto della foto vale 100 mm
PRINT_SHORT_SIDE_MM = 100
STAMP_MARGIN_MM = 3     # distanza dal bordo destro e dal bordo inferiore
STAMP_TEXT_MM = 3       # dimensione del carattere: piccola e discreta
STAMP_OUTLINE_RATIO = 0.035   # contorno scuro sottile, quanto basta per leggerla su sfondi chiari
_STAMP_FONTS = ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf")   # carattere normale, non grassetto


class RotationNotSupported(Exception):
    pass


def is_image(name: str) -> bool:
    dot = name.rfind(".")
    return dot > 0 and name[dot:].lower() in IMAGE_EXTENSIONS


def rotate_cw(img: Image.Image, degrees: int) -> Image.Image:
    degrees %= 360
    return img.transpose(_TRANSPOSE[degrees]) if degrees else img


# --------------------------------------------------------------------------
# EXIF: data di scatto e posizione
# --------------------------------------------------------------------------
@dataclass
class PhotoMeta:
    taken: datetime | None = None
    gps: tuple[float, float] | None = None   # (latitudine, longitudine) in gradi decimali


def _parse_exif_datetime(value) -> datetime | None:
    if isinstance(value, bytes):
        value = value.decode("ascii", "ignore")
    if not isinstance(value, str):
        return None
    value = value.strip("\x00 ").strip()
    # (formato, lunghezza): si ignora ciò che segue, es. fuso orario o frazioni di secondo
    for fmt, length in (("%Y:%m:%d %H:%M:%S", 19), ("%Y-%m-%d %H:%M:%S", 19),
                        ("%Y:%m:%d %H:%M", 16), ("%Y:%m:%d", 10)):
        try:
            dt = datetime.strptime(value[:length], fmt)
        except ValueError:
            continue
        return dt if dt.year >= 1900 else None
    return None


def _dms_to_degrees(dms) -> float:
    if isinstance(dms, (int, float)):
        return float(dms)
    parts = [float(x) for x in dms]
    while len(parts) < 3:
        parts.append(0.0)
    return parts[0] + parts[1] / 60 + parts[2] / 3600


def _parse_gps(gps: dict) -> tuple[float, float] | None:
    try:
        lat = _dms_to_degrees(gps[2])
        lon = _dms_to_degrees(gps[4])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None
    lat_ref = str(gps.get(1, "N")).strip("\x00 ").upper()
    lon_ref = str(gps.get(3, "E")).strip("\x00 ").upper()
    if lat_ref.startswith("S"):
        lat = -lat
    if lon_ref.startswith("W"):
        lon = -lon
    if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (abs(lat) < 1e-6 and abs(lon) < 1e-6):
        return None   # alcune fotocamere scrivono 0,0 quando non hanno il segnale GPS
    return lat, lon


def read_meta(exif: Image.Exif) -> PhotoMeta:
    meta = PhotoMeta()
    try:
        sub = exif.get_ifd(_EXIF_IFD)
    except Exception:
        sub = {}
    for value in (sub.get(_DATETIME_ORIGINAL), sub.get(_DATETIME_DIGITIZED), exif.get(_DATETIME)):
        meta.taken = _parse_exif_datetime(value)
        if meta.taken:
            break
    try:
        gps = exif.get_ifd(_GPS_IFD)
    except Exception:
        gps = {}
    if gps:
        meta.gps = _parse_gps(gps)
    return meta


def read_meta_from_bytes(raw: bytes) -> PhotoMeta:
    try:
        return read_meta(Image.open(BytesIO(raw)).getexif())
    except Exception:
        return PhotoMeta()


# --------------------------------------------------------------------------
# Data stampata in basso a destra
# --------------------------------------------------------------------------
def format_stamp(when: datetime) -> str:
    return when.strftime("%d/%m/%Y")


@lru_cache(maxsize=32)
def _stamp_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    fonts_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    for name in _STAMP_FONTS:
        for candidate in (os.path.join(fonts_dir, name), name):
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    return ImageFont.load_default(size)


def stamp_date(img: Image.Image, when: datetime) -> Image.Image:
    """Restituisce una copia dell'immagine con la data in rosso, piccola, in basso a destra:
    a STAMP_MARGIN_MM dal bordo destro e dal bordo inferiore di una stampa 10x15."""
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() or "transparency" in img.info else "RGB")
    else:
        img = img.copy()
    w, h = img.size
    px_per_mm = min(w, h) / PRINT_SHORT_SIDE_MM
    size = max(8, round(STAMP_TEXT_MM * px_per_mm))
    margin = STAMP_MARGIN_MM * px_per_mm
    ImageDraw.Draw(img).text(
        (w - margin, h - margin), format_stamp(when), font=_stamp_font(size), anchor="rs",  # rs = destra, linea di base
        fill=STAMP_COLOR, stroke_width=max(1, round(size * STAMP_OUTLINE_RATIO)), stroke_fill=STAMP_OUTLINE)
    return img


# --------------------------------------------------------------------------
# Decodifica per la visualizzazione
# --------------------------------------------------------------------------
@dataclass
class LoadedImage:
    raw: bytes                  # contenuto originale del file
    base: Image.Image           # immagine già orientata e ridotta alla risoluzione dello schermo
    full_size: tuple[int, int]  # dimensioni reali (dopo l'orientamento EXIF)
    fmt: str
    rotatable: bool
    meta: PhotoMeta = field(default_factory=PhotoMeta)


def decode_for_display(raw: bytes, max_side: int) -> LoadedImage:
    img = Image.open(BytesIO(raw))
    fmt = img.format or "?"
    w, h = img.size
    frames = getattr(img, "n_frames", 1)
    rotatable = frames == 1 or fmt == "MPO"

    exif = img.getexif()
    meta = read_meta(exif)
    orientation = exif.get(ORIENTATION_TAG, 1)
    full_size = (h, w) if orientation in (5, 6, 7, 8) else (w, h)

    if fmt in ("JPEG", "MPO"):
        # decodifica JPEG già ridotta (1/2, 1/4, 1/8): molto più veloce per foto grandi
        scale = min(max_side / w, max_side / h, 1.0)
        img.draft("RGB", (max(1, int(w * scale)), max(1, int(h * scale))))

    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "RGBA"):
        has_alpha = img.mode in ("LA", "PA") or (img.mode == "P" and "transparency" in img.info)
        img = img.convert("RGBA" if has_alpha else "RGB")
    img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS, reducing_gap=2.0)
    img.load()
    return LoadedImage(raw, img, full_size, fmt, rotatable, meta)


def decode_full(raw: bytes) -> Image.Image:
    """Foto a piena risoluzione (già orientata), usata quando si ingrandisce con lo zoom."""
    img = Image.open(BytesIO(raw))
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "RGBA"):
        has_alpha = img.mode in ("LA", "PA") or (img.mode == "P" and "transparency" in img.info)
        img = img.convert("RGBA" if has_alpha else "RGB")
    if img.width * img.height > FULL_MAX_PIXELS:   # panorami enormi: si limita l'uso di memoria
        factor = (FULL_MAX_PIXELS / (img.width * img.height)) ** 0.5
        img = img.resize((round(img.width * factor), round(img.height * factor)), Image.Resampling.LANCZOS)
    img.load()
    return img


# --------------------------------------------------------------------------
# Vista della foto: adattata alla finestra oppure ingrandita (zoom) e spostata
# --------------------------------------------------------------------------
@dataclass
class View:
    image: Image.Image             # parte visibile della foto, già alla dimensione dello schermo
    zoom: float                    # 1 = foto intera adattata alla finestra
    max_zoom: float
    scale: float                   # pixel dello schermo per ogni pixel della foto
    center: tuple[float, float]    # punto della foto al centro della vista
    origin: tuple[float, float]    # punto della foto nell'angolo in alto a sinistra dell'immagine mostrata
    offset: tuple[float, float]    # posizione dell'immagine mostrata dentro il riquadro

    def to_photo(self, x: float, y: float) -> tuple[float, float]:
        """Coordinate nel riquadro -> coordinate nella foto."""
        return (self.origin[0] + (x - self.offset[0]) / self.scale,
                self.origin[1] + (y - self.offset[1]) / self.scale)


def render_view(src: Image.Image, full_size: tuple[int, int], box: tuple[int, int], zoom: float = 1.0,
                center: tuple[float, float] | None = None, fast: bool = False, margin: int = 20) -> View:
    """Disegna la parte di foto visibile nel riquadro ``box``.

    ``src`` è la foto (a qualsiasi risoluzione) e ``full_size`` le sue dimensioni reali: tutte le
    coordinate sono in pixel reali della foto. Con zoom 1 la foto è intera e adattata al riquadro
    (mai ingrandita oltre il 100%); con zoom maggiore si vede la zona attorno a ``center``."""
    fw, fh = full_size
    bw, bh = max(box[0], 50), max(box[1], 50)
    fit = max(min((bw - margin) / fw, (bh - margin) / fh, 1.0), 1e-6)
    max_zoom = max(1.0, MAX_PIXEL_SCALE / fit)
    zoom = min(max(zoom, 1.0), max_zoom)
    scale = fit * zoom

    # il centro non può portare la vista fuori dalla foto; se la foto è più piccola del riquadro resta centrata
    cx, cy = center if center is not None and zoom > 1 else (fw / 2, fh / 2)
    half_w, half_h = bw / (2 * scale), bh / (2 * scale)
    cx = fw / 2 if fw * scale <= bw else min(max(cx, half_w), fw - half_w)
    cy = fh / 2 if fh * scale <= bh else min(max(cy, half_h), fh - half_h)
    x0, x1 = max(0.0, cx - half_w), min(float(fw), cx + half_w)
    y0, y1 = max(0.0, cy - half_h), min(float(fh), cy + half_h)
    out = (max(1, round((x1 - x0) * scale)), max(1, round((y1 - y0) * scale)))

    # src può essere una versione ridotta della foto. Le due scale vanno calcolate separatamente:
    # l'anteprima ha dimensioni intere, quindi le sue proporzioni non sono esattamente quelle
    # dell'originale (es. 3872x2592 -> 1920x1285) e con una scala sola il ritaglio uscirebbe dai bordi.
    kx, ky = src.width / fw, src.height / fh
    ratio = scale / kx   # pixel dello schermo per ogni pixel di src
    if fast:             # durante rotella e trascinamento: veloce, poi si ridisegna in alta qualità
        resample, gap = (Image.Resampling.BILINEAR if ratio < 1 else Image.Resampling.NEAREST), None
    else:
        resample = Image.Resampling.LANCZOS if ratio < 1 else Image.Resampling.BICUBIC
        gap = 3.0 if ratio < 0.5 else None
    left, top = max(0.0, x0 * kx), max(0.0, y0 * ky)
    right, bottom = min(float(src.width), x1 * kx), min(float(src.height), y1 * ky)
    if right - left < 1 or bottom - top < 1:      # zona minuscola: almeno un pixel di sorgente
        right, bottom = min(float(src.width), left + 1), min(float(src.height), top + 1)
        left, top = max(0.0, right - 1), max(0.0, bottom - 1)
    image = src.resize(out, resample, box=(left, top, right, bottom), reducing_gap=gap)
    return View(image, zoom, max_zoom, scale, (cx, cy), (x0, y0), ((bw - out[0]) / 2, (bh - out[1]) / 2))


# --------------------------------------------------------------------------
# Riscrittura del file (rotazione e/o data stampata)
# --------------------------------------------------------------------------
def rotate_image_bytes(raw: bytes, degrees_cw: int) -> bytes:
    return render_image_bytes(raw, degrees_cw=degrees_cw)


def render_image_bytes(raw: bytes, degrees_cw: int = 0, stamp: datetime | None = None) -> bytes:
    """Ruota e/o stampa la data sulla foto e la riscrive nello stesso formato, conservando
    EXIF, profilo colore e (per i JPEG) le stesse tabelle di quantizzazione, per perdere
    il meno possibile in qualità."""
    degrees_cw %= 360
    if degrees_cw not in _TRANSPOSE and stamp is None:
        return raw

    src = Image.open(BytesIO(raw))
    fmt = src.format
    if getattr(src, "n_frames", 1) > 1 and fmt != "MPO":
        raise RotationNotSupported(tr("Le immagini animate o multipagina non possono essere modificate."))
    if fmt == "MPO":  # JPEG con anteprima incorporata: si salva come JPEG normale
        fmt = "JPEG"

    exif = src.getexif()
    img = rotate_cw(ImageOps.exif_transpose(src), degrees_cw)

    params: dict = {}
    if stamp is not None:
        if img.mode == "CMYK":   # il profilo colore CMYK non vale più dopo la conversione
            src.info.pop("icc_profile", None)
        img = stamp_date(img, stamp)
    if src.info.get("icc_profile"):
        params["icc_profile"] = src.info["icc_profile"]
    if exif and fmt != "TIFF":  # nei TIFF l'"exif" contiene anche larghezza/altezza originali
        if ORIENTATION_TAG in exif:
            exif[ORIENTATION_TAG] = 1
        params["exif"] = exif.tobytes()
    if src.info.get("dpi"):
        params["dpi"] = src.info["dpi"]

    if fmt == "JPEG":
        params["qtables"] = src.quantization
        sampling = JpegImagePlugin.get_sampling(src)
        if sampling != -1:
            params["subsampling"] = sampling
        if src.info.get("progressive") or src.info.get("progression"):
            params["progressive"] = True
        if src.info.get("comment"):
            params["comment"] = src.info["comment"]
        xmp = src.info.get("xmp")
        if xmp:
            if isinstance(xmp, str):
                xmp = xmp.encode("utf-8")
            params["xmp"] = _XMP_ORIENTATION.sub(rb"\g<1>1", xmp)
    elif fmt == "WEBP":
        params["quality"] = 95
        params["method"] = 6
    elif fmt == "TIFF":
        comp = src.info.get("compression")
        if comp in ("tiff_lzw", "tiff_adobe_deflate", "packbits", "raw"):
            params["compression"] = comp
    elif fmt == "HEIF":
        params["quality"] = 92
    elif fmt == "GIF" and "transparency" in src.info and img.mode == "P":
        params["transparency"] = src.info["transparency"]

    if fmt == "JPEG" and img.mode not in ("RGB", "L", "CMYK"):
        img = img.convert("RGB")
    if fmt == "BMP" and img.mode == "RGBA":
        img = img.convert("RGB")

    out = BytesIO()
    img.save(out, format=fmt, **params)
    return out.getvalue()
