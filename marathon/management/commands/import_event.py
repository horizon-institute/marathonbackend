# -*- coding: utf-8 -*-

from marathon.models import Event, RaceType, Race
from django.core.management.base import BaseCommand
from optparse import make_option
import json

class Command(BaseCommand):
    
    help = "Import a race description file"
    
    option_list = BaseCommand.option_list + (
        make_option('-e', '--clear-events',
            dest= 'clear_events',
            action= 'store_true',
            default= False,
            help= 'Clear events'
        ),
        make_option('-r', '--clear-races',
            dest= 'clear_races',
            action= 'store_true',
            default= False,
            help= 'Clear races for the event'
        ),
        make_option('-f','--file_name',
            dest= 'file_name',
            default= None,
            help= 'JSON File name'
        ),
    )
    
    def handle(self, *args, **options):
        
        if options["clear_events"]:
            Event.objects.all().delete()
            
        if not options["file_name"]:
            print "Please give a JSON file name"
            return
            
        with open(options["file_name"],'rb') as json_file:
            data = json.load(json_file)
            event = Event.objects.create(
                 name = data.get("name","[untitled]"),
                 date = data.get("date", None),
                 public = data.get("public",False)
            )
            
            if options["clear_events"]:
                Race.objects.filter(event=event).delete()
            
            for racedata in data["races"]:
                try:
                    racetype = RaceType.objects.get(**{k[5:]:racedata[k] for k in racedata if k[:5] == "type_"})
                    r = Race.objects.create(
                        name = racedata.get("name",None),
                        racetype = racetype,
                        start_time = racedata.get("start_time",None),
                        event = event
                    )
                    print "%d: %s"%(r.id,r.name)
                except Exception as e:
                    print "Error with race %s: %s"%(racedata, e)