# -*- coding: utf-8 -*-

from marathon.models import Event, Spectator, RunnerTag, Video, PositionUpdate
from django.core.management.base import BaseCommand
from optparse import make_option
import json
import datetime
import pytz

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
        
        def fromtimestamp(ts):
            return datetime.datetime.fromtimestamp(ts, pytz.utc)
        
        if options["file_name"] is None:
            print "Please enter a file name"
            return
        
        if options["event_id"] is None:
            if options["event_name"]:
                print options["event_name"]
                event = Event.objects.get(name=options["event_name"])
            else:
                print "Please give an event name or id"
                return
        else:
            event = Event.objects.get(id=options["event_id"])
        
        sqs = Spectator.objects.filter(videos__event=event).distinct()
        tqs = RunnerTag.objects.filter(video__event=event).exclude(runner_number=-99)
        vqs = Video.objects.filter(event=event)
        
        videos_list = []
        
        for v in vqs:
            video_obj = {
                     "_id": v.guid,
                     "start-time": v.start_time.strftime("%s"),
                     "start-time-iso": v.start_time.isoformat(),
                     "spectator": v.spectator.guid,
                     "duration": v.duration,
                         }
            locobj = None
            if v.runnertags.exists():
                locobj = v.runnertags.first()
                print "Used 1st runner"
            else:
                for delta in [0,10,30,60,120,300,600]:
                    puqs = PositionUpdate.objects.filter(
                                 time__gte=v.start_time - datetime.timedelta(0,delta),
                                 time__lte=v.end_time + datetime.timedelta(0,delta),
                                 spectator=v.spectator,
                                 )
                    if puqs.exists():
                        locobj = puqs.order_by("-time").first()
                        print "Used a timespan of %d seconds around Video"%delta
                        break
            if locobj is None:
                print "No location information"
                video_obj["latitude"] = 0.
                video_obj["longitude"] = 0.
            else:
                video_obj["latitude"] = locobj.latitude
                video_obj["longitude"] = locobj.longitude
            
            videos_list.append(video_obj)
            #print video_obj
        
        export_obj = {
                  "spectators": [{
                              "_id": s.guid,
                              "name": s.name
                                  }
                                 for s in sqs],
                  "tags": [{
                        "_id": t.guid,
                        "runner_number": t.runner_number,
                        "latitude": t.latitude,
                        "longitude": t.longitude,
                        "time": t.time.strftime("%s"),
                        "time-iso": t.time.isoformat(),
                        "spectator": t.video.spectator.guid,
                        "video": t.video.guid,
                            }
                           for t in tqs],
                  "videos": videos_list
                      }
        
        
        with open(options["file_name"],'w') as json_file:
            json_file.write(json.dumps(export_obj))
        
