from django import forms
from . import models

class GroupCreationForm(forms.ModelForm):

    class Meta:

        model = models.Group
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Group name eg: (Trip to Paris 2026)'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'A little information about your group...'}),
        }