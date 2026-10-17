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
from .csv_io import write_results_csv
from .models import Settings
from .ocr import OcrEngine
from .pipeline import cpu_name, list_photos, scan_folder
from .startlist import load_start_list


def _settings(args) -> Settings:
    settings = Settings(accept=args.accept, review=args.review, min_len=args.min_len,
                        max_len=args.max_len, max_side=args.max_side)
    if not 0 <= settings.review <= settings.accept <= 1:
        raise ValueError("require 0 <= review <= accept <= 1")
    if settings.min_len < 1 or settings.max_len < settings.min_len or settings.max_side < 1:
        raise ValueError("length bounds and max-side must be positive and ordered")
    return settings


def _add_settings(parser):
    parser.add_argument("--max-side", type=int, default=Settings.max_side)
    parser.add_argument("--accept", type=float, default=Settings.accept)
    parser.add_argument("--review", type=float, default=Settings.review)
    parser.add_argument("--min-len", type=int, default=Settings.min_len)
    parser.add_argument("--max-len", type=int, default=Settings.max_len)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="biblocal")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("scan", help="Read JPEG bibs without changing photos")
    scan.add_argument("photos", type=Path)
    scan.add_argument("--start-list", type=Path)
    scan.add_argument("--out", type=Path)
    scan.add_argument("--progress", choices=["text", "json"], default="text")
    scan.add_argument("--no-review", action="store_true")
    _add_settings(scan)
    args = parser.parse_args(argv)
    try:
        settings = _settings(args)
        folder = args.photos.resolve()
        _, skipped = list_photos(folder)
        start_list = load_start_list(args.start_list) if args.start_list is not None else None
        out = args.out.resolve() if args.out is not None else folder.with_name(folder.name + "_biblocal")
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
        run = {"version": __version__, "started_at": started_at, "ended_at": datetime.now(timezone.utc).isoformat(),
               "arguments": vars(args), "photo_root": str(folder), "settings": asdict(settings),
               "counts": counts, "skipped": skipped, "timing": timing, **engine.info,
               "python": platform.python_version(), "cpu": cpu_name(), "workers": 1}
        (out / "run.json").write_text(json.dumps(run, indent=2, default=str), encoding="utf-8")
        summary = {"type": "summary", **counts, "skipped": skipped, "seconds": seconds}
        print(json.dumps(summary) if args.progress == "json" else
              " ".join(f"{key}={value}" for key, value in summary.items() if key != "type"))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"biblocal: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
