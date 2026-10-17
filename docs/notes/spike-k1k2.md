# Task 1 — CHECKPOINT A

Measured 17 Oct 2026. **K1 PASS; K2 SLOW accepted; GO received 17 Oct.**
K1's dense-list result is weak: correct OCR of unrelated numbers produces many
wrong tags. A truth-derived start list is an optimistic proxy, not proof of
accuracy on a real event's full start list.

## Environment and method

- CPU: **13th Gen Intel(R) Core(TM) i7-13650HX**, Windows 11.
- Python 3.13.7, RapidOCR 3.10.0, ONNX Runtime 1.31.0 CPU, Pillow 13.0.0.
- Bundled PP-OCRv6 small detector/recognizer. Classifier off. No GPU selected.
- One worker, sequential processing. ONNX intra/inter-op thread settings left
  at package defaults (-1); this is not a single-thread benchmark.
- Long side 2048; `Global.max_side_len=2048`, `Det.limit_type=max`,
  `Det.limit_side_len=2048`. JPEG draft preserves source aspect ratio before
  EXIF orientation and thumbnail resize. No upscaling during the OCR loader.
- OCR score floor 0.50; tag threshold 0.80; whole digit runs of length 1–5;
  clock/decimal/distance tokens skipped. No letter mapping or frequent-number
  filter in this throwaway spike; the real rules come in Task 3.
- Effective seconds/photo = sum of per-photo load + OCR time / photos.
  Timings include first-photo lazy model/session initialization, exclude Python
  import/startup and output writing. Median and nearest-rank p90 use the same
  samples. No warm-up was removed. Runs were serial with no concurrent OCR job.
- Hit = readable photo with at least one correct accepted bib / readable
  photos; wrong = accepted bibs absent from that photo's truth / accepted bibs.
  Leading zeros are normalized. These are photo hit rate and tag error rate,
  not per-bib recall and not photo-level error rate.

## Private data preparation

`data/rbnr/datasets/set*_org/list.txt` supplies whitespace-separated Image/RBN
pairs. Headers and Total footers are ignored; repeated image rows become
semicolon-separated bibs. `.mat` files were not needed. All 217 source JPEGs
have labels; 290 image/bib pairs, 244 distinct bibs. Source photos remain private.

Run `.venv/Scripts/python.exe scripts/prepare_rbnr.py` only into empty output
directories. It copies a fixed 100-photo sample into `data/k1`: 34 from set1,
33 from set2, 33 from set3. For each sorted set of N photos and quota Q, select
indices `i*(N-1)//(Q-1)` for `i=0..Q-1`. This gives 143 truth annotations and
135 distinct bibs; dense list = 1 through 90135. The generated `truth.csv` and
`preparation.json` stay in ignored `data/k1/`.

Every selected photo contains an annotated bib. No negative/no-bib real photos
were available. Maximum native source size is 850×1263 (1.07355 MP), with no
source long side above 1263. RBNR is a low-resolution K1 proxy. Increasing the
resize ceiling alone would not add source detail.

**K2 uses upscaled RBNR, not camera originals.** Amit explicitly authorized
this substitute on 17 Oct because he has no 24 MP JPEGs. The first 20 sorted
K1 photos are resized to exactly 6000×4000 using Pillow LANCZOS and saved as
JPEG quality 92 in ignored `data/k2`. This changes aspect ratio for portrait
sources; it follows the requested timing construction. These files are never
used for K1. They measure a synthetic 24 MP decode/OCR workload, not real
24 MP race-photo performance. The original-image comparison uses the same
20 filenames. Hashes of all 100 RBNR sources and byte-identical K1 copies were
verified unchanged after both runs.

## Results

| Run | Photos | Effective s/photo | Median s | p90 s | Verdict |
|---|---:|---:|---:|---:|---|
| Native K1, all 100 | 100 | 0.989500 | 0.887291 | 1.449589 | K1 PASS; native-image timing PASS |
| K2 upscaled RBNR 6000×4000 | 20 | 2.066084 | 1.975725 | 2.403191 | K2 SLOW |
| Matching 20 native RBNR originals | 20 | 0.696063 | 0.716201 | 1.064457 | Comparison PASS |

| K1 start list | Readable | Hit photos | Accepted bibs | Wrong bibs | Exact wrong rate | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Truth-bib union | 100 | 88 (88%) | 125 | 1 | 0.8% | PASS (checkpoint decision) |
| Dense 1–90135 | 100 | 88 (88%) | 171 | 47 | 27.485380% | WEAK |

