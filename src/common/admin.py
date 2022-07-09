from django.contrib import admin

from events.models import Candidacy
from tasks.models import Task
from common.models import User


class CandidacyInLine(admin.TabularInline):
    model = Candidacy.candidates.through
    verbose_name = 'candidacy'
    verbose_name_plural = 'candidacies'
    extra = 0


class TaskInLine(admin.TabularInline):
    model = Task.contributers.through
    verbose_name = 'task'
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [
        CandidacyInLine,
        TaskInLine,
    ]
