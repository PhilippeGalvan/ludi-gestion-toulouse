from django.test import TestCase
from datetime import datetime, timezone

from events.models import Event, Candidacy
from common.models import User
from .app import add_participant_to_event


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
    participants: list[User] = None,
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
    if participants is None:
        participants = []

    event = Event.new_with_participants(
        name,
        description,
        date_and_time,
        location,
        max_participants,
        participants
    )

    return event

class TestEvent(TestCase):
    def setUp(self) -> None:
        self.default_user = User(username='test_user')
        self.default_user.save()

    def tearDown(self) -> None:
        Event.objects.all().delete()
        User.objects.all().delete()

    def test_is_created(self):
        Event.new_with_participants(
            name='Test Event',
            description='Test Event Description',
            date_and_time='2020-01-01T00:00:00Z',
            location='Test Event Location',
            max_participants=10,
            participants=[]
        ).save()

        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().name, 'Test Event')

    def test_can_have_participants(self):
        event = new_test_event(participants=[])

        add_participant_to_event(self.default_user, event)

        self.assertEqual(self.default_user.events.count(), 1)
        self.assertEqual(self.default_user.events.first(), event)
        self.assertEqual(Event.objects.first().participants.count(), 1)


class TestAllEvents(TestCase):
    def setUp(self) -> None:
        self.view_path = '/events/'
        self.list_event_template = 'events/events.html'
        self.default_user = User(username='test_user')
        self.default_user.set_password('test_password')
        self.default_user.save()
        self.client.login(username=self.default_user.username, password='test_password')
    
    def tearDown(self) -> None:
        Event.objects.all().delete()
        User.objects.all().delete()
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
        self.assertIn('S\'inscrire', response.content.decode())


class TestEventRegisterMember(TestCase):
    def setUp(self) -> None:
        self.view_path = '/events/register/'
        self.default_user = User(username='test_user')
        self.default_user.set_password('test_password')
        self.default_user.save()
        self.event_to_register_to = new_test_event()
        self.client.login(username=self.default_user.username, password='test_password')

    def tearDown(self) -> None:
        Event.objects.all().delete()
        User.objects.all().delete()

    def test_register_adds_member_to_event(self):
        self.assertEqual(self.event_to_register_to.participants.count(), 0)

        response = self.client.post(
            self.view_path,
            {
                'event_uuid': self.event_to_register_to.uuid
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        event_with_registration = Event.objects.get(uuid=self.event_to_register_to.uuid)
        self.assertEqual(event_with_registration.participants.count(), 1)
        self.assertEqual(event_with_registration.participants.first(), self.default_user)


class TestEventUnregisterMember(TestCase):
    def setUp(self) -> None:
        self.view_path = '/events/unregister/'
        self.events_view_path = '/events/'
        self.default_user = User(username='test_user')
        self.default_user.set_password('test_password')
        self.default_user.save()
        self.event_to_unregister_from = new_test_event(participants=[self.default_user])
        self.client.login(username=self.default_user.username, password='test_password')

    def tearDown(self) -> None:
        Event.objects.all().delete()
        User.objects.all().delete()

    def test_unregister_removes_member_from_event(self):
        self.assertEqual(self.event_to_unregister_from.participants.count(), 1)

        response = self.client.post(
            self.view_path,
            {
                'event_uuid': self.event_to_unregister_from.uuid
            },
            follow=True,
        )

        self.assertRedirects(response, self.events_view_path)

        event_with_registration = Event.objects.get(uuid=self.event_to_unregister_from.uuid)
        self.assertEqual(event_with_registration.participants.count(), 0)


class TestCandidacyModel(TestCase):
    def setUp(self) -> None:
        self.candidates = [
            User(username='test_user'),
            User(username='test_user2'),
        ]
        for candidate in self.candidates:
            candidate.save()

        self.event_to_candidate_to = new_test_event()

    def test_create_candidacy_can_be_created(self):
        Candidacy.from_event_and_candidates(self.event_to_candidate_to, self.candidates)

    def test_candidacy_must_be_linked_to_an_event(self):
        with self.assertRaises(ValueError) as e:
            Candidacy.from_event_and_candidates(None, self.candidates)
        
        self.assertEqual(str(e.exception), 'An event is required to create a candidacy')

    def test_candidacy_must_be_linked_to_at_least_a_candidate(self):
        Candidacy.from_event_and_candidates(self.event_to_candidate_to, self.candidates[-1:])
        with self.assertRaises(ValueError) as e:
            Candidacy.from_event_and_candidates(self.event_to_candidate_to, [])

        self.assertEqual(str(e.exception), 'At least one candidate is required to create a candidacy')

        with self.assertRaises(ValueError) as e:
            Candidacy.from_event_and_candidates(self.event_to_candidate_to, None)

        self.assertEqual(str(e.exception), 'At least one candidate is required to create a candidacy')

