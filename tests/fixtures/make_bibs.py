"""Deterministic synthetic photos; no real people or external fonts."""

import csv
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def make_bib_image(
    path: Path, number: str, *, size: tuple[int, int] = (1600, 1067),
    bib_width: int = 300, angle: float = 0.0, distractor: str | None = None,
    exif_orientation: int | None = None, seed: int = 0,
) -> Path:
    rng = random.Random(seed)
    image = Image.frombytes("L", size, rng.randbytes(size[0] * size[1]))
    image = image.point(lambda value: 110 + value // 8).convert("RGB")
    height = int(bib_width * .65)
    layer = Image.new("RGBA", (bib_width, height))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle((0, 0, bib_width - 1, height - 1), radius=bib_width // 16, fill="white")
    font_size = int(bib_width * .45)
    font = ImageFont.load_default(size=font_size)
    while draw.textbbox((0, 0), number, font=font)[2] > bib_width * .9:
        font_size -= 1
        font = ImageFont.load_default(size=font_size)
    left, top, right, bottom = draw.textbbox((0, 0), number, font=font)
    draw.text(((bib_width - right - left) / 2, (height - bottom - top) / 2), number, font=font, fill="black")
    if angle:
        layer = layer.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    x = rng.randint(0, max(0, size[0] - layer.width))
    y = rng.randint(size[1] // 3, max(size[1] // 3, size[1] - layer.height))
    image.paste(layer, (x, y), layer)
    if distractor:
        ImageDraw.Draw(image).text((20, 20), distractor, fill="black", font=ImageFont.load_default(size=40))
    exif = Image.Exif()
    if exif_orientation is not None:
        inverse = {
            2: Image.Transpose.FLIP_LEFT_RIGHT, 3: Image.Transpose.ROTATE_180,
            4: Image.Transpose.FLIP_TOP_BOTTOM, 5: Image.Transpose.TRANSPOSE,
            6: Image.Transpose.ROTATE_90, 7: Image.Transpose.TRANSVERSE,
            8: Image.Transpose.ROTATE_270,
        }
        if exif_orientation not in range(1, 9):
            raise ValueError("EXIF orientation must be 1 through 8")
        if exif_orientation in inverse:
            image = image.transpose(inverse[exif_orientation])
        exif[274] = exif_orientation
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "JPEG", quality=90, exif=exif)
    return path


def make_bib_folder(folder: Path, numbers: list[str], **kwargs) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "truth.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["file", "bibs"])
        for index, number in enumerate(numbers):
            path = make_bib_image(folder / f"bib_{index}.jpg", number, **kwargs)
            writer.writerow([path.name, number])
    return folder
