from django.contrib import admin
from marathon.models import Spectator, Event, Video, RunnerTag, PositionUpdate, ContactRegistration

# Register your models here.

admin.site.register(Event)
admin.site.register(Spectator)
admin.site.register(Video)
admin.site.register(RunnerTag)
admin.site.register(PositionUpdate)
admin.site.register(ContactRegistration)