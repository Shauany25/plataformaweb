"""Confere as letras do acervo contra PDFs oficiais, sem alterar as questões.

Requer pypdf apenas como ferramenta editorial. Arquivos baixados ficam em .cache.
"""
import hashlib
import json
import re
import shutil
import subprocess
import unicodedata
from collections import defaultdict
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.cache/inep'
SOURCE = 'https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/provas-e-gabaritos/'

def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s.lower()) if not unicodedata.combining(c))

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.block = ''
        self.book = ''
        self.day = ''
        self.anchor = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in {'p', 'h2', 'h3', 'h4', 'h5'}:
            self.block = ''
        if tag == 'a':
            self.anchor = {'url': dict(attrs).get('href', ''), 'text': '', 'book': self.book, 'day': self.day}

    def handle_data(self, data):
        self.block += data
        if self.anchor is not None:
            self.anchor['text'] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor:
            if 'gabarito' in fold(self.anchor['text']) and 'azul' in fold(self.anchor['book']):
                self.links.append(self.anchor.copy())
            self.anchor = None
        if tag in {'p', 'h2', 'h3', 'h4', 'h5'}:
            text = ' '.join(self.block.split())
            normalized = fold(text)
            if 'dia' in normalized and len(text) < 160:
                self.day = text
            if ('caderno' in normalized or 'azul' in normalized) and len(text) < 200:
                self.book = text

def fetch(url, target):
    if target.exists():
        return target.read_bytes()
    if url.endswith('.pdf') and shutil.which('curl.exe'):
        body = subprocess.run(['curl.exe', '--fail', '--location', '--silent', '--show-error', '--max-time', '35',
                               '--retry', '1', url], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        if not body.startswith(b'%PDF-'):
            raise ValueError('O arquivo recebido não é um PDF.')
    else:
        with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as response:
            body = response.read()
    target.write_bytes(body)
    return body

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    selected = json.loads((ROOT / 'data/questions.json').read_text(encoding='utf-8'))
    report = {'checked_on': '2026-11-13', 'sources': [], 'questions': {}}
    for year in sorted({q['year'] for q in selected.values()}, reverse=True):
        try:
            body = fetch(SOURCE + str(year), CACHE / f'{year}.html').decode('utf-8', 'replace')
            parser = Links()
            parser.feed(body)
            sources = []
            for link in parser.links:
                label = fold(link['book'] + ' ' + link['day'])
                if any(word in label for word in ['digital', 'ppl', 'reaplica', 'ledor', 'libras', 'ampliad', '2a aplica', 'segunda aplica']):
                    continue
                if not link['url'].startswith('https://download.inep.gov.br/'):
                    continue
                if link['url'] in {s['url'] for s in sources}:
                    continue
                sources.append(link)
            print(year, 'PDFs localizados:', len(sources), flush=True)
            for link in sources:
                pdf = fetch(link['url'], CACHE / (hashlib.sha256(link['url'].encode()).hexdigest()[:20] + '.pdf'))
                reader = PdfReader(BytesIO(pdf))
                text = '\n'.join(page.extract_text() or '' for page in reader.pages)
                (CACHE / (hashlib.sha256(link['url'].encode()).hexdigest()[:20] + '.txt')).write_text(text, encoding='utf-8')
                pairs = re.findall(r'(?<!\d)(\d{1,3})\s+(Anulado|Cancelado|[ABCDE])\b(?:\s+([ABCDE])\b)?', text) if len(reader.pages) <= 3 else []
                source = {**link, 'year': year, 'pairs': len(pairs), 'answers': pairs}
                report['sources'].append(source)
        except Exception as error:
            print(year, type(error).__name__, str(error), flush=True)
    for key, question in selected.items():
        matching = []
        for source in report['sources']:
            if source['year'] != question['year']:
                continue
            answers = []
            for number, first, second in source['answers']:
                if int(number) == question['index']:
                    answers.append(second if question.get('language') == 'espanhol' and second else first)
            if question['year'] == 2009:
                # PDF com quatro cadernos: azul é a primeira coluna no dia 1,
                # e a terceira coluna no dia 2.
                answers = answers[:1] if question['index'] <= 90 else answers[2:3]
            if not answers:
                continue
            # Ainda registrar como candidato: o formato das tabelas e as duas
            # línguas estrangeiras exigem inspeção antes de afirmar conferência.
            matching.append({'url': source['url'], 'letters': answers, 'label': source['book']})
        report['questions'][key] = {'transcribed': question['correctAlternative'], 'candidates': matching}
        letters = {letter for candidate in matching for letter in candidate['letters']}
        report['questions'][key]['status'] = 'confirmed' if letters == {question['correctAlternative']} else 'divergent' if letters else 'unverified'
    report['summary'] = {status: sum(q['status'] == status for q in report['questions'].values())
                         for status in ['confirmed', 'divergent', 'unverified']}
    report['excluded'] = json.loads((ROOT / 'data/answer_exclusions.json').read_text(encoding='utf-8'))
    (ROOT / 'data/answer_key_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Comparação de letras do gabarito:', report['summary'])
    print('Esta verificação não confere a transcrição integral dos enunciados e alternativas.')

if __name__ == '__main__':
    main()
