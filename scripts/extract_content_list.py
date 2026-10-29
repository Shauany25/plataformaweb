"""Extrai a lista fornecida pelo grupo; requer pypdf somente nesta etapa editorial."""
import json
import re
import sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
HEADINGS = [
    ('MATEMÁTICA:', 'Matemática', 'matematica'), ('PORTUGUÊS', 'Português', 'linguagens'),
    ('Literatura:', 'Literatura', 'linguagens'), ('INGLÊS:', 'Inglês', 'linguagens'),
    ('ESPANHOL:', 'Espanhol', 'linguagens'), ('ARTES:', 'Artes', 'linguagens'),
    ('EDUCAÇÃO FÍSICA:', 'Educação Física', 'linguagens'), ('HISTÓRIA:', 'História', 'humanas'),
    ('GEOGRAFIA:', 'Geografia', 'humanas'), ('SOCIOLOGIA:', 'Sociologia', 'humanas'),
    ('FILOSOFIA:', 'Filosofia', 'humanas'), ('BIOLOGIA:', 'Biologia', 'natureza'),
    ('QUÍMICA:', 'Química', 'natureza'), ('FÍSICA:', 'Física', 'natureza'), ('REDAÇÃO:', 'Redação', 'linguagens'),
]

def main():
    from unicodedata import normalize
    def slug(s):
        return re.sub(r'[^a-z0-9]+', '-', normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip('-')
    text = ' '.join(' '.join(p.extract_text().split()) for p in PdfReader(sys.argv[1]).pages)
    subjects = []
    cursor = 0
    for index, (heading, name, area) in enumerate(HEADINGS):
        start = text.index(heading, cursor) + len(heading)
        end = text.index(HEADINGS[index + 1][0], start) if index + 1 < len(HEADINGS) else text.index('Referencias:', start)
        cursor = end
        block = text[start:end].replace('● https:', 'https:')
        topics = []
        for item in block.split('●'):
            item = item.strip()
            if not item:
                continue
            title = item.split('https:')[0].strip()
            if 'Vai ser um pdf' in title:
                title = title.split('Vai ser um pdf')[0].strip()
            title = title.replace('Pré- modernismo', 'Pré-modernismo')
            url = item[item.index('https:'):] if 'https:' in item else ''
            url = re.sub(r'\s+', '', url).split('&si=')[0].split('?si=')[0].replace('?feature=shared', '')
            topics.append({'slug': slug(name + '-' + title), 'name': title, 'video_url': url})
        subjects.append({'slug': slug(name), 'name': name, 'area': area, 'topics': topics})
    (ROOT / 'data').mkdir(exist_ok=True)
    (ROOT / 'data' / 'catalog.json').write_text(json.dumps(subjects, ensure_ascii=False, indent=2), encoding='utf-8')
    for subject in subjects:
        print(subject['name'] + ': ' + str(len(subject['topics'])))

if __name__ == '__main__':
    main()
