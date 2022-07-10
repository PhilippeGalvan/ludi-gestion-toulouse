from django.urls import path

from .views import AllEventsView, register_candidacy, unregister_candidacy

app_name = 'events'

urlpatterns = [
    path('', AllEventsView.as_view(), name='all-events'),
    path('register/', register_candidacy, name='register-member'),
    path('unregister/', unregister_candidacy, name='unregister-member'),
]
