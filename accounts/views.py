from django.shortcuts import redirect, render
from django.contrib import messages
from . import models, forms

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