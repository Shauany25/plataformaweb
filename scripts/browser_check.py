"""Verificação de ponta a ponta com o Edge instalado, sem baixar outro navegador."""
import json
import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from playwright.sync_api import sync_playwright, expect
from study.models import Attempt, PlanItem, User

ARTIFACTS = ROOT / 'artifacts'
ARTIFACTS.mkdir(exist_ok=True)
BASE = 'http://127.0.0.1:8000'
email = f'qa-{uuid.uuid4().hex}@example.invalid'
errors = []
report = []

def db_call(func):
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(func).result()

def load_answers():
    attempt = Attempt.objects.get(user__email=email)
    return [{'answer': row.question.answer, 'alternatives': row.question.alternatives}
            for row in attempt.answers.select_related('question')]

with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width':1440,'height':1000}, device_scale_factor=1)
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        page.goto(BASE)
        expect(page.locator('h1')).to_contain_text('Seu futuro começa')
        page.screenshot(path=str(ARTIFACTS / 'inicio-desktop.png'), full_page=True)
        page.get_by_role('navigation', name='Navegação principal').get_by_role('link', name='ENEM', exact=True).click()
        page.get_by_role('link', name='Ciências Humanas e suas Tecnologias').click()
        page.get_by_role('link', name='História', exact=False).click()
        page.get_by_role('link', name='Brasil Império', exact=False).click()
        expect(page.locator('h1')).to_have_text('Brasil Império')
        expect(page.get_by_role('heading', name='Materiais de apoio e videoaulas')).to_be_visible()
        report.append('Área → matéria → conteúdo → materiais')
        page.goto(BASE+'/enem/conteudo/redacao-repertorio-sociocultural/')
        pdf_link = page.locator('a.resource-row[href$="repertorio-sociocultural.pdf"]')
        expect(pdf_link).to_be_visible()
        pdf_response = page.request.get(BASE + pdf_link.get_attribute('href'))
        assert pdf_response.status == 200 and pdf_response.body().startswith(b'%PDF-')
        report.append('PDF de repertório aprovado disponível na página de Redação')

        page.goto(BASE+'/cadastrar/')
        page.get_by_label('E-mail', exact=True).fill(email)
        page.locator('#id_password1').fill('Estudos!Teste2026')
        page.locator('#id_password2').fill('Estudos!Teste2026')
        page.get_by_role('button', name='Cadastrar', exact=False).click()
        expect(page.get_by_role('button', name='Sair', exact=True)).to_be_visible()
        report.append('Cadastro e sessão autenticada')

        page.goto(BASE+'/tecnicas.html')
        # Testar a conclusão com avanço do relógio, sem esperar um minuto real.
        page.clock.install()
        page.locator('#focus-minutes').fill('1')
        page.locator('#focus-minutes').dispatch_event('change')
        expect(page.locator('#timer-display')).to_have_text('01:00')
        page.locator('#timer-start').click()
        page.clock.fast_forward(61000)
        expect(page.locator('#timer-status')).to_contain_text('Estudo concluído')
        page.get_by_role('button', name='Pausa', exact=True).click()
        expect(page.locator('#timer-display')).to_have_text('05:00')
        page.locator('#timer-start').click()
        page.clock.fast_forward(3000)
        page.locator('#timer-start').click()
        paused = page.locator('#timer-display').inner_text()
        page.clock.fast_forward(5000)
        expect(page.locator('#timer-display')).to_have_text(paused)
        page.locator('#timer-reset').click()
        report.append('Temporizador: iniciar, concluir, trocar para pausa, pausar e reiniciar')

        page.locator('#id_kind').select_option('reminder')
        page.locator('#id_due').fill('2030-11-13T10:00')
        page.locator('#id_kind').select_option('task')
        expect(page.locator('#id_due')).to_be_disabled()
        page.locator('#id_title').fill('Revisar geometria para a prova')
        page.get_by_role('button', name='Salvar no meu plano').click()
        expect(page.locator('.plan-board')).to_contain_text('Revisar geometria para a prova')
        page.get_by_role('button', name='Concluir Revisar geometria para a prova').click()
        expect(page.locator('.plan-item.done')).to_contain_text('Revisar geometria para a prova')
        page.reload()
        expect(page.locator('.plan-item.done')).to_contain_text('Revisar geometria para a prova')
        report.append('Tarefa salva, concluída e preservada após recarregar')
        page.screenshot(path=str(ARTIFACTS / 'organizacao-desktop.png'), full_page=True)

        page.locator('#global-search').fill('geometria espacial')
        page.get_by_role('button', name='Pesquisar', exact=True).click()
        page.locator('.search-result').filter(has=page.get_by_role('heading', name='Geometria espacial', exact=True)).click()
        page.get_by_role('link', name='Ir para os exercícios').click()
        page.get_by_role('button', name='Iniciar exercícios').click()
        expect(page.locator('.quiz-top')).to_contain_text('Questão 1 de 10')
        rows = db_call(load_answers)
        for i, row in enumerate(rows):
            answer = row['answer']
            if i == 0:
                answer = next(a['letter'] for a in row['alternatives'] if a['letter'] != answer)
            page.locator(f'input[name=answer][value={answer}]').check()
            page.get_by_role('button', name='Confirmar resposta').click()
            expect(page.locator('.answer-feedback')).to_be_visible()
            if i < len(rows)-1:
                page.get_by_role('link', name='Próxima questão').click()
        expect(page.get_by_text('Lista concluída!', exact=True)).to_be_visible()
        expect(page.locator('.score')).to_contain_text('9')
        report.append('Pesquisa → conteúdo → lista completa de 10 questões, com 9 acertos e 1 erro')
        page.screenshot(path=str(ARTIFACTS / 'exercicio-desktop.png'), full_page=True)
        page.goto(BASE+'/tecnicas.html#progresso')
        expect(page.locator('#progresso .stat').nth(0)).to_contain_text('10')
        expect(page.locator('#progresso .stat').nth(1)).to_contain_text('9')
        expect(page.locator('#progresso .stat').nth(2)).to_contain_text('1')
        expect(page.locator('#progresso .stat').nth(3)).to_contain_text('90%')
        report.append('Resultados e conteúdo estudado exibidos no progresso')

        page.get_by_role('button', name='Sair', exact=True).click()
        page.goto(BASE+'/entrar/')
        page.get_by_label('E-mail', exact=True).fill(email.upper())
        page.get_by_label('Senha', exact=True).fill('Estudos!Teste2026')
        page.get_by_role('button', name='Entrar', exact=False).click()
        expect(page.get_by_role('button', name='Sair', exact=True)).to_be_visible()
        report.append('Sair e entrar novamente com e-mail em maiúsculas')

        page.set_viewport_size({'width':390,'height':844})
        for path in ['/', '/ENEM.html', '/exercicio.html', '/tecnicas.html', '/enem/conteudo/matematica-geometria-espacial/']:
            page.goto(BASE+path)
            width = page.evaluate('({page:document.documentElement.scrollWidth, viewport:innerWidth})')
            assert width['page'] <= width['viewport'], f'Overflow horizontal em {path}: {width}'
            expect(page.locator('h1')).to_be_visible()
        page.goto(BASE)
        page.get_by_role('button', name='Abrir menu').click()
        expect(page.locator('#menu')).to_be_visible()
        page.get_by_role('navigation', name='Navegação principal').get_by_role('link', name='ENEM',exact=True).click()
        expect(page.locator('h1')).to_contain_text('Uma trilha')
        page.screenshot(path=str(ARTIFACTS / 'enem-mobile.png'), full_page=True)
        page.goto(BASE)
        page.screenshot(path=str(ARTIFACTS / 'inicio-mobile.png'), full_page=True)
        report.append('Navegação móvel e cinco páginas sem rolagem horizontal em 390 px')
        for viewport in [320, 360, 768]:
            page.set_viewport_size({'width':viewport, 'height':900})
            for path in ['/', '/ENEM.html', '/exercicio.html', '/tecnicas.html', '/entrar/']:
                page.goto(BASE+path)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow em {viewport}px: {path}'
        report.append('Layouts conferidos também em 320, 360 e 768 px')
        assert not errors, errors
        report.append('Nenhum erro JavaScript durante os fluxos')
        (ARTIFACTS / 'browser-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        page.screenshot(path=str(ARTIFACTS / 'ultima-tela.png'), full_page=True)
        browser.close()
        # Apenas a conta temporária criada por esta execução é removida.
        db_call(lambda: User.objects.filter(email=email).delete())
