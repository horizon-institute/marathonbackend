# -*- coding: utf-8 -*-

from marathon.models import VideoDistance, Video, RacePoint, PositionUpdate, RunnerTag
from django.core.management.base import BaseCommand
from django.db.models import Avg
from optparse import make_option
from marathon.utils import calculate_easting_delta, get_event_from_options
from geopy import distance
from geopy.point import Point
import datetime

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
    )
    
    
    def handle(self, *args, **options):
        
        event = get_event_from_options(options)
        
        print "Clearing Distance points for %s"%event.name
        
        VideoDistance.objects.filter(video__event=event).delete()
                
        rpqs = RacePoint.objects.filter(event=event)
                
        if not rpqs.exists():
            print "No race points for this event. You may import a course using import_race_course"
            return
        
        meanlat = rpqs.aggregate(Avg("latitude"))["latitude__avg"]
        
        maxtolerance = 500.
        longtolerance = calculate_easting_delta(meanlat, maxtolerance)
        lattolerance = maxtolerance * 90./10000000.
        otherleg = maxtolerance * 2
        pointcache = {}        
        vqs = Video.objects.filter(event=event)
        
        for v in vqs:
            
            print "Finding location for video %s"%v.id
            
            locobj = None
            for delta in [0,10,30,60,120,300,600]:
                rtqs = RunnerTag.objects.filter(
                             time__gte=v.start_time - datetime.timedelta(0,delta),
                             time__lte=v.end_time + datetime.timedelta(0,delta),
                             video__spectator=v.spectator,
                             )
                if rtqs.exists():
                    locobj = rtqs.order_by("-time").first()
                    print "Used RunnerTag from a timespan of %d seconds around Video"%delta
                    break
                puqs = PositionUpdate.objects.filter(
                             time__gte=v.start_time - datetime.timedelta(0,delta),
                             time__lte=v.end_time + datetime.timedelta(0,delta),
                             spectator=v.spectator,
                             )
                if puqs.exists():
                    locobj = puqs.order_by("-time").first()
                    print "Used PositionUpdate from a timespan of %d seconds around Video"%delta
                    break
            
            if locobj and locobj.latitude != 0:
                point = (locobj.latitude, locobj.longitude)
                gppoint = Point(point)
                cachekey = "%.5f|%.5f"%point
                if cachekey in pointcache:
                    bestpoints = pointcache[cachekey]
                else:
                    candidateqs = rpqs.filter(
                                          latitude__gt = point[0] - lattolerance,
                                          latitude__lt = point[0] + lattolerance,
                                          longitude__gt = point[1] - longtolerance,
                                          longitude__lt = point[1] + longtolerance)
                    candidatepoints = [
                               { "delta": distance.distance(Point(p.latitude,p.longitude),gppoint).m, "point": p}
                               for p in candidateqs]
                    candidatepoints = [p for p in candidatepoints if p["delta"] < maxtolerance]
                    candidatepoints.sort(key=lambda p: p["delta"])
                    bestpoints = []
                    if not candidatepoints:
                        print "Video is too far from the race"
                    while candidatepoints:
                        lastdist = candidatepoints[0]["point"].distance
                        bestpoints.append(candidatepoints[0])
                        candidatepoints = [p for p in candidatepoints if abs(p["point"].distance-lastdist) > otherleg]
                    pointcache[cachekey] = bestpoints
                    if (len(bestpoints) > 1):
                        print "Ambiguous location: %s"%(",".join(["%dm"%p["point"].distance for p in bestpoints]))
                    pointcache[cachekey] = bestpoints
                    
                for pt in bestpoints:
                    
                    VideoDistance.objects.create(
                                             video = v,
                                             reference_point = pt["point"],
                                             accuracy = max(10, locobj.accuracy, pt["delta"])
                                                 )
                    
            else:
                print "No location found for Video"
            
        
        

            
        print "%d video distances inserted"%VideoDistance.objects.filter(video__event=event).count()
            
        