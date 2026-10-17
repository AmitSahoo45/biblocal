import argparse
import csv
from pathlib import Path

from biblocal.csv_io import read_bib_table
from biblocal.startlist import normalize_bib


def write_start_list(truth_path: Path, output: Path, dense: bool = False) -> None:
    spellings = {}
    for bibs in read_bib_table(truth_path).values():
        for bib in bibs:
            spellings.setdefault(normalize_bib(bib), bib)
    bibs = [str(n) for n in range(1, max(map(int, spellings), default=0) + 1)] if dense else sorted(spellings.values())
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["bib"])
        writer.writerows((bib,) for bib in bibs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("truth", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dense", action="store_true")
    args = parser.parse_args()
    write_start_list(args.truth, args.output, args.dense)
