from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    #Authentication urls
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page= 'accounts:login'), name='logout'),
    path('register/', views.register_user, name='signup'),
    # User profile urls
    path('profile/<int:id>/', views.profile, name='profile'),
    path('profile/<int:id>/edit/', views.profile_edit, name='profile_edit'),
    path('users/search/', views.search_users, name='search_users'),
    path('add-friend/<int:id>/', views.add_friend, name='add_friend'),

]
