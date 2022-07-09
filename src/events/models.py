from uuid import uuid4
from datetime import datetime

from django.db import models, transaction
from django import forms
from common.models import User, BaseModel


class Event(BaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField()
    description = models.TextField()
    date_and_time = models.DateTimeField()
    location = models.TextField()
    max_participants = models.PositiveIntegerField()

    @property
    def date_french_format(self):
        return self.date_and_time.strftime('%d/%m/%Y %H:%M')

    @property
    def candidates(self) -> set[User]:
        candidates = set()
        for candidacy in self.candidacies.all():
            for user in candidacy.candidates.all():
                candidates.add(user)
        return candidates

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'event'

    @classmethod
    @transaction.atomic()
    def factory(
        cls,
        name: str,
        description: str,
        date_and_time: datetime,
        location: str,
        max_participants: int,
        candidacy_as_list_of_users: list[User] = None,
    ):
        event = cls(name=name, description=description, date_and_time=date_and_time, location=location, max_participants=max_participants)
        event.save()
        if candidacy_as_list_of_users:
            Candidacy.from_event_and_candidates(event, candidacy_as_list_of_users)
        return event


class Candidacy(BaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='candidacies')
    candidates = models.ManyToManyField(User, related_name='candidacies', through='CandidacyCandidate')

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

    def __str__(self) -> str:
        return (
            f'Candidacy for {self.event.name} with >>'
            f'{", ".join(candidate.username for candidate in self.candidates.all())}<< '
            f'as candidate{"s" if len(self.candidates.all()) > 1 else ""}'
        )


class CandidacyCandidate(BaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    candidacy = models.ForeignKey(Candidacy, on_delete=models.CASCADE, related_name='detailed_candidacies')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='detailed_candidacies')
    player = models.BooleanField(default=False)
    speaker = models.BooleanField(default=False)
    arbiter = models.BooleanField(default=False)

    class Meta:
        db_table = 'candidacy_candidate'

    def __str__(self) -> str:
        return (
            f'Detailed candidacy for {self.candidacy.event.name} with >>'
            f'{self.candidate.username}<< as candidate'
        )
