from django.template import Library

from events.models import Event
from common.models import User

register = Library()


@register.filter(name='is_candidating_alone')
def is_candidating_alone(user: User, event: Event) -> bool:
    for candidacy in event.candidacies.all():
        candidates = candidacy.candidates.all()
        if (len(candidates) == 1) and (user in candidates):
            return True
    return False
