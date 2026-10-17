import hashlib
import os
import re
import shutil
import string
import subprocess
import sys
import tempfile
import uuid
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path

from .models import PhotoResult


def find_exiftool(cli_value: str | None = None) -> Path | None:
    if cli_value is not None:
        path = Path(cli_value).resolve()
        return path if path.is_file() else None
    paths = []
    if os.environ.get("BIBLOCAL_EXIFTOOL"):
        paths.append(Path(os.environ["BIBLOCAL_EXIFTOOL"]))
    if getattr(sys, "frozen", False):
        paths.append(Path(sys.executable).parent / "exiftool/exiftool.exe")
    found = shutil.which("exiftool") or shutil.which("exiftool.exe")
    if found:
        paths.append(Path(found))
    return next((path.resolve() for path in paths if path.is_file()), None)


def _argument(value: str) -> str:
    if any(character in value for character in "\r\n\x00"):
        raise ValueError("ExifTool arguments cannot contain newline or NUL characters")
    return value


def keywords_for(result: PhotoResult, template: str = "{bib}", with_names: bool = False) -> tuple[list[str], list[str]]:
    if result.status != "tagged" or not result.bibs:
        return [], []
    fields = [(field, spec, conversion) for _, field, spec, conversion in string.Formatter().parse(template)
              if field is not None]
    if not fields or any(field != "bib" or spec or conversion for field, spec, conversion in fields):
        raise ValueError("keyword template must contain {bib}, without other fields or format specifications")
    flat, hierarchical = [], []
    for bib in result.bibs:
        if not bib or not bib.isascii() or not bib.isdigit():
            raise ValueError(f"Invalid bib for {result.file}: {bib!r}")
        flat.append(_argument(template.format(bib=bib)))
        hierarchical.append(f"Bib|{bib}")
    if with_names:
        flat.extend(_argument(name.strip()) for name in result.names if name.strip())
    return list(dict.fromkeys(flat)), list(dict.fromkeys(hierarchical))


def build_args(photo: Path, flat: list[str], hier: list[str], mode: str, backup: bool) -> list[str]:
    if mode not in {"embed", "sidecar"}:
        raise ValueError("write mode must be embed or sidecar")
    photo = photo.resolve()
    args = []
    tags = {"XMP-dc:Subject": flat, "XMP-lr:HierarchicalSubject": hier}
    if mode == "embed":
        # Recode separately: combining this copy with += retains old raw bytes.
        args.extend(["-tagsFromFile", "@", "-IPTC:all", "-IPTC:CodedCharacterSet=UTF8"])
        if not backup:
            args.append("-overwrite_original")
        args.extend([str(photo), "-execute", "-if", "$IPTC:CodedCharacterSet eq 'UTF8'"])
        tags["IPTC:Keywords"] = flat
        target, creating = photo, False
    else:
        target = photo.with_suffix(".xmp")
        creating = not target.exists()
        if creating:
            # -o interprets percent sequences as filename formatting commands.
            if "%" in str(target):
                raise ValueError("New sidecar paths containing percent signs are not supported")
            args.extend(["-o", str(target)])
            target = photo
    for tag, keywords in tags.items():
        for keyword in dict.fromkeys(keywords):
            args.extend([f"-{tag}-={keyword}", f"-{tag}+={keyword}"])
    # With -o, overwrite_original would DELETE the source JPEG after creation.
    if not backup and not creating:
        args.append("-overwrite_original")
    args.extend([str(target), "-execute"])
    return [_argument(arg) for arg in args]


@dataclass
class WriteReport:
    written: int
    skipped: int
    failed: list[tuple[str, str]]


