from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Club(models.Model):
    
    CATEGORY_CHOICES = (
        ('books', 'Books'),
        ('movies', 'Movies'),
        ('music', 'Music'),
        ('games', 'Games')
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_clubs')
    members = models.ManyToManyField(User, through='Membership')
    
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships')
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'club')
    
class Pick(models.Model):
    title = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='picks')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_picks')
    is_active = models.BooleanField(default=True)
    begin_date = models.DateTimeField(auto_now_add=True)
    
class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='authored_comments')
    pick = models.ForeignKey(Pick, on_delete=models.CASCADE, related_name='comments')
    published_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-published_date']
        

class Nomination(models.Model):
    title = models.CharField(max_length=255)
    creator = models.CharField(max_length=255)
    club = models.ForeignKey(Club, on_delete=models.PROTECT, related_name='nominations')
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='authored_nominations')
    date = models.DateTimeField(auto_now_add=True)
    
    
class Vote(models.Model):
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='votes')
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('nomination', 'user')