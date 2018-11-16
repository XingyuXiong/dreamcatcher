from django.db import models

import math


class Angel(models.Model):
    nickname = models.CharField(max_length=30)
    registered_name = models.CharField(max_length=30)
    registered_id = models.CharField(max_length=30)
    score = models.IntegerField()
    identifier = models.CharField(max_length=128)

    def __str__(self):
        return self.nickname

    def calculate_point(self, cost):
        return math.floor(cost * 10)
