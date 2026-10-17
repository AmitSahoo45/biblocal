"""Task 1 spike only; no package imports and no metadata writes."""

import argparse
import csv
import math
import re
import statistics
import sys
from pathlib import Path
from time import perf_counter

from PIL import Image, ImageOps


def photos_in(folder: Path) -> list[Path]:
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg"}
        and not any(part.endswith("_biblocal") for part in p.relative_to(folder).parts[:-1])
    )


def write_truth_template(folder: Path) -> None:
    with (folder / "truth.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["file", "bibs"])
        writer.writerows((p.relative_to(folder).as_posix(), "") for p in photos_in(folder))


def candidates(texts: list[tuple[str, float]]) -> dict[str, float]:
    found = {}
    for text, score in texts:
        if score < .5:
            continue
        for token in text.split():
            if ":" in token or "." in token or token.upper().endswith(("K", "KM")):
                continue
            for number in re.findall(r"[0-9]+", token):
                if len(number) > 5:
                    continue
                number = number.lstrip("0") or "0"
                found[number] = max(found.get(number, 0), float(score))
    return found


def tags_for(read: dict[str, float], allowed: set[str] | None) -> set[str]:
    return {bib for bib, score in read.items() if score >= .8 and (allowed is None or bib in allowed)}


def metrics(reads: dict[str, dict[str, float]], truth: dict[str, list[str]], allowed: set[str]) -> dict:
    readable = hits = total_tags = wrong = photos = 0
    for file, read in reads.items():
        if file not in truth:
            raise ValueError(f"Missing truth for {file}")
        photos += 1
        expected = {bib.lstrip("0") or "0" for bib in truth[file]}
        tags = tags_for(read, allowed)
        readable += bool(expected)
        hits += bool(tags & expected)
        total_tags += len(tags)
        wrong += len(tags - expected)
    return {
        "photos": photos, "readable": readable,
        "hit_rate": hits / readable if readable else 0.,
        "wrong_rate": wrong / total_tags if total_tags else 0.,
    }


def verdict(hit: float | None, wrong: float | None, speed: float) -> tuple[str, str]:
    k1 = "n/a" if hit is None else "KILL" if hit < .5 else "PASS" if hit >= .7 and wrong < .03 else "WEAK"
    k2 = "PASS" if speed <= 2. else "SLOW" if speed <= 5. else "KILL"
    return k1, k2


def make_engine(max_side: int):
    import onnxruntime
    import rapidocr
    from rapidocr import RapidOCR

    if onnxruntime.get_device() != "CPU":
        raise RuntimeError("Install the CPU onnxruntime package")
    onnxruntime.disable_telemetry_events()
    root = Path(rapidocr.__file__).parent / "models"
    params = {
        "Global.max_side_len": max_side, "Global.use_cls": False,
        "Global.text_score": .5, "Global.log_level": "error",
        "Det.limit_type": "max", "Det.limit_side_len": max_side,
        "EngineConfig.onnxruntime.use_cuda": False,
        "EngineConfig.onnxruntime.use_dml": False,
        "EngineConfig.onnxruntime.use_cann": False,
        "EngineConfig.onnxruntime.use_coreml": False,
    }
    for kind, name in (("Det", "PP-OCRv6_det_small.onnx"), ("Rec", "PP-OCRv6_rec_small.onnx"),
                       ("Cls", "ch_ppocr_mobile_v2.0_cls_mobile.onnx")):
        model = root / name
        if not model.is_file():
            raise FileNotFoundError(f"Bundled model missing; repair the installation: {model}")
        params[f"{kind}.model_path"] = str(model.resolve())
    return RapidOCR(params=params)


def load_photo(path: Path, max_side: int) -> Image.Image:
    with Image.open(path) as image:
        ratio = min(1., max_side / max(image.size))
        target = tuple(max(1, round(dimension * ratio)) for dimension in image.size)
        image.draft("RGB", target)
        upright = ImageOps.exif_transpose(image)
        upright.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        return upright.convert("RGB")


def block_network(event, args):
    if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto"}:
        raise RuntimeError(f"Runtime network access is disabled: {event}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--photos", required=True, type=Path)
    parser.add_argument("--make-truth-template", action="store_true")
    parser.add_argument("--truth", type=Path)
    parser.add_argument("--max-side", type=int, default=2048)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args(argv)
    if not args.photos.is_dir() or args.max_side < 1 or args.limit < 1:
        parser.error("photos must be an existing directory; max-side and limit must be positive")
    if args.make_truth_template:
        write_truth_template(args.photos)
        return 0
    photos = photos_in(args.photos)[:args.limit]
    if not photos:
        parser.error("no JPEGs found")
    truth = None
    if args.truth:
        with args.truth.open(encoding="utf-8-sig", newline="") as stream:
            truth = {row["file"]: [b.strip() for b in row["bibs"].split(";") if b.strip()]
                     for row in csv.DictReader(stream)}
        if any(not b.isascii() or not b.isdigit() for bibs in truth.values() for b in bibs):
            parser.error("truth contains a non-digit bib")
        if any(p.relative_to(args.photos).as_posix() not in truth for p in photos):
            parser.error("every measured photo must have a truth row")
    sys.addaudithook(block_network)
    engine = make_engine(args.max_side)
    rows, reads = [], {}
    for index, photo in enumerate(photos, 1):
        started = perf_counter()
        with load_photo(photo, args.max_side) as image:
            result = engine(image)
        elapsed = perf_counter() - started
        raw = list(zip(result.txts or (), result.scores or ()))
        file = photo.relative_to(args.photos).as_posix()
        reads[file] = candidates(raw)
        rows.append({"file": file, "truth": ";".join(truth[file]) if truth is not None else "",
                     "read": ";".join(f"{text}:{score:.4f}" for text, score in raw), "seconds": elapsed})
        if index % 10 == 0 or index == len(photos):
            print(f"Processed {index}/{len(photos)}", file=sys.stderr, flush=True)
    times = [row["seconds"] for row in rows]
    effective = sum(times) / len(times)
    med = statistics.median(times)
    p90 = sorted(times)[math.ceil(.9 * len(times)) - 1]
    allowed = None
    hit = wrong = None
    if truth is not None:
        allowed = {bib.lstrip("0") or "0" for bibs in truth.values() for bib in bibs}
        lists = [("truth", allowed), ("dense", {str(n) for n in range(1, max(map(int, allowed), default=0) + 1)})]
    else:
        lists = [("none", None)]
    for name, proxy in lists:
        report = metrics(reads, truth, proxy) if truth is not None else None
        if name == "truth":
            hit, wrong = report["hit_rate"], report["wrong_rate"]
        values = (f"readable={report['readable']} hit_rate={report['hit_rate']:.2f} wrong_rate={report['wrong_rate']:.2f}"
                  if report else "readable=0 hit_rate=n/a wrong_rate=n/a")
        print(f"list={name} photos={len(photos)} {values} effective_s={effective:.2f} "
              f"median_s={med:.2f} p90_s={p90:.2f} max_side={args.max_side}")
    k1, k2 = verdict(hit, wrong, effective)
    print(f"VERDICT K1={k1} K2={k2}")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["file", "truth", "read", "tags", "seconds"])
            writer.writeheader()
            for row in rows:
                row["tags"] = ";".join(sorted(tags_for(reads[row["file"]], allowed)))
                writer.writerow(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
