# BibLocal

## What it does

BibLocal reads runners' bib numbers in JPEG race photos on a CPU, offline.
Default scans preserve photos and write a CSV and local review page. Opt-in writes add bib keywords.

## Quick start

Tested on Windows 11 with Python 3.13.7. Install Python 3.13 and this checkout on D:.
Run in PowerShell from the checkout:

```powershell
$env:PIP_CACHE_DIR = "D:\.cache\pip"
New-Item -ItemType Directory -Force .tmp | Out-Null
$env:TEMP = (Resolve-Path .tmp).Path
$env:TMP = $env:TEMP
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install .
.venv/Scripts/biblocal.exe scan "D:\Photos\Race" --start-list "D:\Photos\start.csv"
```

Setup needs package access or prepared local wheels. It installs CPU ONNX Runtime and RapidOCR's bundled models.
No CUDA, GPU runtime, account or API key is needed. This is a CLI, with no standalone executable or GUI.
Below, replace `biblocal` with `.venv/Scripts/biblocal.exe`. Venv activation is optional.
macOS and Linux are untested. Create `.venv` with `python3.13 -m venv .venv`.
Then use `.venv/bin/python -m pip install .` and `.venv/bin/biblocal`. Put ExifTool on PATH for writes.
For development, run `.venv/Scripts/python.exe -m pip install -e ".[dev]"`, then `.venv/Scripts/python.exe -m pytest -q`.
Tests use synthetic images and `.pytest_tmp/`. ExifTool and browser tests use separate local ExifTool and Edge installs. They skip when absent.

## Commands

```text
biblocal scan "D:\Photos\Race" --start-list "D:\Photos\start.csv"
biblocal scan "D:\Photos\Race" --start-list "D:\Photos\start.csv" --write embed
biblocal apply "D:\Photos\Race_biblocal\corrections.csv" --results "D:\Photos\Race_biblocal\results.csv" --start-list "D:\Photos\start.csv"
biblocal eval "D:\Photos\Race_biblocal\results.csv" --truth "D:\Photos\truth.csv"
biblocal bench "D:\Photos\Race" --limit 20
```

