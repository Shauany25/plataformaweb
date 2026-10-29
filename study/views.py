import re
import unicodedata
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import LoginForm, PlanForm, SignupForm
from .models import Area, Attempt, AttemptAnswer, PlanItem, Question, StudiedTopic, Subject, Topic


def safe_next(request):
    target = request.POST.get('next') or request.GET.get('next', '')
    return target if url_has_allowed_host_and_scheme(target, {request.get_host()}, require_https=request.is_secure()) else reverse('home')


class EnterView(LoginView):
    template_name = 'auth.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    def get_success_url(self):
        return safe_next(self.request)


class ExitView(LogoutView):
    next_page = 'home'


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
        login(request, user)
        messages.success(request, 'Sua conta foi criada. Boa jornada de estudos!')
        return redirect(safe_next(request))
    return render(request, 'auth.html', {'form': form, 'signup': True, 'next': request.GET.get('next', '')})


def home(request):
    return render(request, 'index.html', {'nav': 'home'})


def enem(request):
    return render(request, 'ENEM.html', {'nav': 'enem', 'areas': Area.objects.prefetch_related('subjects')})


def area(request, slug):
    obj = get_object_or_404(Area, slug=slug)
    return render(request, 'catalog.html', {'nav': 'enem', 'area': obj, 'subjects': obj.subjects.annotate(topic_count=Count('topics'))})


def subject(request, slug):
    obj = get_object_or_404(Subject.objects.select_related('area'), slug=slug)
    exercise = request.GET.get('origem') == 'exercicios'
    return render(request, 'catalog.html', {'nav': 'exercises' if exercise else 'enem', 'subject': obj,
        'exercise': exercise, 'topics': obj.topics.annotate(question_count=Count('questions'))})


def topic(request, slug):
    obj = get_object_or_404(Topic.objects.select_related('subject__area').prefetch_related('resources'), slug=slug)
    studied = request.user.is_authenticated and StudiedTopic.objects.filter(user=request.user, topic=obj).exists()
    return render(request, 'topic.html', {'nav': 'enem', 'topic': obj, 'studied': studied,
        'question_count': min(10, obj.questions.count()), 'writing': obj.subject.slug == 'redacao'})


def exercises(request):
    return render(request, 'exercicio.html', {'nav': 'exercises',
        'subjects': Subject.objects.exclude(slug='redacao').select_related('area').annotate(topic_count=Count('topics'))})


def exercise_topic(request, slug):
    obj = get_object_or_404(Topic.objects.select_related('subject__area'), slug=slug)
    if obj.subject.slug == 'redacao':
        return redirect('topic', slug=obj.slug)
    return render(request, 'exercise_topic.html', {'nav': 'exercises', 'topic': obj, 'questions': obj.questions.all()[:10]})


def owned_attempts(request):
    if request.user.is_authenticated:
        return Attempt.objects.filter(user=request.user)
    if not request.session.session_key:
        request.session.create()
    return Attempt.objects.filter(user__isnull=True, session_key=request.session.session_key)


@require_POST
def start_attempt(request, slug):
    obj = get_object_or_404(Topic, slug=slug)
    questions = list(obj.questions.all()[:10])
    if not questions or obj.subject.slug == 'redacao':
        return redirect('exercise_topic', slug=slug)
    if not request.session.session_key:
        request.session.create()
    with transaction.atomic():
        attempt = Attempt.objects.create(topic=obj, user=request.user if request.user.is_authenticated else None,
                                         session_key='' if request.user.is_authenticated else request.session.session_key)
        AttemptAnswer.objects.bulk_create([AttemptAnswer(attempt=attempt, question=q, position=i + 1) for i, q in enumerate(questions)])
    return redirect('attempt', pk=attempt.pk)


def attempt(request, pk):
    obj = get_object_or_404(owned_attempts(request).select_related('topic__subject'), pk=pk)
    answer_rows = obj.answers.select_related('question')
    total = answer_rows.count()
    try:
        position = int(request.GET.get('questao', 1))
    except (ValueError, TypeError):
        raise Http404
    row = get_object_or_404(answer_rows, position=position)
    if request.method == 'POST':
        selected = request.POST.get('answer', '')
        valid = {a['letter'] for a in row.question.alternatives}
        if selected not in valid:
            messages.error(request, 'Selecione uma alternativa antes de confirmar.')
        else:
            # A resposta é imutável depois da confirmação, inclusive em duas abas.
            updated = AttemptAnswer.objects.filter(pk=row.pk, selected='').update(
                selected=selected, correct=selected == row.question.answer, answered=timezone.now())
            if updated:
                if request.user.is_authenticated:
                    StudiedTopic.objects.get_or_create(user=request.user, topic=obj.topic)
                if not obj.answers.filter(selected='').exists():
                    Attempt.objects.filter(pk=obj.pk, finished__isnull=True).update(finished=timezone.now())
        return redirect(reverse('attempt', args=[pk]) + f'?questao={position}#questao')
    answered = answer_rows.exclude(selected='').count()
    correct = answer_rows.filter(correct=True).count()
    return render(request, 'quiz.html', {'nav': 'exercises', 'attempt': obj, 'row': row, 'rows': answer_rows,
        'total': total, 'answered': answered, 'correct_count': correct, 'wrong_count': answered - correct,
        'percent': round(answered / total * 100), 'next_position': position + 1 if position < total else None,
        'previous_position': position - 1 if position > 1 else None})


