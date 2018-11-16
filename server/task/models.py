from django.db import models
from angel.models import Angel

from textwrap import shorten
from datetime import datetime


class Task(models.Model):
    description = models.CharField(max_length=300)
    cost = models.FloatField()
    point = models.IntegerField()

    created_time = models.DateTimeField(auto_now_add=True)
    finished_time = models.DateTimeField(default=datetime.max)
    is_finished = models.BooleanField(default=False)

    owner = models.ForeignKey(
        Angel,
        related_name='owned_task',
        on_delete=models.CASCADE,
    )
    helper = models.ForeignKey(
        Angel,
        related_name='accepted_tasks',
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return shorten(self.description, 12)
