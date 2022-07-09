from .models import Event, Candidacy
from common.models import User


def add_candidacy_to_event(event: Event, users: list[User]) -> None:
    Candidacy.from_event_and_candidates(event, users)


def remove_candidacy(candidacy: Candidacy) -> None:
    candidacy.delete()
