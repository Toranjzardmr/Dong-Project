from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.contrib import messages
from . import models, forms

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

    print(balances)
    print(debts)

    context = {
        'group' : group,
        'members' : members,
        'balances': balances,
        'debts' : debts,
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
        form.save()

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
