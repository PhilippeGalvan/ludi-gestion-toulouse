from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    """
    Base model for all models
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
