from django.db import models
from angel.models import Angel
from datetime import datetime, timezone
from enum import Enum

_DATETIME_INF = datetime.max.replace(tzinfo=timezone.utc)


class TaskStatus(Enum):
    CREATED = 0
    ACCEPTED = 1
    COMPLETED = 2
    FINSIHED = 3
    CANCELED = -1


class Task(models.Model):
    description = models.TextField()
    # source_geometry
    # destination_geometry
    cost = models.FloatField()
    owner = models.ForeignKey(
        Angel, on_delete=models.PROTECT, related_name="owned_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    helper = models.ForeignKey(
        Angel,
        null=True,
        on_delete=models.PROTECT,
        related_name="helped_tasks")
    accepted_at = models.DateTimeField(default=_DATETIME_INF)
    completed_at = models.DateTimeField(default=_DATETIME_INF)
    finished_at = models.DateTimeField(default=_DATETIME_INF)
    canceled_at = models.DateTimeField(default=_DATETIME_INF)
    contribution = models.FloatField(null=True)

    status = models.IntegerField(
        choices=[(tag.value, tag.name.lower()) for tag in TaskStatus],
        default=TaskStatus.CREATED.value)

    def to_dict(self):
        return {
            'description': self.description,
            'cost': self.cost,
            'owner': self.owner.to_dict(),
            'create_at': self.created_at.timestamp(),
            'helper':
            self.helper.to_dict() if self.helper is not None else None,
            'accepted_at': self.accepted_at.timestamp(),
            'completed_at': self.completed_at.timestamp(),
            'finished_at': self.finished_at.timestamp(),
            'canceled_at': self.canceled_at.timestamp(),
            'contribution': self.contribution,
            'status': TaskStatus(self.status).name.lower(),
        }
