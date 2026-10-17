from dataclasses import dataclass, field

Box = tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]


@dataclass(frozen=True)
class TextHit:
    text: str
    score: float
    box: Box


@dataclass(frozen=True)
class Candidate:
    number: str
    score: float
    box: Box
    mapped: bool = False


@dataclass
class PhotoResult:
    file: str
    status: str
    bibs: list[str] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    ms: int = 0


@dataclass(frozen=True)
class Settings:
    accept: float = 0.80
    review: float = 0.50
    min_len: int = 1
    max_len: int = 5
    max_side: int = 2048
    frequent_share: float = 0.25
    frequent_min_photos: int = 20
