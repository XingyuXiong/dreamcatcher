from django.db import models
from angel.models import Angel
from datetime import datetime, timezone


_DATETIME_INF = datetime.max.replace(tzinfo=timezone.utc)


class Task(models.Model):
    description = models.TextField()
    # source_geometry
    # destination_geometry
    cost = models.FloatField()
    owner = models.ForeignKey(
        Angel, on_delete=models.PROTECT, related_name="owned_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    helper = models.ForeignKey(
        Angel, null=True, on_delete=models.PROTECT,
        related_name="helped_tasks")
    accepted_at = models.DateTimeField(default=_DATETIME_INF)
    completed_at = models.DateTimeField(default=_DATETIME_INF)
    finished_at = models.DateTimeField(default=_DATETIME_INF)
    contribution = models.FloatField(null=True)
