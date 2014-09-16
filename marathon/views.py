from django.shortcuts import render
from marathon.forms import UserForm, ContactRegistrationForm, RunnerSearchForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from marathon.models import  Video, RunnerTag
from django.views.generic import ListView

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

def landing(request):
    showform = True
    if request.method == 'POST':
        form = ContactRegistrationForm(request.POST)
        if form.is_valid():
            showform = False
            form.save()
    else:
        form = ContactRegistrationForm()
    return render(request, "landing.html", {
        'showform': showform,
        'email': request.POST["email"] if request.method == 'POST' else None,
        'form': form,
    })
    
def home(request):
    rtqs = RunnerTag.objects.filter(video__spectator__user=request.user)
    return render(request, "home.html", {
        "runnertags": rtqs.exclude(runner_number=-99).count(),
        "hottags": rtqs.filter(runner_number=-99).count(),
        "videos": Video.objects.filter(spectator__user=request.user).count(),
    })

class RunnerTagList(ListView):
    template_name = "searchrunner.html"
    model = RunnerTag
    
    def get_queryset(self):
        self.form = RunnerSearchForm(self.request.GET, self.request.user)
        if self.form.is_valid():
            return RunnerTag.objects.select_related("video").filter(video__event=self.form.cleaned_data["event"],runner_number=self.form.cleaned_data["runner_number"]).order_by("time")
    
    def get_context_data(self, **kwargs):
        context = super(RunnerTagList, self).get_context_data(**kwargs)
        context["form"] = self.form
        return context
    