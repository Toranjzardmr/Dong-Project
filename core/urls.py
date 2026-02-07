from django.urls import path
from . import views
from django.views.generic import View

app_name = 'core'

urlpatterns = [
    path('', views.index, name='home'),
]
