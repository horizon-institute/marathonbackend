from django.shortcuts import render
from marathon.forms import UserForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from marathon.models import  Video, RunnerTag

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.email = request.POST["email"]
            new_user.first_name = request.POST["first_name"]
            new_user.last_name = request.POST["last_name"]
            new_user.save()
            login_user = authenticate(username=request.POST["username"], password=request.POST["password1"])
            login(request, login_user)
            return HttpResponseRedirect("/")
    else:
        form = UserForm()
    return render(request, "registration/register.html", {
        'form': form,
    })

def home(request):
    rtqs = RunnerTag.objects.filter(video__spectator__user=request.user)
    return render(request, "home.html", {
        "runnertags": rtqs.exclude(runner_number=-99).count(),
        "hottags": rtqs.filter(runner_number=-99).count(),
        "videos": Video.objects.filter(spectator__user=request.user).count(),
    })

    