from uuid import uuid4
from datetime import datetime

from django.db import models, transaction
from common.models import User, BaseModel
from .core import CandidateCandidacyRequest


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
    ):
        event = cls(name=name, description=description, date_and_time=date_and_time, location=location, max_participants=max_participants)
        event.save()
        return event


class Candidacy(BaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='candidacies')
    candidates = models.ManyToManyField(User, related_name='candidacies', through='CandidacyCandidate')

    class Meta:
        db_table = 'candidacy'

    @classmethod
    @transaction.atomic()
    def from_event_and_candidate_candidacy_requests(cls, event: Event, candidate_candidacy_requests: list[CandidateCandidacyRequest]) -> "Candidacy":
        if not event:
            raise ValueError('An event is required to create a candidacy')
        if not candidate_candidacy_requests:
            raise ValueError('At least one CandidacyCandidateRequest is required to create a candidacy')

        candidacy = cls(event=event)
        candidacy.save()
        for candidate_candidacy_request in candidate_candidacy_requests:
            CandidacyCandidate.from_candidate_candidacy_request_and_candidacy(
                candidate_candidacy_request=candidate_candidacy_request,
                candidacy=candidacy,
            )

        return candidacy

    def __str__(self) -> str:
        return (
            f'Candidacy for {self.event.name} with >>'
            f'{", ".join(candidate.username for candidate in self.candidates.all())}<< '
            f'as candidate{"s" if len(self.candidates.all()) > 1 else ""}'
        )


class CandidacyCandidate(BaseModel):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    candidacy = models.ForeignKey(
        Candidacy,
        on_delete=models.CASCADE,
        related_name="detailed_candidates",
    )
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="detailed_candidacies",
    )
    player = models.BooleanField(default=False)
    speaker = models.BooleanField(default=False)
    arbiter = models.BooleanField(default=False)
    disk_jockey = models.BooleanField(default=False)

    class Meta:
        db_table = 'candidacy_candidate'

    @classmethod
    def from_candidate_candidacy_request_and_candidacy(
        cls,
        candidate_candidacy_request: CandidateCandidacyRequest,
        candidacy: Candidacy,
    ) -> "CandidacyCandidate":
        if not candidacy:
            raise ValueError('A candidacy is required to create a candidacy candidate')
        if not candidate_candidacy_request:
            raise ValueError('At least one candidate candidacy request is required to create a candidacy candidate')

        candidacy_candidate = cls(
            candidacy=candidacy,
            candidate=candidate_candidacy_request.candidate,
            player=candidate_candidacy_request.as_player,
            speaker=candidate_candidacy_request.as_speaker,
            arbiter=candidate_candidacy_request.as_arbiter,
            disk_jockey=candidate_candidacy_request.as_disk_jockey,
        )
        candidacy_candidate.save()
        return candidacy_candidate


    def __str__(self) -> str:
        return (
            f'Detailed candidacy for {self.candidacy.event.name} with >>'
            f'{self.candidate.username}<< as candidate'
        )
