import json
from pathlib import Path

import pytest

from biblocal.cli import main
from biblocal.csv_io import read_results_csv, write_results_csv
from biblocal.models import PhotoResult
from biblocal.review import apply_corrections
from biblocal.startlist import Runner, StartList
from tests.fixtures.make_bibs import make_bib_image
from tests.test_exif import exiftool, metadata, values


def test_apply_manual_tags_and_none_without_mutating_inputs():
    rows = [PhotoResult('a.jpg', 'review', suggestions=['88']),
            PhotoResult('b.jpg', 'tagged', ['99'], scores=[.95], names=['Old']),
            PhotoResult('c.jpg', 'tagged', ['12'])]
    result = apply_corrections(rows, {'a.jpg': ['247'], 'b.jpg': []}, None)
    assert [(r.status, r.bibs, r.reasons) for r in result] == [
        ('tagged', ['247'], ['manual']), ('none', [], ['manual']), ('tagged', ['12'], [])]
    assert result[0].suggestions == [] and result[0].scores == []
    assert result[1].names == [] and result[1].scores == []
    assert rows[0].status == 'review' and rows[1].bibs == ['99']


def test_apply_uses_start_list_spelling_names_and_dedupes():
    result = apply_corrections([PhotoResult('a.jpg', 'review')], {'a.jpg': ['7', '007', '88']},
                               StartList([Runner('007', 'Jo'), Runner('88', 'Ana')]))
    assert result[0].bibs == ['007', '88'] and result[0].names == ['Jo', 'Ana']


@pytest.mark.parametrize('bib', ['2A7', '１２３', '', '-1', '2.7'])
def test_apply_rejects_non_ascii_digits(bib):
    with pytest.raises(ValueError, match='a.jpg'):
        apply_corrections([PhotoResult('a.jpg', 'review')], {'a.jpg': [bib]}, None)


def test_apply_rejects_unknown_file_and_nonmember_bib():
    with pytest.raises(ValueError, match='missing.jpg'):
        apply_corrections([], {'missing.jpg': ['247']}, None)
    with pytest.raises(ValueError, match='a.jpg'):
        apply_corrections([PhotoResult('a.jpg', 'review')], {'a.jpg': ['99']}, StartList([Runner('88')]))


def prepare_apply(tmp_path):
    root, out = tmp_path / 'race', tmp_path / 'race_biblocal'
    for name in ['a.jpg', 'b.jpg', 'c.jpg']:
        make_bib_image(root / name, '247')
    rows = [PhotoResult('a.jpg', 'review'), PhotoResult('b.jpg', 'review'), PhotoResult('c.jpg', 'tagged', ['88'])]
    write_results_csv(rows, out / 'results.csv')
    (out / 'run.json').write_text(json.dumps({'photo_root': str(root)}), encoding='utf-8')
    corrections = out / 'corrections.csv'
    corrections.write_text('file,bibs\na.jpg,247\nb.jpg,\n', encoding='utf-8-sig')
    return root, out, corrections


def test_cli_apply_default_preserves_photos_and_original_results(tmp_path):
    root, out, corrections = prepare_apply(tmp_path)
    before = {p.name: p.read_bytes() for p in root.iterdir()}
    original = (out / 'results.csv').read_bytes()
    # Preview-only apply works even when the photos/run manifest are unavailable.
    (out / 'run.json').unlink()
    assert main(['apply', str(corrections), '--results', str(out / 'results.csv')]) == 0
    result = read_results_csv(out / 'results_final.csv')
    assert [(r.status, r.bibs) for r in result] == [('tagged', ['247']), ('none', []), ('tagged', ['88'])]
    assert (out / 'results.csv').read_bytes() == original
    assert {p.name: p.read_bytes() for p in root.iterdir()} == before


@pytest.mark.exiftool
def test_cli_apply_writes_corrected_files_only(tmp_path, exiftool):
    root, out, corrections = prepare_apply(tmp_path)
    before = {p.name: p.read_bytes() for p in root.iterdir()}
    assert main(['apply', str(corrections), '--results', str(out / 'results.csv'),
                 '--write', 'embed', '--exiftool', str(exiftool)]) == 0
    assert values(metadata(exiftool, root / 'a.jpg'), 'XMP-dc:Subject') == ['247']
    assert (root / 'a.jpg_original').read_bytes() == before['a.jpg']
    assert (root / 'b.jpg').read_bytes() == before['b.jpg']
    assert (root / 'c.jpg').read_bytes() == before['c.jpg']


def test_cli_apply_invalid_correction_writes_nothing(tmp_path, capsys):
    root, out, corrections = prepare_apply(tmp_path)
    corrections.write_text('file,bibs\na.jpg,247\nmissing.jpg,88\n', encoding='utf-8')
    assert main(['apply', str(corrections), '--results', str(out / 'results.csv')]) == 2
    assert 'missing.jpg' in capsys.readouterr().err
    assert not (out / 'results_final.csv').exists()


def test_cli_apply_missing_manifest_for_write_fails_before_output(tmp_path, exiftool, capsys):
    root, out, corrections = prepare_apply(tmp_path)
    (out / 'run.json').unlink()
    assert main(['apply', str(corrections), '--results', str(out / 'results.csv'),
                 '--write', 'sidecar', '--exiftool', str(exiftool)]) == 2
    assert 'run.json' in capsys.readouterr().err
    assert not (out / 'results_final.csv').exists()
