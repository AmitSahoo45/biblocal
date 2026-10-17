from html.parser import HTMLParser
import csv
import html
import io
import json
import os
from pathlib import Path
import re
import subprocess

import pytest
from PIL import Image, ImageDraw

from biblocal.models import Candidate, PhotoResult, Settings
from biblocal.review import write_review_page
from tests.fixtures.make_bibs import make_bib_image


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


def test_page_has_local_previews_padded_crop_and_review_content(tmp_path):
    root = tmp_path / 'race'
    root.mkdir()
    image = Image.new('RGB', (1600, 1000), 'white')
    ImageDraw.Draw(image).rectangle((100, 200, 300, 300), fill='blue')
    image.save(root / 'a.jpg')
    before = (root / 'a.jpg').read_bytes()
    box = ((100, 200), (300, 200), (300, 300), (100, 300))
    rows = [PhotoResult('a.jpg', 'review', candidates=[Candidate('247', .7, box)],
                        suggestions=['247', '241'], reasons=['low_confidence']),
            PhotoResult('accepted.jpg', 'tagged', ['88'])]
    page = write_review_page(rows, root, tmp_path / 'out', Settings())
    text = page.read_text(encoding='utf-8')
    assert 'a.jpg' in text and 'accepted.jpg' not in text
    assert '0.70' in text and 'low_confidence' in text
    assert 'http://' not in text and 'https://' not in text
    elements = Elements(text).elements
    images = [attrs['src'] for tag, attrs in elements if tag == 'img']
    assert images == ['thumbs/0.jpg', 'thumbs/0_crop.jpg']
    with Image.open(page.parent / images[0]) as thumb:
        assert thumb.size == (640, 400)
    with Image.open(page.parent / images[1]) as crop:
        assert crop.size == (320, 160)
        assert crop.getpixel((160, 80))[2] > 200
    assert (root / 'a.jpg').read_bytes() == before


def test_page_escapes_file_and_candidate_text(tmp_path):
    file = "Tom & Jerry's.jpg"
    make_bib_image(tmp_path / file, '247')
    row = PhotoResult(file, 'review', suggestions=['<script>alert(1)</script>'])
    page = write_review_page([row], tmp_path, tmp_path / 'out', Settings())
    text = page.read_text(encoding='utf-8')
    assert 'Tom &amp; Jerry&#x27;s.jpg' in text and "Jerry's" not in text
    assert '<script>alert(1)</script>' not in text
    assert any(attrs.get('data-file') == file for tag, attrs in Elements(text).elements)


def test_page_handles_orientation_missing_preview_and_empty_queue(tmp_path):
    make_bib_image(tmp_path / 'portrait-stored.jpg', '247', exif_orientation=6)
    page = write_review_page([PhotoResult('portrait-stored.jpg', 'review'), PhotoResult('missing.jpg', 'review')],
                             tmp_path, tmp_path / 'out', Settings())
    with Image.open(page.parent / 'thumbs/0.jpg') as image:
        assert image.width == 640 and image.height == 427
    assert 'Preview unavailable' in page.read_text(encoding='utf-8')
    empty = write_review_page([], tmp_path, tmp_path / 'empty', Settings())
    assert 'No photos need review' in empty.read_text(encoding='utf-8')


def test_page_rejects_photo_path_outside_root(tmp_path):
    root = tmp_path / 'race'
    root.mkdir()
    with pytest.raises(ValueError, match='outside'):
        write_review_page([PhotoResult('../private.jpg', 'review')], root, tmp_path / 'out', Settings())


def test_page_never_overwrites_an_original_with_a_thumbnail(tmp_path):
    original = make_bib_image(tmp_path / 'thumbs/0.jpg', '88')
    make_bib_image(tmp_path / 'a.jpg', '247')
    before = original.read_bytes()
    rows = [PhotoResult('a.jpg', 'review'), PhotoResult('thumbs/0.jpg', 'tagged', ['88'])]
    with pytest.raises(ValueError, match='source'):
        write_review_page(rows, tmp_path, tmp_path, Settings())
    assert original.read_bytes() == before


def test_browser_confirms_cards_and_exports_only_reviewed_rows(tmp_path):
    browser = Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')
    if not browser.exists():
        pytest.skip('local Edge is unavailable for the offline browser test')
    files = ['a,quoted.jpg', 'b.jpg', 'untouched.jpg']
    for file in files:
        make_bib_image(tmp_path / file, '247')
    page = write_review_page([PhotoResult(file, 'review', suggestions=['247']) for file in files],
                             tmp_path, tmp_path / 'out', Settings())
    probe = r'''<script>
    (async () => {
      let downloaded;
      URL.createObjectURL = blob => { downloaded = blob; return 'blob:captured'; };
      HTMLAnchorElement.prototype.click = function () {};
      const cards = [...document.querySelectorAll('.card')];
      const first = cards[0].querySelector('.bib-input');
      first.value = '007;88'; first.dispatchEvent(new Event('input', {bubbles:true}));
      first.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
      const moved = document.activeElement === cards[1].querySelector('.bib-input');
      const none = cards[1].querySelector('.no-bib');
      none.checked = true; none.dispatchEvent(new Event('change', {bubbles:true}));
      cards[1].querySelector('.confirm').click();
      document.querySelector('#download').click();
      const result = document.createElement('pre'); result.id = 'browser-result';
      result.textContent = JSON.stringify({moved, csv: await downloaded.text(),
        loadedImages: [...document.images].every(image => image.complete && image.naturalWidth > 0)});
      document.body.append(result);
    })().catch(error => { const node=document.createElement('pre');node.id='browser-result';
      node.textContent=JSON.stringify({error:String(error)});document.body.append(node); });
    </script>'''
    page.write_text(page.read_text(encoding='utf-8').replace('</body>', probe + '</body>'), encoding='utf-8')
    command = [str(browser), '--headless=new', '--disable-gpu', '--no-first-run',
               '--disable-background-networking', '--disable-crash-reporter', '--disable-breakpad',
               f'--user-data-dir={tmp_path / "browser-profile"}', f'--disk-cache-dir={tmp_path / "browser-cache"}',
               '--allow-file-access-from-files', '--dump-dom', '--virtual-time-budget=3000', page.as_uri()]
    result = subprocess.run(command, capture_output=True, encoding='utf-8', timeout=45,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                            env={**os.environ, 'TEMP': str(tmp_path), 'TMP': str(tmp_path)})
    match = re.search(r'<pre id="browser-result">(.*?)</pre>', result.stdout, re.S)
    assert match, result.stderr[-1500:]
    evidence = json.loads(html.unescape(match[1]))
    assert evidence.get('moved') and evidence.get('loadedImages'), evidence
    rows = list(csv.DictReader(io.StringIO(evidence['csv'].lstrip('\ufeff'))))
    assert rows == [{'file': 'a,quoted.jpg', 'bibs': '007;88'}, {'file': 'b.jpg', 'bibs': ''}]
