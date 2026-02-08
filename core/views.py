from django.shortcuts import redirect, render
from . import models, forms

# Create your views here.

def index(request):
    
    user_groups = models.Group.objects.filter(members = request.user)

    context = {
        'user_groups' : user_groups
    }
    return render(request,'core/index.html', context)


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

    context = {
        'group' : group,
        'members' : members,
    }
    return render(request,'core/group_detail.html', context)