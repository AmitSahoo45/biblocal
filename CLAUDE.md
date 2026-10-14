# BibLocal

Offline tool that reads runners' bib numbers in race photos on an ordinary CPU-only laptop and writes them as keywords that Lightroom and other photo tools can filter. Entry for the DEV Hacktoberfest 2026 Open-Source AI Challenge, Week 2 ("Side Hustle").

- Code freeze: 18 Oct 2026, 18:00 IST.
- Hard submission deadline: 19 Oct 2026, 12:29 PM IST.

## Documents
- Design, the source of truth for behavior: `docs/superpowers/specs/2026-10-14-biblocal-design.md`
- Task plan, the source of truth for scope and order: `docs/superpowers/plans/2026-10-14-biblocal-mvp.md`
- Background research (evidence, competitors, kill tests): `docs/research.md`. Read it only when a task needs it. Do not redo the research.
- Verified facts about libraries go in `docs/notes/` (for example `docs/notes/rapidocr-api.md`). Check there before guessing an API.

## Non-negotiable rules
1. **CPU only.** Install the `onnxruntime` CPU package. Never install `onnxruntime-gpu` or `onnxruntime-directml`, and never select a GPU execution provider, even though the dev laptop has an RTX 4060. All timings are CPU timings.
2. **Offline at runtime.** The app makes no network calls. Models ship inside the installed package or the release folder. Release candidates are tested with the network disabled.
3. **Preserve originals.** A default run writes only to the output folder. Changing photos or sidecars needs `--write sidecar` or `--write embed`. Embedding keeps exiftool's `_original` backups unless `--no-backup` is passed.
4. **Abstain over guess.** A number becomes a tag only after validation (digits, length, start list, confidence threshold). Anything uncertain goes to review. Suggestions are never written as tags.
5. **Deterministic checks.** Validation, counting and arithmetic are plain code. OCR output is only an input to them.
6. **Licenses.** Runtime Python dependencies must be permissive (MIT, BSD, Apache-2.0, HPND or similar). No AGPL or GPL Python dependencies. Approved exception (15 Oct 2026): tqdm (MPL-2.0) and the LGPL-2.1 libraries bundled in permissive wheels (FFmpeg in opencv-python-headless, GEOS in Shapely), shipped with their notices and licence texts in `THIRD_PARTY_NOTICES.md`. exiftool is a separate program called as a subprocess. Record every model file, its source, version, size, SHA-256 and license in `MODELS.md`. Project license: MIT.
7. **Disk.** Everything lives on D:. Never install or cache anything on C:. Virtual environment: `.venv` in the repo. pip cache: `D:\.cache\pip` (user environment variable `PIP_CACHE_DIR`). Any model cache stays under the repo or D:. pytest temp files: `.pytest_tmp/` in the repo (`--basetemp`). PyInstaller cache: `D:\.cache\pyinstaller` (`PYINSTALLER_CONFIG_DIR`).
8. **No real people's photos in git.** `data/` and `*_biblocal/` output folders are git-ignored. Tests use synthetic images only.
9. **Small changes.** Make the smallest change that passes the current task's tests. No dependency outside the plan without asking first. No refactoring outside the current task.

## Environment
- Windows 11, Python 3.13. Fall back to 3.12 only if a required wheel is missing, and record why in `docs/notes/`.
- Run Python without activating the venv: `.venv/Scripts/python.exe` (works in Git Bash and PowerShell).
- Tests: `.venv/Scripts/python.exe -m pytest -q`
- exiftool: `D:\tools\exiftool\exiftool.exe`, with its `exiftool_files` folder beside it. Lookup order in code: `--exiftool`, then env `BIBLOCAL_EXIFTOOL`, then `<app dir>/exiftool/exiftool.exe` in frozen builds, then PATH. On this machine the user environment variable `BIBLOCAL_EXIFTOOL` points to it.
- Dev photos: `data/` (git-ignored): `data/k1/` for K1 (accuracy), `data/k2/` for K2 (speed, Amit's own 24 MP JPEGs), `data/rbnr/` for the RBNR dataset (never commit or publish).

## Working agreement
- Do one plan task at a time, in order. Test first, watch it fail, implement, watch it pass, commit.
- Commit messages: `task <N>: <what changed>`.
- After each task, report in at most four short lines: done, test result, any deviation from the plan, next task. Then stop and wait.
- Stop and ask before: adding a dependency not in the plan, changing scope, changing a value the spec fixes, or writing to any photo outside a temporary test copy.
- At a CHECKPOINT in the plan, stop and wait for Amit even if everything passed.
- Status messages: result first, numbered steps, no filler.
