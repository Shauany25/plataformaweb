from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Area(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['order', 'name']
    def __str__(self):
        return self.name


class Subject(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='subjects')
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=160)
    summary = models.TextField()
    guide = models.TextField()
    frequency_source = models.URLField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['order', 'name']
    def __str__(self):
        return self.name


class Resource(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='resources')
    kind = models.CharField(max_length=10, choices=[('reading', 'Material de apoio'), ('video', 'Videoaula')])
    title = models.CharField(max_length=200)
    publisher = models.CharField(max_length=100)
    url = models.URLField(max_length=600)


class Question(models.Model):
    key = models.CharField(max_length=80, unique=True)
    topics = models.ManyToManyField(Topic, related_name='questions')
    year = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    language = models.CharField(max_length=20, blank=True)
    context = models.TextField(blank=True)
    prompt = models.TextField()
    alternatives = models.JSONField()
    answer = models.CharField(max_length=1)
    source = models.URLField(max_length=600)
    source_pdf = models.URLField(max_length=600, blank=True)
    booklet = models.CharField(max_length=100, default='Prova azul')
    class Meta:
        ordering = ['-year', 'number', 'key']


class PlanItem(models.Model):
    KINDS = [('schedule', 'Cronograma'), ('goal', 'Meta'), ('task', 'Tarefa'), ('reminder', 'Lembrete')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kind = models.CharField(max_length=10, choices=KINDS)
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    day = models.PositiveSmallIntegerField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    due = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['done', 'day', 'time', 'due', '-created']


class StudiedTopic(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'topic'], name='unique_studied_topic')]


class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    session_key = models.CharField(max_length=40, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()
    selected = models.CharField(max_length=1, blank=True)
    correct = models.BooleanField(null=True)
    answered = models.DateTimeField(null=True)
    class Meta:
        ordering = ['position']
        constraints = [models.UniqueConstraint(fields=['attempt', 'question'], name='unique_attempt_question'),
                       models.UniqueConstraint(fields=['attempt', 'position'], name='unique_attempt_position')]


