import re
from collections import Counter
from dataclasses import replace

from .models import Candidate, PhotoResult, Settings, TextHit
from .startlist import StartList, normalize_bib

_MAP = str.maketrans({"O": "0", "o": "0", "I": "1", "l": "1", "|": "1",
                     "S": "5", "s": "5", "B": "8", "Z": "2", "z": "2"})


def extract_candidates(hits: list[TextHit], settings: Settings, start_list: StartList | None = None) -> list[Candidate]:
    minimum, maximum = ((start_list.min_len, start_list.max_len) if start_list is not None
                        else (settings.min_len, settings.max_len))
    found = {}
    for hit in hits:
        for token in hit.text.split():
            if ":" in token or "." in token or token.upper().endswith(("K", "KM")):
                continue
            mapped_token = token.translate(_MAP) if sum(c in "0123456789" for c in token) * 2 >= len(token) else token
            mapped = mapped_token != token
            score = hit.score * .9 if mapped else hit.score
            for number in re.findall(r"[0-9]+", mapped_token):
                key = normalize_bib(number)
                length = len(key) if start_list is not None else len(number)
                if minimum <= length <= maximum and (key not in found or score > found[key].score):
                    found[key] = Candidate(number, score, hit.box, mapped)
    return sorted(found.values(), key=lambda candidate: (-candidate.score, candidate.number))


def near_matches(number: str, start_list: StartList, limit: int = 3) -> list[str]:
    number = normalize_bib(number)
    # Enumerate edit-distance-one strings; membership lookup is constant time
    # even for the 90,135-entry evaluation list.
    variants = set()
    for i in range(len(number)):
        variants.add(number[:i] + number[i + 1:])
        variants.update(number[:i] + digit + number[i + 1:] for digit in "0123456789")
    for i in range(len(number) + 1):
        variants.update(number[:i] + digit + number[i:] for digit in "0123456789")
    matches = {}
    for variant in variants:
        if not variant or normalize_bib(variant) != variant or variant == number:
            continue
        runner = start_list.lookup(variant)
        if runner is not None:
            matches[variant] = runner.bib
    ordered = sorted(matches, key=lambda bib: (len(bib) != len(number), bib))
    return [matches[bib] for bib in ordered[:limit]]


def decide(file: str, candidates: list[Candidate], start_list: StartList | None, settings: Settings, ms: int = 0) -> PhotoResult:
    accepted = [c for c in candidates if c.score >= settings.accept
                and (start_list is None or c.number in start_list)]
    if accepted:
        runners = [start_list.lookup(c.number) for c in accepted] if start_list is not None else []
        return PhotoResult(
            file, "tagged", [r.bib for r in runners] if runners else [c.number for c in accepted],
            [c.score for c in accepted], [r.name for r in runners], candidates=candidates,
            reasons=["mapped_chars"] if any(c.mapped for c in accepted) else [], ms=ms,
        )
    review = [c for c in candidates if c.score >= settings.review]
    reasons, suggestions = [], []
    for candidate in review:
        if candidate.score < settings.accept and "low_confidence" not in reasons:
            reasons.append("low_confidence")
        if start_list is not None and candidate.number not in start_list:
            if "not_in_start_list" not in reasons:
                reasons.append("not_in_start_list")
            for suggestion in near_matches(candidate.number, start_list):
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
        if candidate.mapped and "mapped_chars" not in reasons:
            reasons.append("mapped_chars")
    return PhotoResult(file, "review" if review else "none", candidates=candidates,
                       suggestions=suggestions[:3], reasons=reasons, ms=ms)


def demote_frequent(results: list[PhotoResult], start_list: StartList | None, settings: Settings) -> list[PhotoResult]:
    counts = Counter(bib for r in results if r.status == "tagged" for bib in {normalize_bib(b) for b in r.bibs})
    frequent = {bib for bib, count in counts.items()
                if len(results) >= settings.frequent_min_photos and count / len(results) > settings.frequent_share
                and (start_list is None or bib not in start_list)}
    output = []
    for result in results:
        keep = [i for i, bib in enumerate(result.bibs) if normalize_bib(bib) not in frequent]
        changed = result.status == "tagged" and len(keep) != len(result.bibs)
        output.append(replace(
            result, bibs=[result.bibs[i] for i in keep],
            scores=[result.scores[i] for i in keep if i < len(result.scores)],
            names=[result.names[i] for i in keep if i < len(result.names)],
            status="review" if changed and not keep else result.status,
            reasons=list(dict.fromkeys(result.reasons + (["frequent_number"] if changed else []))),
            candidates=list(result.candidates), suggestions=list(result.suggestions),
        ))
    return output
