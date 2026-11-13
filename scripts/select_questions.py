"""Triagem editorial do acervo; gera seleção explícita para inspeção, não roda no site."""
import json
import re
import sys
import unicodedata
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from data.editorial import NOTES
from data.curation import SELECTED

def fold(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))

def main():
    catalog = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
    all_questions = {}
    for file in sorted((ROOT / '.cache/enem').glob('*.json')):
        for q in json.loads(file.read_text(encoding='utf-8')):
            language = q.get('language') or ''
            key = f"{q['year']}-{q['index']}-{language or 'regular'}"
            if len(q.get('alternatives', [])) != 5 or q.get('correctAlternative') not in 'ABCDE':
                continue
            q['_key'] = key
            # Alguns registros do acervo têm área incorreta. Conferir pela posição
            # no caderno azul, respeitando a mudança de distribuição em 2017.
            number, year = q['index'], q['year']
            if year >= 2017:
                q['discipline'] = 'linguagens' if number <= 45 else 'ciencias-humanas' if number <= 90 else 'ciencias-natureza' if number <= 135 else 'matematica'
            else:
                q['discipline'] = ('ciencias-natureza' if year == 2009 else 'ciencias-humanas') if number <= 45 else ('ciencias-humanas' if year == 2009 else 'ciencias-natureza') if number <= 90 else 'linguagens' if number <= 135 else 'matematica'
            q['_text'] = fold((q.get('context') or '') + '\n' + (q.get('alternativesIntroduction') or ''))
            all_questions[key] = q
    selection, selected, review = {}, {}, []
    discipline = {'matematica': 'matematica', 'linguagens': 'linguagens', 'humanas': 'ciencias-humanas', 'natureza': 'ciencias-natureza'}
    for subject in catalog:
        notes = NOTES[subject['slug']]
        assert len(notes) == len(subject['topics']), subject['name']
        for topic, (guide, reading_slug, pattern) in zip(subject['topics'], notes):
            if not pattern:
                selection[topic['slug']] = []
                continue
            prompt_only = pattern.startswith('(?PROMPT)')
            pattern = pattern.replace('(?PROMPT)', '')
            candidates = []
            for key, q in all_questions.items():
                if q['discipline'] != discipline[subject['area']]:
                    continue
                if subject['slug'] in ('ingles', 'espanhol'):
                    if q.get('language') != subject['slug']:
                        continue
                elif q.get('language'):
                    continue
                text = fold(q.get('alternativesIntroduction') or '')[-500:] if prompt_only else q['_text']
                if subject['slug'] == 'artes' and not re.search(r'pintur|artistic|escultur|museu|artista|quadro|obra de arte|performance|instalacao|vanguard|cubista|surreal|barroc|renascent|rococo|neoclass', q['_text']):
                    continue
                if subject['slug'] == 'artes' and re.search(r'poema|soneto|poetico|funcao.*linguagem|funcao social|narrador|\bconto\b|cronica|recurso argumentativo', fold(q.get('alternativesIntroduction') or '')):
                    continue
                if subject['slug'] == 'educacao-fisica' and re.search(r'coesao|coesiv|pronome|genero musical|recurso argumentativo|metalinguagem|estrutura.*text|poema porque|contexto em que foi produzido|articulacao entre suas partes|objetivo desse texto', fold(q.get('alternativesIntroduction') or '')):
                    continue
                if subject['slug'] == 'literatura' and re.search(r'coesao|coesiv|pronome|sintatic|pontuacao|concordancia|regencia|funcao.*linguagem|variedade linguistica', fold(q.get('alternativesIntroduction') or '')):
                    continue
                matches = list(re.finditer(pattern, text))
                if not matches:
                    continue
                candidates.append((len(matches), q['year'], -q['index'], key))
            # Termos específicos e enunciados recentes antes dos demais candidatos.
            keys = [item[3] for item in sorted(candidates, reverse=True)[:10]]
            selection[topic['slug']] = keys
            review.append('\n## ' + topic['slug'] + f' ({len(keys)})')
            for key in keys:
                q = all_questions[key]
                if subject['slug'] != 'redacao':
                    selected[key] = {k: v for k, v in q.items() if not k.startswith('_')}
                review.append(key + ': ' + ' '.join((q.get('alternativesIntroduction') or '').split()))
    # Aplicar a seleção explícita após examinar o relatório de candidatos.
    selection, selected = {}, {}
    for subject in catalog:
        choices = SELECTED[subject['slug']]
        assert len(choices) == len(subject['topics']), subject['slug']
        for topic, short_keys in zip(subject['topics'], choices):
            keys = [key + '-regular' if len(key.split('-')) == 2 else key for key in short_keys.split()]
            assert len(keys) <= 10 and len(keys) == len(set(keys)), topic['slug']
            selection[topic['slug']] = keys
            for key in keys:
                selected[key] = {k: v for k, v in all_questions[key].items() if not k.startswith('_')}
    corrections = json.loads((ROOT / 'data/answer_corrections.json').read_text(encoding='utf-8'))
    exclusions = json.loads((ROOT / 'data/answer_exclusions.json').read_text(encoding='utf-8'))
    assert not set(selected).intersection(exclusions), 'A seleção contém questão anulada.'
    for key, correction in corrections.items():
        if key in selected:
            selected[key]['correctAlternative'] = correction['answer']
            for alternative in selected[key]['alternatives']:
                alternative['isCorrect'] = alternative['letter'] == correction['answer']
    (ROOT / 'data/question_selection.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'data/questions.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / '.cache/selection_review.txt').write_text('\n'.join(review), encoding='utf-8')
    print(f'{len(selected)} questões distintas; {sum(len(v) for v in selection.values())} associações a tópicos')
    for topic, keys in selection.items():
        if len(keys) < 10:
            print(topic, len(keys))

if __name__ == '__main__':
    main()
