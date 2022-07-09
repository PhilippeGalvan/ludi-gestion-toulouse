from django.contrib import admin

from .models import Event, Candidacy

admin.site.register(Candidacy)


class CandidacyInline(admin.TabularInline):
    model = Candidacy
    extra = 0


class EventAdmin(admin.ModelAdmin):
    inlines = [CandidacyInline]


admin.site.register(Event, EventAdmin)
