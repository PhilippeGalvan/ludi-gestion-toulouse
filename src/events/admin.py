from django.contrib import admin

from .models import Event, Candidacy


class CandidateInLine(admin.TabularInline):
    model = Candidacy.candidates.through
    verbose_name = 'candidate'
    verbose_name_plural = 'candidates'
    extra = 0

class CandidacyAdmin(admin.ModelAdmin):
    inlines = [
        CandidateInLine,
    ]

admin.site.register(Candidacy, CandidacyAdmin)


class CandidacyInline(admin.TabularInline):
    model = Candidacy
    verbose_name = 'candidacy'
    verbose_name_plural = 'candidacies'
    extra = 0


class EventAdmin(admin.ModelAdmin):
    inlines = [CandidacyInline]


admin.site.register(Event, EventAdmin)
