# BibLocal MVP Implementation Plan

> **Latest ruling, 18 Oct 2026:** K4 PASS in digiKam 9.1.0: Bib > 2605
> matched exactly set1_12.JPG and set1_14.JPG, hierarchy visible. GO received
> for Task 9 then Task 11; list remaining work before 18:00 IST and stop.
>
> **17 Oct ruling:** CHECKPOINT B GO received for Task 8 after
> changing defaults to accept 0.90 and minimum height share 0.04, confirming
> truth-list CLI hit 80% / wrong 0%, and committing. README must label range
> as realistic, truth as best case, disclose set2 hit 69.70%, in-sample data,
> and power conditions for all speed figures. Task 5b stays deferred; Task 10
> stays cut. Stop at CHECKPOINT C after Task 8.

> **Accepted execution scope, 17 Oct 2026:** Tasks 1, 2–6 (5b only if K1 is
> WEAK), 7, 8, 9, 11, with stops at CHECKPOINTS A/B/C. Tasks 10, 12, 13 and
> the Task 14 script are cut. Report single-worker speed; README gives pip
> instructions. MIT copyright: Amit Sahoo. K1 uses a fixed 100-photo RBNR
> sample converted from its text labels. Amit has no 24 MP camera JPEGs:
> K2 instead uses 20 RBNR copies resized to 6000×4000 with Pillow LANCZOS,
> JPEG quality 92, plus timing on their original RBNR images. These copies
> are timing-only and must be described as upscaled RBNR, not camera originals.

> **Task 1 status, 17 Oct:** implemented; 19 synthetic tests passed. K1 PASS
> (88% hit, 0.8% wrong with truth-bib list; dense-list wrong 27.49%). K2 SLOW
> (2.066 s/photo on upscaled RBNR; matching originals 0.696 s/photo), one worker.
> CHECKPOINT A GO received; K2 SLOW accepted. Amit reported airplane-mode smoke
> PASS (`1 passed in 6.29s`). Details: `docs/notes/spike-k1k2.md`.
> certifi's MPL-2.0 exception was approved by Amit, unmodified only; include its
> source link and full license text in `THIRD_PARTY_NOTICES.md`.

> **Task 7 amendment from Amit:** Evaluate truth, per-RBNR-set min-to-max range,
> and dense start lists. If range wrong rate is >=3%, spend at most one hour
> on deterministic rules in bibs.py: reject period/colon/remaining-letter
> tokens after mapping, calibrate minimum box-height share, retain frequent
> filtering, and report before/after. No new model. Stop at CHECKPOINT B.

> **Execution status, 17 Oct:** Tasks 2–6 committed (`4e92af1`, `07bf9f9`,
> `6b2ce01`, `2eee8af`, `51a3911`). Task 7 calibration selects a 5% minimum
> vertical box-height share; accept stays 0.80. Truth K1 is 71% hit / 0% wrong;
> range is 71% / 8.33%, dense 71% / 12%. The multi-list <3% target remains
> unmet. No threshold met it while preserving 70% hits, so the existing
> confidence default is retained. See `docs/notes/calibration.md`. Task 5b
> is not triggered by the controlling truth-list PASS. Task 10 remains cut.
> Fresh K2 on user-reported AC power: PASS, 1.531 s/photo (synthetic 24 MP),
> matching native comparison 0.569 s/photo. Battery-saver runs were much slower
> and remain documented alongside the original 2.07 s/photo spike in
> `docs/notes/bench.md`. CHECKPOINT B requires Amit's GO before Task 8.

> **For agentic workers:** If the superpowers plugin is installed, use superpowers:executing-plans (or superpowers:subagent-driven-development) to run this plan task by task. Otherwise execute the tasks yourself, in order, one per prompt. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An offline, CPU-only tool that tags race photos with runners' bib numbers as Lightroom-readable keywords, shipped as a Windows zip and a pip package before code freeze (18 Oct 2026, 18:00 IST).

**Architecture:** A Python package with pure-logic modules (start list, bib rules) around two adapters: RapidOCR on ONNX Runtime CPU for reading, and exiftool for writing metadata. `scan` produces `results.csv`, `run.json` and a static review page; `apply` writes corrections. An optional tkinter GUI and a PyInstaller build wrap the CLI.

**Tech Stack:** Python 3.13, rapidocr 3.10.0, onnxruntime (CPU), Pillow ≥ 10.1, pytest, exiftool 13.x (external program), PyInstaller (release build only), tkinter (optional GUI).

**Spec:** `docs/superpowers/specs/2026-10-14-biblocal-design.md`

**Execution:** Native is recommended: one task per prompt in the main session, with `/clear` between tasks. The tasks share interfaces closely, there are 14 of them, and the schedule has no slack for per-task review agents. CHECKPOINTS A–D are the human review gates.

## Global Constraints
- Python 3.13 in `.venv` (3.12 only if a wheel is missing; record why). Run Python as `.venv/Scripts/python.exe`.
- CPU only: the `onnxruntime` CPU package, and `onnxruntime.get_device() == "CPU"`. Never install `onnxruntime-gpu` or `onnxruntime-directml`.
- No network calls at runtime. No external URLs in generated HTML.
- Photos are never modified unless `--write sidecar|embed` is passed. Embed keeps `_original` backups unless `--no-backup` is passed.
- `Settings` defaults: accept 0.80; review 0.50; length 1–5; max side 2048; frequent share 0.25 with ≥ 20 photos.
- K1: hit ≥ 0.70 and wrong < 0.03 = PASS; hit 0.50–0.70, or wrong ≥ 0.03 = WEAK; hit < 0.50 = KILL. The verdict uses the truth-bib proxy start list; every K1 run also reports a dense list from 1 to the highest truth bib.
- K2: effective s/photo (wall time ÷ photos) ≤ 2.0 = PASS; 2.0–5.0 = SLOW; > 5.0 = KILL. Measured on ≥ 20 of Amit's own 24 MP JPEGs in `data/k2/`, never on RBNR (≤ 1.07 MP).
- Keywords: flat `{bib}`, hierarchical `Bib|{bib}`. Names only with `--with-names`.
- Default output folder: `<photo folder>_biblocal` beside the photo folder.
- exiftool lookup order: `--exiftool`, then `BIBLOCAL_EXIFTOOL`, then `<app dir>/exiftool/exiftool.exe` in frozen builds, then PATH. On Amit's machine the user variable `BIBLOCAL_EXIFTOOL` is `D:\tools\exiftool\exiftool.exe`.
- Everything on D:, including pytest temp files (`--basetemp=.pytest_tmp` in the repo) and PyInstaller's cache (`PYINSTALLER_CONFIG_DIR=D:\.cache\pyinstaller`). `data/` and `*_biblocal/` are git-ignored. Tests use synthetic images only.
- Commit messages: `task <N>: <what changed>`. Never add `data/` to git.
- Code freeze: 18 Oct 2026, 18:00 IST. Hard deadline: 19 Oct 2026, 12:29 IST.

## Review Focus
1. Folder and file names with spaces and non-ASCII characters (`Lauf 2026/Zieleinlauf ü 01.jpg`) must be read, reported and written correctly. Tests: Task 6 `test_paths_with_spaces_and_non_ascii`; Task 8 `test_non_ascii_path_written`.
2. Start lists exported from Excel (UTF-8 BOM, `;` delimiter, leading zeros like `007`) must load and match OCR reads like `7`. Test: Task 2 `test_semicolon_bom_leading_zeros`.
3. Portrait photos stored with EXIF orientation 6 or 8 must be read upright. Test: Task 4 `test_exif_orientation_applied`.
4. Running twice on the same folder must not duplicate keywords and must keep keywords already present. Tests: Task 8 `test_embed_twice_no_duplicates` and `test_embed_keeps_existing_keyword`.
5. A corrupt or zero-byte JPEG must become an `error` row while the run continues. Tests: Task 4 `test_corrupt_and_empty_files_raise`; Task 6 `test_corrupt_file_marked_error_and_run_continues`.

