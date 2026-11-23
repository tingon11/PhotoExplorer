# Changelog

The most recent section is used by `build.py --release` as the release notes: first the
introduction, then the list of changes.

## 1.0.3

Photos no longer get stuck on "Loading…", the program asks for the language and shows a
disclaimer at the first start, and the executable now carries the licenses of everything it
contains. Updating is recommended.

- **Photos stuck on "Loading…"**: with some image sizes the preview was cut with a box slightly
  larger than the image because of rounding, and the photo was never shown (on a real archive,
  about one photo in four). The box is now kept inside the image. If a photo still cannot be
  shown, the program says so instead of waiting forever, the photo is not marked as viewed, and
  the error is written to `%APPDATA%\PhotoExplorer\photoexplorer.log` together with the photos
  that take more than 3 seconds to open.
- **Large folders**: the list of photos fills faster, because the "to view" counter is updated
  only for the new photos instead of being recounted every time.
- **First start**: the language selection comes first (closing it keeps the Windows language),
  then a disclaimer in the chosen language that must be accepted to continue: no warranty,
  rotation and deletion change the files so keep a backup, not forensic software. Declining
  closes the program. It is shown only once and can be read again from *About → Disclaimer*.
- **Third-party licenses**: the executable includes `THIRD_PARTY_LICENSES.txt` with the license
  texts of Python, Tcl/Tk and all the bundled libraries, shown in the About window and shipped
  in the release zip.
- **New logo and icon**, in the same style as the author's other programs.
- **File properties**: the executable now carries its version, author and copyright.

## 1.0.0

First public version: a photo viewer for NAS devices (SMB) and for folders on the PC, hard disks
and USB sticks.

- Memory of the photos already viewed, with the option to skip them.
- Rotation saved to the file (EXIF data preserved), deletion with double confirmation.
- Copy to the print folder, optionally with the capture date stamped in red.
- Capture date and GPS position from the EXIF data, with a link to Google Maps.
- Favorite photos and a favorites-only view; photos sent to print are marked in the list.
- Interface in Italian, English, Spanish, German and French.
