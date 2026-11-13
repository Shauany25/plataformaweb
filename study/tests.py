import json
from datetime import timedelta
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Attempt, AttemptAnswer, PlanItem, Question, StudiedTopic, Subject, Topic, User


class StudyFlowsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_catalog', verbosity=0)
        cls.user = User.objects.create_user(username='aluno', email='aluno@example.test', password='Trilha!Estudo2026')
        cls.other = User.objects.create_user(username='outro', email='outro@example.test', password='Outra!Trilha2026')
        cls.topic = Topic.objects.get(slug='matematica-geometria-espacial')

    def test_catalog_matches_supplied_list_and_has_no_extra_topics(self):
        catalog = json.loads((settings.BASE_DIR / 'data/catalog.json').read_text(encoding='utf-8'))
        expected = {t['slug'] for subject in catalog for t in subject['topics']}
        self.assertEqual(set(Topic.objects.values_list('slug', flat=True)), expected)
        self.assertEqual(Topic.objects.count(), 128)
        self.assertEqual(Subject.objects.count(), 15)
        for topic in Topic.objects.all():
            self.assertLessEqual(topic.questions.count(), 10)
            if topic.subject.slug == 'redacao':
                self.assertFalse(topic.questions.exists())
        for q in Question.objects.all():
            self.assertEqual(len(q.alternatives), 5)
            self.assertIn(q.answer, {a['letter'] for a in q.alternatives})

    def test_main_pages_and_all_content_pages_render(self):
        for url in ['/', '/index.html', '/ENEM.html', '/exercicio.html', '/tecnicas.html', '/entrar/', '/cadastrar/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        for obj in Topic.objects.all():
            self.assertEqual(self.client.get(reverse('topic', args=[obj.slug])).status_code, 200, obj.slug)
            self.assertIn(self.client.get(reverse('exercise_topic', args=[obj.slug])).status_code, (200, 302))

    def test_signup_login_logout_and_email_case(self):
        response = self.client.post(reverse('signup'), {'email': ' NOVO@EXAMPLE.TEST ', 'password1': 'Nova!Trilha2026', 'password2': 'Nova!Trilha2026'})
        self.assertEqual(response.status_code, 302)
        account = User.objects.get(email='novo@example.test')
        self.assertTrue(account.check_password('Nova!Trilha2026'))
        self.assertNotEqual(account.password, 'Nova!Trilha2026')
        self.assertEqual(self.client.get('/sair/').status_code, 405)
        self.client.post('/sair/')
        response = self.client.post('/entrar/', {'username':'NOVO@EXAMPLE.TEST', 'password':'Nova!Trilha2026'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), account.pk)

    def test_external_redirect_and_duplicate_email_are_rejected(self):
        response = self.client.post('/entrar/?next=https://example.net', {'username':'aluno@example.test', 'password':'Trilha!Estudo2026', 'next':'https://example.net'})
        self.assertRedirects(response, '/')
        self.client.post('/sair/')
        response = self.client.post('/cadastrar/', {'email':'ALUNO@example.test', 'password1':'Trilha!Estudo2026', 'password2':'Trilha!Estudo2026'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Já existe uma conta')

    def test_csrf_is_required_for_mutations(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/cadastrar/', {'email':'x@example.test'}).status_code, 403)
        client.force_login(self.user)
        self.assertEqual(client.post('/organizacao/adicionar/', {'kind':'task','title':'Teste'}).status_code, 403)
        self.assertEqual(client.post(reverse('start_attempt', args=[self.topic.slug])).status_code, 403)

    def test_planning_persists_and_is_private(self):
        self.client.force_login(self.user)
        response = self.client.post('/organizacao/adicionar/', {'kind':'task','title':'Revisar geometria'})
        self.assertEqual(response.status_code, 302)
        item = PlanItem.objects.get(user=self.user)
        self.client.post(reverse('update_plan', args=[item.pk]), {'action':'toggle'})
        item.refresh_from_db()
        self.assertTrue(item.done)
        self.client.force_login(self.other)
        response = self.client.post(reverse('update_plan', args=[item.pk]), {'action':'delete'})
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(self.client.get('/tecnicas.html'), 'Revisar geometria')
        self.assertTrue(PlanItem.objects.filter(pk=item.pk).exists())

    def test_schedule_and_reminder_validation(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post('/organizacao/adicionar/', {'kind':'schedule','title':'Estudar'}).status_code, 400)
        self.assertEqual(self.client.post('/organizacao/adicionar/', {'kind':'reminder','title':'Lembrar'}).status_code, 400)
        response = self.client.post('/organizacao/adicionar/', {'kind':'schedule','title':'Estudar','day':'0','time':'08:00'})
        self.assertEqual(response.status_code, 302)
        item = PlanItem.objects.get(user=self.user)
        self.assertEqual(item.day, 0)
        self.assertEqual(item.time.hour, 8)

    def test_due_reminders_are_visible_only_to_the_owner(self):
        PlanItem.objects.create(user=self.user, kind='reminder', title='Revisar mapas', due=timezone.now()-timedelta(minutes=1))
        PlanItem.objects.create(user=self.user, kind='reminder', title='Amanhã', due=timezone.now()+timedelta(days=1))
        self.client.force_login(self.user)
        self.assertEqual([r['title'] for r in self.client.get('/organizacao/lembretes/').json()['reminders']], ['Revisar mapas'])
        self.client.force_login(self.other)
        self.assertEqual(self.client.get('/organizacao/lembretes/').json()['reminders'], [])

    def test_quiz_corrects_on_server_and_cannot_be_overwritten(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('start_attempt', args=[self.topic.slug]))
        attempt = Attempt.objects.get(user=self.user)
        self.assertEqual(attempt.answers.count(), 10)
        row = attempt.answers.first()
        response = self.client.post(response.url + '?questao=1', {'answer':row.question.answer})
        row.refresh_from_db()
        self.assertTrue(row.correct)
        wrong = next(a['letter'] for a in row.question.alternatives if a['letter'] != row.question.answer)
        self.client.post(reverse('attempt', args=[attempt.pk])+'?questao=1', {'answer':wrong})
        row.refresh_from_db()
        self.assertTrue(row.correct)
        self.assertTrue(StudiedTopic.objects.filter(user=self.user, topic=self.topic).exists())
        self.assertEqual(self.client.get('/tecnicas.html').status_code, 200)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('attempt', args=[attempt.pk])).status_code, 404)

    def test_guest_can_practice_with_session_isolation(self):
        response = self.client.post(reverse('start_attempt', args=[self.topic.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get(response.url).status_code, 200)
        self.assertEqual(Client().get(response.url).status_code, 404)
        self.assertIsNone(Attempt.objects.get().user)

    def test_search_finds_accentless_topics_areas_subjects_and_questions(self):
        for query, expected in [('matematica','Matemática'), ('natureza','Ciências da Natureza'), ('porcentagem','Porcentagem'), ('cilindrica','Questão oficial')]:
            response = self.client.get('/pesquisa/', {'q':query})
            self.assertContains(response, expected)
        response = self.client.get('/pesquisa/', {'q':'<script>alert(1)</script>'})
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_mark_studied_is_unique_and_can_be_undone(self):
        self.client.force_login(self.user)
        url = reverse('mark_studied', args=[self.topic.slug])
        self.client.post(url, {'studied':'yes'})
        self.client.post(url, {'studied':'yes'})
        self.assertEqual(StudiedTopic.objects.filter(user=self.user).count(), 1)
        self.client.post(url, {'studied':'no'})
        self.assertFalse(StudiedTopic.objects.filter(user=self.user).exists())

    def test_external_question_html_and_urls_are_sanitized(self):
        from .templatetags.study_tags import exam_text
        output = str(exam_text('<script>alert(1)</script> [teste](javascript:alert(1)) ![x](https://evil.example/x.png)'))
        self.assertNotIn('<script>', output)
        self.assertNotIn('href="javascript:', output)
        self.assertNotIn('src="https://evil', output)

    def test_hidden_dates_do_not_leak_between_planning_tools(self):
        self.client.force_login(self.user)
        due = (timezone.localtime() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post('/organizacao/adicionar/', {'kind':'task', 'title':'Revisar funções', 'due':due})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(PlanItem.objects.get(user=self.user).due)
        response = self.client.post('/organizacao/adicionar/', {'kind':'schedule', 'title':'Revisar história', 'day':'2', 'time':'10:00', 'due':due})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(PlanItem.objects.get(user=self.user, kind='schedule').due)

    def test_repertoire_pdf_matches_documented_version_and_is_linked(self):
        import hashlib
        published = settings.BASE_DIR / 'assets/materials/repertorio-sociocultural.pdf'
        reviewed = settings.BASE_DIR / 'docs/repertorio-sociocultural.pdf'
        self.assertEqual(hashlib.sha256(published.read_bytes()).hexdigest(), hashlib.sha256(reviewed.read_bytes()).hexdigest())
        response = self.client.get('/enem/conteudo/redacao-repertorio-sociocultural/')
        self.assertContains(response, '/assets/materials/repertorio-sociocultural.pdf')
        self.assertNotContains(response, 'aguarda aprovação')

    def test_official_answer_corrections_and_annulled_question(self):
        for key, answer in [('2021-145-regular', 'C'), ('2021-15-regular', 'D'), ('2011-81-regular', 'D')]:
            self.assertEqual(Question.objects.get(key=key).answer, answer)
        self.assertFalse(Topic.objects.filter(questions__key='2022-157-regular').exists())

    def test_only_approved_video_replacements_are_published(self):
        from .models import Resource
        expected = json.loads((settings.BASE_DIR / 'data/catalog.json').read_text(encoding='utf-8'))
        overrides = json.loads((settings.BASE_DIR / 'data/resource_overrides.json').read_text(encoding='utf-8'))
        for subject in expected:
            for topic in subject['topics']:
                if topic.get('video_url'):
                    actual = Resource.objects.get(topic__slug=topic['slug'], kind='video')
                    self.assertEqual(actual.url, overrides.get(topic['slug'], {}).get('url', topic['video_url']))