## File Structure
```
CLAUDE.md                        project rules for Claude Code
README.md  MODELS.md  THIRD_PARTY_NOTICES.md  LICENSE
pyproject.toml                   package, scripts, pytest config
.gitignore
src/biblocal/
  __init__.py                    __version__ = "0.1.0"
  models.py                      TextHit, Candidate, PhotoResult, Settings
  startlist.py                   Runner, StartList, normalize_bib, load_start_list
  bibs.py                        extract_candidates, decide, near_matches, demote_frequent
  loader.py                      LoadedImage, LoadError, load_for_ocr
  ocr.py                         OcrEngine
  pipeline.py                    list_photos, scan_folder
  csv_io.py                      write_results_csv, read_results_csv, read_bib_table
  evaluate.py                    EvalReport, evaluate
  bench.py                       BenchReport, bench
  exif.py                        find_exiftool, keywords_for, build_args, write_keywords
  review.py                      write_review_page, apply_corrections
  cli.py                         main: scan, apply, eval, bench
  gui.py                         optional tkinter front end
scripts/spike_k1k2.py            throwaway spike (Task 1)
scripts/startlist_from_truth.py  K1 proxy start list (Task 7)
scripts/collect_writeup_facts.py (Task 14)
packaging/                       PyInstaller spec, build script, .bat launchers (Task 13)
tests/                           test_*.py, conftest.py (session-scoped OcrEngine), fixtures/make_bibs.py
docs/                            research.md, notes/, superpowers/specs/, superpowers/plans/
```

## Schedule (IST)
| Day | Tasks | Amit | Hours |
|---|---|---|---|
| Wed 14 Oct, evening | 1 → CHECKPOINT A | 50 photos in `data/k1`, fill `truth.csv`; 20 own 24 MP JPEGs in `data/k2` | 2.5 |
| Thu 15 Oct | 2, 3, 4, 5 (+5b if A said WEAK) | K5: post one question on the dgrin sports forum | 3 |
| Fri 16 Oct | 6, 7 → CHECKPOINT B | K3: free-chatbot test on 20 photos (30 min) | 3 |
| Sat 17 Oct | 8 → CHECKPOINT C, 9, 10 (if B said SLOW), 11, 13 → CHECKPOINT D, release v0.1.0 | Post for first users 19:00–21:00 IST using the template in `docs/research.md` | 7 |
| Sun 18 Oct | Fixes from user feedback; 10 or 12 if ≥ 3 h remain; rebuild; 14 | Demo video, DEV post draft. Code freeze 18:00 | 7 |
| Mon 19 Oct | none | Final read; submit by 10:00 (deadline 12:29) | 1 |

---

### Task 1: Environment, fixtures and OCR spike (CHECKPOINT A)

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `src/biblocal/__init__.py`, `tests/__init__.py`, `tests/fixtures/__init__.py`, `tests/fixtures/make_bibs.py`, `tests/test_smoke_ocr.py`, `scripts/spike_k1k2.py`, `docs/notes/rapidocr-api.md`, `docs/notes/spike-k1k2.md`

**Interfaces:**
- Produces:
  - `make_bib_image(path: Path, number: str, *, size: tuple[int, int] = (1600, 1067), bib_width: int = 300, angle: float = 0.0, distractor: str | None = None, exif_orientation: int | None = None, seed: int = 0) -> Path`. `size` is the upright display size. With `exif_orientation`, the stored pixels are transformed so that applying the orientation shows the upright image.
  - `make_bib_folder(folder: Path, numbers: list[str], **kwargs) -> Path`: writes `bib_<i>.jpg` per number plus `truth.csv` (`file,bibs`).
  - `docs/notes/rapidocr-api.md`: verified API facts that Tasks 5 and 5b rely on.

- [ ] **Step 1: Check prerequisites.** `py -3.13 --version` → `Python 3.13.x`. `PIP_CACHE_DIR` is `D:\.cache\pip` (Git Bash: `echo $PIP_CACHE_DIR`; PowerShell: `$env:PIP_CACHE_DIR`). `D:/tools/exiftool/exiftool.exe -ver` → a version number. `BIBLOCAL_EXIFTOOL` is `D:\tools\exiftool\exiftool.exe`. If any check fails, stop and tell Amit which one.
- [ ] **Step 2: Create the venv and install.**
  - `py -3.13 -m venv .venv`
  - `.venv/Scripts/python.exe -m pip install --upgrade pip`
  - `.venv/Scripts/python.exe -m pip install rapidocr==3.10.0 onnxruntime "pillow>=10.1" pytest`
  - `pyproject.toml`: name `biblocal`, version `0.1.0`, `requires-python = ">=3.12"`, src layout. Dependencies: the exact installed versions of `rapidocr` and `onnxruntime`, plus `pillow>=10.1`. `[project.optional-dependencies] dev = ["pytest"]`. `[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `markers = ["exiftool: needs exiftool on disk"]`, `addopts = "--basetemp=.pytest_tmp"` (keeps pytest temp files off C:).
  - Then `.venv/Scripts/python.exe -m pip install -e ".[dev]"`.
  - `.gitignore`: `.venv/`, `data/`, `*_biblocal/`, `dist/`, `build/`, `__pycache__/`, `.pytest_cache/`, `.pytest_tmp/`, `*_original` (exiftool backups of any extension).
- [ ] **Step 3: Confirm CPU only.** Run `.venv/Scripts/python.exe -c "import onnxruntime as o; print(o.__version__, o.get_device(), o.get_available_providers())"`. Expected: device `CPU`; providers include `CPUExecutionProvider` and none of `CUDAExecutionProvider`, `DmlExecutionProvider` or `TensorrtExecutionProvider`.
- [ ] **Step 4: Write `docs/notes/rapidocr-api.md` from the installed package source, not from memory.** Record:
  - the exact import, the call signature and keyword arguments (`use_det`, `use_cls`, `use_rec`, score thresholds), and whether each exists;
  - the result attributes (boxes, texts, scores, timing) with types and shapes, and what is returned when nothing is found;
  - the accepted input types (path, PIL image, ndarray) and the colour order for ndarrays;
  - the parameter keys for detection input size and ONNX Runtime thread counts;
  - `Global.max_side_len` (default 2000; RapidOCR shrinks larger inputs before detection), `Det.limit_type` and `Det.limit_side_len`, and how to override all three;
  - the default model version and language, plus model file paths, sizes and SHA-256;
  - whether any code path downloads models (search for `requests`, `urlopen`, `download`).
  
  Then disable the network, run one recognition, re-enable the network, and record the result.
- [ ] **Step 5: Write the failing smoke test** `tests/test_smoke_ocr.py`:
```python
from rapidocr import RapidOCR
from tests.fixtures.make_bibs import make_bib_image

def test_rapidocr_reads_synthetic_bib_on_cpu(tmp_path):
    img = make_bib_image(tmp_path / "b.jpg", "4721")
    result = RapidOCR()(str(img))
    joined = "".join(result.txts or ()).replace(" ", "")
    assert "4721" in joined
