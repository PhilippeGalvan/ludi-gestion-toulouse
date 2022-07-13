from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Event, Candidacy
from .app import remove_candidacy, register_new_candidacy
from .core import CandidateCandidacyRequest
from .forms import MainCandidacyForm, GroupCandidacyFormSet


class AllEventsView(LoginRequiredMixin, ListView):
    model = Event
    ordering = ['date_and_time']
    template_name = 'events/events.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["individual_candidacy_form"] = MainCandidacyForm()
        return context


@login_required
def register_candidacy(request, event_uuid: str):
    if request.method != 'POST':
        raise ValueError('Only POST requests are allowed')

    form = MainCandidacyForm(request.POST)
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


class RegisterBulkCandidacies(LoginRequiredMixin, FormView):
    form_class = GroupCandidacyFormSet
    template_name = 'events/register-bulk-candidacies.html'
    success_url = reverse_lazy('events:all-events')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["main_candidacy_form"] = MainCandidacyForm()
        context["event_uuid"] = self.kwargs['event_uuid']
        return context

    def form_valid(self, formset):
        main_form = MainCandidacyForm(self.request.POST)
        if not main_form.is_valid():
            return super.form_invalid(formset)

        event = Event.objects.get(pk=self.kwargs['event_uuid'])
        candidate_candidacy_requests = [
            CandidateCandidacyRequest(
                candidate=self.request.user,
                as_player=main_form.cleaned_data["player"],
                as_arbiter=main_form.cleaned_data["arbiter"],
                as_disk_jockey=main_form.cleaned_data["disk_jockey"],
                as_speaker=main_form.cleaned_data["speaker"],
            )
        ]
        candidates = set()
        for form in formset.forms:
            if form.cleaned_data and form.is_valid():

                if form.cleaned_data['candidate'] in candidates:
                    return super().form_invalid(formset)
                else:
                    candidates.add(form.cleaned_data['candidate'])

                candidate_candidacy_requests.append(
                    CandidateCandidacyRequest(
                        candidate=form.cleaned_data["candidate"],
                        as_player=form.cleaned_data["player"],
                        as_arbiter=form.cleaned_data["arbiter"],
                        as_disk_jockey=form.cleaned_data["disk_jockey"],
                        as_speaker=form.cleaned_data["speaker"],
                    )
                )

        register_new_candidacy(event, candidate_candidacy_requests)
        return super().form_valid(formset)


@login_required
def unregister_candidacy(request, event_uuid: str, candidacy_uuid: str):
    if request.method != 'POST':
        raise ValueError('Only POST requests are allowed')

    candidacy = Candidacy.objects.get(pk=candidacy_uuid)
    remove_candidacy(candidacy)
    return redirect('events:all-events')
