from django.urls import path

from .views import AllEventsView, register_candidacy, unregister_candidacy, RegisterBulkCandidacies

app_name = 'events'

urlpatterns = [
    path('', AllEventsView.as_view(), name='all-events'),
    path('<str:event_uuid>/candidacies/bulk/', RegisterBulkCandidacies.as_view(), name='register-bulk-candidacies'),
    path('<str:event_uuid>/candidacies/', register_candidacy, name='register-member'),
    path('<str:event_uuid>/candidacies/<str:candidacy_uuid>/cancel', unregister_candidacy, name='unregister-candidacy'),
]
