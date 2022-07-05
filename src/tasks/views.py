from django.views.generic import ListView

from .models import Task


class TaskListView(ListView):
    model = Task
    template_name: str = 'tasks/tasks.html'
    context_object_name = 'tasks'
