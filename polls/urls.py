from django.urls import path
from .views import *

app_name = 'polls'

urlpatterns = [
    path('', index, name='index'),

    # Polls
    path('polls/', PollListView.as_view(), name='poll-list'),
    path('polls/<int:pk>/', PollDetailView.as_view(), name='poll-detail'),
    path('polls/create/', PollCreateView.as_view(), name='poll-create'),
    path('polls/<int:pk>/update/', PollUpdateView.as_view(), name='poll-update'),
    path('polls/<int:pk>/delete/', PollDeleteView.as_view(), name='poll-delete'),

    # Votes
    path('votes/<int:pk>/', VoteCreateView.as_view(), name='vote'),

    # login and register
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
]