# -*- coding: utf-8 -*-

from marathon.models import Spectator, RunnerTag, Video, PositionUpdate
from django.core.management.base import BaseCommand
from marathon.utils import get_event_from_options
from optparse import make_option
import json
import datetime
import pytz

class Command(BaseCommand):
    
    help = "Exports a tag and video description file"
    
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
        make_option('-o', '--online-only',
            dest= 'online_only',
            action= 'store_true',
            default= False,
            help= 'Export only online videos'
        ),
    )
    
    
    def handle(self, *args, **options):
        
        def fromtimestamp(ts):
            return datetime.datetime.fromtimestamp(ts, pytz.utc)
        
        if options["file_name"] is None:
            print "Please enter a file name"
            return
        
        event = get_event_from_options(options)
        
        sqs = Spectator.objects.filter(videos__event=event).distinct()
        tqs = RunnerTag.objects.filter(video__event=event).exclude(runner_number=-99)
        vqs = Video.objects.filter(event=event)
        
        if options["online_only"]:
            tqs = tqs.filter(video__online=True)
            vqs = vqs.filter(online=True)
        
        videos_list = []
        
        for v in vqs:
            video_obj = {
                     "_id": v.guid,
                     "start-time": v.start_time.strftime("%s"),
                     "start-time-iso": v.start_time.isoformat(),
                     "url": v.url,
                     "spectator": v.spectator.guid,
                     "duration": v.duration,
                     "thumbnail": v.thumbnail,
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
                    
            video_obj["latitude"] = getattr(locobj, "latitude", 0.)
            video_obj["longitude"] = getattr(locobj, "longitude", 0.)
            video_obj["accuracy"] = getattr(locobj, "accuracy", -1)
            
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
                        "accuracy": t.accuracy,
                        "time": t.time.strftime("%s"),
                        "time-iso": t.time.isoformat(),
                        "spectator": t.video.spectator.guid,
                        "video": t.video.guid,
                        "thumbnail": t.thumbnail,
                            }
                           for t in tqs],
                  "videos": videos_list
                      }
        
        
        with open(options["file_name"],'w') as json_file:
            json_file.write(json.dumps(export_obj,indent=4))
        
