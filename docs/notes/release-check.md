# Task 11 verification and freeze checklist

Recorded 18 Oct 2026. Code freeze: **Sunday 18 Oct, 18:00 IST**.
Tasks 9 and 11 are implemented. K4 passed in digiKam 9.1.0, reported by Amit;
see [K4](k4.md). No original RBNR photo was written during this work.

## 18 Oct amendment: configurable 2% minimum height

Amit authorized `scan --min-bib-height`, a new default of `0.02` and a
commit and push before 18:00 IST. Accept remains `0.90`. No model,
dependency, worker or metadata-writing behavior changed.
This amendment supersedes the earlier 4% freeze candidate below.

- Test-first check: **10 failed, 1 passed** before implementation;
  **11 passed** after implementation. Tests cover the default, explicit
  4%, the 0 and 1 bounds, rejection of invalid/non-finite shares, saved
  settings and source-photo preservation.
- Full regression suite for the intended release contents: **134 passed
  in 270.73 seconds**, with no skips. This includes the existing CPU OCR,
  offline, ExifTool and local Edge checks.
- Tests ran in `.tmp/height-002-verification`, an isolated D: copy of
  committed files overlaid with this amendment. Imports were verified to
  come from that copy, and changed source/test files matched the working
  tree byte for byte.
- Two pre-existing working-tree deletions in `THIRD_PARTY_NOTICES.md`
  remove upstream attribution text and fail the notice-preservation test.
  They are excluded from this amendment; its tested release contents
  retain the complete committed notices. No test was weakened.
- RBNR rules were recalibrated on validated cached OCR at both 2% and 4%.
  At 2%, all three lists reach **87% hit**. Wrong rates are **0.81% truth,
  19.08% range and 23.13% dense**. At 4%, all reach **80% hit**, with
  **0%, 7.76% and 13.71% wrong**, respectively. These are in-sample
  results on 100 photos, with no held-out set.
- The fresh CPU preview scan of 30 demo JPEGs with Amit's supplied start
  list returned **23 tagged, 4 review, 3 none, 0 errors**. All 30 listed
  bibs occur across those 23 tagged photos. This is coverage, not a
  measured accuracy rate. All 31 source-file hashes remained unchanged.
- README retains 119 lines and reports both calibration settings, the
  demo counts, small-bib misses and the higher false-positive rate.

