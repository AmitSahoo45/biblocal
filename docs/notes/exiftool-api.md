# ExifTool writer verification — 17 Oct 2026

Verified against the installed **ExifTool 13.59** at
`D:\tools\exiftool\exiftool.exe`, its `exiftool_files/windows_exiftool.txt`,
`exiftool.pl`, and `lib/Image/ExifTool/{Writer.pl,WriteIPTC.pl,IPTC.pm}`.
No download or Python dependency was added.

## Batch protocol

- `-@ -` reads a UTF-8 argument file from stdin until EOF, one argument per
  line without shell quoting. No shell or disk argument file is used.
- `-common_args` belongs on the actual command line, after `-@ -`.
  `-charset filename=utf8 -charset UTF8` applies to each `-execute` command.
- `-echo3` and `-echo4` expand `${status}` after each command. Unique markers
  delimit stdout statuses and stderr diagnostics, so one corrupt photo does
  not hide the status of another photo in the same process.
- There is one ExifTool process per batch of at most 500 photos. Embed uses
  two commands per photo; sidecar uses one. Both embed commands must pass.
- The child process uses `LC_ALL=C`: this Windows Perl does not provide the
  inherited `C.UTF-8` locale. UTF-8 filenames and metadata are explicit options;
  actual non-ASCII path/name tests pass.
- CR, LF and NUL are rejected in arguments. Photo paths must stay inside the
  selected photo folder, and sidecars may not resolve outside it.

## Preserving existing IPTC

Unmarked legacy IPTC defaults to Latin-1 in ExifTool. Simply setting
`CodedCharacterSet=UTF8` reinterprets existing bytes and corrupts text.
Combining `-tagsFromFile @ -IPTC:all` with keyword `-=` / `+=` in the same
command retains raw list bytes as well as copied values, causing corrupt
text and duplicate keywords. Synthetic `café` / `El niño` tests reproduced it.

Embed first runs a separate `-tagsFromFile @ -IPTC:all
-IPTC:CodedCharacterSet=UTF8` command. The next command requires
`$IPTC:CodedCharacterSet eq 'UTF8'`, then removes and adds each requested
XMP/IPTC keyword. This preserves ordinary legacy text and avoids duplicates.

ExifTool can truncate IPTC text with only a warning and exit status zero.
A valid 40-byte Latin-1 keyword becomes 80 bytes in UTF-8, exceeding the
64-byte IPTC keyword limit. A regression test reproduced truncation of
keywords and captions. `-m` would bypass length checks but also suppress
unrelated minor errors; BibLocal does not use it.

To preserve sources, embed works on copies in a temporary `.biblocal-*`
directory under the photo folder, limited to one batch. Only clean results
are moved over their sources. ExifTool's original backup from that temporary
copy is retained as `<photo>_original`, unless `--no-backup` is selected;
an existing backup is never replaced. The source SHA-256 is compared with the
staged input immediately before publishing; a detected concurrent edit causes
failure and leaves that newer source intact. Temporary copies are removed on normal
completion, including failures. This needs temporary disk space for the batch
and backups. A process interruption may leave a temporary directory behind.

Warnings and nonzero/missing statuses cause per-file failure. The sole
expected warning ignored is `No writable tags set from ...` during the first
IPTC-copy command for a photo without IPTC; the subsequent UTF-8 condition
must still pass. Unsafe recodes, including overlength text, leave the source
unchanged and suggest `--write sidecar`. No tag is silently shortened.

## Sidecars and backups

- New sidecars use `-o <stem>.xmp` with the JPEG as input. Existing sidecars
  are edited directly, preserving unrelated XMP such as Rating.
- **Never combine `-o` with `-overwrite_original` when creating a sidecar:**
  ExifTool deletes the source JPEG in that combination. `--no-backup` therefore
  only adds `-overwrite_original` when editing an existing target.
- `-o` interprets percent sequences as filename formatting. Creation of a new
  sidecar whose path contains `%` is rejected with a per-file error. Existing
  sidecars with such names can be edited directly.
- ExifTool JSON may serialize numeric-looking keyword strings as JSON numbers.
  Tests normalize these values when comparing keywords.

## CLI behavior

Metadata writing requires `--write embed` or `--write sidecar`. Only `tagged`
rows are written; review suggestions never become tags. Default flat keywords
are bibs, with `Bib|<bib>` hierarchical values. Names require `--with-names`;
`--keyword-template` supports the `{bib}` field.

Lookup order is explicit `--exiftool`, `BIBLOCAL_EXIFTOOL`, frozen application
directory, then PATH. An invalid explicit path fails rather than falling back.
Missing ExifTool produces an installation hint before OCR starts. Write counts
and per-file failures appear in `run.json` and the final CLI summary; metadata
failures return exit code 2. Results CSV remains available after write failures.
