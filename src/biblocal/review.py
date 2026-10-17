import html
import math
from dataclasses import replace
from pathlib import Path

from PIL import Image

from .loader import LoadError, load_for_ocr
from .models import PhotoResult, Settings
from .startlist import StartList, normalize_bib


def apply_corrections(results: list[PhotoResult], corrections: dict[str, list[str]],
                      start_list: StartList | None) -> list[PhotoResult]:
    known = {result.file for result in results}
    if len(known) != len(results):
        raise ValueError('Duplicate photo filenames in results')
    unknown = corrections.keys() - known
    if unknown:
        raise ValueError(f'Correction file is not in results: {sorted(unknown)[0]}')
    output = []
    for result in results:
        if result.file not in corrections:
            output.append(result)
            continue
        bibs, names, seen = [], [], set()
        for number in corrections[result.file]:
            if not number or not number.isascii() or not number.isdigit():
                raise ValueError(f'Non-digit bib for {result.file}: {number!r}')
            runner = start_list.lookup(number) if start_list is not None else None
            if start_list is not None and runner is None:
                raise ValueError(f'Bib {number} for {result.file} is not in the start list')
            key = normalize_bib(number)
            if key not in seen:
                seen.add(key)
                bibs.append(runner.bib if runner else number)
                if runner and runner.name and runner.name not in names:
                    names.append(runner.name)
        output.append(replace(result, status='tagged' if bibs else 'none', bibs=bibs,
                              names=names, scores=[], suggestions=[], reasons=['manual']))
    return output


def _escape(value: str) -> str:
    return html.escape(value, quote=True).replace('http:', 'http&#58;').replace('https:', 'https&#58;')


def write_review_page(results: list[PhotoResult], photo_root: Path, out_dir: Path, settings: Settings,
                      statuses: frozenset[str] = frozenset({'review'})) -> Path:
    root = photo_root.resolve()
    selected = [result for result in results if result.status in statuses]
    paths = [(root / result.file).resolve() for result in selected]
    if any(not path.is_relative_to(root) for path in paths):
        raise ValueError('Review photo path is outside the photo folder')
    thumbs = out_dir / 'thumbs'
    protected = {(root / result.file).resolve() for result in results}
    targets = [thumbs / f'{index}{suffix}.jpg' for index in range(len(selected)) for suffix in ('', '_crop')]
    if any(target.resolve() in protected for target in targets):
        raise ValueError('A review thumbnail would overwrite a source photo')
    thumbs.mkdir(parents=True, exist_ok=True)
    cards = []
    for index, (result, photo) in enumerate(zip(selected, paths)):
        best = max(result.candidates, key=lambda item: item.score, default=None)
        guess = best.number if best else next(iter(result.suggestions), '')
        preview = '<p>Preview unavailable</p>'
        try:
            loaded = load_for_ocr(photo, settings.max_side).image
            thumbnail = loaded.copy()
            thumbnail.thumbnail((640, 640), Image.Resampling.LANCZOS)
            thumbnail.save(thumbs / f'{index}.jpg', quality=85)
            preview = f'<img class="photo" src="thumbs/{index}.jpg" alt="Photo to review">'
            if best and all(math.isfinite(value) for point in best.box for value in point):
                xs, ys = zip(*best.box)
                width, height = max(xs) - min(xs), max(ys) - min(ys)
                bounds = (max(0, math.floor(min(xs) - width / 2)), max(0, math.floor(min(ys) - height / 2)),
                          min(loaded.width, math.ceil(max(xs) + width / 2)),
                          min(loaded.height, math.ceil(max(ys) + height / 2)))
                if width > 0 and height > 0 and bounds[2] > bounds[0] and bounds[3] > bounds[1]:
                    crop = loaded.crop(bounds)
                    crop = crop.resize((max(1, round(crop.width * 160 / crop.height)), 160), Image.Resampling.LANCZOS)
                    crop.save(thumbs / f'{index}_crop.jpg', quality=90)
                    preview += f'<img class="crop" src="thumbs/{index}_crop.jpg" alt="Enlarged candidate bib">'
        except LoadError:
            pass
        candidates = ', '.join(f'{_escape(candidate.number)} ({candidate.score:.2f})' for candidate in result.candidates)
        suggestions = ''.join(f'<button type="button" class="suggestion" data-bib="{_escape(bib)}">{_escape(bib)}</button>'
                              for bib in result.suggestions)
        cards.append(f'''<article class="card" data-file="{_escape(result.file)}">
<h2>{_escape(result.file)}</h2><div class="images">{preview}</div>
<p>Candidates: {candidates or 'none'}</p><p class="reasons">{_escape(', '.join(result.reasons))}</p>
<div class="suggestions">{suggestions}</div>
<label for="bib-{index}">Bib numbers (separate with semicolons)</label>
<input class="bib-input" id="bib-{index}" value="{_escape(guess)}" inputmode="numeric" autocomplete="off">
<label class="none-label"><input type="checkbox" class="no-bib"> No bib</label>
<button type="button" class="confirm">Confirm &amp; next</button><p class="message" role="status"></p>
</article>''')
    body = '\n'.join(cards) if cards else '<p class="empty">No photos need review.</p>'
    page = out_dir / 'review.html'
    page.write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>BibLocal review</title><style>''' + _STYLE + '''</style></head><body>
