"""Private, reproducible K1 calibration with one OCR pass and three list types."""

import argparse
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

from biblocal.bibs import decide, demote_frequent, extract_candidates
from biblocal.csv_io import read_bib_table, write_results_csv
from biblocal.evaluate import evaluate
from biblocal.loader import load_for_ocr
from biblocal.models import Settings, TextHit
from biblocal.ocr import OcrEngine
from biblocal.pipeline import list_photos
from biblocal.startlist import Runner, StartList, normalize_bib


def load_ranges(source: Path) -> dict[str, tuple[int, int]]:
    ranges = {}
    for path in sorted(source.glob("set*_org/list.txt")):
        bibs = []
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            fields = line.split()
            if fields and fields[0].lower() not in {"image", "total"}:
                if len(fields) != 2 or not fields[1].isdigit():
                    raise ValueError(f"Invalid truth row in {path}: {line}")
                bibs.append(int(fields[1]))
        if bibs:
            ranges[path.parent.name.removesuffix("_org")] = (min(bibs), max(bibs))
    if not ranges:
        raise ValueError("No RBNR label ranges found")
    return ranges


def score_records(records: list[dict], truth: dict[str, list[str]], ranges: dict,
                  mode: str, settings: Settings):
    global_bibs = {normalize_bib(bib): bib for bibs in truth.values() for bib in bibs}
    if mode == "truth":
        shared = StartList([Runner(bib) for bib in global_bibs.values()])
    elif mode == "dense":
        shared = StartList([Runner(str(n)) for n in range(1, max(map(int, global_bibs), default=0) + 1)])
    elif mode != "range":
        raise ValueError(f"Unknown list type: {mode}")
    groups = {}
    for record in records:
        groups.setdefault(Path(record["file"]).name.split("_", 1)[0], []).append(record)
    results = []
    for group, entries in sorted(groups.items()):
        if mode == "range":
            lo, hi = ranges[group]
            start_list = StartList([Runner(str(n)) for n in range(lo, hi + 1)])
        else:
            start_list = shared
        subset = []
        for entry in entries:
            hits = [TextHit(h["text"], h["score"], tuple(tuple(point) for point in h["box"])) for h in entry["hits"]]
            candidates = extract_candidates(hits, settings, start_list, image_height=entry["height"])
            subset.append(decide(entry["file"], candidates, start_list, settings))
        results.extend(demote_frequent(subset, start_list, settings))
    results.sort(key=lambda result: result.file)
    return evaluate(results, truth), results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--photos", type=Path, default=Path("data/k1"))
    parser.add_argument("--truth", type=Path, default=Path("data/k1/truth.csv"))
    parser.add_argument("--source", type=Path, default=Path("data/rbnr/datasets"))
    parser.add_argument("--out", type=Path, default=Path("data/k1_biblocal/calibration-before"))
    parser.add_argument("--reuse-ocr", type=Path)
    parser.add_argument("--height-shares", type=float, nargs="+", default=[Settings.min_bib_height_share])
    args = parser.parse_args(argv)
    settings = Settings()
    engine = OcrEngine(max_side=settings.max_side)
    photos, _ = list_photos(args.photos)
    fingerprint = {
        "max_side": settings.max_side, "models": engine.info["models"],
        "rapidocr": engine.info["rapidocr"], "onnxruntime": engine.info["onnxruntime"],
        "photos": {p.relative_to(args.photos).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in photos},
    }
    args.out.mkdir(parents=True, exist_ok=True)
    if args.reuse_ocr:
        cache = json.loads(args.reuse_ocr.read_text(encoding="utf-8"))
        if cache["fingerprint"] != fingerprint:
            raise ValueError("OCR cache does not match photos, models or OCR settings")
        records = cache["records"]
    else:
        records = []
        for index, path in enumerate(photos, 1):
            loaded = load_for_ocr(path, settings.max_side)
            try:
                records.append({"file": path.relative_to(args.photos).as_posix(), "height": loaded.image.height,
                                "hits": [asdict(hit) for hit in engine.read(loaded.image)]})
            finally:
                loaded.image.close()
            if index % 10 == 0:
                print(f"OCR {index}/{len(photos)}", flush=True)
        (args.out / "ocr-cache.json").write_text(json.dumps({"fingerprint": fingerprint, "records": records}, indent=2), encoding="utf-8")
    truth, ranges = read_bib_table(args.truth), load_ranges(args.source)
    table = []
    for height in args.height_shares:
        for accept in (.70, .80, .90):
            for mode in ("truth", "range", "dense"):
                report, results = score_records(records, truth, ranges, mode,
                                                replace(settings, accept=accept, min_bib_height_share=height))
                accepted = sum(len(result.bibs) for result in results if result.status == "tagged")
                per_set = {}
                for group in ranges:
                    subset = [result for result in results if result.file.startswith(group + "_")]
                    per_set[group] = {**asdict(evaluate(subset, truth)),
                                      "accepted": sum(len(result.bibs) for result in subset if result.status == "tagged")}
                row = {"accept": accept, "min_bib_height_share": height, "list": mode,
                       "accepted": accepted, "per_set": per_set, **asdict(report)}
                table.append(row)
                write_results_csv(results, args.out / f"{mode}-{accept:.2f}-height-{height:.3f}.csv")
                print(f"height={height:.3f} accept={accept:.2f} list={mode} hit={report.hit_rate:.6f} wrong={report.wrong_rate:.6f}", flush=True)
    (args.out / "reports.json").write_text(json.dumps({"ranges": ranges, "reports": table}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
