from django.test import TestCase
from .models import Task
from common.models import BaseModel


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
