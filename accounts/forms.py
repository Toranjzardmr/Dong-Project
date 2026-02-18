from django import forms
from django.contrib.auth import get_user_model


class UserRegisterForm(forms.ModelForm):

    class Meta:

        model = get_user_model()
        fields = ['username', 'email']

    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise forms.ValidationError('Passwords do not match !')
        

class ProfileEditForm(forms.ModelForm):

    class Meta:

        model = get_user_model()
        fields = ['username', 'email', 'profile_photo']