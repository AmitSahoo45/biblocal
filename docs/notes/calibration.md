# K1 calibration — 17 Oct 2026

**CHECKPOINT B: truth-list K1 PASS; range and dense lists remain WEAK.**
The authorized deterministic rules improve errors but do not meet the <3%
wrong-tag target on realistic or dense start lists. No new model was added.

## Current selection: 2% after the 18 Oct demo test

Amit authorized a **0.02 minimum height share**, keeping **accept 0.90**,
after reporting better recovery of bibs in 30 friends' race photos. The new
`scan --min-bib-height` option accepts finite shares from 0 through 1; zero
disables the height filter. Other validation and review rules stay unchanged.

The same 100-photo RBNR OCR cache was replayed with fingerprint validation.
No model or photo changed. At accept 0.90:

| Start list | 2% hit | 2% wrong / accepted | 2% wrong rate | 4% hit | 4% wrong / accepted | 4% wrong rate |
|---|---:|---:|---:|---:|---:|---:|
| Truth | 87% | 1/124 | 0.81% | 80% | 0/107 | 0% |
| Range | 87% | 29/152 | 19.08% | 80% | 9/116 | 7.76% |
| Dense | 87% | 37/160 | 23.13% | 80% | 17/124 | 13.71% |

Set2 recovers six photos: **23/33 (69.70%) at 4% to 29/33 (87.88%) at 2%**.
Set3 recovers one; set1 is unchanged. The additional recall costs more false
tags, including one on the optimistic truth list. Range and dense lists still
fail the less-than-3% target. These are in-sample results with no held-out set.
See [the full 2%/4% comparison](height-002-calibration.md) for counts, commands
and verification. Earlier sections below remain historical evidence.

## Previous selection after CHECKPOINT B GO (4%, superseded)

On 17 Oct Amit selected **accept 0.90 and minimum height share 0.04**,
superseding the initial 0.80 / 0.05 selection recorded below. This uses the
existing calibration grid; no new model or rule was added. Task 5b stays
deferred and Task 10 stays cut.

| List | Hit | Wrong / accepted | Wrong rate |
|---|---:|---:|---:|
| Truth (best case) | 80/100 | 0/107 | 0% |
| Range (realistic proxy) | 80/100 | 9/116 | 7.76% |
| Dense | 80/100 | 17/124 | 13.71% |

Compared with 5% / 0.80, this recovers nine hit photos (71% to 80%) and
reduces range wrong rate from 8.33% to 7.76%. Dense wrong increases from 12%
to 13.71%. Truth wrong remains zero. This is an explicit user-selected
tradeoff; the multi-list <3% target is still unmet, not a passing calibration.

| Set | Hit / photos, all lists | Truth wrong / accepted | Range wrong / accepted | Dense wrong / accepted |
|---|---:|---:|---:|---:|
| set1 | 25/34 | 0/27 | 3/30 | 5/32 |
| set2 | 23/33 | 0/28 | 2/30 | 5/33 |
| set3 | 32/33 | 0/52 | 4/56 | 7/59 |

At confidence 0.90, set2 hits fall from 29/33 (87.88%) without the height
filter to **23/33 (69.70%) at 4%**. The small-bib loss remains a known limit.
At the new default, review is 1% and none is 19% for all three lists.
All figures remain in-sample on 100 photos, with no held-out set.

The requested fresh CLI scan/eval confirmed **80% hit, 0% wrong, K1 PASS**:
80 tagged, 1 review, 19 none, 0 errors, 98.279 seconds. Its results match
the saved 0.90 / 0.04 truth-list configuration exactly; all 100 K1 photo
hashes are unchanged. The full test suite passed (78 tests), after observing
the new default-behavior tests fail before the change.

```powershell
.venv/Scripts/biblocal.exe scan data/k1 --start-list data/k1_biblocal/start-truth.csv --out data/k1_biblocal/selected-090-004-live --progress json --no-review
.venv/Scripts/biblocal.exe eval data/k1_biblocal/selected-090-004-live/results.csv --truth data/k1/truth.csv
```

## Data and method

The same fixed 100 native RBNR JPEGs as Task 1: 34 from set1, 33 from set2,
33 from set3, 143 annotated bib/photo pairs, 135 distinct bibs. Every photo
has an annotated bib; there are no negative examples. Images are at most
1.07 MP. The upscaled K2 images are never used for accuracy.

One fresh pass through the production Pillow loader and CPU OcrEngine saved
raw text, scores and boxes. All 100 filenames are unique. Each deterministic
configuration then uses the production extraction, decision, frequent-number
and evaluation functions against those same records. Cache reuse checks
photo SHA-256, model inventory, library versions and max side. These are
cached rule replays, not separate model runs for every setting.

