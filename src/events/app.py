from .models import Event, Candidacy
from common.models import User
from .core import CandidateCandidacyRequest


def register_new_candidacy(
    event: Event,
    candidate_candidacy_requests: list[CandidateCandidacyRequest],
) -> None:
    Candidacy.from_event_and_candidate_candidacy_requests(event, candidate_candidacy_requests)


def remove_candidacy(candidacy: Candidacy) -> None:
    candidacy.delete()
