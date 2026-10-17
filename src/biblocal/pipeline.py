import os
import platform
from pathlib import Path
from time import perf_counter
from typing import Callable

from .bibs import decide, demote_frequent, extract_candidates
from .loader import LoadError, load_for_ocr
from .models import PhotoResult, Settings
from .ocr import OcrEngine
from .startlist import StartList


def list_photos(folder: Path) -> tuple[list[Path], int]:
    if not folder.is_dir():
        raise ValueError(f"Photo folder does not exist: {folder}")
    photos, skipped = [], 0
    for root, directories, files in os.walk(folder, followlinks=False):
        directories[:] = [name for name in directories if not name.lower().endswith("_biblocal")]
        for name in files:
            path = Path(root) / name
            if path.suffix.lower() in {".jpg", ".jpeg"}:
                photos.append(path)
            else:
                skipped += 1
    return sorted(photos, key=lambda p: p.relative_to(folder).as_posix()), skipped


def scan_folder(folder: Path, start_list: StartList | None, settings: Settings, engine: OcrEngine,
                on_progress: Callable[[int, int, PhotoResult], None] | None = None) -> list[PhotoResult]:
    photos, _ = list_photos(folder)
    results = []
    for index, path in enumerate(photos, 1):
        started = perf_counter()
        file = path.relative_to(folder).as_posix()
        try:
            loaded = load_for_ocr(path, settings.max_side)
            try:
                hits = engine.read(loaded.image)
                candidates = extract_candidates(hits, settings, start_list)
            finally:
                loaded.image.close()
            result = decide(file, candidates, start_list, settings, round((perf_counter() - started) * 1000))
        except LoadError:
            result = PhotoResult(file, "error", reasons=["decode_error"], ms=round((perf_counter() - started) * 1000))
        results.append(result)
        if on_progress is not None:
            on_progress(index, len(photos), result)
    return demote_frequent(results, start_list, settings)


def cpu_name() -> str:
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass
    return platform.processor() or platform.machine()
