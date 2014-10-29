# -*- coding: utf-8 -*-

from marathon.models import RacePoint, LocationName, LocationDistance
from django.core.management.base import BaseCommand
from marathon.utils import get_event_from_options
from optparse import make_option

class Command(BaseCommand):
    
    help = "Create markers along the race"
    
    option_list = BaseCommand.option_list + (
        make_option('-n', '--event-name',
            dest= 'event_name',
            default= None,
            help= 'Event name'
        ),
        make_option('-i', '--event-id',
            dest= 'event_id',
            default= None,
            help= 'Event ID'
        ),
        make_option('-t','--race-type',
            dest= 'race_type',
            default= None,
            help= 'Race type (e.g. half-marathon)'
        ),
        make_option('-d','--race-distance',
            dest= 'race_distance',
            default= None,
            help= 'Race distance, in metres'
        ),
    )
    
    RACE_TYPES = {
              "half-marathon": 21100,
              "marathon": 42200,
              }
    
    LOCNAME_TYPE = "race marker"
    
    DISTANCE_TYPES = (
                      {"distance": 1000, "singular": "kilometre", "plural": "kilometres"},
                      {"distance": 1609.344, "singular": "mile", "plural": "miles"}
                      )
    
    event = None
    
    def make_point(self, distance, name):
        nearest_dist = 10 * int(distance/10)
        print "Making point for distance=%dm, named %s"%(nearest_dist, name)
        refpoint = RacePoint.objects.get(
                                 distance = nearest_dist,
                                 event = self.event
                                 )
        locname, created = LocationName.objects.get_or_create(
                                                      name = name,
                                                      type = self.LOCNAME_TYPE
                                                      )
        LocationDistance.objects.create(
                                  location_name = locname,
                                  accuracy = 0,
                                  reference_point = refpoint
                                  )
    
    def handle(self, *args, **options):
        
        self.event = get_event_from_options(options)
        
        distance = options["race_distance"]
        if distance is None:
            distance = self.RACE_TYPES.get(options["race_type"],None)
        if distance is None:
            print "You must specify a race distance"
            return
        
        LocationDistance.objects.filter(location_name__type=self.LOCNAME_TYPE, reference_point__event=self.event).delete()
        
        rpqs = RacePoint.objects.filter(event=self.event)
        
        if not rpqs.exists():
            print "No race points for this event. You may import a course using import_race_course"
            return
        
        self.make_point(0, "Race start")
        self.make_point(distance, "Race finish")
        
        for dt in self.DISTANCE_TYPES:
            for k in range(1,int(distance/dt["distance"])):
                self.make_point(k*dt["distance"], "%d %s"%(k, dt["plural" if k > 1 else "singular"]))
        
        
        
        
        
        
            