Measured upscaled K2 extrapolation: **34.43 minutes per 1,000 photos** for
load + OCR, excluding startup imports and outputs. This is an extrapolation
from 20 synthetic-size images on this laptop's CPU, not a 1,000-photo run.

Exact printed summary lines (display rounded to two decimals):

```text
list=truth photos=100 readable=100 hit_rate=0.88 wrong_rate=0.01 effective_s=0.99 median_s=0.89 p90_s=1.45 max_side=2048
list=dense photos=100 readable=100 hit_rate=0.88 wrong_rate=0.27 effective_s=0.99 median_s=0.89 p90_s=1.45 max_side=2048
VERDICT K1=PASS K2=PASS

list=none photos=20 readable=0 hit_rate=n/a wrong_rate=n/a effective_s=2.07 median_s=1.98 p90_s=2.40 max_side=2048
VERDICT K1=n/a K2=SLOW

list=none photos=20 readable=0 hit_rate=n/a wrong_rate=n/a effective_s=0.70 median_s=0.72 p90_s=1.06 max_side=2048
VERDICT K1=n/a K2=PASS
```

The first command's K2 label refers only to native RBNR timing. The checkpoint
K2 decision uses the separately authorized upscaled 20-photo set: **SLOW**.
Neither controlling test was KILL, so no 3072/1536 retry was triggered.

Commands and ignored per-photo evidence:

```powershell
.venv/Scripts/python.exe scripts/spike_k1k2.py --photos data/k1 --truth data/k1/truth.csv --csv data/k1_biblocal/spike-2048.csv
.venv/Scripts/python.exe scripts/spike_k1k2.py --photos data/k2 --limit 20 --csv data/k2_biblocal/spike-2048.csv
.venv/Scripts/python.exe scripts/spike_k1k2.py --photos data/k1 --limit 20 --csv data/k1_biblocal/comparison-original-2048.csv
```

The initial K1 PowerShell command redirected progress on stderr, causing
PowerShell's NativeCommandError wrapper to report exit 1 despite complete
100-photo summaries and CSV. There was no Python traceback; later commands
used the native exit code explicitly. All metrics above were recomputed from
the complete CSV and agree with the printed output.

## Five misses

There are 12 photo misses. All have one truth bib; the following are the first
five by filename (tied by missing-bib count). Full text is retained in the CSV.

| File | Truth | OCR read |
|---|---|---|
| set1_09.JPG | 184 | `Triathi n; SEAT; o emoción; AT; auto emoción; CELLENCE; port.; 34.18; ROD; 84` |
| set1_23.JPG | 898 | `Union` |
| set1_28.JPG | 311 | no text |
| set1_42.JPG | 400 | `IXITA; TI` |
| set1_58.JPG | 814 | no text |

The truth-list wrong tag is `3750` in `set3_01.JPG`; supplied truth is
`4345;4454;3778;4407`. It is counted as wrong against the supplied labels;
the labels were not edited after seeing model output.

## Verification and checkpoint

- Test-first: initial smoke/fixture/spike/conversion collection failed because
  the new modules did not exist. Implemented them; **19 tests passed**.
- Synthetic tests cover CPU OCR, all eight EXIF orientations, repeatability,
  source-preserving conversion, timing-only 24 MP copies, metric denominators,
  exact threshold boundaries and refusing to overwrite truth labels.
- CPU package and actual CPU session providers verified; models use explicit
  local paths. Recognition and both timed workloads passed with Python network
  access blocked. See [rapidocr-api.md](rapidocr-api.md).
- **Airplane-mode check: PASS, reported by Amit on 17 Oct 2026.** In response
  to the airplane-mode result clarification, Amit reported terminal output
  `1 passed in 6.29s`. This is the user-run smoke check, not an agent-observed
  network-adapter state. The agent's separate application-level blocking
  checks also passed.
- certifi MPL-2.0 exception was explicitly approved, unmodified only; rules and
  its notice/full license text were updated. No extra application dependency
  was added. Full remaining notices stay in Task 11.
- Task 5b is not triggered by the controlling K1 verdict. Dense-list wrong tags
  must be reported and assessed in Task 7 calibration. Task 10 remains cut
  despite SLOW; single-worker performance will be reported honestly.
- **CHECKPOINT A GO received 17 Oct.** Continue Tasks 2–7, stopping at B.
  K2 SLOW is accepted; Task 10 stays cut. README must describe the measured
  2.07 s/photo (about 34 minutes/1,000), single worker, synthetic 24 MP set.
  Task 7 adds each RBNR set's min-to-max bib range list alongside truth/dense
  lists. If range wrong rate is at least 3%, use at most one hour for the
  authorized deterministic token/relative-box-height rules, keep the frequent
  filter, and report before/after. No new model.
