from django.contrib import admin

from events.models import Event
from common.models import User


class EventInLine(admin.TabularInline):
    model = Event.participants.through
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [
        EventInLine,
    ]