<header><div><p class="eyebrow">BIBLOCAL · OFFLINE REVIEW</p><h1>Check the bibs.</h1>
<p>Confirm only what you can read. Unconfirmed cards are left out of the download.</p>
<p>Enter confirms a card and moves to the next. Downloading does not change photos.</p></div>
<div class="toolbar"><p id="progress" aria-live="polite"></p>
<button id="download" type="button" disabled>Download corrections.csv</button></div></header>
<main>''' + body + '</main><script>' + _SCRIPT + '</script></body></html>', encoding='utf-8')
    return page


_STYLE = '''
:root{font-family:Segoe UI,Arial,sans-serif;color:#172638;background:#f1f4f7;color-scheme:light}
*{box-sizing:border-box}body{margin:0}header,main{max-width:1100px;margin:auto;padding:24px}
header{display:flex;align-items:center;justify-content:space-between;gap:24px}h1{font-size:36px;margin:8px 0}
h2{font-size:18px;overflow-wrap:anywhere}.eyebrow{font-size:12px;font-weight:700;letter-spacing:2px}
p{line-height:1.5}.toolbar{min-width:240px}.card{background:white;border:2px solid #d7dfe8;border-radius:12px;padding:24px;margin-bottom:24px}
.card.confirmed{border-color:#26764d}.images{display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.photo{max-width:100%;max-height:460px;object-fit:contain}.crop{max-width:100%;object-fit:contain}
label{display:block;margin:14px 0 6px}.bib-input{display:block;width:min(100%,420px);padding:12px;border:1px solid #677889;border-radius:6px;font:inherit;font-size:20px}
button{background:#174a78;color:white;border:0;border-radius:6px;padding:12px 16px;font:inherit;cursor:pointer}
button:disabled{opacity:.5;cursor:default}.suggestion{background:#e8eff6;color:#174a78;margin:4px 6px 4px 0}
input:focus,button:focus{outline:3px solid #c28a18;outline-offset:3px}.none-label{margin:14px 0}.message{min-height:24px;margin-bottom:0}
.reasons{color:#526273}.confirmed .message{color:#24623d}.empty{padding:32px;background:white;border-radius:12px}
@media(max-width:700px){header{display:block}header,main{padding:16px}.card{padding:16px}}
'''

_SCRIPT = r'''
const cards = [...document.querySelectorAll('.card')];
const download = document.querySelector('#download');
function refresh() {
  const count = cards.filter(card => card.dataset.confirmed === 'yes').length;
  document.querySelector('#progress').textContent = count + ' of ' + cards.length + ' confirmed';
  download.disabled = count === 0;
}
function reset(card) {
  delete card.dataset.confirmed; card.classList.remove('confirmed');
  card.querySelector('.message').textContent = ''; refresh();
}
function confirm(card) {
  const noBib = card.querySelector('.no-bib').checked;
  const values = card.querySelector('.bib-input').value.trim().split(/[;,\u0020\t]+/).filter(Boolean);
  if (!noBib && (!values.length || values.some(value => !/^[0-9]+$/.test(value)))) {
    card.querySelector('.message').textContent = 'Enter digits only, or choose No bib.'; return;
  }
  card.dataset.bibs = noBib ? '' : [...new Set(values)].join(';');
  card.dataset.confirmed = 'yes'; card.classList.add('confirmed');
  card.querySelector('.message').textContent = noBib ? 'Confirmed: no bib.' : 'Confirmed.'; refresh();
  const following = cards.slice(cards.indexOf(card) + 1).find(item => item.dataset.confirmed !== 'yes');
  const next = following || cards.find(item => item.dataset.confirmed !== 'yes');
  if (next) { const input = next.querySelector('.bib-input'); input.focus(); next.scrollIntoView({block:'center'}); }
}
for (const card of cards) {
  const input = card.querySelector('.bib-input'), none = card.querySelector('.no-bib');
  input.addEventListener('input', () => reset(card));
  input.addEventListener('keydown', event => { if (event.key === 'Enter') { event.preventDefault(); confirm(card); } });
  none.addEventListener('change', () => { input.disabled = none.checked; reset(card); });
  card.querySelector('.confirm').addEventListener('click', () => confirm(card));
  for (const button of card.querySelectorAll('.suggestion')) button.addEventListener('click', () => {
    input.value = button.dataset.bib; input.disabled = false; none.checked = false; reset(card); input.focus();
  });
}
download.addEventListener('click', () => {
  const quote = value => '"' + value.replace(/"/g, '""') + '"';
  const rows = cards.filter(card => card.dataset.confirmed === 'yes')
    .map(card => [card.dataset.file, card.dataset.bibs].map(quote).join(','));
  const blob = new Blob(['\ufefffile,bibs\r\n' + rows.join('\r\n') + '\r\n'], {type:'text/csv;charset=utf-8'});
  const url = URL.createObjectURL(blob), link = document.createElement('a');
  link.href = url; link.download = 'corrections.csv'; document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
refresh();
'''
