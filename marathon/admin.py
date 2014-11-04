from django.contrib import admin
from marathon.models import *

# Register your models here.

for m in [
          Event,
          Spectator,
          Video,
          RunnerTag,
          PositionUpdate,
          ContactRegistration,
          ContentFlag,
          RacePoint,
          VideoDistance,
          LocationName,
          LocationDistance,
          RunningClub,
          RaceResult,
      ]:
    admin.site.register(m)
