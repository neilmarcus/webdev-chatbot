from django.utils.timezone import localtime, now
from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    Message = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.author.username}: {self.Message[:20]}"

    def get_local_timestamp(self):
        return localtime(self.timestamp)

