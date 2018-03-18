from django.db import models


class Identity(models.Model):
    firstName = models.CharField(max_length=30, null=True)
    lastName = models.CharField(max_length=30, null=True)


class Person(models.Model):
    Identity = models.OneToOneField(Identity, related_name='person',
                                    on_delete=models.PROTECT)
