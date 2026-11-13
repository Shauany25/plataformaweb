import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from study.models import Area, Question, Resource, Subject, Topic
from data.editorial import NOTES

AREAS = [
    ('humanas', 'Ciências Humanas e suas Tecnologias', 'História, Geografia, Filosofia e Sociologia.'),
    ('natureza', 'Ciências da Natureza e suas Tecnologias', 'Biologia, Química e Física.'),
    ('matematica', 'Matemática e suas Tecnologias', 'Razões, funções, estatística, geometria e os demais conteúdos selecionados.'),
    ('linguagens', 'Linguagens, Códigos e suas Tecnologias', 'Português, Literatura, Inglês, Espanhol, Artes, Educação Física e materiais de Redação.'),
]
SOURCE = 'https://blog.unoeste.br/assuntos-que-mais-caem-no-enem/'
INEP = 'https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem'

class Command(BaseCommand):
    help = 'Carrega, de forma idempotente, o catálogo do grupo e a seleção de questões oficiais.'

    @transaction.atomic
    def handle(self, *args, **options):
        root = settings.BASE_DIR / 'data'
        catalog = json.loads((root / 'catalog.json').read_text(encoding='utf-8'))
        selection = json.loads((root / 'question_selection.json').read_text(encoding='utf-8'))
        questions = json.loads((root / 'questions.json').read_text(encoding='utf-8'))
        checks = json.loads((root / 'resource_checks.json').read_text(encoding='utf-8'))
        overrides = json.loads((root / 'resource_overrides.json').read_text(encoding='utf-8'))
        readings = json.loads((root / 'reading_checks.json').read_text(encoding='utf-8')) if (root / 'reading_checks.json').exists() else {}
        images = json.loads((root / 'image_checks.json').read_text(encoding='utf-8')) if (root / 'image_checks.json').exists() else {}
        def local_images(value):
            for url, image in images.items():
                if image.get('status') == 'available':
                    value = value.replace(url, image['local'])
            return value
        area_map = {}
        for order, (slug, name, description) in enumerate(AREAS):
            area_map[slug], _ = Area.objects.update_or_create(slug=slug, defaults={'name': name, 'description': description, 'order': order})
        topic_map = {}
        for s in catalog:
            subject, _ = Subject.objects.update_or_create(slug=s['slug'], defaults={'name': s['name'], 'area': area_map[s['area']]})
            if len(NOTES[s['slug']]) != len(s['topics']):
                raise CommandError('Roteiros incompatíveis com a lista de ' + s['name'])
            for order, (t, notes) in enumerate(zip(s['topics'], NOTES[s['slug']])):
                guide, reading_slug, _ = notes
                obj, _ = Topic.objects.update_or_create(slug=t['slug'], defaults={'subject': subject, 'name': t['name'],
                    'order': order, 'summary': guide.split('. ')[0] + '.', 'guide': guide,
                    'frequency_source': SOURCE})
                topic_map[t['slug']] = obj
                # Apenas os recursos editoriais são substituídos; dados pessoais são preservados.
                obj.resources.all().delete()
                if s['slug'] == 'redacao':
                    Resource.objects.create(topic=obj, kind='reading', title='Cartilha do participante e documentos do ENEM',
                        publisher='Inep · fonte oficial', url=INEP + '/outros-documentos')
                reading = readings.get(t['slug'])
                if reading and reading.get('status') == 'available':
                    Resource.objects.create(topic=obj, kind='reading', title=reading['title'], publisher='Toda Matéria', url=reading['url'])
                if t.get('video_url'):
                    check = checks.get(t['slug'], {})
                    confirmed = check.get('status') == 'available'
                    override = overrides.get(t['slug'])
                    Resource.objects.create(topic=obj, kind='video', title=override['title'] if override else check.get('title') or ('Videoaula: ' + t['name']),
                        publisher=override['publisher'] if override else check.get('publisher') or ('Link do grupo · disponibilidade confirmada' if confirmed else 'Link do grupo · disponibilidade não confirmada'),
                        url=override['url'] if override else t['video_url'])
        question_map = {}
        for key, q in questions.items():
            lang = q.get('language') or ''
            source_url = f"https://api.enem.dev/v1/exams/{q['year']}/questions/{q['index']}" + (f'?language={lang}' if lang else '')
            obj, _ = Question.objects.update_or_create(key=key, defaults={'year': q['year'], 'number': q['index'], 'language': lang,
                'context': local_images(q.get('context') or ''), 'prompt': local_images(q.get('alternativesIntroduction') or ''),
                'alternatives': [{'letter': a['letter'], 'text': local_images(a.get('text') or ''), 'file': local_images(a.get('file') or '')} for a in q['alternatives']],
                'answer': q['correctAlternative'], 'source': source_url, 'source_pdf': INEP + f"/provas-e-gabaritos/{q['year']}",
                'booklet': 'Caderno azul'})
            question_map[key] = obj
        for slug, keys in selection.items():
            if len(keys) > 10 or len(keys) != len(set(keys)):
                raise CommandError('Seleção inválida para ' + slug)
            topic_map[slug].questions.set([question_map[key] for key in keys])
        exclusions = json.loads((root / 'answer_exclusions.json').read_text(encoding='utf-8'))
        # Retirar apenas as questões explicitamente anuladas, sem apagar um
        # registro que esteja sendo usado no histórico pessoal de uma tentativa.
        Question.objects.filter(key__in=exclusions, topics__isnull=True, attemptanswer__isnull=True).delete()
        self.stdout.write(self.style.SUCCESS(f'Catálogo carregado: {len(topic_map)} conteúdos e {len(question_map)} questões oficiais.'))
