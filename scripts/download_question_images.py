"""Armazena localmente as imagens usadas pelas questões selecionadas."""
import concurrent.futures
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'assets/exam'

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    data = json.loads((ROOT / 'data/questions.json').read_text(encoding='utf-8'))
    urls = set()
    for question in data.values():
        urls.update(re.findall(r'!\[[^\]]*\]\((https://[^\s)]+)\)', (question.get('context') or '') + '\n' + question.get('alternativesIntroduction', '')))
        for alt in question['alternatives']:
            if alt.get('file'):
                urls.add(alt['file'])
    def download(url):
        parsed = urlsplit(url)
        if parsed.hostname not in {'enem.dev', 'api.enem.dev', 'raw.githubusercontent.com'}:
            return url, {'status': 'unverified'}
        suffix = Path(parsed.path).suffix.lower()
        if suffix not in {'.jpg', '.jpeg', '.png', '.webp'}:
            return url, {'status': 'unverified'}
        name = hashlib.sha256(url.encode()).hexdigest()[:24] + suffix
        target = DEST / name
        try:
            if not target.exists():
                with urlopen(Request(url, headers={'User-Agent':'TrilhaDeEstudos/1.0'}), timeout=25) as response:
                    if not response.headers.get('Content-Type', '').startswith('image/'):
                        raise ValueError('Resposta não é imagem')
                    target.write_bytes(response.read())
            return url, {'status': 'available', 'local': '/assets/exam/' + name}
        except Exception as error:
            return url, {'status': 'unverified', 'error': str(error)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        result = dict(pool.map(download, sorted(urls)))
    (ROOT / 'data/image_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Imagens:', len(urls), 'disponíveis:', sum(v['status'] == 'available' for v in result.values()), flush=True)

if __name__ == '__main__':
    main()