@login_required
@require_POST
def mark_studied(request, slug):
    obj = get_object_or_404(Topic, slug=slug)
    if request.POST.get('studied') == 'yes':
        StudiedTopic.objects.get_or_create(user=request.user, topic=obj)
    else:
        StudiedTopic.objects.filter(user=request.user, topic=obj).delete()
    return redirect('topic', slug=slug)


def tools_context(request, form=None):
    context = {'nav': 'techniques', 'plan_form': form if form is not None else PlanForm(),
               'days': [(0, 'Segunda'), (1, 'Terça'), (2, 'Quarta'), (3, 'Quinta'), (4, 'Sexta'), (5, 'Sábado'), (6, 'Domingo')]}
    if request.user.is_authenticated:
        items = list(PlanItem.objects.filter(user=request.user).select_related('subject'))
        for kind, _ in PlanItem.KINDS:
            context[kind + '_items'] = [item for item in items if item.kind == kind]
        answers = AttemptAnswer.objects.filter(attempt__user=request.user).exclude(selected='')
        correct = answers.filter(correct=True).count()
        total = answers.count()
        context.update({'correct_count': correct, 'wrong_count': total - correct, 'answer_count': total,
            'accuracy': round(correct / total * 100) if total else 0,
            'studied_topics': StudiedTopic.objects.filter(user=request.user).select_related('topic__subject'),
            'subject_progress': Subject.objects.annotate(answer_total=Count('topics__attempt__answers',
                filter=Q(topics__attempt__user=request.user, topics__attempt__answers__selected__in=list('ABCDE'))),
                correct_total=Count('topics__attempt__answers', filter=Q(topics__attempt__user=request.user,
                topics__attempt__answers__correct=True))).filter(answer_total__gt=0),
            'due_reminders': [item for item in items if item.kind == 'reminder' and not item.done and item.due and item.due <= timezone.now()]})
    return context


def techniques(request):
    return render(request, 'tecnicas.html', tools_context(request))


@login_required
@require_POST
def add_plan(request):
    form = PlanForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.save()
        messages.success(request, 'Seu planejamento foi salvo.')
        return redirect(reverse('techniques') + '#organizacao')
    return render(request, 'tecnicas.html', tools_context(request, form), status=400)


@login_required
@require_POST
def update_plan(request, pk):
    obj = get_object_or_404(PlanItem, pk=pk, user=request.user)
    if request.POST.get('action') == 'delete':
        obj.delete()
    elif request.POST.get('action') == 'toggle':
        obj.done = not obj.done
        obj.save(update_fields=['done'])
    else:
        return HttpResponseBadRequest('Ação inválida.')
    return redirect(reverse('techniques') + '#organizacao')


def reminder_status(request):
    if not request.user.is_authenticated:
        return JsonResponse({'reminders': []})
    rows = PlanItem.objects.filter(user=request.user, kind='reminder', done=False, due__lte=timezone.now())
    response = JsonResponse({'reminders': [{'id': p.pk, 'title': p.title} for p in rows]})
    response['Cache-Control'] = 'no-store'
    return response


def fold(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))


def search(request):
    query = request.GET.get('q', '').strip()[:200]
    tokens = re.findall(r'\w+', fold(query))
    results = []
    def matches(*parts):
        haystack = fold(' '.join(str(p) for p in parts))
        return bool(tokens) and all(t in haystack for t in tokens)
    for obj in Area.objects.all():
        if matches(obj.name, obj.description):
            results.append({'kind': 'Área de conhecimento', 'title': obj.name, 'detail': obj.description,
                'url': reverse('area', args=[obj.slug])})
    for obj in Subject.objects.select_related('area'):
        if matches(obj.name, obj.area.name):
            results.append({'kind': 'Matéria', 'title': obj.name, 'detail': obj.area.name,
                'url': reverse('subject', args=[obj.slug])})
    for obj in Topic.objects.select_related('subject__area'):
        if matches(obj.name, obj.subject.name, obj.subject.area.name, obj.summary):
            results.append({'kind': 'Conteúdo', 'title': obj.name, 'detail': obj.subject.name,
                'url': reverse('topic', args=[obj.slug])})
    for obj in Question.objects.prefetch_related('topics__subject'):
        linked = list(obj.topics.all())
        if linked and matches(obj.context, obj.prompt, obj.year, obj.number,
            ' '.join(a.get('text') or '' for a in obj.alternatives), ' '.join(t.name + ' ' + t.subject.name for t in linked)):
            results.append({'kind': 'Questão oficial', 'title': f'ENEM {obj.year} · Questão {obj.number}',
                'detail': linked[0].name + ' · ' + obj.prompt,
                'url': reverse('exercise_topic', args=[linked[0].slug]) + f'#q-{obj.pk}'})
    return render(request, 'search.html', {'query': query, 'results': results, 'result_count': len(results)})
