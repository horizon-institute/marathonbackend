from django.contrib import admin
from marathon.models import Finisher, Spectator, Event, RaceType, Race, Video, RunnerTag

# Register your models here.

admin.site.register(RaceType)
admin.site.register(Event)
admin.site.register(Race)
admin.site.register(Spectator)
admin.site.register(Finisher)
admin.site.register(Video)
admin.site.register(RunnerTag)