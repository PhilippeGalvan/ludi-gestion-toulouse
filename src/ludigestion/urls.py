"""ludigestion URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from common.forms import CustomUserCreationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),
    path('tasks/', include('tasks.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', CreateView.as_view(
            template_name='register.html',
            form_class=CustomUserCreationForm,
            success_url='/'
    )),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('random_gif/', TemplateView.as_view(template_name='random_gif.html'), name='random_gif'),
]
