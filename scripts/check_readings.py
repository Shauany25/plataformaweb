import concurrent.futures
import html
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data.editorial import NOTES

def check(item):
    slug, path = item
    url = 'https://www.todamateria.com.br/' + path + '/'
    try:
        with urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=20) as response:
            body = response.read().decode('utf-8', 'replace')
            title = re.search(r'<title>(.*?)</title>', body, re.S)
            title = html.unescape(title.group(1)).replace(' - Toda Matéria', '').strip() if title else ''
            if not title or 'não encontrad' in title.lower() or 'Just a moment' in title:
                return slug, {'status': 'unverified', 'url': url}
            return slug, {'status': 'available', 'url': response.url, 'title': title}
    except Exception as error:
        return slug, {'status': 'unverified', 'url': url, 'error': str(error)}

catalog = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
items = [(t['slug'], note[1]) for s in catalog for t, note in zip(s['topics'], NOTES[s['slug']])]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = dict(pool.map(check, items))
(ROOT / 'data/reading_checks.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print('Materiais confirmados:', sum(v['status'] == 'available' for v in results.values()))
