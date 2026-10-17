# BibLocal Design

Status: draft for Amit's review, 14 Oct 2026. Nothing is built until Amit approves this spec and the plan.
Plan: `docs/superpowers/plans/2026-10-14-biblocal-mvp.md`. Background: `docs/research.md`.

## 1. Understanding

What Amit said:
- Build BibLocal for DEV Hacktoberfest Week 2: an offline bib tagger for race photographers.
- Use Claude Code locally. Plan first, then build.
- Building through to Monday 19 Oct is acceptable to him.

Assumptions (correct any that are wrong):
- About 2.5–3 focused hours on weekday evenings and about 7 hours on each of Saturday and Sunday.
- Amit's laptop is the dev machine: Windows 11, Python 3.13, everything on D:. Its RTX 4060 is not used.
- No Lightroom Classic licence is assumed. digiKam (free) is the fallback for the keyword check.
- Amit writes the DEV post himself, with AI help disclosed.

One change from what Amit said: code freeze is Sunday 18 Oct, 18:00 IST, not Monday. The hard deadline is Monday 19 Oct, 12:29 PM IST, and writing quality carries the most judging weight, so Monday morning is for submitting, not building.

## 2. Problem and users
Freelance and small-team race photographers shoot 1,000–5,000 photos per event. So that runners can find their photos, they type each runner's bib number into keywords by hand; forum posts put this at 90 minutes to several hours per race. Cloud tools exist, but they upload photos of the public (often including minors) and charge per photo or per credit.

## 3. Goals and non-goals
Goals (MVP):
- Read bib numbers from a folder of JPEG race photos, offline, on a CPU-only laptop.
- Tag only validated numbers; send uncertain photos to a fast review page.
- Write keywords that Lightroom, digiKam, darktable and Photo Mechanic can read, without damaging originals.
- Ship a Windows zip a non-technical photographer can run, plus `pip install` for Mac and Linux.

Non-goals (MVP): face recognition, galleries or sales, video, motorsport number plates, accounts, payments, anything in the cloud, GPU acceleration, RAW decoding. RAW files get tags through sidecars named after the JPEG's stem.

## 4. Requirements
Functional:
- F1 Scan a folder recursively for `.jpg` and `.jpeg` files (any case). Skip and count other files. Skip folders whose names end in `_biblocal`.
- F2 Optional start list CSV: `bib` (or `number`) column required; `name` and `category` optional; comma, semicolon or tab delimiter; UTF-8 with or without BOM.
- F3 For each photo, a status of `tagged`, `review`, `none` or `error`, with bibs, scores, names, raw candidates, suggestions and reason codes.
- F4 Outputs in the output folder: `results.csv`, `run.json`, `review.html` and `thumbs/`.
- F5 `--write sidecar` writes `<stem>.xmp` beside the photo; `--write embed` writes into the JPEG. By default nothing is written to photos.
- F6 The review page exports `corrections.csv`. `biblocal apply` merges the corrections and writes their keywords.
- F7 `biblocal eval` and `biblocal bench` measure kill tests K1 and K2.
- F8 (optional) A small GUI and drag-a-folder launchers for Windows.

Non-functional (exact values):
- N1 CPU only; no GPU execution provider.
- N2 No network calls at runtime; works with Wi-Fi off after install.
- N3 Throughput: effective time per photo (wall time ÷ photos) ≤ 2.0 s for 24 MP JPEGs on Amit's laptop, about 35 minutes per 1,000 photos. Kill above 5.0 s.
- N4 Accuracy on readable photos with a start list: hit rate ≥ 70% and wrong-tag rate < 3%. Kill below a 50% hit rate.
- N5 Photos are unchanged unless `--write` is passed; pixel data is unchanged even then.
- N6 Re-running never duplicates keywords and keeps keywords that were already there.
- N7 Every shipped dependency and model has a permissive licence, except the approved MPL-2.0 (tqdm; certifi unmodified only, approved 17 Oct 2026) and LGPL-2.1 libraries bundled in opencv-python-headless (FFmpeg) and Shapely (GEOS), which ship with their notices and licence texts. Include certifi's source link, https://github.com/certifi/python-certifi. exiftool ships unmodified as a separate program, with its notice.
- N8 Windows 10/11 first. Mac and Linux through pip, marked "untested" until someone tests them.

