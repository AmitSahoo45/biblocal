# Real-photo check at 2% minimum bib height

Recorded 18 Oct 2026. This is a preview-only CPU scan of 30 race JPEGs
provided by Amit in `data/demo`. The photos and all scan outputs are
git-ignored. No photo was embedded, renamed or overwritten.

## Settings and command

The scan uses accept `0.90`, review `0.50`, minimum OCR box height
`0.02` of upright image height, maximum side `2048`, one CPU worker and
the existing local RapidOCR models. No model or dependency was added.

`data/demo-startlist.csv` has columns `bib,name`. It contains the 30 bibs
Amit supplied, in his order, with names `Runner 1` through `Runner 30`.

```powershell
.venv/Scripts/biblocal.exe scan data/demo --start-list data/demo-startlist.csv --min-bib-height 0.02 --out data/demo_biblocal/height-002-startlist
```

The completed scan returned exit code 0: **23 tagged, 4 review, 3 none,
0 errors**. It skipped one non-JPEG file, `images.7z`. Write mode was
`none`: 0 written, 30 skipped for metadata writing, no write failures.
All 30 accepted tags are distinct and belong to the supplied start list.
All 30 supplied bibs occur across the 23 tagged photos.

## Per-photo results

| Photo | Status | Accepted bibs |
|---|---|---|
| 1.jpg | tagged | 10457 |
| 2.jpg | none | — |
| 3.jpg | tagged | 11081 |
| 4.jpg | tagged | 42659 |
| 5.jpg | none | — |
| 6.jpg | tagged | 50343;50220;55320 |
| 7.jpg | review | — |
| 8.jpg | tagged | 3519 |
| 9.jpg | tagged | 20211 |
| 10.jpg | tagged | 8901 |
| 11.jpg | tagged | 3013 |
| 12.jpg | tagged | 15660 |
| 13.jpg | tagged | 42156 |
| 14.jpg | tagged | 14023 |
| 15.jpg | none | — |
| 16.jpg | tagged | 40748;44773 |
| 17.jpg | tagged | 23418;21270 |
| 18.jpg | review | — |
| 19.jpg | review | — |
| 20.jpg | tagged | 54122 |
| 21.jpg | review | — |
| 22.jpg | tagged | 14392 |
| 23.jpg | tagged | 37420;37426 |
| 24.jpg | tagged | 17620 |
| 25.jpg | tagged | 36141 |
| 26.jpg | tagged | 47651;77585 |
| 27.jpg | tagged | 45294;42847 |
| 28.jpg | tagged | 71341 |
| 29.jpg | tagged | 54998 |
| 30.jpg | tagged | 83464 |

`7.jpg` has candidate `2111` below the accept threshold and outside the
start list. `18.jpg` (`3816`), `19.jpg` (`7244;17947`) and `21.jpg`
(`28025;28026;2248`) have high-confidence candidates outside the start list.
These candidates remain in review and were not accepted as tags.
`2.jpg`, `5.jpg` and `15.jpg` have no candidates after the filters.

## Comparison with the earlier manual check

Amit reported 10/30 tagged at 4% and 26/30 tagged at 2%, with correct
main-subject bibs. Those are his preceding observations. The new,
reproducible scan above uses the supplied start list and measures 23/30.

Replaying the saved candidates through the deterministic decision and
frequent-number filters without start-list membership gives **26 tagged,
1 review, 3 none**. The three additional tagged photos are `18.jpg`,
`19.jpg` and `21.jpg`. This isolates the membership check on the saved
candidates; it is not a fresh OCR scan without a start list.
The start-list guard remains unchanged.

There is no complete per-photo truth CSV for this set. Tagged count and
start-list coverage are not accuracy rates. This check does not establish
zero wrong tags or complete detection of every runner.
The JPEGs span approximately 0.50 to 12.58 MP. This is not a
uniform 24 MP benchmark.

## Preservation and private evidence

SHA-256 checks before and after the scan matched for all 31 files in
`data/demo`, including all 30 JPEGs and `images.7z`.
Private evidence is in `data/demo_biblocal/height-002-startlist/`:
`results.csv`, `run.json` and `verification.json`.
The original hash manifest is `.tmp/demo-height-002-before.json`.

- Start-list SHA-256:
  `567befd7e13d36a547c617154586cbdb8801526877e6dcb0eebb56e18ebf7f77`.
- Results CSV SHA-256:
  `56f83410ccfab802bbeca54f178bed1b6a02d18626b755f971c85745752d0855`.
- Recorded scan time: `490.16466340003535` seconds. Power condition was
  not recorded for this run; it is not a replacement for the controlled
  [K2 timing comparisons](bench.md).

The [RBNR recalibration](height-002-calibration.md) reports the separate
accuracy tradeoff: 2% recovers more bibs and accepts more wrong tags.
