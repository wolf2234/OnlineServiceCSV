from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

CHOICES = [
    ('1', 'Full name'),
    ('2', 'email'),
    ('3', 'job'),
    ('4', 'company'),
    ('5', 'date'),
    ('6', 'phone'),
    ('7', 'address'),
    ('8', 'Integer'),
]


class DataSchemas(models.Model):
    title = models.CharField("Name", max_length=100)
    column_separator = models.CharField("Column separator", max_length=100, default='')
    status = models.CharField("Status", max_length=100)
    modified = models.DateTimeField("Modified", auto_now=True)

    


class Schemas(models.Model):
    name = models.CharField("Column name", max_length=100)
    type = models.CharField("Type", max_length=100, choices=CHOICES)
    order = models.IntegerField("Order", default=0, validators=[MinValueValidator(0), MaxValueValidator(9)])
    data_schema = models.ForeignKey(DataSchemas, on_delete=models.CASCADE)


