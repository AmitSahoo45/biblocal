"""Prepare private K1 labels/copies and Amit's authorized upscaled K2 set."""

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


def prepare(source: Path, k1: Path, k2: Path, sample_size: int = 100, timing_size: int = 20) -> dict:
    sets = []
    for label_file in sorted(source.glob("set*_org/list.txt")):
        labels = {}
        for line in label_file.read_text(encoding="utf-8-sig").splitlines():
            fields = line.split()
            if not fields or fields[0].lower() in {"image", "total"}:
                continue
            if len(fields) != 2 or not fields[1].isascii() or not fields[1].isdigit():
                raise ValueError(f"Bad label in {label_file}: {line}")
            name, bib = fields
            if Path(name).name != name or not (label_file.parent / name).is_file():
                raise ValueError(f"Missing or invalid image: {name}")
            labels.setdefault(name, []).append(bib)
        sets.append((label_file.parent, labels))
    if not sets or sum(len(labels) for _, labels in sets) < sample_size:
        raise ValueError("Not enough labelled RBNR photos")
    for destination in (k1, k2):
        if destination.exists() and any(destination.iterdir()):
            raise FileExistsError(f"Refusing to overwrite {destination}")
    selected = []
    for index, (folder, labels) in enumerate(sets):
        quota = sample_size // len(sets) + (index < sample_size % len(sets))
        names = sorted(labels)
        if quota > len(names):
            raise ValueError(f"Insufficient images in {folder}")
        for i in range(quota):
            name = names[i * (len(names) - 1) // (quota - 1)] if quota > 1 else names[0]
            selected.append((folder / name, labels[name]))
    selected.sort(key=lambda item: item[0].name)
    if len({path.name for path, _ in selected}) != len(selected):
        raise ValueError("Duplicate image filenames across sets")
    k1.mkdir(parents=True, exist_ok=True)
    k2.mkdir(parents=True, exist_ok=True)
    manifest = {"sample": [], "k2_source": "upscaled RBNR, not camera originals", "k2": []}
    with (k1 / "truth.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["file", "bibs"])
        for index, (path, bibs) in enumerate(selected):
            shutil.copy2(path, k1 / path.name)
            writer.writerow([path.name, ";".join(bibs)])
            with Image.open(path) as image:
                manifest["sample"].append({
                    "file": path.name, "source": str(path), "bibs": bibs,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size": list(image.size),
                })
                if index < timing_size:
                    enlarged = image.convert("RGB").resize((6000, 4000), Image.Resampling.LANCZOS)
                    enlarged.save(k2 / path.name, "JPEG", quality=92)
                    manifest["k2"].append(path.name)
    (k1 / "preparation.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/rbnr/datasets"))
    parser.add_argument("--k1", type=Path, default=Path("data/k1"))
    parser.add_argument("--k2", type=Path, default=Path("data/k2"))
    args = parser.parse_args()
    result = prepare(args.source, args.k1, args.k2)
    print(f"K1={len(result['sample'])} K2={len(result['k2'])}; K2 is upscaled RBNR, timing only")