The three allowed-bib lists are:

| List | Construction |
|---|---|
| Truth | Union of the 135 distinct K1 truth bibs, retaining their spelling |
| Range | Every integer from each event's **full source-label** minimum to maximum, applied only to that event |
| Dense | Every integer 1–90,135, the highest K1 truth bib |

Full-source ranges: set1 **48–3,719**; set2 **891–90,135**; set3 **139–4,649**.
Sample-only ranges would exclude valid entrants. Event ranges are not merged.
The set2 maximum makes its proxy very broad; no outliers were silently removed.
Truth/dense lists remain global for comparison with Task 1.

Hit rate is photos with at least one correct accepted tag / 100 readable
photos. Wrong rate is incorrect accepted tags / all accepted tags, pooled
across events. Suggestions never count as tags. Scores compare normalized
bibs, ignoring leading zeros. Errors are measured against the supplied labels;
labels were not changed after seeing predictions.

## Before the rule change

Task 6 rules (`51a3911`), no height minimum. Review threshold 0.50, max side
2048, one CPU worker, classifier off, unchanged bundled PP-OCRv6 models.

| Accept | List | Hit | Wrong / accepted | Wrong rate |
|---:|---|---:|---:|---:|
| 0.70 | Truth | 88% | 1/125 | 0.80% |
| 0.70 | Range | 88% | 33/157 | 21.02% |
| 0.70 | Dense | 88% | 51/175 | 29.14% |
| 0.80 | Truth | 88% | 1/125 | 0.80% |
| 0.80 | Range | 88% | 33/157 | 21.02% |
| 0.80 | Dense | 88% | 47/171 | 27.49% |
| 0.90 | Truth | 87% | 1/124 | 0.81% |
| 0.90 | Range | 87% | 30/153 | 19.61% |
| 0.90 | Dense | 87% | 44/167 | 26.35% |

## Authorized deterministic correction

The range result triggered Amit's one-hour allowance. Rule work started at
12:47:46 UTC and the selected implementation was in place at 12:52:14 UTC
(under five minutes); verification and reporting continued afterward.

- Reject tokens containing period/colon or letters remaining after conservative
  mapping. Existing distance rejection and mapping score penalty remain.
- Before deduplication, reject a hit when `(max(box_y) - min(box_y)) /
  loaded_upright_image_height` is below the minimum share. The boundary is
  inclusive. Production scanning supplies the actual loaded image height.
  When filtering is enabled, missing/nonpositive height raises an error.
- Retain the frequent-number filter. Start-list members remain exempt, as the
  spec requires; it therefore cannot remove these in-list false positives.

Candidate rejection can leave a photo `none`; it does not invent a suggestion
or tag. Remaining candidates still follow normal confidence/review rules.

The coarse minimum-share grid was 0%, 1%, 1.5%, 2%, 2.5%, 3%, 4%, 5%, 6%,
8%, 10%, each at accept 0.70, 0.80 and 0.90. Selected grid excerpts at 0.80:

| Minimum share | Hit | Truth wrong | Range wrong | Dense wrong |
|---:|---:|---:|---:|---:|
| 0%, letters rejected | 88% | 0.80% | 21.02% | 26.19% |
| 2% | 88% | 0.80% | 20.51% | 24.39% |
| 2.5% | 87% | 0.82% | 18.79% | 22.93% |
| 3% | 86% | 0.83% | 16.78% | 21.19% |
| 4% | 81% | 0.00% | 9.24% | 14.96% |
| **5%** | **71%** | **0.00%** | **8.33%** | **12.00%** |
| 6% | 52% | 0.00% | 4.84% | 6.35% |
| 8% | 14% | 0.00% | 12.50% | 12.50% |
| 10% | 7% | 0.00% | 0.00% | 0.00% |

**Initial selection, superseded above: minimum height share 0.05; accept 0.80.** Five
percent is the tested height with the lowest range/dense wrong rates at the
existing confidence while retaining the 70% aggregate hit gate. No useful
setting met the plan's requirement of <3% wrong on both lists, so there is no
qualifying confidence threshold to adopt. A 10% height threshold produces
only seven hit photos: its zero wrong rate is not a successful calibration.

## After: minimum height share 5%

