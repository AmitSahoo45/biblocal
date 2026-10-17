import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Runner:
    bib: str
    name: str = ""
    category: str = ""


def normalize_bib(number: str) -> str:
    return number.lstrip("0") or "0"


class StartList:
    def __init__(self, runners: list[Runner]):
        self._runners = {}
        for runner in runners:
            if not runner.bib.isascii() or not runner.bib.isdigit():
                raise ValueError(f"invalid bib {runner.bib!r}")
            key = normalize_bib(runner.bib)
            if key in self._runners:
                raise ValueError(f"duplicate bib {runner.bib}")
            self._runners[key] = runner
        lengths = [len(bib) for bib in self._runners]
        self.min_len = min(lengths, default=1)
        self.max_len = max(lengths, default=5)

    def lookup(self, number: str) -> Runner | None:
        return self._runners.get(normalize_bib(number))

    def __contains__(self, number: str) -> bool:
        return self.lookup(number) is not None

    def __len__(self) -> int:
        return len(self._runners)

    @property
    def bibs(self) -> list[str]:
        return sorted(runner.bib for runner in self._runners.values())


def load_start_list(path: Path) -> StartList:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        sample = stream.read(8192)
        stream.seek(0)
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
        except csv.Error:
            header = sample.splitlines()[0] if sample else ""
            delimiter = ";" if ";" in header else "\t" if "\t" in header else ","
        rows = csv.reader(stream, delimiter=delimiter)
        header = [value.strip().lower() for value in next(rows, [])]
        key = "bib" if "bib" in header else "number"
        if key not in header:
            raise ValueError("start list requires a bib or number column")
        runners = []
        for row_number, row in enumerate(rows, 2):
            if not any(value.strip() for value in row):
                continue
            values = dict(zip(header, (value.strip() for value in row)))
            bib = values.get(key, "")
            if not bib.isascii() or not bib.isdigit():
                raise ValueError(f"invalid bib at row {row_number}: {bib!r}")
            runners.append(Runner(bib, values.get("name", ""), values.get("category", "")))
    return StartList(runners)
