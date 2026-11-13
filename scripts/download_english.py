import json
import time
from pathlib import Path
from urllib.request import urlopen
ROOT = Path(__file__).resolve().parent.parent

for year in range(2023, 2009, -1):
    target = ROOT / '.cache/enem' / f'{year}-english.json'
    if target.exists():
        continue
    with urlopen(f'https://api.enem.dev/v1/exams/{year}/questions?language=ingles&limit=50', timeout=30) as response:
        data = json.load(response)
    questions = [q for q in data['questions'] if q.get('language') == 'ingles']
    target.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding='utf-8')
    print(year, len(questions), flush=True)
    time.sleep(1)
