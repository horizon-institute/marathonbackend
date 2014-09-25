from django.shortcuts import render
from marathon.forms import UserForm, ContactRegistrationForm, RunnerSearchForm, CustomLoginForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.db.models import Count
from marathon.models import  Video, RunnerTag
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.conf import settings

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

def processlogin(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            login_user = authenticate(username=form.cleaned_data.get("user"), password=form.cleaned_data.get("password"))
            login(request, login_user)
            return None
    else:
        form = CustomLoginForm()
    return form

def home(request):
    context = {}
    rtqs = RunnerTag.objects.filter(video__spectator__user=request.user)
    context["runnertags"] = rtqs.exclude(runner_number=-99).count()
    context["hottags"] = rtqs.filter(runner_number=-99).count()
    context["videos"] = Video.objects.filter(spectator__user=request.user).count()
    context["runner_search_form"] = RunnerSearchForm(None,request.user)
    return render(request, "home.html", context)

def customlogin(request):
    login_form = processlogin(request)
    if login_form:
        return render(request, "login.html", {
            'login_form': login_form,
            'break_before_consent': True,
        })
    else:
        return HttpResponseRedirect(reverse('home'))

def searchrunner(request):
    if 'runner_number' in request.GET or 'event' in request.GET:
        form = RunnerSearchForm(request.GET,request.user)
    else:
        form = RunnerSearchForm(None,request.user)
    if form.is_valid():
        return HttpResponseRedirect(reverse('runner_results', kwargs={'event': request.GET["event"], 'runner_number': request.GET["runner_number"]}))
    return render(request, "searchrunner.html", {"runner_search_form": form})

class RunnerTagList(ListView):
    template_name = "searchrunner.html"
    model = RunnerTag
    paginate_by = 8
    
    def get_queryset(self):
        self.form = RunnerSearchForm(self.kwargs,self.request.user)
        if self.form.is_valid():
            return RunnerTag.objects.select_related("video__spectator,video__event").filter(video__event=self.form.cleaned_data["event"],runner_number=self.form.cleaned_data["runner_number"]).order_by("time")
        else:
            return RunnerTag.objects.none()
        
    def get_context_data(self, **kwargs):
        context = super(RunnerTagList, self).get_context_data(**kwargs)
        context["runner_search_form"] = self.form
        context["GMAPS_API_KEY"] = settings.GMAPS_API_KEY
        return context

class MyVideoList(ListView):
    template_name = "myvideos.html"
    model = Video
    paginate_by = 8
    
    def get_queryset(self):
        return Video.objects.filter(spectator__user=self.request.user).select_related('tags').annotate(tagcount=Count("runnertags")).order_by("-start_time")

class AllVideosList(ListView):
    template_name = "allvideos.html"
    model = Video
    paginate_by = 12
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Video.objects.select_related('runnertags').annotate(tagcount=Count("runnertags")).order_by("-start_time")
        else:
            return Video.objects.none()

class MyTagList(ListView):
    template_name = "mytags.html"
    model = RunnerTag
    paginate_by = 8
    tagtype = None
    
    def get_queryset(self):
        qs = RunnerTag.objects.filter(video__spectator__user=self.request.user).select_related("video__event").order_by("time")
        runnertags = qs.exclude(runner_number=-99)
        hottags = qs.filter(runner_number=-99)
        self.hottag_count = hottags.count()
        self.runnertag_count = runnertags.count()
        self.total_count = qs.count()
        self.tagtype = self.kwargs.get("tagtype","")
        if self.tagtype == "runner":
            return runnertags
        if self.tagtype == "hot":
            return hottags
        return qs
        
    def get_context_data(self, **kwargs):
        context = super(MyTagList, self).get_context_data(**kwargs)
        context["tagtype"] = self.tagtype
        context["runnertag_count"] = self.runnertag_count
        context["hottag_count"] = self.hottag_count
        context["total_count"] = self.total_count
        context["GMAPS_API_KEY"] = settings.GMAPS_API_KEY
        return context

class AllTagsList(ListView):
    template_name = "alltags.html"
    model = RunnerTag
    paginate_by = 12
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return RunnerTag.objects.select_related("video__event").order_by("-time")
        else:
            return RunnerTag.objects.none()
        
    def get_context_data(self, **kwargs):
        context = super(AllTagsList, self).get_context_data(**kwargs)
        context["GMAPS_API_KEY"] = settings.GMAPS_API_KEY
        return context