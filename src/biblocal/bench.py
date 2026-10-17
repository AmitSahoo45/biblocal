import math
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

from .loader import LoadError, load_for_ocr
from .models import Settings
from .ocr import OcrEngine
from .pipeline import cpu_name, list_photos


@dataclass
class BenchReport:
    photos: int
    workers: int
    median_ms: float
    p90_ms: float
    effective_s_per_photo: float
    minutes_per_1000: float
    cpu: str
    settings: dict


def bench(folder: Path, settings: Settings, limit: int = 100) -> BenchReport:
    if limit < 1:
        raise ValueError("limit must be positive")
    photos = list_photos(folder)[0][:limit]
    if not photos:
        raise ValueError(f"No JPEGs to benchmark in {folder}")
    started = perf_counter()
    engine = OcrEngine(max_side=settings.max_side)
    times = []
    for path in photos:
        photo_start = perf_counter()
        try:
            loaded = load_for_ocr(path, settings.max_side)
        except LoadError as error:
            raise ValueError(f"Cannot benchmark undecodable photo: {path}") from error
        try:
            engine.read(loaded.image)
        finally:
            loaded.image.close()
        times.append((perf_counter() - photo_start) * 1000)
    effective = (perf_counter() - started) / len(photos)
    return BenchReport(len(photos), 1, statistics.median(times), sorted(times)[math.ceil(.9 * len(times)) - 1],
                       effective, effective * 1000 / 60, cpu_name(), asdict(settings))


def k2_verdict(seconds: float) -> str:
    return "PASS" if seconds <= 2. else "SLOW" if seconds <= 5. else "KILL"
