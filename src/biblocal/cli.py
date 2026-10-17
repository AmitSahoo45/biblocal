import argparse
import json
import math
import platform
import statistics
import sys
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from . import __version__
from .csv_io import read_bib_table, read_results_csv, write_results_csv
from .exif import find_exiftool, write_keywords
from .models import Settings
from .ocr import OcrEngine
from .pipeline import cpu_name, list_photos, scan_folder
from .review import apply_corrections, write_review_page
from .startlist import load_start_list


def _settings(args) -> Settings:
    settings = Settings(accept=args.accept, review=args.review, min_len=args.min_len,
                        max_len=args.max_len, max_side=args.max_side)
    if not .5 <= settings.review <= settings.accept <= 1:
        raise ValueError("require 0.50 <= review <= accept <= 1; OCR filters scores below 0.50")
    if settings.min_len < 1 or settings.max_len < settings.min_len or settings.max_side < 1:
        raise ValueError("length bounds and max-side must be positive and ordered")
    return settings


def _add_settings(parser):
    parser.add_argument("--max-side", type=int, default=Settings.max_side)
    parser.add_argument("--accept", type=float, default=Settings.accept)
    parser.add_argument("--review", type=float, default=Settings.review)
    parser.add_argument("--min-len", type=int, default=Settings.min_len)
    parser.add_argument("--max-len", type=int, default=Settings.max_len)


def _add_writer(parser):
    parser.add_argument("--write", choices=["none", "sidecar", "embed"], default="none")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--exiftool")
    parser.add_argument("--keyword-template", default="{bib}")
    parser.add_argument("--with-names", action="store_true")


