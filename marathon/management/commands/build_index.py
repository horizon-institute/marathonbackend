# -*- coding: utf-8 -*-

from marathon.models import LocationName, SearchIndex, RunningClub, RaceResult, RunnerTag, RacePoint
from django.core.management.base import BaseCommand
from django.db.models import Min, Max
from marathon.utils import get_event_from_options
from optparse import make_option
import datetime, math

class Command(BaseCommand):
    
    help = "Build the index for the search box"
    
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
    )
    
    
    def handle(self, *args, **options):
        
        event = get_event_from_options(options)
        
        print "Clearing index for event"
        
        SearchIndex.objects.filter(event=event).delete()
        
        print "Buiding the At Distance indexes"
        
        maxdist = RacePoint.objects.filter(event=event).aggregate(Max("distance"))["distance__max"]
        
        for k in range(1,int(math.ceil(float(maxdist)/SearchIndex.KILOMETRE))):
            SearchIndex.objects.create(event=event, reference_object_AtKilometre=k)
            
        for k in range(1,int(math.ceil(float(maxdist)/SearchIndex.MILE))):
            SearchIndex.objects.create(event=event, reference_object_AtMile=k)
        
        print "Building AllTag and AllVideo sets"
        
        SearchIndex.objects.create(event=event, reference_object_AllTags=True)
        SearchIndex.objects.create(event=event, reference_object_AllVideos=True)
        
        print "Building the Index of Locations"
        
        locations = LocationName.objects.filter(points__reference_point__event=event).distinct()
        
        for location in locations:
            
            SearchIndex.objects.create(
                       event = event,
                       reference_object_LocationName = location
                               )
        
        print "Building the Index of Named runners"
        
        runners = RaceResult.objects.filter(event=event)
        
        for runner in runners:
            
            SearchIndex.objects.create(
                       event = event,
                       reference_object_RunnerNumber = runner
                           )
        
        print "Building the Index of Running Clubs"
        
        clubs = RunningClub.objects.filter(runners__event=event).distinct()
        
        for club in clubs:
            SearchIndex.objects.create(
                       event = event,
                       reference_object_RunningClub = club
                                       )
        
        print "Building the Index for AtMinute"
        
        times = RunnerTag.objects.filter(video__event=event).aggregate(Min("time"),Max("time"))
        start_time = 60*(int(times["time__min"].strftime("%s"))/60)
        end_time = 60*(int(times["time__min"].strftime("%s"))/60)
        for timestamp in range(start_time, end_time, 60):
            
            SearchIndex.objects.create(
                           event = event,
                           reference_object_AtMinute = datetime.datetime.fromtimestamp(timestamp)
                           )
        
        
