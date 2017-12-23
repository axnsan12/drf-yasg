from django.db import models


class Article(models.Model):
    title = models.CharField(help_text="title model help_text", max_length=255, blank=False, unique=True)
    body = models.TextField(help_text="article model help_text", max_length=5000, blank=False)
    slug = models.SlugField(help_text="slug model help_text", unique=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('auth.User', related_name='articles', on_delete=models.CASCADE)

    cover = models.ImageField(upload_to='article/original/', blank=True)
