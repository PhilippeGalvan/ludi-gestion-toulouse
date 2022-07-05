from uuid import uuid4

from django.db import models

from common.models import BaseModel


class Task(BaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField()
    description = models.TextField()

    class Meta:
        db_table = 'task'
