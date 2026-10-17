from importlib.metadata import distribution
from pathlib import Path
import tomllib

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


ROOT = Path(__file__).resolve().parents[1]


def runtime_distributions():
    pending, found = ['rapidocr', 'onnxruntime', 'pillow'], {}
    while pending:
        item = distribution(pending.pop())
        key = canonicalize_name(item.metadata['Name'])
        if key in found:
            continue
        found[key] = item
        for value in item.requires or []:
            required = Requirement(value)
            if required.marker is None or required.marker.evaluate({'extra': ''}):
                pending.append(required.name)
    return found.values()


def test_models_inventory_covers_engine_files_and_hashes(engine):
    text = (ROOT / 'MODELS.md').read_text(encoding='utf-8')
    for model in engine.info['models']:
        assert model['file'] in text
        assert str(model['bytes']) in text
        assert model['sha256'] in text
    assert 'MODEL_LICENSES.md' in text and 'Apache-2.0' in text


def test_notices_cover_current_runtime_distributions():
    text = (ROOT / 'THIRD_PARTY_NOTICES.md').read_text(encoding='utf-8')
    for item in runtime_distributions():
        assert f'| {item.metadata["Name"]} | {item.version} |' in text
    assert 'https://github.com/certifi/python-certifi' in text


def test_notices_preserve_native_and_exception_license_texts():
    text = (ROOT / 'THIRD_PARTY_NOTICES.md').read_text(encoding='utf-8')
    sources = [
        ('opencv-python-headless', 'cv2/LICENSE-3RD-PARTY.txt'),
        ('shapely', 'shapely-2.2.0.dist-info/licenses/LICENSE_GEOS'),
        ('numpy', 'numpy-2.5.4.dist-info/licenses/LICENSE.txt'),
        ('onnxruntime', 'onnxruntime/ThirdPartyNotices.txt'),
        ('certifi', 'certifi-2026.7.22.dist-info/licenses/LICENSE'),
        ('tqdm', 'tqdm-4.70.1.dist-info/licenses/LICENCE'),
    ]
    for package, relative in sources:
        original = distribution(package).locate_file(relative).read_text(encoding='utf-8').strip()
        assert original in text, relative
    assert 'Mozilla Public License Version 2.0' in text
    assert 'GCC-exception-3.1' in text and 'LGPL-2.1' in text


def test_project_license_and_package_metadata():
    text = (ROOT / 'LICENSE').read_text(encoding='utf-8')
    assert text.startswith('MIT License') and 'Copyright (c) 2026 Amit Sahoo' in text
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']
    assert project['license'] == 'MIT'
    assert {'LICENSE', 'THIRD_PARTY_NOTICES.md', 'MODELS.md'} <= set(project['license-files'])


def test_readme_has_install_and_all_commands_without_placeholders():
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert 'pip install .' in text
    assert all('biblocal ' + command in text for command in ('scan', 'apply', 'eval', 'bench'))
    assert 'untested' in text.lower()
    assert not any(value in text for value in ('TODO', '<user>', 'your-username', '<PASS/FAIL>'))
