from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.contrib import messages
from . import models, forms
from django.contrib.auth import get_user_model

# Create your views here.

def index(request):
    
    user_groups = models.Group.objects.filter(members = request.user)

    context = {
        'user_groups' : user_groups
    }
    return render(request,'core/index.html', context)


"""
================================
    Group Views
================================
"""

def group_create(request):

    if request.method == 'POST':
        form = forms.GroupCreationForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.creator = request.user
            new_group.save()
            new_group.members.add(request.user)
            return redirect('core:home')
    else:
        form = forms.GroupCreationForm()

    context = {
        'form' : form
    }
    return render(request,'core/group_create.html', context)



def group_detail(request,pk):
    
    group = models.Group.objects.get(id=pk)
    members = group.members.all()

    balances = {user.username: amount for user, amount in group.get_balance_summary().items()}
    debts = group.get_settlement_overview()

    group_invite_link = group.get_invite_link()

    context = {
        'group' : group,
        'members' : members,
        'balances': balances,
        'debts' : debts,
        'group_invite_link' : group_invite_link,
    }
    return render(request,'core/group_detail.html', context)


def group_update(request,pk):
    
    group = models.Group.objects.get(id=pk)
    form = forms.GroupCreationForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save()
        return redirect('core:group_detail', group.id)
    context = {
        'form' : form,
        'group' : group,
    }
    return render(request,'core/group_update.html', context)



def group_delete(request,pk):

    models.Group.objects.get(id = pk).delete()

    return redirect('core:home')


def group_join(request, invite_link):

    group = get_object_or_404(models.Group, invite_link=invite_link)
    
    if request.user in group.members.all():
        messages.info(request, "You are already a member of this group.")
    else:
        group.members.add(request.user)
        messages.success(request, f"You have successfully joined the group '{group.name}'.")

    return redirect('core:group_detail', group.id)


def member_remove(request, pk, user_id):

    group = get_object_or_404(models.Group,pk = pk)
    user_to_delete = get_object_or_404(get_user_model(), id = user_id)
    
    if request.user != group.creator:
        messages.error(request, "You don't have permission to remove members from this group.")
        return redirect('core:group_detail', group.id)

    group.members.remove(user_to_delete)
    models.Expense.participants.through.objects.filter(expense__group=group, customuser=user_to_delete).delete()

    messages.success(request, f"User '{user_to_delete.username}' has been removed from the group.")

    return redirect('core:group_detail', group.id)

"""
================================
    Expense Views
================================
"""


def group_expenses(request, pk):

    group = get_object_or_404(models.Group, id = pk)
    expenses = get_list_or_404(models.Expense, group = group)

    context = {
        'expenses' : expenses,
        'group' : group
    }
    return render(request,'core/group_expenses.html', context)



def expense_add(request, pk):

    group = models.Group.objects.get(id = pk)

    if request.method == 'POST':
        
        form = forms.ExpenseCreationForm(request.POST)
        if form.is_valid():
            new_expense = form.save(commit=False)
            new_expense.group = group
            new_expense.save()

            form.save_m2m()
            new_expense.calculate_and_save_shares()


            return redirect('core:group_detail', group.id)

    form = forms.ExpenseCreationForm()

    context = {
        'form' : form,
        'group' : group
    }
    return render(request,'core/expense_add.html', context)


def expense_detail(request,id):
    
    expense = models.Expense.objects.get(id=id)
    shares = expense.shares.all()

    context = {
        'expense' : expense,
        'shares' : shares,
    }
    return render(request,'core/expense_detail.html', context)


def expense_update(request,id):
    
    expense = get_object_or_404(models.Expense, id = id)
    form = forms.ExpenseCreationForm(request.POST or None, instance=expense)

    if form.is_valid():
        updated_expense = form.save()
        updated_expense.calculate_and_save_shares()

        return redirect('core:expense_detail', expense.id)
   
    context = {
        'form' : form,
        'expense' : expense
    }
    return render(request,'core/expense_update.html', context)


def expense_delete(request,id) :

    expense = get_object_or_404(models.Expense, id = id)
    group = expense.group
    expense.delete()
    messages.success(request, 'Expense Deleted Successfully.')

    return redirect('core:group_detail', group.id)