See [calibration evidence](height-002-calibration.md) and
[every demo photo's result](demo-height-002.md).
The earlier wheel and physical network-off check below describe the
previous application version; neither was repeated for this amendment.
The automated offline test passed as part of the new 134-test suite.
No new speed benchmark was run.

## Earlier Task 11 verification

- Task 11 tests first reported **4 failed, 1 passed** for the missing
  documentation/license requirements, then **5 passed** after implementation.
- Final full regression suite: **126 passed in 161.25 seconds**. ExifTool and
  local Edge integration tests ran; none were skipped.
- Built `biblocal-0.1.0-py3-none-any.whl` with pip, using repository temporary
  files and the pip cache on D:. No runtime dependency was added. The existing
  setuptools build requirement now starts at 77 for SPDX license metadata.
- Installed that wheel into an isolated target folder, using the existing
  verified runtime dependencies. This was not a new dependency installation
  into a clean machine. The smoke test confirmed imports came from the wheel,
  not the source tree.
- The installed wheel passed `scan`, `apply` and `eval` on a synthetic photo,
  with network and model-download calls blocked. The photo's SHA-256 stayed
  unchanged. All four command help pages worked. This smoke test is not a new
  accuracy evaluation or speed measurement.
- The wheel contains MIT license metadata, Amit Sahoo's copyright and complete
  `LICENSE`, `MODELS.md` and `THIRD_PARTY_NOTICES.md` files. It contains no
  photos or model binaries; RapidOCR supplies the local models as a dependency.
- The notices inventory covers 21 installed runtime distributions. All 50
  supplied license/notice files are preserved in 46 distinct text blocks.
  Upstream whitespace in verbatim license texts is retained intentionally.
  Model sizes and SHA-256 values match the final engine inventory.

Private build: `.tmp/wheel-final/biblocal-0.1.0-py3-none-any.whl`

SHA-256:

```text
e4ac5e24690b0ebc672ba74bf3bf3aa8cdd03831a5ddb29f95ecdfd8071e4c3d
```

Private verification details: `.tmp/package-smoke/verification.json`.
The build and smoke files are git-ignored. These checks did not publish a
package, push commits or create a release.

## Check 1: manual review and preview apply — PASS

Amit reported the review complete on 18 Oct. The saved `corrections.csv`
contains **20 confirmed rows**, including two No bib choices. The browser
name was not supplied (the report retained a placeholder).

The agent ran the requested preview-only command with the original start list:

```powershell
.venv/Scripts/biblocal.exe apply data/k1_biblocal/task9-review/corrections.csv --results data/k1_biblocal/task9-review/results.csv --start-list data/k1_biblocal/start-truth.csv
```

Validation correctly rejected `211` for `set1_28.JPG` because it is absent
from the start list. Inspection found six rejected numbers across four rows:

| Photo | Entered numbers absent from start list | RBNR annotated bibs for the photo |
|---|---|---|
| set1_28.JPG | 211 | 311 |
| set1_92.JPG | 3278 | 3276 |
| set2_36.JPG | 0190 | 10190 |
| set3_02.JPG | 3455;3632;2073 | 3855;3236;3482;775 |

No `results_final.csv` was created by the rejected apply. Source/input hashes
were unchanged. Amit then explicitly approved all four RBNR-label replacements
shown above and instructed that the start-list guard stay unchanged.

The agent created `corrections-validated.csv` with exactly those four changes.
The original export remains intact; the other 16 correction rows are unchanged.
The approved group-photo order is `3855;3236;3482;775`.

```powershell
.venv/Scripts/biblocal.exe apply data/k1_biblocal/task9-review/corrections-validated.csv --results data/k1_biblocal/task9-review/results.csv --start-list data/k1_biblocal/start-truth.csv
```

This command exited successfully: **20 corrected**, write mode **none**,
**0 written**, **20 write-skipped**, **0 failures**. Inspection of
`results_final.csv` verified:

- All **100 rows** remain in their original order.
- Exactly **20 rows** have reason `manual`: **18 tagged, 2 none**.
- Their bibs match the approved CSV and start-list spelling; manual scores
  and stale suggestions are cleared.
- The other **80 result rows** are unchanged.
- SHA-256 checks match for all **100 source JPEGs**, the original
  `corrections.csv`, `results.csv` and the start list.
- The unchanged guard still rejects the original `211` entry. No application
  code or validation rule was changed.

Private evidence: `data/k1_biblocal/task9-review/apply-verification.json`.
This is acceptance testing with four explicitly approved dataset-label
replacements, not a new OCR accuracy measurement. Check 1 is complete;
the browser name remains unreported.

Focused validation regression: **12 passed in 1.92 seconds**
(`tests/test_apply.py`). No application defect has been identified.
See [the review check](task9-review.md) for the original acceptance procedure.

## Check 2: physical network-off scan — PASS

Amit confirmed **Wi-Fi off and Ethernet unplugged** for this run on the
finished application code at `a4cd8fc`. Adapter state is user-reported; saved
run artifacts were independently inspected by the agent.

```powershell
.venv/Scripts/biblocal.exe scan data/k4 --start-list data/k1_biblocal/start-truth.csv --out data/k4_biblocal/final-offline
```

The saved run spans **18 Oct 2026, 09:07:15–09:07:25 IST**, with **CPU,
one worker**, accept 0.90 and minimum height share 0.04:

```text
tagged=8 review=0 none=2 error=0 skipped=13 seconds=9.90929859993048
write={'mode': 'none', 'written': 0, 'skipped': 10, 'failed': []}
```

The CSV has exactly ten rows and all eight accepted tags match the annotations.
Bib 2605 appears on exactly `set1_12.JPG` and `set1_14.JPG`.
The 13 skipped files are eight `_original` backups, four digiKam database
files and `.dtrash/digikam.uuid`; **no JPEG was skipped**.
The local review page exists, has no external resource references, and
correctly shows an empty review queue. The two `none` rows are abstentions,
not evidence that those photos have no visible bib.

No metadata writes were requested or recorded. The elapsed 9.91 seconds is a
ten-photo functional smoke result; power condition was not supplied. It does
not replace the documented K2 benchmark. Private evidence is in
`data/k4_biblocal/final-offline/` and `.tmp/final-check-inspection.json`.

## Earlier freeze readiness (superseded by the amendment above)

**Both final acceptance checks pass.** No implementation fixes or acceptance
checks remain in the reduced scope. The commit recording this completion is
the freeze candidate; its application code and package metadata are unchanged
from `a4cd8fc`, the version used for the physical offline check and built wheel.
The existing 126-test full-suite result still applies; no code changed during
these final checks. No tag, push or release publication was performed.

The real range-list wrong rate is still 7.76%, and small bibs remain a known
limit. These are disclosed limitations, not a claimed less-than-3% result.
Task 5b stays deferred. Tasks 10, 12, 13 and the Task 14 script remain cut.
Lightroom, macOS and Linux remain untested.

## Submission work owned by Amit

Collect write-up facts by hand, prepare the demo and DEV post, and arrange
the public source/release. A Git remote is configured, but publication of
this final commit/release was not verified or performed here. K3 chatbot
comparison and K5 demand feedback have no recorded results in the current
notes; report them only if actually completed. They are not additional coding
tasks. Submission deadline: **Monday 19 Oct, 12:29 PM IST**.