def _apply(args) -> int:
    corrections = read_bib_table(args.corrections)
    start_list = load_start_list(args.start_list) if args.start_list is not None else None
    results = apply_corrections(read_results_csv(args.results), corrections, start_list)
    out = args.results.resolve().parent
    exiftool, folder = None, None
    if args.write != "none":
        exiftool = find_exiftool(args.exiftool)
        if exiftool is None:
            raise ValueError("ExifTool was not found; install it and set --exiftool PATH or BIBLOCAL_EXIFTOOL")
        manifest = out / "run.json"
        run = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(run, dict) or not isinstance(run.get("photo_root"), str):
            raise ValueError(f"{manifest} requires photo_root")
        folder = Path(run["photo_root"])
        if not folder.is_absolute() or not folder.is_dir():
            raise ValueError(f"Photo folder in {manifest} is missing or not absolute")
    write_results_csv(results, out / "results_final.csv")
    changed = [result for result in results if result.file in corrections]
    report = {"mode": args.write, "written": 0, "skipped": len(changed), "failed": []}
    if args.write != "none":
        report = {"mode": args.write, **asdict(write_keywords(
            folder, changed, args.write, exiftool, backup=not args.no_backup,
            template=args.keyword_template, with_names=args.with_names))}
        for file, reason in report["failed"]:
            print(f"biblocal: metadata write failed for {file}: {reason}", file=sys.stderr)
    print(json.dumps({"corrected": len(changed), "results": str(out / "results_final.csv"), "write": report}))
    return 2 if report["failed"] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="biblocal")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("scan", help="Read JPEG bibs; write metadata only with --write")
    scan.add_argument("photos", type=Path)
    scan.add_argument("--start-list", type=Path)
    scan.add_argument("--out", type=Path)
    scan.add_argument("--progress", choices=["text", "json"], default="text")
    scan.add_argument("--no-review", action="store_true")
    _add_writer(scan)
    _add_settings(scan)
    apply = commands.add_parser("apply", help="Validate and apply manually confirmed corrections")
    apply.add_argument("corrections", type=Path)
    apply.add_argument("--results", type=Path, required=True)
    apply.add_argument("--start-list", type=Path)
    _add_writer(apply)
    evaluation = commands.add_parser("eval", help="Evaluate results against labelled truth")
    evaluation.add_argument("results", type=Path)
    evaluation.add_argument("--truth", type=Path, required=True)
    benchmark = commands.add_parser("bench", help="Measure one-worker CPU decode and OCR speed")
    benchmark.add_argument("photos", type=Path)
    benchmark.add_argument("--limit", type=int, default=100)
    _add_settings(benchmark)
    args = parser.parse_args(argv)
    try:
        if args.command == "apply":
            return _apply(args)
        if args.command == "eval":
            from .evaluate import evaluate, k1_verdict
            report = evaluate(read_results_csv(args.results), read_bib_table(args.truth))
            print(f"photos={report.photos} readable={report.readable} hit_rate={report.hit_rate:.6f} "
                  f"wrong_rate={report.wrong_rate:.6f} review_rate={report.review_rate:.6f}")
            print(f"VERDICT K1={k1_verdict(report)}")
            return 0
        settings = _settings(args)
        folder = args.photos.resolve()
        if args.command == "bench":
            from .bench import bench, k2_verdict
            report = bench(folder, settings, args.limit)
            out = folder.with_name(folder.name + "_biblocal")
            out.mkdir(parents=True, exist_ok=True)
            (out / "bench.json").write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
            print(" ".join(f"{key}={value}" for key, value in asdict(report).items()))
            print(f"VERDICT K2={k2_verdict(report.effective_s_per_photo)}")
            return 0
        _, skipped = list_photos(folder)
        exiftool = find_exiftool(args.exiftool) if args.write != "none" else None
        if args.write != "none" and exiftool is None:
            raise ValueError("ExifTool was not found; install it and set --exiftool PATH or BIBLOCAL_EXIFTOOL")
        start_list = load_start_list(args.start_list) if args.start_list is not None else None
        out = args.out.resolve() if args.out is not None else folder.with_name(folder.name + "_biblocal")
        if out.is_relative_to(folder) or (out / "thumbs").resolve().is_relative_to(folder):
            raise ValueError("The output folder and thumbnails must be outside the photo folder")
        started_at = datetime.now(timezone.utc).isoformat()
        started = perf_counter()
        engine = OcrEngine(max_side=settings.max_side)

        def progress(done, total, result):
            if args.progress == "json":
                print(json.dumps({"type": "progress", "done": done, "total": total,
                                  "file": result.file, "status": result.status}), flush=True)
            else:
                print(f"{done}/{total} {result.file}: {result.status}", flush=True)

        results = scan_folder(folder, start_list, settings, engine, progress)
        seconds = perf_counter() - started
        counts = {status: Counter(r.status for r in results)[status] for status in ("tagged", "review", "none", "error")}
        milliseconds = sorted(r.ms for r in results)
        timing = {"seconds": seconds, "median_ms": statistics.median(milliseconds) if milliseconds else 0,
                  "p90_ms": milliseconds[math.ceil(.9 * len(milliseconds)) - 1] if milliseconds else 0,
                  "effective_s_per_photo": seconds / len(results) if results else 0}
        out.mkdir(parents=True, exist_ok=True)
        write_results_csv(results, out / "results.csv")
        writing = {"mode": args.write, "written": 0, "skipped": len(results), "failed": []}
        if args.write != "none":
            report = write_keywords(folder, results, args.write, exiftool, backup=not args.no_backup,
                                    template=args.keyword_template, with_names=args.with_names)
            writing = {"mode": args.write, **asdict(report)}
            for file, reason in report.failed:
                print(f"biblocal: metadata write failed for {file}: {reason}", file=sys.stderr)
        run = {"version": __version__, "started_at": started_at, "ended_at": datetime.now(timezone.utc).isoformat(),
               "arguments": vars(args), "photo_root": str(folder), "settings": asdict(settings),
               "counts": counts, "skipped": skipped, "timing": timing, **engine.info,
               "python": platform.python_version(), "cpu": cpu_name(), "workers": 1, "write": writing}
        (out / "run.json").write_text(json.dumps(run, indent=2, default=str), encoding="utf-8")
        if not args.no_review:
            write_review_page(results, folder, out, settings)
        summary = {"type": "summary", **counts, "skipped": skipped, "seconds": seconds, "write": writing}
        print(json.dumps(summary) if args.progress == "json" else
              " ".join(f"{key}={value}" for key, value in summary.items() if key != "type"))
        return 2 if writing["failed"] else 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"biblocal: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