```
  Adjust only the result-access line to match `rapidocr-api.md`.
- [ ] **Step 6: Run** `.venv/Scripts/python.exe -m pytest tests/test_smoke_ocr.py -q`. Expected: FAIL with `ModuleNotFoundError` for `tests.fixtures.make_bibs`.
- [ ] **Step 7: Implement `make_bib_image` and `make_bib_folder`.**
  - Grey, noisy background.
  - A white rounded-rectangle "bib" at a seeded position, with the number in black via `ImageFont.load_default(size=int(bib_width * 0.45))`.
  - Optional: rotation of the bib layer by `angle`; distractor text near the top; EXIF `Orientation` tag.
  - JPEG quality 90; deterministic for a given seed.
- [ ] **Step 8: Run the smoke test.** Expected: PASS.
- [ ] **Step 9: Write `scripts/spike_k1k2.py`** (throwaway; never imported by the package).
  - `--photos DIR --make-truth-template` writes `DIR/truth.csv` with one row per JPEG and an empty `bibs` column, then exits.
  - `--photos DIR [--truth FILE] [--max-side 2048] [--limit 100] [--csv OUT]`. Without `--truth` only K2 is reported (`K1=n/a`). For each JPEG, sorted:
    1. Open with Pillow and call `draft("RGB", target)`, where `target` is the stored size scaled so its long side equals max side (keep the aspect ratio; a square target defeats draft mode on landscape photos).
    2. Apply `ImageOps.exif_transpose`, then resize so the long side is ≤ max side.
    3. Run RapidOCR with `Global.max_side_len`, `Det.limit_type: max` and `Det.limit_side_len` set to max side. Split texts with score ≥ 0.5 on whitespace, skip tokens that contain `:` or `.` or end in `K`/`KM`, and take digit runs (`\d{1,5}`).
    4. Time load + OCR per photo.
  - Proxy start lists: `truth` = union of all bibs in truth; `dense` = every number from 1 to the highest truth bib. Tags = digit runs that are in the proxy list and have score ≥ 0.80.
  - Print exactly:
    - one line per proxy list (one line with `list=none` without `--truth`): `list=<truth|dense|none> photos=<n> readable=<n> hit_rate=<x.xx> wrong_rate=<x.xx> effective_s=<x.xx> median_s=<x.xx> p90_s=<x.xx> max_side=<n>`
    - `VERDICT K1=<PASS|WEAK|KILL|n/a> K2=<PASS|SLOW|KILL>`, using the Global Constraints thresholds, the `truth` list for K1, and effective_s (total load + OCR time ÷ photos) for K2.
  - Per-photo CSV: `file,truth,read,tags,seconds`.
- [ ] **Step 10: Get the photos.** Ask Amit to put 50 race JPEGs in `data/k1/`. Run the template command; Amit fills `bibs` (about 15 minutes). If the photos come from a dataset that ships labels, convert the labels into `truth.csv` instead.
  - RBNR (`data/rbnr/datasets/set*_org/`): copy the images into `data/k1/` and build `truth.csv` from each set's `list.txt`. Its rows are whitespace-separated `Image RBN` pairs, one row per bib (join an image's bibs with `;`); skip the header and the `Total …` footer lines. No `.mat` reader is needed.
  - Also ask Amit for at least 20 of his own 24 MP JPEGs in `data/k2/` for K2 (no truth needed).
- [ ] **Step 11: Run the spike** at max side 2048: on `data/k1` with `--truth` for K1, and on `data/k2` without truth for K2. If K1 is KILL, re-run once at 3072; if K2 is KILL, re-run once at 1536.
  - Write `docs/notes/spike-k1k2.md` with the CPU name, the settings, every summary line, and the five worst misses (file, truth, what OCR read).
- [ ] **Step 12: Commit:** `task 1: env, fixtures, OCR spike`.
- [ ] **CHECKPOINT A — stop for Amit.**
  - GO if K1 is PASS or WEAK and K2 is PASS or SLOW.
  - WEAK adds Task 5b; SLOW makes Task 10 required.
  - Any KILL that remains after its retry: stop the project and report.

---

### Task 2: Types and start list

**Files:**
- Create: `src/biblocal/models.py`, `src/biblocal/startlist.py`
- Test: `tests/test_startlist.py`

**Interfaces:**
- Produces (`models.py`):
```python
Box = tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]

@dataclass(frozen=True)
class TextHit: text: str; score: float; box: Box

@dataclass(frozen=True)
class Candidate: number: str; score: float; box: Box; mapped: bool = False

@dataclass
class PhotoResult:
    file: str                      # relative to the photo folder, forward slashes
    status: str                    # "tagged" | "review" | "none" | "error"
    bibs: list[str] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    ms: int = 0

@dataclass(frozen=True)
class Settings:
    accept: float = 0.80; review: float = 0.50; min_len: int = 1; max_len: int = 5
    max_side: int = 2048; frequent_share: float = 0.25; frequent_min_photos: int = 20
```
- Produces (`startlist.py`):
  - `Runner(bib: str, name: str = "", category: str = "")`, a frozen dataclass.
  - `normalize_bib(number: str) -> str`: strips leading zeros; `"000"` → `"0"`.
  - `StartList(runners: list[Runner])` with `lookup(number) -> Runner | None`, `__contains__`, `__len__`, `min_len` and `max_len` (over normalized bibs) and `bibs` (original spellings, sorted). Raises `ValueError("duplicate bib …")` on duplicate normalized bibs.
  - `load_start_list(path: Path) -> StartList`.
    - Header required, with a `bib` or `number` column (case-insensitive, trimmed); optional `name` and `category`; other columns ignored.
    - Delimiter sniffed among `,`, `;` and tab; UTF-8 with or without BOM; blank rows skipped.
    - A non-digit bib raises `ValueError` naming the row; the header is row 1.

- [ ] **Step 1: Write the failing tests**:
```python
def test_semicolon_bom_leading_zeros(tmp_path):
    p = tmp_path / "sl.csv"
    p.write_bytes("\ufeffBib;Name\n007;Ana Silva\n247;Jo Lee\n\n".encode("utf-8"))
    sl = load_start_list(p)
    assert len(sl) == 2
    assert sl.lookup("7") == Runner("007", "Ana Silva")
    assert sl.lookup("247").name == "Jo Lee"
    assert sl.lookup("999") is None
    assert (sl.min_len, sl.max_len) == (1, 3)

def test_number_header_tab_delimiter_extra_columns(tmp_path):
    p = tmp_path / "sl.tsv"
    p.write_text("number\tname\tclub\n12\tAna\tRC\n", encoding="utf-8")
    assert load_start_list(p).lookup("12").name == "Ana"

def test_non_digit_bib_names_row(tmp_path):
    p = tmp_path / "sl.csv"; p.write_text("bib\n12\nA7\n", encoding="utf-8")
    with pytest.raises(ValueError, match="row 3"):
        load_start_list(p)

