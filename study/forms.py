import uuid
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone
from .models import PlanItem, User


class SignupForm(UserCreationForm):
    email = forms.EmailField(label='E-mail', max_length=254)
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = uuid.uuid4().hex
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()


class PlanForm(forms.ModelForm):
    day = forms.TypedChoiceField(label='Dia da semana', required=False, coerce=int, empty_value=None,
        choices=[('', 'Selecione'), (0, 'Segunda-feira'), (1, 'Terça-feira'), (2, 'Quarta-feira'),
                 (3, 'Quinta-feira'), (4, 'Sexta-feira'), (5, 'Sábado'), (6, 'Domingo')])
    due = forms.DateTimeField(label='Data e horário', required=False,
        input_formats=['%Y-%m-%dT%H:%M'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'))
    class Meta:
        model = PlanItem
        fields = ['kind', 'title', 'subject', 'day', 'time', 'due']
        labels = {'kind': 'Ferramenta', 'title': 'O que você vai estudar ou fazer?', 'subject': 'Matéria (opcional)', 'time': 'Horário'}
        widgets = {'time': forms.TimeInput(attrs={'type': 'time'})}

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if not title:
            raise forms.ValidationError('Escreva uma descrição.')
        return title

    def clean(self):
        data = super().clean()
        if data.get('kind') == 'schedule':
            if data.get('day') is None:
                self.add_error('day', 'Escolha um dia para o cronograma.')
            if not data.get('time'):
                self.add_error('time', 'Informe o horário de estudo.')
        else:
            data['day'], data['time'] = None, None
        if data.get('kind') == 'reminder' and not data.get('due'):
            self.add_error('due', 'Informe quando o lembrete deve aparecer.')
        return data
