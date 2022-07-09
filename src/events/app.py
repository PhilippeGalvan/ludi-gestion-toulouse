from .models import Event
from common.models import User


def add_participant_to_event(user: User, event: Event) -> None:
    event.participants.add(user)
    event.save()


def remove_participant_from_event(user: User, event: Event) -> None:
    event.participants.remove(user)
    event.save()
