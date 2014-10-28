import math
from marathon.models import Event

EARTH_RADIUS = 6371000.

def calculate_easting_delta(latitude, metres):
    radlat = math.radians(latitude)
    reldist = float(metres) / EARTH_RADIUS
    return math.degrees(math.atan2( reldist * math.cos(radlat), math.cos(reldist) - math.pow(math.sin(radlat),2)))

def get_event_from_options(options):
    if options["event_id"] is None:
        if options["event_name"]:
            print options["event_name"]
            event = Event.objects.get(name=options["event_name"])
        else:
            raise Event.DoesNotExist
    else:
        event = Event.objects.get(id=options["event_id"])
    return event