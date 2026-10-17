import warnings
from dataclasses import dataclass

from .models import PhotoResult
from .startlist import normalize_bib


@dataclass
class EvalReport:
    photos: int
    readable: int
    hit_rate: float
    wrong_rate: float
    review_rate: float
    none_rate: float
    misses: list[str]
    wrong: list[tuple[str, str]]


def evaluate(results: list[PhotoResult], truth: dict[str, list[str]]) -> EvalReport:
    known = [result for result in results if result.file in truth]
    if len(known) != len(results):
        warnings.warn(f"{len(results) - len(known)} photos missing from truth were ignored", stacklevel=2)
    readable = hits = accepted = 0
    misses, wrong = [], []
    for result in known:
        expected = {normalize_bib(bib) for bib in truth[result.file]}
        tags = {normalize_bib(bib) for bib in result.bibs} if result.status == "tagged" else set()
        readable += bool(expected)
        hits += bool(expected & tags)
        if expected and not expected & tags:
            misses.append(result.file)
        accepted += len(tags)
        wrong.extend((result.file, bib) for bib in sorted(tags - expected))
    n = len(known)
    return EvalReport(n, readable, hits / readable if readable else 0., len(wrong) / accepted if accepted else 0.,
                      sum(r.status == "review" for r in known) / n if n else 0.,
                      sum(r.status == "none" for r in known) / n if n else 0., misses, wrong)


def k1_verdict(report: EvalReport) -> str:
    if report.hit_rate < .5:
        return "KILL"
    return "PASS" if report.hit_rate >= .7 and report.wrong_rate < .03 else "WEAK"
