from uuid import uuid4

from django.db import models
from common.models import User, BaseModel


class Event(BaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField()
    description = models.TextField()
    date_and_time = models.DateTimeField()
    location = models.TextField()
    max_participants = models.PositiveIntegerField()
    participants = models.ManyToManyField(User, blank=True, related_name='events')

    @property
    def date_french_format(self):
        return self.date_and_time.strftime('%d/%m/%Y %H:%M')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'event'


class Candidacy(BaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    candidates = models.ManyToManyField(User, blank=True, related_name='candidacies')

    class Meta:
        db_table = 'candidacy'

    @classmethod
    def from_event_and_candidates(cls, event: Event, candidates: list[User]) -> "Candidacy":
        if not event:
            raise ValueError('An event is required to create a candidacy')
        if not candidates:
            raise ValueError('At least one candidate is required to create a candidacy')

        candidacy = cls(event=event)
        candidacy.save()
        candidacy.candidates.set(candidates)
        return candidacy
