from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Event
from .app import add_participant_to_event, remove_participant_from_event


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
    add_participant_to_event(request.user, event)
    return redirect('events:all-events')


@login_required
def unregister_member(request):
    if request.method != 'POST':
        raise ValueError('Only POST requests are allowed')

    event = Event.objects.get(pk=request.POST["event_uuid"])
    remove_participant_from_event(request.user, event)
    return redirect('events:all-events')
