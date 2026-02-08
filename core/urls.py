from django.urls import path
from . import views
from django.views.generic import View

app_name = 'core'

urlpatterns = [
    path('', views.index, name='home'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
]
