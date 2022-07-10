from django.test import TestCase
from datetime import datetime, timezone

from events.models import Event, Candidacy
from common.models import User
from .app import register_new_candidacy
from .core import CandidateCandidacyRequest
from .forms import IndividualCandidacyForm


class TestObjectSequence:
    _event = 0

    @classmethod
    def next_event_seq_num(cls):
        def event_sequence_generator():
            yield cls._event
            cls._event += 1

        return next(event_sequence_generator())

test_object_sequence = TestObjectSequence()


def new_test_event(
    name: str = None,
    description: str = None,
    date_and_time: datetime = None,
    location: str = None,
    max_participants: int = None,
    candidate_candidacy_requests: list[User] = None,
) -> Event:

    event_seq_num = test_object_sequence.next_event_seq_num()

    if name is None:
        name = f'Test Event {event_seq_num}'
    if description is None:
        description = f'Test Event {event_seq_num} description'
    if date_and_time is None:
        date_and_time = datetime.utcnow().astimezone(timezone.utc)
    if location is None:
        location = f'Test Event {event_seq_num} location'
    if max_participants is None:
        max_participants = 10

    event = Event.factory(
        name,
        description,
        date_and_time,
        location,
        max_participants,
    )
    if candidate_candidacy_requests:
        Candidacy.from_event_and_candidate_candidacy_requests(event, candidate_candidacy_requests)

    return event

class TestEvent(TestCase):
    def setUp(self) -> None:
        self.default_user = User(username='test_user')
        self.default_user.save()

    def tearDown(self) -> None:
        pass

    def test_is_created(self):
        Event.factory(
            name='Test Event',
            description='Test Event Description',
            date_and_time='2020-01-01T00:00:00Z',
            location='Test Event Location',
            max_participants=10,
        )

        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().name, 'Test Event')

    def test_can_have_candidacies(self):
        event = new_test_event()
        candidate_candidacy_request = CandidateCandidacyRequest(
            candidate=self.default_user,
            as_player=True,
        )

        register_new_candidacy(event, [candidate_candidacy_request])

        self.assertEqual(self.default_user.candidacies.count(), 1)
        new_candidacy = self.default_user.candidacies.first()
        self.assertEqual(new_candidacy.event, event)
        self.assertEqual(new_candidacy.candidates.count(), 1)
        self.assertEqual(new_candidacy.candidates.first(), self.default_user)


class TestAllEvents(TestCase):
    def setUp(self) -> None:
        self.view_path = '/events/'
        self.list_event_template = 'events/events.html'
        self.default_user = User(username='test_user')
        self.default_user.set_password('test_password')
        self.default_user.save()
        self.client.login(username=self.default_user.username, password='test_password')
    
    def tearDown(self) -> None:
        self.client.logout()

    def test_without_events_returns_no_events(self):
        response = self.client.get(self.view_path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,self.list_event_template)
        self.assertEqual(response.context['events'].count(), 0)

    def test_with_events_returns_events(self):
        nb_events = 2
        [new_test_event() for _ in range(nb_events)]

        response = self.client.get(self.view_path, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.list_event_template)
        self.assertEqual(response.context['events'].count(), nb_events)

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.view_path)

        self.assertRedirects(response, '/accounts/login/?next=/events/')

    def test_with_events_displays_event_name(self):
        event = new_test_event()

        response = self.client.get(self.view_path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.list_event_template)
        self.assertIn(event.name, response.content.decode())

    def test_with_events_display_register_button(self):
        new_test_event()

        response = self.client.get(self.view_path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.list_event_template)
        self.assertIn('Postuler', response.content.decode())


