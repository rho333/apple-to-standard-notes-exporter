# Apple Notes to Standard Notes Exporter
## Purpose
After recently switching from iOS to Android, I found that my Apple notes (of which I had many thousands, accrued over several years) were not easily exported to any equivalent platform on Android. Further to that, I found that most popular note applications on Android similarly prevent import/export.

One exception is the Standard Notes application and service, which provides client-side encryption for all notes, and free cloud syncing, with clients on iOS, Android, macOS, Windows and Linux. For that reason, I wrote this simple script to extract notes from the macOS Notes app database and convert them into the Standard Notes format.

## Functionality
This script will find all notes in all accounts, and generate a valid Standard Notes 'export' (which can be imported through the Standard Notes desktop app), preserving creation date, edit date, title and basic formatting. As Standard Notes doesn't support rich text/HTML rendering by default, the HTML structures used by Apple Notes for lists, titles, etc. will be converted into valid Markdown during export.

## Usage
`python3 apple_notes_to_sn.py <path_to_notes_db_file>` will write out the Standard Notes export to `Standard_Notes-apple_notes_export.txt`.