# -*- coding: utf-8 -*-

from marathon.models import RacePoint
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
            help= 'GeoJSON File name'
        ),
    )
    
    
    def handle(self, *args, **options):
        
        event = get_event_from_options(options)
        
        print "Clearing Race points for %s"%event.name
        
        RacePoint.objects.filter(event=event).delete()
        
        if not options["file_name"]:
            print "Please give a JSON file name"
            return
        
        with open(options["file_name"],'r') as json_file:
            featurelist = json.loads(json_file.read())
            
            basecourse = []

            for feature in featurelist["features"]:
                if feature["geometry"]["type"] == "LineString":
                    basecourse = feature["geometry"]["coordinates"]
                    break
            
            basecourse = [(ll[1],ll[0]) for ll in basecourse]
            
            print "Base course made of %d points"%len(basecourse)
            
            RacePoint.objects.create(
                             distance = 0,
                             latitude = basecourse[0][0],
                             longitude = basecourse[0][1],
                             event = event
                             )
            totald = 0
            pointpitch = 10
            nxt = pointpitch
            
            for i,p in enumerate(basecourse):
                if i:
                    lastp = basecourse[i-1]
                    dist = distance.distance(Point(lastp),Point(p)).m
                    distafterp = totald + dist
                    while distafterp > nxt:
                        kp = (nxt - totald)/dist
                        latitude = (kp * p[0] + (1-kp) * lastp[0])
                        longitude = (kp * p[1] + (1-kp) * lastp[1])
                        RacePoint.objects.create(
                             distance = nxt,
                             latitude = latitude,
                             longitude = longitude,
                             event = event
                        )
                        nxt += pointpitch
                    totald = distafterp
            
            print "%d Race point objects created"%RacePoint.objects.filter(event=event).count()
            
        