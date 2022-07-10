from attrs import frozen

from common.models import User


@frozen
class CandidateCandidacyRequest:
    candidate: User
    as_player: bool = False
    as_arbiter: bool = False
    as_disk_jockey: bool = False
    as_speaker: bool = False

    def __attrs_post_init__(self):
        if not any([self.as_player, self.as_arbiter, self.as_disk_jockey, self.as_speaker]):
            raise ValueError('At least one role is required to create a candidacy request')