Scan reads JPEGs recursively and skips RAW and other formats. Output goes beside the source folder: `D:\Photos\Race_biblocal\`.
It contains `results.csv`, `run.json`, `review.html` and thumbnails. Keep `--out` outside the photo folder. `--no-review` skips the page.

The optional UTF-8 start list needs `bib` or `number`. It accepts `name` and `category` columns and comma, semicolon or tab separators.
Leading zeros stay intact. Duplicate numbers such as `007` and `7` are rejected.

Open `review.html` for uncertain results, thumbnails and candidate crops. Accepted and no-candidate rows remain in `results.csv`.
Enter bibs separated by semicolons. Press Enter or **Confirm & next**. Select **No bib** when needed, then confirm.
Save `corrections.csv` beside the results. Only confirmed cards export. Prefilled guesses and suggestions need confirmation.

Apply checks digits and membership in the supplied start list. An empty bib field means `none`. Use the same start list as the scan.
It writes `results_final.csv` and preserves the original CSV and photos by default. Keep `run.json` beside the results for the source path.
Add `--write embed` or `--write sidecar` to apply to write corrected files only. Suggestions never become tags.

Embed writes accepted JPEG keywords and keeps `<photo>_original` backups. `--no-backup` disables backups.
Writes keep existing keywords and avoid duplicate bibs. Changing a bib or choosing No bib does not remove old keywords; remove wrong tags in your photo manager.
Default flat keywords are bib numbers. `--keyword-template "Race-{bib}"` changes them. `--with-names` adds start-list names. Hierarchy is `Bib|<bib>`.

Sidecar mode creates or updates `<stem>.xmp` beside accepted photos. JPEG bytes stay unchanged.
Lightroom uses embedded metadata for JPEGs and same-stem sidecars for RAW. For catalogued photos, use **Metadata > Read Metadata from Files**.

Only writes need separate [ExifTool](https://exiftool.org/). Keep `exiftool.exe` and `exiftool_files` together in `D:\tools\exiftool\`.
Set `$env:BIBLOCAL_EXIFTOOL = "D:\tools\exiftool\exiftool.exe"` or pass `--exiftool "D:\tools\exiftool\exiftool.exe"`.
Write failures return exit code 2. Details go in `run.json` for scans and the JSON summary for apply.

Embeds stage copies under the photo folder and reject metadata-loss warnings. Long legacy IPTC text can require sidecars. New sidecar paths containing `%` are unsupported.
Amit confirmed keyword filtering and hierarchy in **digiKam 9.1.0**. Lightroom Classic is untested. See [K4](docs/notes/k4.md) and [writer checks](docs/notes/exiftool-api.md).

Eval takes a UTF-8 `file,bibs` CSV. Paths are relative to the photo folder. Separate bibs with semicolons; blank means no readable bib.
Eval prints hit, wrong and review rates plus the K1 verdict. Bench prints CPU timing and K2. It saves `bench.json` in the sibling output folder. Record the power condition.
Eval and bench do not write photo metadata.

## Accuracy and limits

Defaults: accept **0.90**, review **0.50**, minimum box height **4%** of upright image height, maximum side **2048 pixels**.
The CLI requires `0.50 <= review <= accept <= 1`. OCR filters lower scores. Plain code checks digits, length, start-list membership, height and frequent numbers.
Results are **in-sample: 100 RBNR photos, no held-out set**. All have annotated bibs; none exceeds 1.07 MP. Bib-free and native high-resolution photos were not evaluated.

| Start list | Meaning | Photo hit rate | Wrong accepted tags |
|---|---|---:|---:|
| Range | Realistic proxy: each event's lowest through highest truth bib | 80% | **7.76% (9/116)** |
| Truth | Best case: only bibs in the labelled sample | 80% | 0% (0/107) |
| Dense | Stress test: every number from 1 to 90,135 | 80% | 13.71% (17/124) |

A hit means at least one correct tag, not every runner found. Wrong rate is wrong tags divided by accepted tags, not photos.
Range lists fail the **less-than-3% wrong** target. Truth-list results do not represent real start lists.

The height rule misses small bibs. At accept 0.90, set2 falls from **29/33 (87.88%) without it to 23/33 (69.70%) at 4%**.
Blurred, obscured and angled bibs can be missed. Human review is needed. The small-bib fallback (Task 5b) is deferred.
Changing 5% / 0.80 to 4% / 0.90 raised hits **71% to 80%**. Range wrong fell **8.33% to 7.76%**. Dense wrong rose **12% to 13.71%**. See [calibration](docs/notes/calibration.md).

Timings use **one CPU worker**, default OCR thread counts and an Intel Core i7-13650HX. The worker pool (Task 10) is cut.
K2 uses **20 upscaled RBNR JPEGs**, 6000x4000, quality 92: synthetic 24 MP, not camera originals. They are never used for accuracy.

| Run | Power condition | Seconds/photo | Estimated minutes/1,000 |
|---|---|---:|---:|
| Original spike, synthetic 24 MP, max side 2048 | Not recorded | **2.07** | **34** |
| Task 7, synthetic 24 MP, max side 2048 | AC, user-reported | **1.53** | **25.5** |
| Task 7, synthetic 24 MP, max side 2048 | Battery saver, user-reported | **12.49** | **208** |
| Task 7 retry, synthetic 24 MP, max side 1536 | Battery saver, user-reported | **14.39** | **240** |
| Task 7, matching 20 native RBNR images, max side 2048 | AC, user-reported | **0.57** | **9.5** |

The 2.07 figure is that spike run. Battery saver took about **12-14 s/photo**, versus **1.53 on AC**. Power condition matters.
Per-1,000 times are estimates, not measured batches. Timings include decode, resize, OCR and first-use setup. They exclude metadata writes. See [timing methods](docs/notes/bench.md).

## Privacy/offline

Photos, start lists and results stay local. The app makes no network calls and has no telemetry.
Local model checksums are checked before use. Missing or changed models cause an error, with no automatic download. Repair them by reinstalling pinned RapidOCR during setup.

After setup, scan with Wi-Fi off and Ethernet unplugged to check offline use. The review page is a local file; it needs no server.
Thumbnails, CSVs and logs contain private photo data. Protect output folders like originals. Save browser downloads beside results on D:.
Git ignores `data/` and `*_biblocal/`. Keep other photo/output paths outside the checkout or explicitly ignore them. Never commit real people's photos.

## Licence

[MIT](LICENSE), copyright 2026 Amit Sahoo. [MODELS.md](MODELS.md) lists model sources, versions, sizes, checksums and licences.
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) lists tested dependencies and full supplied licence texts, including approved MPL/LGPL components.
ExifTool is installed separately under its own terms. Built with help from Claude Code. Implementation and verification also used OpenAI Codex.
