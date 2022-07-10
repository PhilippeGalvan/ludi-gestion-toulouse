from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Event, Candidacy
from .app import remove_candidacy, register_new_candidacy
from .core import CandidateCandidacyRequest


class AllEventsView(LoginRequiredMixin, ListView):
    model = Event
    ordering = ['date_and_time']
    template_name = 'events/events.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user

        return context


@login_required
def register_member(request):
    if request.method != 'POST':
        raise ValueError('Only POST requests are allowed')

    event = Event.objects.get(pk=request.POST["event_uuid"])
    candidate_candidacy_requests = [
        CandidateCandidacyRequest(
            candidate=request.user,
            as_player=True,
        )
    ]
    register_new_candidacy(event, candidate_candidacy_requests)

    return redirect('events:all-events')


@login_required
def unregister_member(request):
    if request.method != 'POST':
        raise ValueError('Only POST requests are allowed')

    candidacy = Candidacy.objects.get(pk=request.POST["candidacy_uuid"])
    remove_candidacy(candidacy)
    return redirect('events:all-events')
