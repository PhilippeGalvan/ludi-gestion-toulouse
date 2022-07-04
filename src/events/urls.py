from django.urls import path

from .views import AllEventsView, register_member, unregister_member

app_name = 'events'

urlpatterns = [
    path('', AllEventsView.as_view(), name='all-events'),
    path('register/', register_member, name='register-member'),
    path('unregister/', unregister_member, name='unregister-member'),
]
