from decimal import Decimal

from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=50)


class TodoAnother(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)


class TodoYetAnother(models.Model):
    todo = models.ForeignKey(TodoAnother, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)


class TodoTree(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True)
    title = models.CharField(max_length=50)


class Pack(models.Model):
    SIZE_10x20 = Decimal(200.000)
    SIZE_10x10 = Decimal(100.000)
    SIZE_5x10 = Decimal(50.000)

    size_code_choices = (
        (SIZE_5x10, '5x10'),
        (SIZE_10x10, '10x10'),
        (SIZE_10x20, '10x20'),
    )
    size_code = models.DecimalField(max_digits=7,
                                    decimal_places=3,
                                    choices=size_code_choices,
                                    default=SIZE_10x20)
