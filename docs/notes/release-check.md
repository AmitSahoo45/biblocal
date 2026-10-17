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

## Remaining before 18:00 IST

1. **Amit's five-card review check.** Amit said he will run it; PASS/FAIL and
   browser are still pending. Follow [the prepared check](task9-review.md),
   including inspecting `results_final.csv` after preview-only apply.
2. **Physical network-off check on the finished version.** The earlier spike
   airplane-mode PASS remains valid historical evidence; it predates Tasks
   9 and 11. Turn Wi-Fi off and disconnect Ethernet, then run the following
   preview scan on the existing K4 temporary copies. Inspect its CSV and open
   its local review page. Record PASS/FAIL, command output and power condition
   here, then restore networking.

   ```powershell
   .venv/Scripts/biblocal.exe scan data/k4 --start-list data/k1_biblocal/start-truth.csv --out data/k4_biblocal/final-offline
   ```

   Expected: 10 result rows, no errors or metadata writes; the known K4 run has
   eight tagged and two none. An empty review queue is valid for these copies.
   This command has no `--write` flag and preserves their metadata and pixels.
3. **Resolve any failures from those two checks, rerun affected tests, commit
   the results/fixes and identify the final frozen commit by 18:00 IST.**
   No further planned feature work remains in the reduced scope.

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
