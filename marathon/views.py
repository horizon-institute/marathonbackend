from django.shortcuts import render
from marathon.forms import UserForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from marathon.models import PositionUpdate, Video, RunnerTag
import datetime

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

def feed(request):
    timespan = request.GET.get("timespan", 60)
    spectator_id = request.GET.get("spectator", None)
    
    puqs = PositionUpdate.objects.all()
    vqs = Video.objects.all()
    rtqs = RunnerTag.objects.all()
    
    if timespan:
        earliest_date = datetime.datetime.now() - datetime.timedelta(0,timespan)
        puqs = puqs.filter(time_geq=earliest_date)
        rtqs = rtqs.filter(time_geq=earliest_date)
        vqs = vqs.filter(start_time_geq=earliest_date)
    
    if spectator_id:
        puqs = puqs.filter(spectator_id=spectator_id)
        rtqs = rtqs.filter(video__spectator_id=spectator_id)
        vqs = vqs.filter(spectator_id=spectator_id)
    