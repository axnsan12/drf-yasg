from django.db import models

LANGUAGE_CHOICES = sorted((item, item) for item in ('cpp', 'python', 'js'))
STYLE_CHOICES = sorted((item, item) for item in ('solarized-dark', 'monokai', 'vim'))


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField(help_text="code model help text")
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='solarized-dark', max_length=100)

    class Meta:
        ordering = ('created',)

    @property
    def owner_snippets(self):
        return Snippet._default_manager.filter(owner=self.owner)

    @property
    def nullable_secondary_language(self):
        return None


class SnippetViewer(models.Model):
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='viewers')
    viewer = models.ForeignKey('auth.User', related_name='snippet_views', on_delete=models.CASCADE)
