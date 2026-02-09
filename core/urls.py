from django.urls import path
from . import views
from django.views.generic import View

app_name = 'core'

urlpatterns = [
    path('', views.index, name='home'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/update/', views.group_update, name='group_update'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    #Expenses
    path('groups/<int:pk>/expenses/', views.group_expenses, name='group_expenses'),
    path('groups/<int:pk>/expenses/new/', views.expense_add, name='expense_add'),
    path('expenses/<int:id>/', views.expense_detail, name='expense_detail'),
    path('/expenses/<int:id>/update/', views.expense_update, name='expense_update'),
    path('expenses/<int:id>/delete/', views.expense_delete, name='expense_delete'),
]