## 5. Approaches considered
| | A. Python CLI + optional tkinter GUI (recommended) | B. C#/.NET WinForms | C. Browser app |
|---|---|---|---|
| OCR | RapidOCR 3.10.0 (official, Apache-2.0) on ONNX Runtime CPU | ONNX Runtime C# with a RapidOCR .NET port | ONNX Runtime Web with PP-OCR ONNX files |
| Platforms | Windows zip; Mac and Linux via pip | Windows only | Any browser |
| Writing keywords | exiftool | exiftool | Not reliable from a browser |
| Build speed | Fastest; evaluation scripts are trivial | Slower; port maturity unknown | Slow; memory limits on large folders |
| Weak point | Package size; SmartScreen warning | Excludes Mac photographers | Cannot edit files in place |

Decision: A. Reaching Mac photographers and using the maintained Python package matter more than Amit's C# strength.

## 6. Architecture
```
photos folder
  └─ list_photos             JPEGs only, recursive, skips *_biblocal folders
      └─ load_for_ocr         Pillow draft decode → EXIF orientation → long side ≤ 2048
          └─ OcrEngine.read   RapidOCR on ONNX Runtime (CPU)
              └─ extract_candidates   digit runs, length limits, letter→digit map
                  └─ decide           start list + thresholds → tagged / review / none / error
                      └─ demote_frequent (whole run)   signage numbers → review
                          ├─ results.csv + run.json
                          ├─ review.html + thumbs/ ─► corrections.csv ─► biblocal apply ─┐
                          └─ exiftool (only with --write) ◄─────────────────────────────┘
```
Modules, one responsibility each: `models.py` (types), `startlist.py`, `bibs.py` (rules), `loader.py`, `ocr.py`, `pipeline.py`, `csv_io.py`, `exif.py`, `review.py`, `evaluate.py`, `bench.py`, `cli.py`, `gui.py`.

