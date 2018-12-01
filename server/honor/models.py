from django.db import models


class Honor(models.Model):
    description = models.TextField()
    logo = models.ImageField()