def write_keywords(photo_root: Path, results: list[PhotoResult], mode: str, exiftool: Path,
                   backup: bool = True, batch_size: int = 500, *, template: str = "{bib}",
                   with_names: bool = False) -> WriteReport:
    if mode not in {"embed", "sidecar"} or batch_size < 1:
        raise ValueError("require embed/sidecar mode and positive batch size")
    root = photo_root.resolve()
    report, pending = WriteReport(0, 0, []), []
    for result in results:
        if result.status != "tagged" or not result.bibs:
            report.skipped += 1
            continue
        try:
            photo = (root / result.file).resolve()
            if not photo.is_relative_to(root):
                raise ValueError("Photo path escapes the photo folder")
            if not photo.is_file() or photo.suffix.lower() not in {".jpg", ".jpeg"}:
                raise ValueError("Photo is missing or is not a JPEG")
            if mode == "sidecar" and not photo.with_suffix(".xmp").resolve().is_relative_to(root):
                raise ValueError("Sidecar path escapes the photo folder")
            flat, hier = keywords_for(result, template, with_names)
            build_args(photo, flat, hier, mode, backup)  # Validate before staging.
            pending.append((result.file, photo, flat, hier))
        except (ValueError, OSError) as error:
            report.failed.append((result.file, str(error)))

    for offset in range(0, len(pending), batch_size):
        batch = pending[offset:offset + batch_size]
        # ExifTool may truncate IPTC with only a warning and exit 0. Stage embeds
        # beside the source folder; publish only after all commands are clean.
        context = tempfile.TemporaryDirectory(prefix=".biblocal-", dir=root) if mode == "embed" else nullcontext(None)
        with context as scratch:
            jobs, blocks = [], []
            for index, (file, photo, flat, hier) in enumerate(batch):
                try:
                    staged = Path(scratch) / f"{index}.jpg" if scratch else photo
                    fingerprint = None
                    if scratch:
                        shutil.copy2(photo, staged)
                        with staged.open("rb") as stream:
                            fingerprint = hashlib.file_digest(stream, "sha256").digest()
                    blocks.append(build_args(staged, flat, hier, mode, backup))
                    jobs.append((file, photo, staged, fingerprint))
                except (OSError, ValueError) as error:
                    report.failed.append((file, str(error)))
            for (file, photo, staged, fingerprint), reason in zip(jobs, _execute_batch(exiftool, blocks)):
                if reason:
                    if mode == "embed":
                        reason += "; source unchanged; consider --write sidecar"
                    report.failed.append((file, reason))
                    continue
                try:
                    if mode == "embed":
                        with photo.open("rb") as stream:
                            if hashlib.file_digest(stream, "sha256").digest() != fingerprint:
                                raise OSError("Photo changed during metadata processing; source preserved")
                        if backup:
                            _keep_backup(Path(str(staged) + "_original"), Path(str(photo) + "_original"))
                        os.replace(staged, photo)
                    report.written += 1
                except OSError as error:
                    report.failed.append((file, str(error)))
    return report


def _keep_backup(source: Path, target: Path) -> None:
    try:
        destination = target.open("xb")
    except FileExistsError:
        if not target.is_file():
            raise OSError(f"Backup path is not a file: {target}")
        return
    try:
        with destination, source.open("rb") as original:
            shutil.copyfileobj(original, destination)
        shutil.copystat(source, target)
    except OSError:
        target.unlink(missing_ok=True)
        raise


def _execute_batch(exiftool: Path, blocks: list[list[str]]) -> list[str | None]:
    if not blocks:
        return []
    prefix = "biblocal-" + uuid.uuid4().hex
    args, stages = [], {}
    for index, block in enumerate(blocks):
        stage = 0
        for argument in block:
            if argument == "-execute":
                marker = f"{prefix}:{index}:{stage}:${{status}}"
                args.extend(["-echo3", marker, "-echo4", marker, "-execute"])
                stage += 1
            else:
                args.append(argument)
        stages[index] = stage
    try:
        process = subprocess.run(
            [str(exiftool), "-@", "-", "-common_args", "-charset", "filename=utf8", "-charset", "UTF8"],
            input=("\n".join(args) + "\n").encode("utf-8"), capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            env={**os.environ, "LC_ALL": "C"},  # UTF-8 is explicit; C.UTF-8 is absent in Windows Perl.
        )
    except OSError as error:
        return [str(error)] * len(blocks)
    marker_re = re.compile(rf"^{prefix}:(\d+):(\d+):(\d+)$")
    statuses, errors, segment = {}, {}, []
    for line in process.stdout.decode("utf-8", errors="replace").splitlines():
        if match := marker_re.fullmatch(line):
            statuses[int(match[1]), int(match[2])] = int(match[3])
    for line in process.stderr.decode("utf-8", errors="replace").splitlines():
        if match := marker_re.fullmatch(line):
            if int(match[2]) == 0 and stages[int(match[1])] == 2:
                # A JPEG with no IPTC has nothing to recopy; the next stage's
                # charset condition still must succeed before publishing it.
                segment = [item for item in segment if not item.startswith("Warning: No writable tags set from ")]
            errors[int(match[1]), int(match[2])] = "\n".join(segment).strip()
            segment = []
        else:
            segment.append(line)
    outcomes = []
    for index in range(len(blocks)):
        reason = "\n".join(errors.get((index, stage), "") for stage in range(stages[index])).strip()
        clean = all(statuses.get((index, stage)) == 0 for stage in range(stages[index]))
        outcomes.append(None if clean and not reason else reason or
                        f"ExifTool did not confirm success (exit {process.returncode})")
    return outcomes
