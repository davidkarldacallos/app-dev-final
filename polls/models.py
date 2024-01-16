from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    birthdate = models.DateField()
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name_plural = "User profiles"

class Poll(BaseModel):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='polls', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    views = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    hidden = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.votes = self.votes + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Polls"

class Question(BaseModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name_plural = "Questions"

class Choice(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name_plural = "Choices"

class Vote(BaseModel):
    voter = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.voter.user.username} voted for {self.choice.text}"
    
    class Meta:
        verbose_name_plural = "Votes"

class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"{self.user.username} commented on {self.poll.title}: {self.text}"
    
    class Meta:
        verbose_name_plural = "Comments"