## 7. Decision rules
Defaults (`Settings`): accept 0.80; review 0.50; length 1–5 digits (from the start list's normalized lengths when a list is given); max side 2048 px; frequent share 0.25 with at least 20 photos.
1. Each OCR text is split on whitespace into tokens. Tokens that contain `:` or `.`, or end in `K` or `KM` (any case), are skipped, so race-clock times (`1:23:45`) and distances (`10K`, `42.195`) never yield candidates; a start list cannot catch them because start lists often run 1…N. Letter-to-digit mapping applies only to a token in which at least half the characters are digits: O,o→0; I,l,|→1; S,s→5; B→8; Z,z→2. So `"BIB 247"` yields only `247`, while `"2O7"` yields `207`. Mapped candidates get score × 0.9 and the reason `mapped_chars`.
2. Task 7 amendment (authorized 17 Oct): reject tokens with any letters remaining after mapping. Skip hits whose vertical box span divided by the loaded upright image height is below 0.05, before deduplicating. Candidates are digit runs within the length limits. If the same number appears twice in one photo, the higher score is kept. The 5% minimum was calibrated on K1; range/dense wrong rates still fail the 3% target (see `docs/notes/calibration.md`).
3. Bibs are compared with leading zeros removed, so `"007"` matches `"7"`. Tags use the start list's spelling.
4. `tagged`: at least one candidate with score ≥ accept that is in the start list (or any such candidate when there is no list).
5. `review`: nothing accepted, but a candidate scores ≥ review, or a candidate fails only the start-list check and has a near match (edit distance 1, at most 3 suggestions, same-length matches first). Reasons: `low_confidence`, `not_in_start_list`.
6. `none`: everything else. `error`: the file could not be decoded (`decode_error`); the run continues.
7. Frequent-number filter, after the run: a number tagged in more than 25% of photos, in a run of at least 20 photos, is treated as signage (race clock, year, sponsor) and removed. With a start list, only numbers outside the list are filtered. A photo left with no bibs moves to `review` with `frequent_number`.
8. Thresholds change only with evidence from `biblocal eval` (Task 7), recorded in `docs/notes/calibration.md`.

## 8. Files and formats
- `results.csv`: `file,status,bibs,scores,names,candidates,suggestions,reasons,ms`. `file` is relative to the photo folder, with forward slashes. List fields are separated by `;`. Each `candidates` item is `number:score`.
- `truth.csv` and `corrections.csv`: `file,bibs`, with bibs separated by `;`. Empty means "no readable bib".
- `run.json`: tool version, start and end time, arguments, counts per status, median and p90 ms, effective seconds per photo, RapidOCR and ONNX Runtime versions, model files with SHA-256, Python version, CPU name, worker count.
- Keywords: flat `{bib}` (template configurable) and hierarchical `Bib|{bib}`. Runner names only with `--with-names`.
- Default output folder: `<photo folder>_biblocal`, beside the photo folder.

## 9. Writing metadata
- One exiftool process per batch of up to 500 files, driven by an argument file with `-execute` between files. Argument files hold one argument per line, without quotes. File names are UTF-8 (`-charset filename=utf8`); IPTC is written as UTF-8. Options for every file, such as these charset options, go after `-common_args` on the command line: options do not carry past `-execute`, and `-common_args` does not work inside an argument file (tested with exiftool 13.59).
- Each keyword is removed and then added (`-TAG-=K -TAG+=K`), so reruns never duplicate it.
- Embed (JPEG): `XMP-dc:Subject`, `IPTC:Keywords` and `XMP-lr:HierarchicalSubject`. exiftool's `_original` backup is kept unless `--no-backup` is passed.
- Sidecar: `<stem>.xmp` beside the photo, the naming Lightroom, Capture One and Photo Mechanic use. It also covers a RAW file with the same stem. It is created if missing and edited in place if present, so existing sidecar content survives.
- Lightroom reads embedded keywords for JPEGs and `.xmp` sidecars for RAW files. Photos already in a catalog need Metadata > Read Metadata from Files.

## 10. Review page
- A static `review.html` with inline CSS and JS and no external URLs. Images live in `thumbs/`: a 640 px thumbnail plus a zoomed crop of the best candidate box.
- One card per `review` photo, showing:
  - the thumbnail and the zoomed crop;
  - candidates with their scores;
  - suggestion buttons;
  - an input prefilled with the best guess;
  - a "No bib" toggle.
- Enter accepts the card and moves to the next one.
- "Download corrections.csv" builds the file in the browser. `biblocal apply` validates it (digits only) and writes keywords.

## 11. Performance
- Decode at reduced size with Pillow's JPEG draft mode, then apply EXIF orientation, then resize to a long side of 2048 px. Request the draft at the target size with the photo's own aspect ratio, not a square, so a 6000×4000 JPEG decodes at 3000×2000 instead of full size.
- The detection input size matches the max side. RapidOCR 3.10.0 shrinks any input larger than `Global.max_side_len` (default 2000) before detection, so the engine sets `Global.max_side_len`, `Det.limit_type: max` and `Det.limit_side_len` to the max side (keys verified in Task 1). Without this, any max side above 2000, including the K1 retry at 3072, has no effect. The angle classifier stays off unless K1 shows rotated failures.
- Parallelism (Task 10, if needed): a process pool with one OCR engine per worker, and a Windows-safe entry point with `freeze_support()`.
- Small-bib fallback (Task 5b, only if K1 is WEAK): re-run recognition on full-resolution crops of small boxes, or detect on 2×2 overlapping full-resolution tiles if detection itself misses them. Keep whichever `eval` proves better.

## 12. Evaluation and kill tests
| Test | Measure | Pass | Kill |
|---|---|---|---|
| K1 accuracy | 50–100 real photos with `truth.csv`; start list built from truth, and reported again with a dense list from 1 to the highest truth bib | hit ≥ 70% and wrong < 3% | hit < 50% after one retry at max side 3072 |
| K2 speed | effective s/photo (wall time ÷ photos) on at least 20 of Amit's own 24 MP JPEGs in `data/k2/` (no truth needed), CPU only | ≤ 2.0 s | > 5.0 s after one retry at max side 1536 |
| K3 chatbot | the same 20 photos in free ChatGPT, Gemini and Claude: accuracy, minutes spent, upload limits hit; then ask each to keyword 2,000 files | the chatbots cannot handle the volume or the file output | none; report honestly |
| K4 metadata | keywords visible in Lightroom Classic, or digiKam without Lightroom | pass | fail blocks the release |
| K5 demand | one question (not a promotion) on the dgrin sports forum | ≥ 2 replies by Saturday 17 Oct | soft signal only |

Report timings as measured on Amit's gaming laptop CPU, and also with one worker. Many photographers' laptops are slower.

## 13. Packaging
- `pip install .` provides the console script `biblocal` (and `biblocal-gui` if the GUI ships).
- Windows zip, built with PyInstaller in one-folder mode. It contains:
  - the RapidOCR model files;
  - exiftool and its `exiftool_files` in `exiftool/`;
  - two launchers: `BibLocal-preview.bat` (scan only, writes nothing to photos) and `BibLocal-tag.bat` (scan and embed, with backups).
- The build is unsigned, so Windows SmartScreen warns; the README says so.
- Every release candidate: network disabled, run on a copy of a real folder, check the outputs and the keywords.

## 14. Risks and mitigations
| Risk | Root cause | Mitigation | Task |
|---|---|---|---|
| Small, blurred or angled bibs missed | The bib covers few pixels after downscaling | Tune the max side; small-bib fallback; review queue; near-match suggestions | 1, 5b, 7, 9 |
| Non-bib numbers tagged | Race clock, year, sponsor text | Start list; length limits; frequent-number filter | 3 |
| Letter/digit confusion | Fonts, motion blur | Conservative mapping with a score penalty; start list | 3 |
| Keywords not visible in Lightroom | JPEG vs RAW metadata rules; catalog cache | Embed for JPEG, sidecar for RAW; README note; K4 | 8, 11 |
| Install friction | Non-technical users, unsigned exe | Zip plus drag-a-folder launchers; three-step README | 11, 13 |
| Slow on old laptops | CPU-bound OCR | Draft decode, worker pool, `--max-side`, progress with counts | 4, 10 |
| Offline claim broken | A library downloads models on first run | Checked in Task 1; network-off test before release | 1, 13 |
| Deadline | Building spills into Monday | Code freeze Sunday 18:00 IST; GUI optional | all |

## 15. Lateral pass (provocation)
Target: read bibs accurately and fast on a CPU from 24 MP photos.
Rules everyone treats as fixed: every photo is OCR'd; OCR reads the whole photo; each photo is decided alone; the photographer waits until the tool finishes; the bib is only what the pixels say.
- **Po: the photographer reads the bibs and the AI types.**
  - Principle: people recognise faster than they type.
  - Movement: show a zoomed crop with a prefilled guess; Enter accepts.
  - Kept: review page (section 10).
- **Po: the start list reads the photo.**
  - Principle: the set of valid bibs is known before the race.
  - Movement: only list members become tags; near misses become one-click suggestions.
  - Kept: rules 4–5.
- **Po: the tool OCRs one photo in ten.**
  - Principle: photographers shoot bursts of the same runner.
  - Movement: read the sharpest frame and suggest its bib for neighbours within 2 s.
  - Deferred to v2 ("burst consensus"), as suggestions only.
- **Po: the number is printed on the runner's face.** No useful movement after two attempts; a face detector would add a model and days of work. Abandoned.
- **Po: runners tag themselves.**
  - Principle: runners know their own bib.
  - Movement leads to gallery search, which already exists. Abandoned for this tool.

Pattern: the provocations that paid off used information the photographer already has (the start list, burst order, a human glance) instead of a bigger model.

## 16. Open questions (defaults apply if unanswered)
1. Do you have Lightroom Classic? Default: run K4 in digiKam.
2. Can you put 50 real race photos in `data/k1/` tonight? Default: use the RBNR dataset for testing only. Its licence is unknown, so never commit or publish it. RBNR photos are at most 1.07 MP and every one contains a bib, so RBNR is only a low-resolution K1 proxy; K2 always uses 24 MP photos in `data/k2/`.
3. GUI or not? Default: only after v0.1.0 ships, and only if at least 3 hours remain before code freeze. Until then, the drag-a-folder launchers cover non-technical users.

## 17. What to revisit after the challenge
Burst consensus; fine-tuning the recognizer on bib fonts with PaddleOCR; person crops for wide shots; a Lightroom Classic plugin; signed Windows and macOS builds; gallery export (SmugMug, Pixieset).
