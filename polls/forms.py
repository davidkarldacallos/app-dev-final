import pytz

from django import forms
from django.contrib.auth.models import User
from django.forms import BaseFormSet, ClearableFileInput, inlineformset_factory
from django.utils import timezone
from .models import UserProfile, Poll, Question, Choice, Vote, Comment

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput,
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput,
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
    )
    email = forms.EmailField(
        required=False,
    )

    def save(self, commit=True):
        user_profile = self.instance
        cleaned_data = self.cleaned_data
        user = User.objects.create_user(
            username=cleaned_data['username'],
            email=cleaned_data['email'],
            password=cleaned_data['password1'],
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
        )
        if commit:
            user_profile.user = user
            user_profile.save()
        return user_profile

    class Meta:
        model = UserProfile
        fields = ['bio', 'birthdate']
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }

class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput,
    )
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput,
    )


class PollForm(forms.ModelForm):
    author = forms.ModelChoiceField(
        queryset=UserProfile.objects.all(),
        widget=forms.HiddenInput,
        required=False,
    )
    expires_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['author'].initial = UserProfile.objects.get(user=self.request.user)

    def clean_author(self):
        print(f'clean author got: {self.fields["author"].initial}')
        return self.fields['author'].initial

    def save(self, commit=True):
        poll = self.instance
        cleaned_data = self.cleaned_data
        poll.author = cleaned_data['author']
        poll.image = cleaned_data['image']
        poll.title = cleaned_data['title']
        poll.description = cleaned_data['description']
        poll.expires_at = cleaned_data['expires_at']
        poll.hidden = cleaned_data['hidden']
        # poll = Poll.objects.create(
        #     author=cleaned_data['author'],
        #     image=cleaned_data['image'],
        #     title=cleaned_data['title'],
        #     description=cleaned_data['description'],
        #     expires_at=cleaned_data['expires_at'],
        #     hidden=cleaned_data['hidden'],
        # )
        if commit:
            poll.save()
        return poll

    class Meta:
        model = Poll
        fields = ['author', 'image', 'title', 'description', 'expires_at', 'hidden']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']

ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=1, min_num=1, validate_min=True)
QuestionFormSet = inlineformset_factory(Poll, Question, form=QuestionForm, extra=1, min_num=1, validate_min=True)

class VoteForm(forms.Form):
    voter = forms.ModelChoiceField(
        queryset=UserProfile.objects.all(),
        widget=forms.HiddenInput,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['voter'].initial = UserProfile.objects.get(user=self.request.user)

    def clean_voter(self):
        return self.fields['voter'].initial
    
    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        vote = Vote.objects.create(
            voter=cleaned_data['voter'],
            choice=cleaned_data['choice'],
        )
        return vote

    class Meta:
        model = Vote
        fields = ['voter', 'choice']