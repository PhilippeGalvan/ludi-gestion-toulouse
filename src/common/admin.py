from django.contrib import admin

from events.models import Event
from tasks.models import Task
from common.models import User


class EventInLine(admin.TabularInline):
    model = Event.participants.through
    extra = 0


class TaskInLine(admin.TabularInline):
    model = Task.contributers.through
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [
        EventInLine,
        TaskInLine,
    ]
