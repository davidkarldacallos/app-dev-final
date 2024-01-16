from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.forms import formset_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import PollForm, UserProfileForm, UserLoginForm
from .models import UserProfile, Poll, Question, Choice, Vote, Comment


def index(request):
    return render(request, 'base.html')

def register_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            user.user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user.user)
            messages.success(request, 'Registration successful!')
            return redirect('polls:poll-list')
    else:
        form = UserProfileForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('polls:poll-list')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful!')
    return redirect('polls:index')

class PollListView(LoginRequiredMixin, ListView):
    model = Poll
    template_name = 'poll_list.html'
    context_object_name = 'polls'
    paginate_by = 3
    # ordering = '-expires_at'
    ordering = '-created_at'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')

        if search_query:
            queryset = queryset.exclude(hidden=True).filter(
                Q(author__user__username=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset

class PollDetailView(LoginRequiredMixin, DetailView):
    model = Poll
    template_name = 'poll_detail.html'
    context_object_name = 'poll'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll = self.get_object()
        is_author = poll.author.user == self.request.user
        has_voted = Vote.objects.filter(voter__user=self.request.user, choice__question__poll=poll).exists()
        context['already_voted'] = has_voted
        context['question'] = Question.objects.filter(poll=poll).first()
        context['choices'] = Choice.objects.filter(question__poll=poll)
        context['is_author'] = is_author
        if is_author:
            context['choice_stats'] = [
                {
                    'choice': choice,
                    'votes': Vote.objects.filter(choice=choice).count(),
                }
                for choice in context['choices']
            ]
        return context

class PollCreateView(LoginRequiredMixin, CreateView):
    model = Poll
    form_class = PollForm
    template_name = 'poll_create.html'
    success_url = reverse_lazy('polls:poll-list')

    def form_invalid(self, form):
        print(f'form.errors: {form.errors}')
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        with transaction.atomic():
            question = Question.objects.create(poll=self.object, text=self.request.POST.get('formtext'))
            for choice in self.request.POST.getlist('choices[]'):
                Choice.objects.create(question=question, text=choice)

        return response

class PollUpdateView(LoginRequiredMixin, UpdateView):
    model = Poll
    template_name = 'poll_form.html'
    form_class = PollForm
    context_object_name = 'poll'
    success_url = reverse_lazy('polls:poll-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        choices = Choice.objects.filter(question__poll=self.object)
        context['question'] = Question.objects.filter(poll=self.object).first()
        context['choices'] = Choice.objects.filter(question__poll=self.object)
        return context

    def form_invalid(self, form):
        print(f'form.errors: {form.errors}')
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        # Save the form to get the latest instance
        self.object = form.save()

        # Delete existing choices associated with the poll
        Choice.objects.filter(question__poll=self.object).delete()

        # Create new choices for the updated poll
        question = Question.objects.filter(poll=self.object).first()

        if question is None:
            raise Http404("No question found for the given poll.")

        question.text = self.request.POST.get('formtext')
        question.save()

        for choice in self.request.POST.getlist('choices[]'):
            Choice.objects.create(question=question, text=choice)

        return super().form_valid(form)

class PollDeleteView(LoginRequiredMixin, DeleteView):
    model = Poll
    template_name = 'poll_confirm_delete.html'
    context_object_name = 'poll'
    success_url = reverse_lazy('polls:poll-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Poll deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
class VoteCreateView(LoginRequiredMixin, CreateView):
    model = Vote
    fields = []  # No fields to display, as they are handled in the form

    def form_valid(self, form):
        choice_id = self.request.POST.get('choice_id')
        choice = Choice.objects.get(id=choice_id)
        poll = choice.question.poll

        # Check if the user has already voted
        has_voted = Vote.objects.filter(voter__user=self.request.user, choice__question__poll=poll).exists()
        if has_voted:
            messages.error(self.request, 'You have already voted in this poll.')
            return redirect('polls:poll-detail', pk=choice.question.poll.pk)

        # Create a new vote
        vote = form.save(commit=False)
        vote.voter = self.request.user.userprofile  # Assuming user is logged in
        vote.choice = choice
        vote.save()
        poll.votes += 1
        poll.views += 1
        poll.save()

        messages.success(self.request, 'Vote submitted successfully.')
        return redirect('polls:poll-detail', pk=choice.question.poll.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid vote submission.')
        return redirect('polls:poll-list')  # Redirect to some appropriate page

    def get_success_url(self):
        # You can customize the success URL if needed
        return reverse('polls:poll-list')
