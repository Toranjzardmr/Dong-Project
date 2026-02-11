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

class ExpenseCreationForm(forms.ModelForm):

    class Meta:

        model = models.Expense
        fields = [
            'name',
            'amount',
            'paid_by',
            'participants',
            'split_type',
            'date',
            'note',
            ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Add more information...'}),
            'paid_by': forms.Select(attrs={'class': 'form-select'}),
            'split_type': forms.Select(attrs={'class': 'form-select'}),
            'participants': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
        def __init__(self, group: models.Group, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            self.fields['participants'].queryset = group.members.all()
            self.fields['paid_by'].queryset = group.members.all()


            if self.instance.pk is None:  # فقط برای ایجاد جدید
                self.fields['participants'].initial = group.members.all()

            # self.fields['paid_by'].queryset = group.members.order_by('first_name')