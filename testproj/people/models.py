from django.db import models
from django.utils.safestring import mark_safe


class Identity(models.Model):
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True, help_text=mark_safe("<strong>Here's some HTML!</strong>"))


class Person(models.Model):
    identity = models.OneToOneField(Identity, related_name='person', on_delete=models.PROTECT)
