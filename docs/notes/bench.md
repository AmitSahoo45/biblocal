# CPU benchmark — 17 Oct 2026

**CHECKPOINT B K2: PASS on user-reported AC power, 1.531128 s/photo at 2048.**
Battery-saver runs failed the speed gate. Power condition materially affects
the result and must accompany any quoted timing.

Task 10 (worker pool) remains cut. All measurements use one worker on the
**13th Gen Intel Core i7-13650HX**, Windows 11, Python 3.13.7,
RapidOCR 3.10.0, ONNX Runtime 1.31.0 CPU, Pillow 13.0.0. One worker can use
multiple CPU threads: ORT intra/inter-op thread counts retain library defaults.
No GPU provider is selected. Other OCR tests/runs did not overlap these runs.

## Timing data

K2 contains **20 upscaled RBNR images, not camera originals**. Task 1 took the
first 20 sorted native K1 JPEGs, resized each to exactly 6000×4000 with Pillow
LANCZOS, and saved JPEG quality 92. This creates a synthetic 24 MP decode/OCR
workload; it cannot represent native camera detail or high-resolution accuracy.
The prescribed dimensions also change the source aspect ratio. K2 is never
used for K1 calibration. Matching native images are the first 20 files in K1.

`bench` times production JPEG decode, EXIF orientation, downsampling and OCR,
including engine construction, model hash checks and first-use initialization.
It excludes process/import startup, file discovery, CSV/report writes,
start-list validation, bib decisions and metadata writing. Per-photo median
and nearest-rank p90 include the first OCR call but exclude engine construction.
No warm-up photo is discarded. Effective time is timed wall time / photos;
minutes per 1,000 is an extrapolation, not a measured 1,000-photo batch.

| Run | Images | Max side | Effective s/photo | Median s | p90 s | Minutes/1,000 | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Task 1 spike, synthetic 24 MP | 20 | 2048 | 2.066084 | 1.975725 | 2.403191 | 34.43 | SLOW |
| Task 1 spike, matching native RBNR | 20 | 2048 | 0.696063 | 0.716201 | 1.064457 | 11.60 | Comparison only |
| Task 7, battery saver, synthetic 24 MP | 20 | 2048 | 12.488684 | 15.951029 | 18.837040 | 208.14 | Above 5 s; retry required |
| Task 7 retry, battery saver, synthetic 24 MP | 20 | 1536 | 14.388912 | 13.951665 | 17.466558 | 239.82 | KILL in this power condition |
| Task 7, AC, synthetic 24 MP | 20 | 2048 | **1.531128** | 1.467985 | 1.823628 | **25.52** | **PASS** |
| Task 7, AC, matching native RBNR | 20 | 2048 | **0.569212** | 0.488438 | 0.879631 | **9.49** | Comparison only |

After these two slow runs, Amit reported: **"Was on battery saver. Plugged
in the charger"**. The battery-saver rows remain part of the evidence; they
are not replaced by the original spike. The first native comparison near the
power change measured 0.660034 s/photo, but its exact power-transition timing
was not observed, so it is excluded from the AC comparison.
Both synthetic K2 and native images were measured again after the reported
AC connection. Those two runs were sequential and used the same worker,
thread, model and max-side settings. No 1536 retry was needed on AC because
2048 passed. Power status is user-reported; no power settings were changed
by the agent. Temperature and external workload were not controlled.

Task 1 and Task 7 timers both include first-use OCR initialization, but Task 7
also includes construction and hash checks. This difference must not be
presented as the established cause of the battery-saver slowdown.

Task 6's separate 100-photo native K1 scan took 168.874 seconds (1.69 s/photo),
including decisions, before the Task 7 height rule. It is a different workload
from synthetic 24 MP K2 and must not be presented as K2 speed.

## Reproduction

```powershell
.venv/Scripts/biblocal.exe bench data/k2 --limit 50
.venv/Scripts/biblocal.exe bench data/k2 --limit 50 --max-side 1536
.venv/Scripts/biblocal.exe bench data/k1 --limit 20
```

Only 20 K2 files exist, so `--limit 50` measures all 20. The first fresh result
is preserved in ignored `data/k2_biblocal/bench-task7-2048.json`; `bench.json`
is the most recent run for each folder. The battery retry is preserved as
`bench-task7-1536.json`; AC K2 is `bench-task7-ac-2048.json`; AC native is
`data/k1_biblocal/bench-task7-ac-native-2048.json`. The one retry at 1536 was
required by the plan when 2048 exceeded 5 s/photo. It did not change the
default max side, which remains 2048 for K1 and the final AC K2 result.

The README must retain Amit's accepted spike figure **2.07 s/photo, about
34 minutes per 1,000, single worker, synthetic 24 MP**, clearly labelled as
that measured run. It must also disclose the newer measurements and variation.
No average-laptop performance claim follows from this gaming-laptop CPU test.
