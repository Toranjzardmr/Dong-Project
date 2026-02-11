from django.db import models
from django.db.models import Sum
from collections import defaultdict
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import uuid

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
    invite_link = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)


    class Meta :
        ordering = ["-created_at"]

    def get_invite_link(self):
        return f"{settings.BASE_URL}/groups/join/{self.invite_link}/"

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
    

    def get_settlement_overview(self):
        """
        Returns minimal list of suggested payments after netting opposite debts
        """
        
        # مرحله ۱: جمع بدهی‌های مستقیم (from → to)
        aggregated = defaultdict(Decimal)
        
        for expense in self.expenses.all():
            for share in expense.shares.filter(amount_owed__gt=0):
                if share.user != expense.paid_by:
                    key = (share.user, expense.paid_by)  # (debtor, creditor)
                    aggregated[key] += share.amount_owed

        # مرحله ۲: netting (جبران بدهی‌های دوطرفه)
        net_debts = {}
        for (u1, u2), amt12 in aggregated.items():
            # چک کن آیا جهت معکوس وجود داره
            reverse_key = (u2, u1)
            amt21 = aggregated.get(reverse_key, Decimal('0.00'))
            
            if amt12 > amt21:
                net_debts[(u1, u2)] = amt12 - amt21
            elif amt21 > amt12:
                net_debts[(u2, u1)] = amt21 - amt12
            # اگر برابر بودند → هیچی نمی‌مونه

        # مرحله ۳: تبدیل به لیست مرتب‌شده
        debts = []
        for (from_user, to_user), amount in net_debts.items():
            if amount > 0:
                debts.append({
                    'from': from_user,
                    'to': to_user,
                    'amount': amount,
                })
        
        # مرتب‌سازی نزولی
        debts.sort(key=lambda x: x['amount'], reverse=True)
        
        return debts
    


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


    def save(self, *args, **kwargs):
       
        super().save(*args, **kwargs)

        self.shares.all().delete()

        if self.participants.exists():
            self.calculate_and_save_shares()


    def clean(self):
        if self.amount < 0 :
            raise ValidationError('The amount needs to be a positive number !')
        
        
    def calculate_and_save_shares(self):

        self.shares.all().delete()
        
        participants = self.participants.all()
        if not participants.exists() :
            return
        
        if self.split_type == 'equal' :

            share_amount = self.amount / participants.count()

            for user in participants :
                ExpenseShare.objects.create(
                    user = user,
                    expense = self,
                    amount_owed = share_amount
                )
        if self.split_type == 'percerntage' or self.split_type == 'exact' :
            pass
        
        



class ExpenseShare(models.Model):

    def __str__(self):
        
        if self.user == self.expense.paid_by :
            return f'{self.user} gets back {self.amount_owed} in {self.expense}'
        else:
            return f'{self.user} ows {self.amount_owed} in {self.expense}'
    
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta :
        unique_together = ['expense', 'user']
