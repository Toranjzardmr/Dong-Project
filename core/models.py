from django.db import models
from django.db.models import Sum
from collections import defaultdict
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.

class Group(models.Model):

    def __str__(self):
        return self.name
    

    name = models.CharField(max_length=70)
    description = models.TextField(max_length=200, null=True, blank=True)
    members = models.ManyToManyField(get_user_model(), related_name='groups_joined')
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_groups'
        )
    created_at = models.DateField(auto_now_add=True)


    class Meta :
        ordering = ["-created_at"]

    def get_total_expenses(self):
        
        total = self.expenses.aggregate(total = Sum("amount"))["total"]
        return total or 0
    
    def get_balance_summary(self):

        balances = defaultdict(Decimal)

        for expense in self.expenses.all():
            balances[expense.paid_by] += expense.amount

            for share in expense.shares.all():
                balances[share.user] -= share.amount_owed
        return dict(balances)
    
    


class Expense(models.Model):

    def __str__(self):
        return f'{self.name} - {self.amount}'
    
    SPLIT_CHOICES = [
    ('equal','برابر'),
    ( 'percentage','درصد'),
    ( 'exact','دقیق')
        ]
    

    name = models.CharField(max_length=70, null=False)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='expense_payer')
    participants = models.ManyToManyField(get_user_model(), related_name='expense_participants')
    split_type = models.CharField(max_length=20, choices=SPLIT_CHOICES, default='equal')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField(default=timezone.now)
    note = models.TextField(max_length=200, null=True, blank=True)


    def clean(self):
        if self.amount < 0 :
            raise ValidationError('The amount needs to be a positive number !')
        
        
    def calculate_and_save_shares(self):
        
        participants = self.participants.all()
        if not participants.exists() :
            return
        
        if self.split_type == 'equal' :

            share_amount = self.amount / participants.count()

            for user in participants :
                ExpenseShare.objects.create(
                    user = user,
                    expense = self,
                    amount_owed = share_amount if user != self.paid_by else Decimal('0.00')
                )
        if self.split_type == 'percerntage' or self.split_type == 'exact' :
            pass
        
        



class ExpenseShare(models.Model):

    def __str__(self):
        return f'{self.user} owes {self.amount_owed} in {self.expense}'
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta :
        unique_together = ['expense', 'user']
