from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps


@dataclass(frozen=True)
class LoadedImage:
    image: Image.Image
    scale: float
    original_size: tuple[int, int]


class LoadError(Exception):
    pass


def load_for_ocr(path: Path, max_side: int) -> LoadedImage:
    if max_side < 1:
        raise ValueError("max_side must be positive")
    try:
        with Image.open(path) as image:
            original_size = image.size
            orientation = image.getexif().get(274, 1)
            ratio = min(1., max_side / max(original_size))
            target = tuple(max(1, round(dimension * ratio)) for dimension in original_size)
            if image.format == "JPEG":
                image.draft("RGB", target)
            upright = ImageOps.exif_transpose(image)
            upright.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
            rgb = upright.convert("RGB")
            if orientation in (5, 6, 7, 8):
                original_size = original_size[::-1]
            return LoadedImage(rgb, max(rgb.size) / max(original_size), original_size)
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as error:
        raise LoadError(path, str(error)) from error
