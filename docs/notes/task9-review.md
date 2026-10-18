# Review and apply verification — 18 Oct 2026

K4 PASS/GO was received from Amit for digiKam 9.1.0. Task 9 adds a static,
offline review page to normal scans and a validated `apply` command.

## Verified behavior

Tests first failed because the module was missing, then passed against the
implementation. A local headless Edge test exercises Enter-to-confirm,
focus movement, No bib, actual CSV Blob contents, comma quoting, leading
zeros and omission of unconfirmed cards. Thumbnails load from disk. The
rendered synthetic page was also inspected visually.

Final full suite: **121 passed in 133.35 seconds**, including actual Edge
and ExifTool tests. No new dependency was added.

Python tests cover padded crops, upright EXIF images, escaped text, unavailable
previews, start-list spelling/names, invalid corrections, default source
preservation and writing corrected files only through real ExifTool.

Final review found two issues, reproduced with failing tests and fixed:

- Output inside the photo folder could collide with source JPEGs. The CLI now
  requires output outside that folder; the renderer also checks thumbnail
  destinations against source paths before saving.
- OCR filters scores below 0.50. The CLI now explicitly rejects lower review
  thresholds instead of silently accepting ineffective settings. Defaults
  remain accept 0.90 / review 0.50.

Manual corrections must be ASCII digits, and must belong to the supplied start
list. Only confirmed cards are exported. Empty corrections set a result to
`none`. Metadata writes remain additive: replacing a previously written bib
or choosing No bib does **not** delete earlier photo keywords. Existing
keywords belong to the photographer and are preserved.

## Amit's review check — PASS

A private acceptance page is ready at:

```text
D:\Projects\24-HacktoberFest-2026\03-Week-3\data\k1_biblocal\task9-review\review.html
```

It displays the 20 review/none rows from the existing K1 run, reusing cached
OCR boxes. This broader acceptance page lets you inspect five photos; normal
scans display only review rows. No new accuracy run was performed and no
source photo was changed.

1. Open the page locally. Read and correct five cards; use No bib where you
   cannot confidently read one. Confirm each card with Enter or the button.
2. Download `corrections.csv`, saving it into
   `D:\Projects\24-HacktoberFest-2026\03-Week-3\data\k1_biblocal\task9-review\`.
3. From the repository, run the preview-only command:

   ```powershell
   .venv/Scripts/biblocal.exe apply data/k1_biblocal/task9-review/corrections.csv --results data/k1_biblocal/task9-review/results.csv --start-list data/k1_biblocal/start-truth.csv
   ```

4. Inspect `data/k1_biblocal/task9-review/results_final.csv`. The five corrected
   rows should have reason `manual`, with your bibs (or none). Other rows
   should retain their previous values. This command does not write metadata.
5. Report PASS or FAIL, and the browser used.

Amit reported completion on 18 Oct and exported all **20 cards**, including
two No bib choices. Browser name was not supplied. The first preview-only
apply correctly rejected numbers in four rows. Amit explicitly approved
replacing those rows with their RBNR labels while retaining the start-list
guard. Those four changes are in a separate `corrections-validated.csv`;
the original exported file and the other 16 corrections are preserved.

Preview-only apply on the validated file **passed**. The inspected
`results_final.csv` contains 100 rows: 20 manual results (18 tagged, two none)
and 80 unchanged rows. All 100 source JPEG hashes and original input CSV
hashes match. No metadata was written, and the original invalid correction
still fails validation. The exact command and evidence are recorded in
[release-check.md](release-check.md). End-to-end acceptance is **PASS**.
These manually resolved results do not change the published OCR accuracy.
