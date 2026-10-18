# Task 11 verification and freeze checklist

Recorded 18 Oct 2026. Code freeze: **Sunday 18 Oct, 18:00 IST**.
Tasks 9 and 11 are implemented. K4 passed in digiKam 9.1.0, reported by Amit;
see [K4](k4.md). No original RBNR photo was written during this work.

## Verification completed

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

## Freeze readiness

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
