from django.test import TestCase
from .models import Task
from common.models import BaseModel, User


class TestTask(TestCase):
    def test_task_model_name_is_tasks(self):
        self.assertEqual(Task._meta.db_table, 'task')

    def test_task_model_can_be_created_with_mandatory_field(self):
        task_model = Task(
            name='Test task',
        )

        self.assertIsInstance(task_model, BaseModel)
        self.assertTrue(task_model.name, 'Test task')

    def test_task_model_can_be_created_with_all_fields(self):
        task_model = Task(
            name='Test task',
            description='Test task description',
        )

        self.assertIsInstance(task_model, BaseModel)
        self.assertTrue(task_model.name, 'Test task')
        self.assertTrue(task_model.description, 'Test task description')


class TestTasksDisplay(TestCase):
    def test_task_display_exists(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)

    def test_task_display_has_all_tasks(self):
        Task(name='Test task').save()
        Task(name='Test task 2').save()

        response = self.client.get("/tasks/")

        self.assertContains(response, 'Test task')
        self.assertContains(response, 'Test task 2')


class TestTaskCanBeClaimedByUser(TestCase):
    def setUp(self):
        self.task = Task(name='Test task')
        self.task.save()
        self.user = User(username='test_user')
        self.user.set_password('test_password')
        self.user.save()
        self.client.login(username=self.user.username, password='test_password')

    def tearDown(self) -> None:
        pass

    def test_task_can_have_users(self):
        self.task.contributers.add(self.user)
        self.assertEqual(self.task.contributers.count(), 1)
        self.assertEqual(self.task.contributers.first(), self.user)
