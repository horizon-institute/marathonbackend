# -*- coding: utf-8 -*-

from marathon.models import RaceResult
from marathon.utils import get_event_from_options
from django.core.management.base import BaseCommand
from optparse import make_option
import json
from geopy import distance
from geopy.point import Point

class Command(BaseCommand):
    
    help = "Import a tag and video description file"
    
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
        make_option('-f','--file_name',
            dest= 'file_name',
            default= None,
            help= 'JSON File name'
        ),
    )
    
    
    def handle(self, *args, **options):
        
        event = get_event_from_options(options)
        
        print "Clearing Race results for %s"%event.name
        
        RaceResult.objects.filter(event=event).delete()
        
        if not options["file_name"]:
            print "Please give a JSON file name"
            return
        
        with open(options["file_name"],'r') as json_file:
            result_list = json.loads(json_file.read())
            
            for result in result_list:
                if result["name"]:
                    finish_time_parts = [int(k) for k in result["finish_time"].split(":")]
                    finish_time = 3600 * finish_time_parts[0] + 60 * finish_time_parts[1] + finish_time_parts[2]
                    RaceResult.objects.create(
                                              event = event,
                                              finishing_time = finish_time,
                                              name = result["name"],
                                              runner_number = result["bib"]
                                              )
            
            print "%d Race result objects created"%RaceResult.objects.filter(event=event).count()
            
        