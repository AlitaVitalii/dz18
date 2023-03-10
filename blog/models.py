from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.


# class Author(models.Model):
#     user = models.OneToOneField(User,on_delete=models.SET_NULL, null=True)
#     bio = models.TextField(max_length=500)
#
#     def __str__(self):
#         return self.user.username
#
#     def get_absolute_url(self):
#         return reverse('author-detail', args=[str(self.pk)])


class Blog(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_date = models.DateField(default=date.today)
    is_posted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog-detail', args=[str(self.pk)])


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField(max_length=1000)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        # title_text = self.text[:15] + '...'
        return self.text
