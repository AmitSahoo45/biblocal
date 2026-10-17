# BibLocal

BibLocal reads runners' bib numbers in JPEG race photos on a CPU, offline.
The default scan writes results to an output folder and preserves the photos.

## Writing keywords

From the repository's configured virtual environment:

```powershell
.venv/Scripts/biblocal.exe scan "D:\Photos\Race" --start-list "D:\Photos\start.csv"
.venv/Scripts/biblocal.exe scan "D:\Photos\Race" --start-list "D:\Photos\start.csv" --write embed
```

The first command writes only results. The second embeds accepted bib keywords
in JPEGs and keeps `<photo>_original` backups. Reruns keep existing keywords and
do not duplicate the requested bibs. Review suggestions are never written.
`--no-backup` disables backups; `--keyword-template "Race-{bib}"` changes flat
keywords, and `--with-names` adds start-list names.

Use `--write sidecar` to create or update `<stem>.xmp` beside each accepted
photo. JPEG bytes stay unchanged. Lightroom reads embedded metadata for JPEGs
and sidecars for RAW files with the same stem. For photos already catalogued,
use **Metadata > Read Metadata from Files** after writing.

Writing requires the separate ExifTool program. Set `BIBLOCAL_EXIFTOOL` or pass
`--exiftool "D:\tools\exiftool\exiftool.exe"`. Per-file write failures appear in
`run.json`, and the command returns exit code 2. Embeds use temporary copies
under the photo folder and refuse writes when ExifTool warns of metadata loss;
long legacy IPTC text may require sidecars. Creating a new sidecar in a path
containing `%` is unsupported. See [writer verification](docs/notes/exiftool-api.md).

Keyword filtering and hierarchy passed in **digiKam 9.1.0**, confirmed by Amit
at [CHECKPOINT C](docs/notes/k4.md). Lightroom Classic remains untested.

## Accuracy

Current defaults: confidence **0.90**, minimum text-box height **4%** of the
upright image height. Results below are **in-sample**, on **100 RBNR photos**;
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
