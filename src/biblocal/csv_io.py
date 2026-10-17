import csv
from pathlib import Path

from .models import Candidate, PhotoResult

_FIELDS = ["file", "status", "bibs", "scores", "names", "candidates", "suggestions", "reasons", "ms"]
_ZERO_BOX = ((0., 0.),) * 4


def write_results_csv(results: list[PhotoResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow({
                "file": result.file, "status": result.status, "bibs": ";".join(result.bibs),
                "scores": ";".join(f"{score:.2f}" for score in result.scores),
                "names": ";".join(result.names),
                "candidates": ";".join(f"{c.number}:{c.score:.6g}" for c in result.candidates),
                "suggestions": ";".join(result.suggestions), "reasons": ";".join(result.reasons), "ms": result.ms,
            })


def read_results_csv(path: Path) -> list[PhotoResult]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(_FIELDS).issubset(reader.fieldnames or []):
            raise ValueError("results CSV is missing required columns")
        output = []
        for row in reader:
            split = lambda key: row[key].split(";") if row[key] else []
            candidates = [Candidate(number, float(score), _ZERO_BOX)
                          for number, score in (item.rsplit(":", 1) for item in split("candidates"))]
            output.append(PhotoResult(row["file"], row["status"], split("bibs"),
                                      [float(s) for s in split("scores")], split("names"), candidates,
                                      split("suggestions"), split("reasons"), int(row["ms"])))
    return output


def read_bib_table(path: Path) -> dict[str, list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"file", "bibs"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires file,bibs columns")
        output = {}
        for row in reader:
            file = row["file"]
            if not file or file in output:
                raise ValueError(f"missing or duplicate file: {file!r}")
            bibs = [value.strip() for value in (row["bibs"] or "").split(";") if value.strip()]
            if any(not bib.isascii() or not bib.isdigit() for bib in bibs):
                raise ValueError(f"non-digit bib for {file}")
            output[file] = bibs
    return output
