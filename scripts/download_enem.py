"""Download de dados públicos; a aplicação usa apenas o catálogo revisado local."""
import json
import time
from pathlib import Path
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.cache' / 'enem'

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    for year in range(2023, 2008, -1):
        target = CACHE / f'{year}.json'
        if target.exists():
            continue
        questions = []
        for offset in range(0, 200, 50):
            url = f'https://api.enem.dev/v1/exams/{year}/questions?limit=50&offset={offset}'
            for retry in range(4):
                try:
                    with urlopen(Request(url, headers={'User-Agent': 'TrilhaDeEstudos/1.0'}), timeout=35) as response:
                        data = json.load(response)
                    break
                except Exception:
                    if retry == 3:
                        raise
                    time.sleep(2 + retry * 3)
            batch = data['questions']
            questions.extend(batch)
            time.sleep(0.7)
            if len(batch) < 50:
                break
        target.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'{year}: {len(questions)} questões', flush=True)

if __name__ == '__main__':
    main()
