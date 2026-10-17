# BibLocal

BibLocal reads runners' bib numbers in JPEG race photos on a CPU, offline.
It can write accepted bibs as photo keywords. A default scan preserves photos
and writes a CSV and a local review page beside the photo folder.

## Install on Windows

Tested on Windows 11 with Python 3.13.7. Install Python 3.13 on D: and put this
source checkout on D:, then run these commands in PowerShell from its folder:

```powershell
$env:PIP_CACHE_DIR = "D:\.cache\pip"
New-Item -ItemType Directory -Force .tmp | Out-Null
$env:TEMP = (Resolve-Path .tmp).Path
$env:TMP = $env:TEMP
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install .
```

Installation needs access to Python packages (or a prepared local wheel
directory). It installs CPU-only ONNX Runtime and RapidOCR's bundled models.
No CUDA, GPU runtime, account or API key is needed. This release is a Python
CLI; there is no standalone Windows executable or desktop GUI.

The command examples below use `biblocal`. On Windows, run it as
`.venv/Scripts/biblocal.exe` from the checkout; activating the venv is optional.
For example:

```powershell
.venv/Scripts/biblocal.exe scan "D:\Photos\Race" --start-list "D:\Photos\start.csv"
```

Scan reads JPEGs recursively. RAW files and other formats are skipped. The
default output is `D:\Photos\Race_biblocal\`, containing `results.csv`,
`run.json`, `review.html` and its thumbnails. A custom `--out` must be outside
the photo folder. Use `--no-review` to omit the review page.

An optional UTF-8 start list has a `bib` (or `number`) column and optional
`name` and `category` columns. Comma, semicolon and tab delimiters work.
Leading zeros are preserved; duplicate numbers such as `007` and `7` are
rejected. Example:

```csv
bib,name
007,Sam
2605,Alex
```

macOS and Linux are **untested**. From a source checkout, use Python 3.13 to
create `.venv`, then `.venv/bin/python -m pip install .` and
`.venv/bin/biblocal`. Metadata writing also needs a separate ExifTool
installation on PATH. Only the Windows environment above was verified.

## Privacy and offline use

Photos, start lists and results stay on your computer. The application makes
no network calls and has no telemetry. OCR uses local model files whose
checksums are verified before use; a missing or changed model causes an
error rather than an automatic download. Reinstall the pinned RapidOCR
package during setup if its model files need repair.

After installation, turn Wi-Fi off (and disconnect Ethernet) and run a scan
to check this yourself. The review page also works as a local file without
a server. Its thumbnails, CSVs and run log contain private photo information;
keep the output folder as private as the originals. Browser downloads should
be saved beside the results, on D: for this development setup.

## Review and correct

Open `review.html` in your browser after `biblocal scan`. It lists uncertain
results with thumbnails and a cropped candidate. Accepted tags and photos
with no candidates are still listed in `results.csv`.

1. Read the photo, enter bibs separated by semicolons, and press Enter or
   **Confirm & next**. Use **No bib** when appropriate, then confirm.
2. Download `corrections.csv` into the output folder. Only confirmed cards
   are exported; a prefilled guess or suggestion alone is never confirmation.
3. Run `biblocal apply` with the same start list to validate your corrections:

```text
biblocal apply "D:\Photos\Race_biblocal\corrections.csv" --results "D:\Photos\Race_biblocal\results.csv" --start-list "D:\Photos\start.csv"
```

This writes `results_final.csv` and preserves the original results CSV and
photos. Corrections must contain digits; with a start list, numbers must
belong to it. An empty bib field records `none`. To write the confirmed
corrections into photos, repeat the command with `--write embed`, or use
`--write sidecar`. Only corrected files are considered for those writes.
Keep `run.json` beside the results: it records the source folder for writing.

## Writing keywords

Writing is opt-in:

```text
biblocal scan "D:\Photos\Race" --start-list "D:\Photos\start.csv"
biblocal scan "D:\Photos\Race" --start-list "D:\Photos\start.csv" --write embed
```

The first command writes only results. The second embeds accepted bib keywords
in JPEGs and keeps `<photo>_original` backups. Reruns keep existing keywords and
do not duplicate the requested bibs. Review suggestions are never written.
`--no-backup` disables backups; `--keyword-template "Race-{bib}"` changes flat
keywords, and `--with-names` adds start-list names.
Each bib also gets a hierarchical keyword `Bib|<bib>`.

Metadata writes are **additive**. Changing a bib or choosing No bib in review
does not delete a keyword already written to the photo. Remove an earlier
wrong keyword in your photo manager if necessary.

Use `--write sidecar` to create or update `<stem>.xmp` beside each accepted
photo. JPEG bytes stay unchanged. Lightroom reads embedded metadata for JPEGs
and sidecars for RAW files with the same stem. For photos already catalogued,
use **Metadata > Read Metadata from Files** after writing.

Writing requires the separate [ExifTool](https://exiftool.org/) program; scan,
review, evaluation and benchmarking do not. On Windows, keep `exiftool.exe`
and its supplied `exiftool_files` folder together under `D:\tools\exiftool\`.
Set `$env:BIBLOCAL_EXIFTOOL = "D:\tools\exiftool\exiftool.exe"` or pass
`--exiftool "D:\tools\exiftool\exiftool.exe"`. Per-file write failures appear in
`run.json` for scans, or the JSON summary for apply, and the command returns
exit code 2. Embeds use temporary copies
under the photo folder and refuse writes when ExifTool warns of metadata loss;
long legacy IPTC text may require sidecars. Creating a new sidecar in a path
containing `%` is unsupported. See [writer verification](docs/notes/exiftool-api.md).

Keyword filtering and hierarchy passed in **digiKam 9.1.0**, confirmed by Amit
at [CHECKPOINT C](docs/notes/k4.md). Lightroom Classic remains untested.

## Accuracy

Current defaults: confidence **0.90**, minimum text-box height **4%** of the
upright image height, review threshold **0.50**, maximum processing side
**2048 pixels**. The CLI requires `0.50 <= review <= accept <= 1` because the
OCR engine filters lower scores. Digits, length, start-list membership,
height and frequent-number rules are checked in ordinary code; uncertain
suggestions are never written as tags.

Results below are **in-sample**, on **100 RBNR photos**;
there is **no held-out set**. Every photo contains an annotated bib, and images
are at most 1.07 MP. These results do not establish accuracy on bib-free photos
or native high-resolution camera images.

| Start list | Meaning | Photo hit rate | Wrong accepted tags |
|---|---|---:|---:|
| Range | Realistic proxy: each event's lowest through highest truth bib | 80% | **7.76% (9/116)** |
| Truth | Best case: only bibs present in the labelled sample | 80% | 0% (0/107) |
| Dense | Broad stress test: every number from 1 through 90,135 | 80% | 13.71% (17/124) |

A hit requires at least one correct tag in a photo; it does not mean every
runner was found. Wrong rate counts incorrect accepted tags, not photos.
The realistic range-list result **does not meet the target of less than 3%
wrong tags**. The best-case truth list must not be used to claim that accuracy
for real start lists.

Small bibs are a known limit of the height rule. On set2, hits fall from
**29/33 (87.88%) without the height filter to 23/33 (69.70%) at 4%**, both at
confidence 0.90. Blurred, obscured and angled bibs can also be missed. Task 5b's
small-bib fallback remains deferred.

The 4% / 0.90 selection raises aggregate hits from 71% to 80% and reduces
range wrong from 8.33% to 7.76% compared with the earlier 5% / 0.80 setting;
dense wrong rises from 12% to 13.71%. See the full
[calibration evidence](docs/notes/calibration.md).

## Speed

All figures below use **one worker**, CPU only, on an Intel Core i7-13650HX.
K2 is **20 upscaled RBNR JPEGs**, resized to 6000×4000, quality 92: synthetic
24 MP images, not camera originals and never used for accuracy. One worker
uses the OCR runtime's default CPU thread counts. Task 10's worker pool is cut.

| Measured run | Power condition | Seconds/photo | Estimated minutes/1,000 |
|---|---|---:|---:|
| Original spike, synthetic 24 MP, max side 2048 | **Not recorded** | **2.07** | **34** |
| Task 7, synthetic 24 MP, max side 2048 | **AC power, user-reported** | **1.53** | **25.5** |
| Task 7, synthetic 24 MP, max side 2048 | **Battery saver, user-reported** | **12.49** | **208** |
| Task 7 retry, synthetic 24 MP, max side 1536 | **Battery saver, user-reported** | **14.39** | **240** |
| Task 7, matching 20 native RBNR images, max side 2048 | **AC power, user-reported** | **0.57** | **9.5** |

The original **2.07 s/photo** is the result of that spike run, whose power
condition was not recorded. Later battery-saver measurements were about
**12–14 s/photo**, versus **1.53 s/photo on AC**. Power condition matters.
The per-1,000 figures are extrapolations, not measured 1,000-photo batches.
Benchmarks cover decode, resize and OCR, including first-use initialization;
they exclude metadata writing. See [timing methods and saved results](docs/notes/bench.md).

## Evaluate and benchmark

Use `biblocal eval` with a UTF-8 truth CSV whose columns are `file,bibs`.
File paths are relative to the scanned folder, multiple bibs use semicolons,
and a blank bib field means no readable bib:

```csv
file,bibs
race_01.jpg,007;2605
race_02.jpg,
```

```text
biblocal eval "D:\Photos\Race_biblocal\results.csv" --truth "D:\Photos\truth.csv"
biblocal bench "D:\Photos\Race" --limit 20
```

Evaluation prints hit, wrong and review rates and the K1 verdict. `biblocal
bench` writes `bench.json` in the sibling output folder and prints CPU
timing and the K2 verdict. Record your power condition alongside the result.
Neither command writes photo metadata.

## Development and licenses

Install the test extra with `.venv/Scripts/python.exe -m pip install -e ".[dev]"`,
then run `.venv/Scripts/python.exe -m pytest -q`. Test images are synthetic;
pytest temporary files stay in `.pytest_tmp/`. ExifTool integration tests need
the separate executable; the browser interaction test uses an existing local
Microsoft Edge installation. Those tests skip if their programs are absent.

BibLocal is [MIT licensed](LICENSE), copyright 2026 Amit Sahoo.
[MODELS.md](MODELS.md) records model sources, versions, sizes, checksums and
licenses. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) contains the tested
dependency inventory and full supplied license texts, including the approved
MPL/LGPL components. ExifTool is separately installed and keeps its own terms.
`data/` and `*_biblocal/` folders are excluded from Git. Keep other photo
folders and custom output paths outside the checkout, or explicitly ignore
them before use. Never commit real people's photos.

Built with help from Claude Code. Implementation and verification also used
OpenAI Codex. Human review remains necessary; the measured limits above are
part of this release.
