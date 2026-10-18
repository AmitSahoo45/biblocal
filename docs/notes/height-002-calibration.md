# Minimum bib height: 2% versus 4%

Recorded 18 Oct 2026 for Amit's authorized change to a 2% default minimum
bib height share. At confidence **0.90**, reducing the height threshold from
4% to 2% increases K1 hit rate from **80% to 87%**, but increases the
realistic range-list wrong rate from **7.76% to 19.08%**. This trades fewer
missed bibs for more incorrect tags; it does not meet the less-than-3%
wrong-tag target on range or dense lists.

## Reproduction and cache validation

Executed from the repository on the existing CPU installation:

```powershell
$env:TEMP = (Resolve-Path -LiteralPath '.tmp').Path
$env:TMP = $env:TEMP
$env:PYTHONDONTWRITEBYTECODE = '1'
.venv/Scripts/python.exe -B scripts/calibrate_k1.py --reuse-ocr data/k1_biblocal/calibration-before/ocr-cache.json --height-shares .02 .04 --out data/k1_biblocal/calibration-height-002-final
```

The command exited successfully. It replayed deterministic rules over the
100 cached OCR records; no OCR inference, model download or metadata write
was performed. The script generated 18 configurations (two heights, three
confidence thresholds and three list types). The tables below select only
confidence 0.90. Private results are in the new, git-ignored output folder's
`reports.json` and per-configuration CSV files.

The script checked the complete cache fingerprint against the installed
engine: max side 2048, RapidOCR 3.10.0, CPU ONNX Runtime 1.31.0, all three
model files' sizes and SHA-256 values, and all 100 K1 JPEG SHA-256 values.
An independent before/after hash comparison confirmed that the 100 K1 input
JPEGs still match the cache, and that the OCR cache, `truth.csv` and all
three full-source `list.txt` files were unchanged. Independent arithmetic
from each of the six selected CSV files matched its JSON report's hit,
wrong-tag and accepted-tag counts.

Input SHA-256 values:

| File | SHA-256 |
|---|---|
| `data/k1_biblocal/calibration-before/ocr-cache.json` | `ff84535f1014cf5b73035f060c5d388fd4c50bedce8fe611cb0aa977ee59bba3` |
| `data/k1/truth.csv` | `c9caeb60911a8278ec04591d32b7f98ce4017fa350341d37d93681fa5931a5c2` |
| `data/rbnr/datasets/set1_org/list.txt` | `a88e772695d5d9493f38cdc6092cbe1650f9dcdfa91ec43d96f797805d03c7fc` |
| `data/rbnr/datasets/set2_org/list.txt` | `196b8e88da17c03fde6a31ece08e2aed94228f421da3175bcc7c872c792101a1` |
| `data/rbnr/datasets/set3_org/list.txt` | `0208cb1ff5ba01c7a39113a17e102eda44a45169dad1b91d2e2e4467f3c4a691` |

## Results at confidence 0.90

Hit rate is photos with at least one correctly accepted bib divided by
100 readable photos. Wrong rate is incorrect accepted bib/photo pairs
divided by all accepted pairs; it is not a percentage of photos. Leading
zeros are normalized for scoring. Suggestions never count as accepted tags.

| Minimum height share | Start list | Hit / photos | Hit rate | Wrong / accepted | Wrong rate |
|---|---|---:|---:|---:|---:|
| 2% | Truth | 87/100 | 87% | 1/124 | 0.81% |
| 2% | Range | 87/100 | 87% | 29/152 | 19.08% |
| 2% | Dense | 87/100 | 87% | 37/160 | 23.13% |
| 4% | Truth | 80/100 | 80% | 0/107 | 0.00% |
| 4% | Range | 80/100 | 80% | 9/116 | 7.76% |
| 4% | Dense | 80/100 | 80% | 17/124 | 13.71% |

The 4% replay reproduces the previously selected results in
[calibration.md](calibration.md). At 2%, the truth list has 87 tagged,
2 review and 11 none photos. Range and dense each have 88 tagged, 1 review
and 11 none: one tagged photo has no correct tag, so tagged count must not
be reported as hit count. At 4%, each list has 80 tagged, 1 review and 19 none.

| Minimum height share | Set | Hit / photos, all lists | Truth wrong / accepted | Range wrong / accepted | Dense wrong / accepted |
|---|---|---:|---:|---:|---:|
| 2% | set1 | 25/34 (73.53%) | 0/27 | 5/32 | 7/34 |
| 2% | set2 | 29/33 (87.88%) | 0/34 | 6/40 | 9/43 |
| 2% | set3 | 33/33 (100.00%) | 1/63 | 18/80 | 21/83 |
| 4% | set1 | 25/34 (73.53%) | 0/27 | 3/30 | 5/32 |
| 4% | set2 | 23/33 (69.70%) | 0/28 | 2/30 | 5/33 |
| 4% | set3 | 32/33 (96.97%) | 0/52 | 4/56 | 7/59 |

The 2% threshold recovers six hit photos in set2 and one in set3; set1 is
unchanged. This improves recovery of smaller bibs, while accepting 20 more
wrong tags on both the range and dense lists. Even the optimistic truth list
now accepts one wrong tag: `3750` on `set3_01.JPG`.

## Interpretation and limits

This is an in-sample comparison on the same 100 native RBNR photos used for
earlier calibration, with 143 annotated bib/photo pairs. It has no held-out
set, no bib-free photos and no high-resolution camera-original accuracy
test. Hit rate does not measure recovery of every runner in a group photo.
It is not a new speed benchmark or evidence about the separate demo set.

The truth list is the optimistic union of the 135 distinct K1 truth bibs.
Range lists include every integer between each event's full-source minimum
and maximum: set1 48-3719, set2 891-90135, set3 139-4649. Each range applies
only to its own event; ranges are not merged. The dense list contains every
integer from 1 to 90135. No source labels or range outliers were altered.

The same confidence, digit/start-list validation and frequent-number filter
apply at both heights. Bounding-box height is the vertical span in the OCR
image, so angled text can appear taller. Lowering the height threshold does
not resolve the ambiguity between bibs and other numbers. The larger range
and dense wrong rates must accompany any claim about the improved hit rate.