def test_duplicate_after_normalization(tmp_path):
    p = tmp_path / "sl.csv"; p.write_text("bib\n007\n7\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_start_list(p)

def test_missing_bib_column(tmp_path):
    p = tmp_path / "sl.csv"; p.write_text("name\nAna\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bib"):
        load_start_list(p)
```
- [ ] **Step 2: Run** `.venv/Scripts/python.exe -m pytest tests/test_startlist.py -q`. Expected: FAIL (import error).
- [ ] **Step 3: Implement** `models.py` and `startlist.py` with the signatures above. Use `csv.Sniffer` restricted to `,;\t`, falling back to comma when sniffing fails (single-column files).
- [ ] **Step 4: Run the tests.** Expected: PASS.
- [ ] **Step 5: Commit:** `task 2: types and start list`.

---

### Task 3: Bib rules

**Files:**
- Create: `src/biblocal/bibs.py`
- Test: `tests/test_bibs.py`

**Interfaces:**
- Consumes: `TextHit`, `Candidate`, `PhotoResult`, `Settings` (Task 2); `StartList`, `Runner`, `normalize_bib` (Task 2).
- Produces:
  - `extract_candidates(hits: list[TextHit], settings: Settings, start_list: StartList | None = None, *, image_height: int | None = None) -> list[Candidate]`: candidates sorted by score, descending. When a start list is given, length limits come from it. Task 7 requires positive loaded-image height when the calibrated minimum share is enabled (default 0.04 after CHECKPOINT B).
  - `decide(file: str, candidates: list[Candidate], start_list: StartList | None, settings: Settings, ms: int = 0) -> PhotoResult`
  - `near_matches(number: str, start_list: StartList, limit: int = 3) -> list[str]`: bibs at edit distance 1 (substitution, insertion, deletion) on normalized values; same-length matches first, then the rest; each group sorted by string.
  - `demote_frequent(results: list[PhotoResult], start_list: StartList | None, settings: Settings) -> list[PhotoResult]`: returns new objects and leaves the input unchanged.
- Rules: spec section 7, items 1–7, with the exact values given there.

- [ ] **Step 1: Write the failing tests**:
```python
S = Settings()
BOX = ((0, 0), (10, 0), (10, 10), (0, 10))
def hit(text, score=0.95): return TextHit(text, score, BOX)

def test_digit_runs_within_length():
    assert [c.number for c in extract_candidates([hit("BIB 247"), hit("123456")], S)] == ["247"]

def test_clock_and_distance_tokens_skipped():
    hits = [hit("1:23:45"), hit("10K"), hit("5km"), hit("42.195"), hit("247")]
    assert [c.number for c in extract_candidates(hits, S)] == ["247"]

def test_mapping_only_in_mostly_digit_tokens():
    c = extract_candidates([hit("2O7"), hit("STOP")], S)
    assert [(x.number, x.mapped) for x in c] == [("207", True)]
    assert c[0].score == pytest.approx(0.855)

def test_duplicate_number_keeps_best_score():
    c = extract_candidates([hit("88", 0.6), hit("88", 0.9)], S)
    assert [(x.number, x.score) for x in c] == [("88", 0.9)]

def test_tagged_uses_start_list_spelling_and_name():
    sl = StartList([Runner("007", "Ana")])
    r = decide("a.jpg", extract_candidates([hit("7", 0.9)], S, sl), sl, S)
    assert (r.status, r.bibs, r.names) == ("tagged", ["007"], ["Ana"])

def test_not_in_list_goes_to_review_with_suggestion():
    sl = StartList([Runner("247")])
    r = decide("a.jpg", extract_candidates([hit("217", 0.92)], S, sl), sl, S)
    assert (r.status, r.suggestions) == ("review", ["247"])
    assert "not_in_start_list" in r.reasons

def test_review_band_and_none():
    r = decide("a.jpg", extract_candidates([hit("247", 0.6)], S), None, S)
    assert (r.status, r.reasons) == ("review", ["low_confidence"])
    assert decide("a.jpg", extract_candidates([hit("247", 0.3)], S), None, S).status == "none"

def test_near_matches_order_and_limit():
    sl = StartList([Runner(b) for b in ["247", "2170", "17", "999", "218"]])
    assert near_matches("217", sl) == ["218", "247", "17"]

def test_frequent_number_demoted():
    rs = [decide(f"{i}.jpg", extract_candidates([hit("2026")], S), None, S) for i in range(20)]
    rs.append(decide("x.jpg", extract_candidates([hit("88")], S), None, S))
    out = demote_frequent(rs, None, S)
    assert all(r.status == "review" and "frequent_number" in r.reasons for r in out[:20])
    assert out[20].bibs == ["88"] and rs[0].status == "tagged"

def test_frequent_filter_skips_start_list_members():
    sl = StartList([Runner("2026")])
    rs = [decide(f"{i}.jpg", extract_candidates([hit("2026")], S, sl), sl, S) for i in range(20)]
    assert all(r.status == "tagged" for r in demote_frequent(rs, sl, S))
```
- [ ] **Step 2: Run** `.venv/Scripts/python.exe -m pytest tests/test_bibs.py -q`. Expected: FAIL (import error).
- [ ] **Step 3: Implement** `bibs.py` with the signatures above. Split each `TextHit.text` on whitespace into tokens; skip tokens that contain `:` or `.` or end in `K`/`KM` (any case). Mapping applies to a token when at least half its characters are digits; mapped score = score × 0.9. Digit runs come from `re.findall(r"\d+", token)` after mapping.
- [ ] **Step 4: Run the tests.** Expected: PASS.
- [ ] **Step 5: Commit:** `task 3: bib rules`.

---

### Task 4: Loader

**Files:**
- Create: `src/biblocal/loader.py`
- Test: `tests/test_loader.py`

**Interfaces:**
- Produces:
  - `LoadedImage(image: PIL.Image.Image, scale: float, original_size: tuple[int, int])`, a frozen dataclass. `image` is RGB and upright, with long side ≤ max side and no upscaling. `scale` = loaded long side ÷ original long side. `original_size` is the upright full-resolution `(w, h)`.
  - `LoadError(Exception)`, raised with `(path, reason)`.
  - `load_for_ocr(path: Path, max_side: int) -> LoadedImage`
- Approach:
  1. `Image.open`; record the full size.
  2. For JPEG, call `draft("RGB", target)` before loading, where `target` is the stored size scaled so its long side equals `max_side` (same aspect ratio, never a square box).
  3. Apply `ImageOps.exif_transpose`, then `thumbnail((max_side, max_side), LANCZOS)`.
  4. Swap `original_size` for EXIF orientations 5–8.
  5. Wrap any decode failure in `LoadError`.

- [ ] **Step 1: Write the failing tests**:
```python
def test_downscales_long_side(tmp_path):
    p = make_bib_image(tmp_path / "a.jpg", "12", size=(4000, 3000))
    li = load_for_ocr(p, 2048)
    assert li.image.size == (2048, 1536)
    assert li.scale == pytest.approx(0.512)
    assert li.original_size == (4000, 3000)

def test_exif_orientation_applied(tmp_path):
    p = make_bib_image(tmp_path / "r.jpg", "12", size=(1600, 1067), exif_orientation=6)
    assert Image.open(p).size == (1067, 1600)                    # stored rotated
    assert load_for_ocr(p, 2048).image.size == (1600, 1067)      # loaded upright

def test_small_image_not_upscaled(tmp_path):
    li = load_for_ocr(make_bib_image(tmp_path / "s.jpg", "12", size=(800, 600)), 2048)
    assert (li.image.size, li.scale) == ((800, 600), 1.0)

def test_corrupt_and_empty_files_raise(tmp_path):
    bad = tmp_path / "bad.jpg"; bad.write_bytes(b"not a jpeg")
    empty = tmp_path / "empty.jpg"; empty.write_bytes(b"")
    for p in (bad, empty):
        with pytest.raises(LoadError):
            load_for_ocr(p, 2048)
```
- [ ] **Step 2: Run** `.venv/Scripts/python.exe -m pytest tests/test_loader.py -q`. Expected: FAIL (import error).
- [ ] **Step 3: Implement** `loader.py` as described.
- [ ] **Step 4: Run the tests.** Expected: PASS.
- [ ] **Step 5: Commit:** `task 4: loader`.

---

### Task 5: OCR engine (CPU only)

**Files:**
- Create: `src/biblocal/ocr.py`, `tests/conftest.py` (session-scoped `engine` fixture)
- Test: `tests/test_ocr.py`

**Interfaces:**
- Consumes: `LoadedImage` (Task 4), `TextHit` (Task 2), `docs/notes/rapidocr-api.md` (Task 1).
- Produces:
```python
class OcrEngine:
    def __init__(self, max_side: int = 2048, threads: int | None = None) -> None
    def read(self, image: PIL.Image.Image) -> list[TextHit]   # boxes in the given image's pixel coordinates
    @property
    def info(self) -> dict  # {"rapidocr": str, "onnxruntime": str, "device": "CPU",
                            #  "models": [{"file": str, "bytes": int, "sha256": str}], "params": dict}
```
- Construction raises `RuntimeError("GPU build of onnxruntime detected; install the CPU package")` when `onnxruntime.get_device() != "CPU"`.
- Angle classifier off. `Global.max_side_len`, `Det.limit_type: max` and `Det.limit_side_len` are set to `max_side` (RapidOCR otherwise shrinks inputs above 2000 px); `info["params"]` records them under these dotted names. `threads` is passed through when given. Use the parameter names recorded in `rapidocr-api.md`.

- [ ] **Step 1: Write the failing tests**:
```python
def test_reads_synthetic_number(tmp_path, engine):
    p = make_bib_image(tmp_path / "a.jpg", "4721")
    hits = engine.read(load_for_ocr(p, 2048).image)
    assert any("4721" in h.text.replace(" ", "") for h in hits)

def test_boxes_inside_image(tmp_path, engine):
    li = load_for_ocr(make_bib_image(tmp_path / "a.jpg", "88"), 2048)
    w, h = li.image.size
    assert all(0 <= x <= w and 0 <= y <= h for hit in engine.read(li.image) for (x, y) in hit.box)

def test_blank_image_returns_no_hits(engine):
    assert engine.read(Image.new("RGB", (800, 600), "white")) == []

def test_refuses_gpu_build(monkeypatch):
    import onnxruntime
    monkeypatch.setattr(onnxruntime, "get_device", lambda: "GPU")
    with pytest.raises(RuntimeError, match="CPU"):
        OcrEngine()

def test_info_lists_models_with_sha256(engine):
    info = engine.info
    assert info["device"] == "CPU" and info["models"]
    assert all(len(m["sha256"]) == 64 for m in info["models"])

def test_params_follow_max_side():
    assert OcrEngine(max_side=3072).info["params"]["Global.max_side_len"] == 3072
```
- [ ] **Step 2: Run** `.venv/Scripts/python.exe -m pytest tests/test_ocr.py -q`. Expected: FAIL (import error).
- [ ] **Step 3: Implement** `OcrEngine` and the `engine` fixture (`@pytest.fixture(scope="session")`).
- [ ] **Step 4: Run all tests.** Expected: PASS.
- [ ] **Step 5: Commit:** `task 5: CPU OCR engine`.

### Task 5b (only if CHECKPOINT A or B says WEAK): small-bib fallback

**Files:** Modify `src/biblocal/ocr.py` and `src/biblocal/pipeline.py` (if Task 6 is done). Test: `tests/test_ocr_smallbib.py`.

**Interfaces:**
- Changes the signature to `OcrEngine.read(image, full_res: PIL.Image.Image | None = None, scale: float = 1.0) -> list[TextHit]`. Returned boxes stay in reduced-image coordinates.
- When `full_res` is given, every detected box shorter than 24 px is recognized again on its full-resolution crop (box ÷ scale, padded 15%). The higher-scoring text wins.
- If the misses come from detection itself, implement 2×2 overlapping full-resolution tiles for detection instead. Keep only the variant that `biblocal eval` shows is better on `data/k1`.

- [ ] **Step 1: Failing test.** `test_small_bib_recovered`: `make_bib_image(..., "583", size=(6000, 4000), bib_width=140)`, loaded at max side 1536. The fallback finds `"583"` with score ≥ 0.80.
- [ ] **Step 2:** Run it → FAIL. **Step 3:** Implement. **Step 4:** Run it → PASS. Record the before/after eval numbers in `docs/notes/calibration.md`.
- [ ] **Step 5: Commit:** `task 5b: small-bib fallback`.

---

### Task 6: Pipeline, results CSV and the `scan` command

**Files:**
- Create: `src/biblocal/pipeline.py`, `src/biblocal/csv_io.py`, `src/biblocal/cli.py`
- Modify: `pyproject.toml` (`[project.scripts] biblocal = "biblocal.cli:main"`)
- Test: `tests/test_pipeline.py`, `tests/test_cli_scan.py`

**Interfaces:**
- Consumes: Tasks 2–5.
- Produces:
```python
# pipeline.py
def list_photos(folder: Path) -> tuple[list[Path], int]   # (sorted JPEGs, count of skipped files); recursive; skips dirs ending "_biblocal"
def scan_folder(folder: Path, start_list: StartList | None, settings: Settings, engine: OcrEngine,
                on_progress: Callable[[int, int, PhotoResult], None] | None = None) -> list[PhotoResult]
# csv_io.py
def write_results_csv(results: list[PhotoResult], path: Path) -> None
def read_results_csv(path: Path) -> list[PhotoResult]     # candidate boxes are not stored; read back as all zeros
def read_bib_table(path: Path) -> dict[str, list[str]]    # truth.csv and corrections.csv
# cli.py
def main(argv: list[str] | None = None) -> int
```
- `scan_folder`, per photo: `load_for_ocr` → `engine.read` → `extract_candidates` → `decide`. A `LoadError` becomes status `error` with reason `decode_error`. After all photos, `demote_frequent` runs over the whole list.
- CLI: `biblocal scan PHOTOS [--start-list FILE] [--out DIR] [--max-side 2048] [--accept 0.80] [--review 0.50] [--min-len 1] [--max-len 5] [--progress text|json] [--no-review]`.
  - `--write` arrives in Task 8 and the review page in Task 9; until then no review page is written.
  - Writes `results.csv` and `run.json` (fields in spec section 8).
  - Exit codes: 0 when the run finishes (even with per-file errors); 2 for a missing folder or an invalid start list, with a message naming the problem.
- Progress lines with `--progress json`:
  - `{"type":"progress","done":12,"total":300,"file":"a/IMG_1.JPG","status":"tagged"}`
  - last line: `{"type":"summary","tagged":n,"review":n,"none":n,"error":n,"skipped":n,"seconds":x}`

- [ ] **Step 1: Write the failing tests**:
```python
def test_scan_synthetic_folder(tmp_path, engine):
    folder = make_bib_folder(tmp_path / "ev", ["247", "88", "1093"])
    rs = scan_folder(folder, None, Settings(), engine)
    assert [(r.file, r.status, r.bibs) for r in rs] == [
        ("bib_0.jpg", "tagged", ["247"]), ("bib_1.jpg", "tagged", ["88"]), ("bib_2.jpg", "tagged", ["1093"])]

def test_list_photos_filters_and_counts(tmp_path):
    # files: a.JPG, b.jpeg, c.CR3, Thumbs.db, sub/d.jpg, x_biblocal/e.jpg
    photos, skipped = list_photos(tmp_path)
    assert [p.relative_to(tmp_path).as_posix() for p in photos] == ["a.JPG", "b.jpeg", "sub/d.jpg"]
    assert skipped == 2

def test_corrupt_file_marked_error_and_run_continues(tmp_path, engine): ...
    # one valid bib image + one b"not a jpeg" file → statuses ["tagged", "error"], reasons of the error == ["decode_error"]

def test_paths_with_spaces_and_non_ascii(tmp_path, engine): ...
    # folder "Lauf 2026", file "Zieleinlauf ü 01.jpg" with bib "512" → file == "Zieleinlauf ü 01.jpg", bibs == ["512"]

def test_results_csv_round_trip(tmp_path): ...
    # status, bibs, scores (2 decimals), names, suggestions and reasons survive write → read

def test_cli_scan_outputs_and_photos_untouched(tmp_path): ...
    # SHA-256 of every photo is unchanged; results.csv and run.json exist in "<folder>_biblocal";
    # run.json has "models", "onnxruntime" and "timing" -> "median_ms"

def test_cli_bad_start_list_exit_2(tmp_path): ...

def test_progress_json_lines(tmp_path, capsys): ...
    # every stdout line parses as JSON; the last one has type "summary"
```
- [ ] **Step 2: Run** `.venv/Scripts/python.exe -m pytest tests/test_pipeline.py tests/test_cli_scan.py -q`. Expected: FAIL (import error).
- [ ] **Step 3: Implement** `pipeline.py`, `csv_io.py` and `cli.py` (argparse subcommands) with the signatures above.
- [ ] **Step 4: Run all tests.** Expected: PASS. Then try `biblocal scan data/k1` by hand and open `results.csv`.
- [ ] **Step 5: Commit:** `task 6: pipeline, results CSV, scan command`.

---

### Task 7: `eval` and `bench` (CHECKPOINT B)

**Files:**
- Create: `src/biblocal/evaluate.py`, `src/biblocal/bench.py`, `scripts/startlist_from_truth.py`, `docs/notes/calibration.md`, `docs/notes/bench.md`
- Modify: `src/biblocal/cli.py`
- Test: `tests/test_evaluate.py`

**Interfaces:**
```python
@dataclass
class EvalReport:
    photos: int; readable: int; hit_rate: float; wrong_rate: float; review_rate: float; none_rate: float
    misses: list[str]; wrong: list[tuple[str, str]]
def evaluate(results: list[PhotoResult], truth: dict[str, list[str]]) -> EvalReport

@dataclass
class BenchReport:
    photos: int; workers: int; median_ms: float; p90_ms: float
    effective_s_per_photo: float; minutes_per_1000: float; cpu: str; settings: dict
def bench(folder: Path, settings: Settings, limit: int = 100) -> BenchReport   # workers = 1 until Task 10
```
- Hit: a photo with at least one truth bib where some tagged bib equals a truth bib after `normalize_bib`.
- `wrong_rate` = tags not in that photo's truth ÷ all tags (0 when there are no tags). Photos missing from truth are ignored and counted in a warning.
- CLI:
  - `biblocal eval RESULTS_CSV --truth TRUTH_CSV` prints `photos=… readable=… hit_rate=… wrong_rate=… review_rate=…` and `VERDICT K1=PASS|WEAK|KILL`.
  - `biblocal bench PHOTOS [--limit 100]` prints the report, writes `bench.json` to the output folder, and prints `VERDICT K2=PASS|SLOW|KILL` from `effective_s_per_photo`.
- `scripts/startlist_from_truth.py TRUTH_CSV OUT_CSV [--dense]` writes a start list containing every bib in truth (the K1 proxy), or with `--dense` every number from 1 to the highest truth bib.

- [x] **Step 1: Write the failing tests**:
```python
def test_eval_exact_metrics():
    truth = {"a.jpg": ["247"], "b.jpg": ["12"], "c.jpg": []}
    rs = [PhotoResult("a.jpg", "tagged", ["247"]), PhotoResult("b.jpg", "tagged", ["13"]), PhotoResult("c.jpg", "none")]
    rep = evaluate(rs, truth)
    assert (rep.readable, rep.hit_rate, rep.wrong_rate) == (2, 0.5, 0.5)
    assert rep.misses == ["b.jpg"] and rep.wrong == [("b.jpg", "13")]

def test_eval_matches_leading_zeros():
    rep = evaluate([PhotoResult("a.jpg", "tagged", ["7"])], {"a.jpg": ["007"]})
    assert (rep.hit_rate, rep.wrong_rate) == (1.0, 0.0)
```
- [x] **Step 2:** Run → FAIL. **Step 3:** Implement. **Step 4:** Run → PASS.
- [x] **Step 5: Calibrate on `data/k1`** with the proxy start list.
  - Run scan + eval for accept ∈ {0.70, 0.80, 0.90}, with both the truth and the dense proxy lists, and put the table in `docs/notes/calibration.md`.
  - Pick the lowest accept with wrong < 0.03 on both lists. Change the `Settings` default only if that value differs from 0.80, and say so.
- [x] **Step 6: Bench:** `biblocal bench data/k2 --limit 50`. Put the numbers in `docs/notes/bench.md`.
- [x] **Step 7: Commit:** `task 7: eval, bench, calibration`.
- [ ] **CHECKPOINT B — stop for Amit.** Report K1 (truth and dense lists) and K2 from the real pipeline, the calibration choice, and whether Task 5b or Task 10 is now required.

---

### Task 8: exiftool keyword writer and `--write` (CHECKPOINT C)

**17 Oct status:** implementation complete; 101 tests passed, including actual
ExifTool integration tests (none skipped). Test-first regressions cover legacy
IPTC conversion, duplicate prevention, overlength-text refusal, concurrent
source edits, backups, unchanged pixels, Unicode paths and sidecar preservation.
Ten K4 copies are prepared: eight written, two skipped, no failures; all 100 K1
original hashes and all ten K4 decoded-pixel hashes are unchanged. Human
validation **PASS in digiKam 9.1.0**, reported 18 Oct; see `docs/notes/k4.md`.

**Files:**
- Create: `src/biblocal/exif.py`, `docs/notes/k4.md`
- Modify: `src/biblocal/cli.py`
- Test: `tests/test_exif.py`

**Interfaces:**
```python
def find_exiftool(cli_value: str | None = None) -> Path | None
def keywords_for(result: PhotoResult, template: str = "{bib}", with_names: bool = False) -> tuple[list[str], list[str]]  # (flat, hierarchical)
def build_args(photo: Path, flat: list[str], hier: list[str], mode: str, backup: bool) -> list[str]  # one file's block, ends with "-execute"
@dataclass
class WriteReport: written: int; skipped: int; failed: list[tuple[str, str]]
def write_keywords(photo_root: Path, results: list[PhotoResult], mode: str, exiftool: Path,
                   backup: bool = True, batch_size: int = 500) -> WriteReport
```
- Only `tagged` results are written. `mode` is `"embed"` or `"sidecar"`, following spec section 9.
- One exiftool process per batch, driven by an argument file: one argument per line, no quotes. exiftool's per-file output fills `failed`.
- Global filename/text charset options go on the command line after `-common_args` (`exiftool -@ ARGFILE -common_args …`), not in the argument file: options do not carry past `-execute`, and `-common_args` does not work inside an argument file (tested with exiftool 13.59). Embed recodes IPTC in a separate first command, setting `CodedCharacterSet=UTF8` there only; a guarded second command updates keywords. Embeds run on temporary copies and publish only after clean results, preserving originals on truncation warnings. See `docs/notes/exiftool-api.md` for the verified protocol and regression evidence.
- CLI flags on `scan` (and on `apply` in Task 9): `--write none|sidecar|embed` (default none), `--no-backup`, `--exiftool PATH`, `--keyword-template "{bib}"`, `--with-names`. With `--write` other than none and no exiftool found: exit 2 with an install hint.

- [x] **Step 1: Write the failing pure tests**:
```python
def test_keywords_default():
    assert keywords_for(PhotoResult("a.jpg", "tagged", ["247"])) == (["247"], ["Bib|247"])

def test_keywords_with_names():
    r = PhotoResult("a.jpg", "tagged", ["247"], names=["Jo Lee"])
    assert keywords_for(r, with_names=True) == (["247", "Jo Lee"], ["Bib|247"])

def test_build_args_dedupes_and_ends_with_execute(tmp_path):
    a = build_args(tmp_path / "a.jpg", ["247"], ["Bib|247"], "embed", backup=True)
    assert a.index("-XMP-dc:Subject-=247") < a.index("-XMP-dc:Subject+=247")
    assert "-IPTC:Keywords+=247" in a and "-overwrite_original" not in a and a[-1] == "-execute"
```
- [x] **Step 2: Write the failing integration tests.** Mark them `@pytest.mark.exiftool`; skip them when `find_exiftool()` is None.
  - `test_embed_twice_no_duplicates`: write twice; `exiftool -j -XMP-dc:Subject -IPTC:Keywords` lists `247` exactly once in each tag.
  - `test_embed_keeps_existing_keyword`: keyword `finish` set first → both keywords present afterwards.
  - `test_embed_backup_default_and_no_backup`: `<name>.jpg_original` exists by default and is absent with `backup=False`.
  - `test_embed_pixels_unchanged`: decoded pixels before == after.
  - `test_sidecar_create_and_preserve`: an existing `<stem>.xmp` with `XMP:Rating=3` keeps Rating 3 and gains Subject `247`; a photo without a sidecar gets a new one.
  - `test_non_ascii_path_written`: folder `Lauf 2026`, files `ü 01.jpg` and `ü 02.jpg` written in one batch; both get the keyword.
- [x] **Step 3:** Run → FAIL. **Step 4:** Implement. **Step 5:** Run all tests → PASS. Integration tests must run, not skip, on Amit's machine (`BIBLOCAL_EXIFTOOL` is set).
- [x] **Step 6: Commit:** `task 8: exiftool writer and --write`.
- [x] **CHECKPOINT C — K4, Amit, about 20 minutes.** PASS reported 18 Oct, digiKam 9.1.0.
  1. Copy 10 photos from `data/k1` to `data/k4`.
  2. Run `biblocal scan data/k4 --start-list <list> --write embed`.
  3. Import `data/k4` into Lightroom Classic (or digiKam) and filter by one tagged bib's keyword. Confirm the right photos appear. For photos already in a catalog, use Metadata > Read Metadata from Files.
  4. Record pass or fail in `docs/notes/k4.md`. A fail blocks Task 13.

---

### Task 9: Review page and `apply`

**18 Oct implementation status:** complete; test-first, 121 tests passed,
including local Edge export/keyboard interactions and real ExifTool apply.
Final review fixes reject output within the source folder and unsupported
CLI review thresholds below the OCR floor of 0.50. Defaults are unchanged.
Amit's five-card acceptance check is pending; the page and exact instructions
are in `docs/notes/task9-review.md`. Continue Task 11 under the received GO.

**Files:**
- Create: `src/biblocal/review.py`
- Modify: `src/biblocal/cli.py`
- Test: `tests/test_review.py`, `tests/test_apply.py`

**Interfaces:**
```python
def write_review_page(results: list[PhotoResult], photo_root: Path, out_dir: Path, settings: Settings,
                      statuses: frozenset[str] = frozenset({"review"})) -> Path   # out_dir / "review.html"
def apply_corrections(results: list[PhotoResult], corrections: dict[str, list[str]],
                      start_list: StartList | None) -> list[PhotoResult]
```
- Page content follows spec section 10.
- Thumbnails:
  - `thumbs/<index>.jpg`, long side 640;
  - `thumbs/<index>_crop.jpg`, the best candidate box padded 50% and scaled to a height of 160.
- Render thumbnails from `load_for_ocr(photo, settings.max_side)` so the boxes line up.
- All text is HTML-escaped. The file never contains `http://` or `https://`.
- `scan` writes the page after the run unless `--no-review` is passed.
- `apply_corrections`:
  - A corrected file becomes `tagged` with the given bibs, using the start-list spelling and names when a list is given. An empty bib list makes it `none`. Either way the reason is `manual`.
  - A non-digit bib, or a file not in results, raises `ValueError` naming the file.
- CLI: `biblocal apply CORRECTIONS_CSV --results RESULTS_CSV [--start-list FILE] [--write none|sidecar|embed] [writer flags]`. It writes `results_final.csv` next to `results.csv` and keywords for corrected files only.

- [x] **Step 1: Write the failing tests**:
```python
def test_page_self_contained_and_lists_review_files(tmp_path, engine): ...
    # review.html exists, has no "http://" or "https://", names each review file, thumbs/ has one image per card

def test_page_escapes_names(tmp_path, engine): ...
    # photo "Tom & Jerry's.jpg" in review → html contains "Tom &amp; Jerry" and not "Jerry's"

def test_apply_manual_tags_and_none():
    rs = [PhotoResult("a.jpg", "review"), PhotoResult("b.jpg", "review")]
    out = apply_corrections(rs, {"a.jpg": ["247"], "b.jpg": []}, None)
    assert [(r.status, r.bibs, r.reasons) for r in out] == [("tagged", ["247"], ["manual"]), ("none", [], ["manual"])]

def test_apply_rejects_bad_bib():
    with pytest.raises(ValueError, match="a.jpg"):
        apply_corrections([PhotoResult("a.jpg", "review")], {"a.jpg": ["2A7"]}, None)
```
- [x] **Step 2:** Run → FAIL. **Step 3:** Implement. **Step 4:** Run all tests → PASS.
- [ ] **Step 5: Manual check (Amit, 5 minutes).** Open `review.html` from a real run, fix 5 cards, download `corrections.csv`, run `apply`, and check `results_final.csv`.
- [x] **Step 6: Commit:** `task 9: review page and apply`.

---

### Task 10: Worker pool (required if CHECKPOINT B says SLOW, otherwise optional)

**Files:**
- Modify: `src/biblocal/pipeline.py`, `src/biblocal/cli.py`, `src/biblocal/bench.py`
- Test: `tests/test_pipeline_parallel.py`

**Interfaces:**
- `scan_folder(..., workers: int = 1)`: `engine` is used only when `workers == 1`.
- CLI `--workers N` on `scan` and `bench`, defaulting to `max(1, (os.cpu_count() or 2) // 2)`.
- `bench(..., workers: int = 1)`.

- Process pool: the initializer builds one `OcrEngine` per worker, with the thread count the bench shows is best.
- Results are sorted by file, and progress is reported from the main process.
- `multiprocessing.freeze_support()` is the first call in `cli.main`.

- [ ] **Step 1: Failing test.** `test_parallel_matches_serial`: statuses and bibs are identical for `workers=1` and `workers=2` on a six-image synthetic folder.
- [ ] **Step 2:** Run → FAIL. **Step 3:** Implement. **Step 4:** Run all tests → PASS.
- [ ] **Step 5: Bench** with workers 1, 2, 4 and the default. Put the before/after table in `docs/notes/bench.md`.
- [ ] **Step 6: Commit:** `task 10: worker pool`.

---

### Task 11: README, MODELS.md, licences

**18 Oct implementation status:** complete under the reduced pip-only scope.
MIT copyright is Amit Sahoo. Task 11 checks: four expected failures first,
then five passing; final full suite 126 passed. Built and tested the installed
wheel with runtime network/download calls blocked. Complete vendor license
texts and model inventory are included in the wheel. ExifTool and PyInstaller
are not redistributed. Verification and remaining human checks are recorded
in `docs/notes/release-check.md`. Stop after this task as requested.

**Files:**
- Create: `README.md`, `MODELS.md`, `THIRD_PARTY_NOTICES.md`, `LICENSE` (MIT; ask Amit for the name on the copyright line)
- Test: `tests/test_docs.py`

- README, in plain language with no marketing:
  - What it does, in two lines.
  - Privacy: it runs offline; check it yourself with Wi-Fi off.
  - Windows quick start: download the zip, unzip it, drag a folder onto `BibLocal-preview.bat` or `BibLocal-tag.bat`, then open `review.html`.
  - Command-line examples for `scan`, `apply`, `eval` and `bench`.
  - Mac and Linux: `pip install git+https://github.com/<user>/biblocal`, plus exiftool installation; labelled untested.
  - Lightroom notes (spec section 9).
  - Accuracy and limits: the real K1 and K2 numbers from `docs/notes/`, and what fails (occluded, angled, muddy bibs).
  - Licences: links to `MODELS.md` and `THIRD_PARTY_NOTICES.md`.
  - "Built with help from Claude Code."
- `MODELS.md`: one row per model file from `OcrEngine().info["models"]`: file, bytes, SHA-256, upstream (the PaddleOCR PP-OCR version recorded in `rapidocr-api.md`), licence Apache-2.0. Link RapidOCR's `MODEL_LICENSES.md`.
- `THIRD_PARTY_NOTICES.md`:
  - Generate it from installed runtime distributions with `importlib.metadata` (name, version, licence field), not from memory.
  - Add what the metadata misses, with licence texts (approved by Amit, 15 Oct 2026): FFmpeg (LGPL-2.1, `cv2/opencv_videoio_ffmpeg*.dll` in opencv-python-headless; see its `LICENSE-3RD-PARTY.txt`), GEOS (LGPL-2.1, `shapely.libs/geos*.dll`; see Shapely's `LICENSE_GEOS`) and tqdm (MPL-2.0 AND MIT).
  - Add exiftool: Phil Harvey; same terms as Perl (Artistic License or GPL); shipped unmodified as a separate program in the Windows zip.
  - Add the PyInstaller bootloader notice.

- [x] **Step 1: Failing test**:
```python
def test_models_md_has_every_model_sha256(engine):
    text = Path("MODELS.md").read_text(encoding="utf-8")
    assert all(m["sha256"] in text for m in engine.info["models"])

def test_readme_has_no_placeholders():
    assert "TODO" not in Path("README.md").read_text(encoding="utf-8")

def test_notices_cover_bundled_copyleft():
    text = Path("THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert all(s in text for s in ("FFmpeg", "GEOS", "LGPL-2.1", "MPL-2.0"))
```
- [x] **Step 2:** Run → FAIL. **Step 3:** Write the documents. **Step 4:** Run → PASS.
- [x] **Step 5: Commit:** `task 11: README, models, notices`.

---

### Task 12: GUI (optional: only after v0.1.0 ships and if ≥ 3 h remain before code freeze)

**Files:**
- Create: `src/biblocal/gui.py`
- Modify: `pyproject.toml` (`[project.gui-scripts] biblocal-gui = "biblocal.gui:main"`)
- Test: `tests/test_gui_progress.py`

**Interfaces:**
- `parse_progress_line(line: str) -> dict | None`: returns None for non-JSON lines and unknown types.
- `main() -> None`.
- The tkinter window has:
  - a photos folder picker and an optional start list picker;
  - write mode radio buttons: "Don't change photos", "Sidecar .xmp", "Embed in JPEG";
  - Run, a progress bar with counts, and buttons to open the output folder and the review page.
- How it runs: it starts `biblocal scan … --progress json` as a subprocess (the CLI exe beside it when frozen; `sys.executable -m biblocal.cli` otherwise). A thread reads stdout line by line, and the UI updates through `after()`.

- [ ] **Step 1: Failing test**:
```python
def test_parse_progress_line():
    assert parse_progress_line('{"type":"progress","done":3,"total":10,"file":"a.jpg","status":"tagged"}')["done"] == 3
    assert parse_progress_line("not json") is None
    assert parse_progress_line('{"type":"other"}') is None
```
- [ ] **Step 2:** Run → FAIL. **Step 3:** Implement. **Step 4:** Run → PASS, then a manual smoke run on a synthetic folder.
- [ ] **Step 5: Commit:** `task 12: GUI`.

---

### Task 13: Windows release build (CHECKPOINT D)

**Files:**
- Create: `packaging/biblocal.spec`, `packaging/build_release.ps1`, `packaging/BibLocal-preview.bat`, `packaging/BibLocal-tag.bat`, `docs/notes/release-check.md`
- Modify: `README.md` (download section)

- Install PyInstaller into the venv only; it is a dev tool, not a runtime dependency.
- One-folder build `dist/BibLocal/` containing:
  - `biblocal.exe` (console), plus `biblocal-gui.exe` if Task 12 shipped;
  - the RapidOCR package data (model files and config);
  - `D:\tools\exiftool\exiftool.exe` and `exiftool_files\`, copied into `dist/BibLocal/exiftool/`;
  - `LICENSE`, `MODELS.md`, `THIRD_PARTY_NOTICES.md` and `README.md`.
- Launchers. Each takes a folder dragged onto it (`%~1`), pauses at the end and opens the output folder:
  - `BibLocal-preview.bat` runs `scan` without `--write`.
  - `BibLocal-tag.bat` runs `scan --write embed`, with backups kept.
- `build_release.ps1` sets `PYINSTALLER_CONFIG_DIR=D:\.cache\pyinstaller` (keeps PyInstaller's cache off C:), runs the tests, builds, zips to `dist/BibLocal-win64-v<version>.zip`, and prints the SHA-256.

- [ ] **Step 1: Build.** Run the script; it must succeed with all tests passing.
- [ ] **Step 2: Automated smoke test.** `dist/BibLocal/biblocal.exe scan <synthetic folder>` exits 0 and writes `results.csv`, without the venv on PATH.
- [ ] **Step 3: Commit:** `task 13: Windows release build`.
- [ ] **CHECKPOINT D — Amit, about 20 minutes.**
  1. Unzip into a fresh `D:\test-release\` and turn on airplane mode.
  2. Drop a copy of a real folder onto `BibLocal-tag.bat`.
  3. Check `results.csv`, `review.html` and the keywords (digiKam or Lightroom), and note the time taken.
  4. Turn networking back on and record everything in `docs/notes/release-check.md`.
  5. Then tag `v0.1.0` and create the GitHub release with the zip and its SHA-256.

---

### Task 14: Demo set and write-up facts

**Files:**
- Create: `scripts/collect_writeup_facts.py`, `docs/notes/writeup-facts.md`, `docs/notes/demo-credits.md`

- Demo folder `data/demo/`: about 300 photos (Amit's own consented photos plus CC BY 4.0 dataset images). Never committed; credits go in `demo-credits.md`.
- The script reads `run.json`, `bench.json`, the eval output and the numbers in `docs/notes/`. It writes a facts table:
  - photos, wall-clock minutes, effective s/photo;
  - hit rate, wrong rate, review rate;
  - model sizes, the Wi-Fi-off result and the K3 chatbot comparison.
- Demo video, 60 seconds:
  1. Wi-Fi off on camera.
  2. A run on 300 photos with a timer on screen.
  3. Filter by keyword in Lightroom or digiKam.
  4. One honest "not sure" in the review page.
  5. Closing line: no uploads, no cost, open model you can swap.
- Amit writes the DEV post himself, discloses AI assistance per DEV's guidelines, and leaves out any sales pitch.

- [ ] **Step 1: Failing test.** `test_collect_facts_reads_run_json(tmp_path)`: the script turns a sample `run.json` and `bench.json` into a table that contains their median_ms and minutes_per_1000 values.
- [ ] **Step 2:** Run → FAIL. **Step 3:** Implement. **Step 4:** Run → PASS. Generate `writeup-facts.md` from the real runs.
- [ ] **Step 5: Commit:** `task 14: write-up facts`.
