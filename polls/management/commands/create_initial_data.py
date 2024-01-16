import random
import pytz
import ssl

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
from io import BytesIO
from urllib.request import urlopen, Request
from urllib.parse import urlparse

from polls.models import UserProfile, Poll, Question, Choice, Vote, Comment


fake = Faker()
fake_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
ssl._create_default_https_context = ssl._create_unverified_context

class Command(BaseCommand):
    help = 'Populate the database with fake data'

    def handle(self, *args, **options):
        self.create_superuser_if_not_exists()
        self.create_users()
        self.create_polls()

    def create_superuser_if_not_exists(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@yahoo.com', 'pass')

    def create_users(self):
        for _ in range(10):
            username = fake.user_name()
            email = fake.email()
            password = fake.password()

            user = User.objects.create_user(username=username, email=email, password=password)

        for user in User.objects.all():
            bio = fake.paragraph()
            birthdate = fake.date_of_birth(tzinfo=pytz.UTC)

            UserProfile.objects.create(
                user=user,
                bio=bio,
                birthdate=birthdate
            )

    def create_polls(self):
        users = UserProfile.objects.all()

        for _ in range(20):
            author = random.choice(users)
            title = fake.sentence()
            description = fake.paragraph()
            views = fake.random_int(0, 1000)
            votes = fake.random_int(0, 500)
            expires_at = timezone.now() + timedelta(days=fake.random_int(1, 30))
            hidden = fake.boolean()

            poll = Poll.objects.create(
                author=author,
                title=title,
                description=description,
                views=views,
                votes=votes,
                expires_at=expires_at,
                hidden=hidden
            )

            url = fake.image_url()
            req = Request(url, headers={'User-Agent': fake_user_agent})
            image_file_name = urlparse(url).path.split('/')[-1] + '.jpg'
            image_file_content = BytesIO(urlopen(req).read())
            poll.image.save(image_file_name, image_file_content)

            question_text = fake.sentence()
            question = Question.objects.create(
                poll=poll,
                text=question_text
            )

            self.create_choices_votes_comments(question)

    def create_choices_votes_comments(self, question):
        for _ in range(3):
            choice_text = fake.word()
            score = fake.random_int(0, 100)

            choice = Choice.objects.create(
                question=question,
                text=choice_text,
                score=score
            )

            for _ in range(2):
                voter = random.choice(UserProfile.objects.all())

                Vote.objects.create(
                    voter=voter,
                    choice=choice
                )

            for _ in range(2):
                user = random.choice(User.objects.all())
                comment_text = fake.paragraph()

                Comment.objects.create(
                    user=user,
                    poll=question.poll,
                    text=comment_text
                )

        self.stdout.write(self.style.SUCCESS('Fake data has been successfully created.'))