class TestEventRegisterCandidacy(TestCase):
    def setUp(self) -> None:
        self.view_path = '/events/register/'
        self.default_user = User(username='test_user')
        self.default_user.set_password('test_password')
        self.default_user.save()
        self.event_to_register_to = new_test_event()
        self.client.login(username=self.default_user.username, password='test_password')

    def tearDown(self) -> None:
        pass

    def test_register_adds_candidacy_to_event(self):
        self.assertEqual(self.event_to_register_to.candidacies.count(), 0)
        individual_candidacy_form_response = {
            'player': ['on'],
            'speaker': ['on'],
            'arbiter': ['on'],
            'disk_jockey': ['on'],
        }

        response = self.client.post(
            self.view_path,
            {
                'event_uuid': self.event_to_register_to.uuid,
                **individual_candidacy_form_response,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        event_with_registration = Event.objects.get(uuid=self.event_to_register_to.uuid)
        self.assertEqual(event_with_registration.candidacies.count(), 1)

        candidacy = event_with_registration.candidacies.first()
        self.assertEqual(candidacy.candidates.all()[0], self.default_user)
        self.assertEqual(candidacy.event, self.event_to_register_to)

    def test_that_a_candidacy_is_added_with_at_least_one_role_per_candidate(self):
        self.assertEqual(self.event_to_register_to.candidacies.count(), 0)
        individual_candidacy_form_response = {
        }

        response = self.client.post(
            self.view_path,
            {
                'event_uuid': self.event_to_register_to.uuid,
                **individual_candidacy_form_response,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.event_to_register_to.candidacies.count(), 0)


class TestEventUnregisterCandidacy(TestCase):
    def setUp(self) -> None:
        self.events_view_path = '/events/'
        self.default_user = User(username='test_user')
        self.default_user.set_password('test_password')
        self.default_user.save()
        candidate_candidacy_request = CandidateCandidacyRequest(
            candidate=self.default_user,
            as_player=True,
        )
        self.event_to_unregister_from = new_test_event(
            candidate_candidacy_requests=[candidate_candidacy_request],
        )
        self.client.login(username=self.default_user.username, password='test_password')

    def tearDown(self) -> None:
        pass

    def test_removes_candidacy_from_event(self):
        self.assertEqual(self.event_to_unregister_from.candidacies.count(), 1)
        path = f'/events/{self.event_to_unregister_from.uuid}/candidacies/{self.event_to_unregister_from.candidacies.first().uuid}/'
        response = self.client.post(
            path,
            follow=True,
        )

        self.assertRedirects(response, self.events_view_path)

        event_with_registration = Event.objects.get(uuid=self.event_to_unregister_from.uuid)
        self.assertEqual(event_with_registration.candidacies.count(), 0)


class TestCandidacyModel(TestCase):
    def setUp(self) -> None:
        candidates = [
            User(username='test_user'),
            User(username='test_user2'),
        ]
        for candidate in candidates:
            candidate.save()

        self.event_to_candidate_to = new_test_event()
        self.candidate_candidacy_requests = [
            CandidateCandidacyRequest(
                candidate=candidate,
                as_player=True,
            ) for candidate in candidates
        ]

    def test_create_candidacy_can_be_created(self):
        Candidacy.from_event_and_candidate_candidacy_requests(self.event_to_candidate_to, self.candidate_candidacy_requests)

    def test_candidacy_must_be_linked_to_an_event(self):
        with self.assertRaises(ValueError) as e:
            Candidacy.from_event_and_candidate_candidacy_requests(None, self.candidate_candidacy_requests)
        
        self.assertEqual(str(e.exception), 'An event is required to create a candidacy')

    def test_candidacy_must_be_linked_to_at_least_a_candidate(self):
        Candidacy.from_event_and_candidate_candidacy_requests(self.event_to_candidate_to, self.candidate_candidacy_requests[-1:])
        with self.assertRaises(ValueError) as e:
            Candidacy.from_event_and_candidate_candidacy_requests(self.event_to_candidate_to, [])

        self.assertEqual(str(e.exception), 'At least one CandidacyCandidateRequest is required to create a candidacy')

        with self.assertRaises(ValueError) as e:
            Candidacy.from_event_and_candidate_candidacy_requests(self.event_to_candidate_to, None)

        self.assertEqual(str(e.exception), 'At least one CandidacyCandidateRequest is required to create a candidacy')


class TestCandidateCandidacyRequest(TestCase):
    def setUp(self) -> None:
        self.user = User(username='test_user')
        self.user.save()

    def test_can_be_created(self):
        candidate_candidacy_request = CandidateCandidacyRequest(
            candidate=self.user,
            as_player=True,
            as_arbiter=True,
            as_disk_jockey=True,
            as_speaker=True,
        )

        self.assertEqual(candidate_candidacy_request.candidate, self.user)
        self.assertTrue(candidate_candidacy_request.as_player)
        self.assertTrue(candidate_candidacy_request.as_arbiter)
        self.assertTrue(candidate_candidacy_request.as_disk_jockey)
        self.assertTrue(candidate_candidacy_request.as_speaker)

    def test_cannot_be_created_without_at_least_one_role(self):
        parameters_to_tweak = {
            'as_player': True,
            'as_arbiter': True,
            'as_disk_jockey': True,
            'as_speaker': True,
        }
        default_parameters = {
            'as_player': False,
            'as_arbiter': False,
            'as_disk_jockey': False,
            'as_speaker': False,
        }
        for parameter, value in parameters_to_tweak.items():
            test_valid_parameters = default_parameters.copy()
            test_valid_parameters[parameter] = value
            CandidateCandidacyRequest(
                candidate=self.user,
                **test_valid_parameters,
            )
        with self.assertRaises(ValueError) as e:
            CandidateCandidacyRequest(
                candidate=self.user,
                as_player=False,
                as_arbiter=False,
                as_disk_jockey=False,
                as_speaker=False,
            )

        self.assertEqual(str(e.exception), 'At least one role is required to create a candidacy request')
