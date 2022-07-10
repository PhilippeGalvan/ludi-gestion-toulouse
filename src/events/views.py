from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Event, Candidacy
from .app import remove_candidacy, register_new_candidacy
from .core import CandidateCandidacyRequest
from .forms import IndividualCandidacyForm


class AllEventsView(LoginRequiredMixin, ListView):
    model = Event
    ordering = ['date_and_time']
    template_name = 'events/events.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["individual_candidacy_form"] = IndividualCandidacyForm()
        return context


@login_required
def register_candidacy(request, event_uuid: str):
    if request.method != 'POST':
        raise ValueError('Only POST requests are allowed')

    form = IndividualCandidacyForm(request.POST)
    if form.is_valid():
        event = Event.objects.get(pk=event_uuid)
        candidate_candidacy_requests = [
            CandidateCandidacyRequest(
                candidate=request.user,
                as_player=form.cleaned_data["player"],
                as_arbiter=form.cleaned_data["arbiter"],
                as_disk_jockey=form.cleaned_data["disk_jockey"],
                as_speaker=form.cleaned_data["speaker"],
            )
        ]
        register_new_candidacy(event, candidate_candidacy_requests)

    return redirect('events:all-events')


@login_required
def unregister_candidacy(request, event_uuid: str, candidacy_uuid: str):
    if request.method != 'POST':
        raise ValueError('Only POST requests are allowed')

    candidacy = Candidacy.objects.get(pk=candidacy_uuid)
    remove_candidacy(candidacy)
    return redirect('events:all-events')
