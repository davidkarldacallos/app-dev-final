from django.contrib import admin
from .models import UserProfile, Poll, Question, Choice, Vote, Comment

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Poll)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Vote)
admin.site.register(Comment)