| Accept | List | Hit | Wrong / accepted | Wrong rate |
|---:|---|---:|---:|---:|
| 0.70 | Truth | 71% | 0/88 | 0.00% |
| 0.70 | Range | 71% | 8/96 | 8.33% |
| 0.70 | Dense | 71% | 12/100 | 12.00% |
| **0.80** | **Truth** | **71%** | **0/88** | **0.00%** |
| **0.80** | **Range** | **71%** | **8/96** | **8.33%** |
| **0.80** | **Dense** | **71%** | **12/100** | **12.00%** |
| 0.90 | Truth | 71% | 0/88 | 0.00% |
| 0.90 | Range | 71% | 6/94 | 6.38% |
| 0.90 | Dense | 71% | 10/98 | 10.20% |

At the initial selection, review rates are truth 4%, range 1%, dense 0%;
`none` is 25% for all three lists. Hit rate is not complete bib recall:
a multi-runner photo needs only one correct tag to count as a hit.

| Set | Hit / photos, all lists | Truth wrong / accepted | Range wrong / accepted | Dense wrong / accepted |
|---|---:|---:|---:|---:|
| set1 | 23/34 | 0/25 | 3/28 | 5/30 |
| set2 | 18/33 | 0/22 | 1/23 | 2/24 |
| set3 | 30/33 | 0/41 | 4/45 | 5/46 |
| Total | 71/100 | 0/88 | 8/96 | 12/100 |

Before the change, range hits were 26/34, 29/33, 33/33 and wrong/accepted
were 6/34, 6/40, 21/83 respectively. Set2 hit rate falls from 87.88% to
54.55%; the aggregate 71% masks that loss. Every event remains above 3%
range wrong. A confidence of 0.90 helps slightly but also fails the target.

## Limits and checkpoint decision

All 33 baseline range wrong tags survive the remaining-letter rule. Their
height shares overlap true bibs (about 1.95–8.19%); several have confidence
above 0.999. The permitted deterministic rules cannot reliably separate them.
The axis-aligned vertical span also overstates text height for rotated boxes.

This is **in-sample tuning**, with no held-out set, no bib-free photos and no
real high-resolution accuracy test. A truth-derived start list is optimistic.
The results do not establish a <3% wrong rate for a real race. Range/dense
automatic tagging remains an unresolved risk at CHECKPOINT B.

The controlling truth-list K1 verdict remains PASS, so Task 5b is not
automatically triggered. It targets small-bib recall, not this false-positive
problem. No fallback, new model, or worker pool was added. Await Amit's
checkpoint decision before Task 8. That GO was subsequently received with
the revised selection at the top of this note.

## Reproduction and private artifacts

Run from the repository with `.venv/Scripts/python.exe`:

```powershell
.venv/Scripts/python.exe scripts/startlist_from_truth.py data/k1/truth.csv data/k1_biblocal/start-truth.csv
.venv/Scripts/python.exe scripts/startlist_from_truth.py data/k1/truth.csv data/k1_biblocal/start-dense.csv --dense
.venv/Scripts/python.exe scripts/calibrate_k1.py --out data/k1_biblocal/calibration-current
.venv/Scripts/python.exe scripts/calibrate_k1.py --reuse-ocr data/k1_biblocal/calibration-before/ocr-cache.json --out data/k1_biblocal/calibration-after --height-shares 0 .01 .015 .02 .025 .03 .04 .05 .06 .08 .10
.venv/Scripts/biblocal.exe eval data/k1_biblocal/calibration-after/range-0.80-height-0.050.csv --truth data/k1/truth.csv
```

`calibration-before/` retains pre-fix results and raw OCR; `calibration-after/`
contains all 99 rule configurations, per-event reports and per-photo CSVs.
The current code always uses the stricter token rule, even with height 0;
that row is not the pre-fix baseline. All artifacts and photos stay ignored.

## Initial selection verification (0.80 / 0.05)

The full suite passed: **75 tests**, including an observed failing test before
each new evaluation/benchmark feature and the four deterministic-rule
regressions. A separate fresh CLI scan with the selected settings and truth
list processed all 100 photos after the AC connection:

```powershell
.venv/Scripts/biblocal.exe scan data/k1 --start-list data/k1_biblocal/start-truth.csv --out data/k1_biblocal/calibrated-live --progress json --no-review
.venv/Scripts/biblocal.exe eval data/k1_biblocal/calibrated-live/results.csv --truth data/k1/truth.csv
```

It produced 71 tagged, 4 review, 25 none and 0 errors in 76.795 seconds.
Files, statuses, bibs, suggestions and reasons matched the selected cached
truth-list decisions exactly. The real CLI eval reported 71% hit, 0% wrong,
K1 PASS. Range/dense CLI evals of the cached-rule outputs reported WEAK with
8.33% and 12% wrong respectively. Hash checks verified all 100 source RBNR
files and 100 K1 copies unchanged; no photos/data files are tracked by git.
