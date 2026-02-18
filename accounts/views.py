from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from . import models, forms

from django.contrib.auth import get_user_model
from django.db.models import Q

# Create your views here.


def register_user(request):
    
    if request.method == 'POST':

        form = forms.UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f"Account created, {user.username}! You can now Login.")
            return redirect('accounts:login')

    else:
        form = forms.UserRegisterForm()
        form.order_fields(field_order=['username', 'email', 'password', 'password2'])

    context = {
        'form' : form,
    }
    return render(request,'accounts/register.html', context)

def profile(request, id):

    if request.user.id != id:
        messages.error(request, "You can only view your own profile.")
        return redirect('accounts:profile', id = request.user.id)
    
    user = models.CustomUser.objects.get(id = id)
    user_groups = user.groups_joined.all().order_by('-created_at')
    friends = user.friends.all()

    context = {
        'user' : user,
        'groups' : user_groups,
        'friends' : friends,
    }
    return render(request, 'accounts/profile.html', context)


def profile_edit(request, id):

    user = models.CustomUser.objects.get(id = id)
    form = forms.ProfileEditForm(instance=user)

    if request.method == 'POST':
        form = forms.ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile', id=user.id)


    context = {
        'user' : user,
        'form' : form,
    }
    return render(request, 'accounts/profile_edit.html', context)



def search_users(request):
    query = request.GET.get('search', '').strip()
    users = []

    if query:
        users = get_user_model().objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:20]

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'accounts/search_users.html', context)



def add_friend(request, id):
    if request.method != 'POST':
        return redirect('search_users')

    target_user = get_object_or_404(get_user_model(), id=id)

    if target_user == request.user:
        messages.error(request, "You cannot add yourself as a friend.")
        return redirect('accounts:search_users')

    request.user.friends.add(target_user)

    messages.success(request, f"{target_user.username} added to friends." )
    return redirect('accounts:search_users')