# -*- coding: utf-8 -*-

from marathon.models import Finisher, Event, Spectator, RunnerTag, Video
from django.core.management.base import BaseCommand
from optparse import make_option
import json
import datetime
import pytz

class Command(BaseCommand):
    
    help = "Import a tag and video description file"
    
    option_list = BaseCommand.option_list + (
        make_option('-t', '--clear-tags',
            dest= 'clear_tags',
            action= 'store_true',
            default= False,
            help= 'Clear tags for the event'
        ),
        make_option('-c', '--clear-videos',
            dest= 'clear_videos',
            action= 'store_true',
            default= False,
            help= 'Clear videos for the event'
        ),
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
        
        if options["event_id"] is None:
            if options["event_name"]:
                print options["event_name"]
                event = Event.objects.get(name=options["event_name"])
            else:
                print "Please give a race name or id"
                return
        else:
            event = Event.objects.get(id=options["event_id"])
        
        if options["clear_tags"]:
            RunnerTag.objects.filter(video__event=event).delete()
            
        if options["clear_videos"]:
            Video.objects.filter(event=event).delete()
        
        if not options["file_name"]:
            print "Please give a JSON file name"
            return
        
        with open(options["file_name"],'r') as json_file:
            docs = [row["doc"] for row in json.load(json_file)["rows"]]
            videos = [doc for doc in docs if doc.get("type",None) == "video"]
            for video in videos:
                try:
                    spectator = Spectator.objects.get(guid=video["ownerID"])
                    Video.objects.create(
                             guid = video["_id"],
                             event = event,
                             spectator = spectator,
                             start_time = fromtimestamp(video["time"]),
                             duration = video["duration"],
                             distance = video["position"],
                             latitude = video["lat"],
                             longitude = video["lon"],
                         )
                except Exception as e:
                    print "Error with video %s: %s"%(video["_id"], e)
            
            finishers = Finisher.objects.filter(race__event=event)
            tags = [doc for doc in docs if doc.get("type",None) == "tag"]
            print "%d tags in file, %d tags in database"%(len(tags), RunnerTag.objects.count())
            for tag in tags:
                try:
                    video = Video.objects.get(guid=tag["videoID"])
                    rs = finishers.filter(bib_number=tag["runnerNumber"])
                    RunnerTag.objects.create(
                               guid = tag["_id"],
                               finisher = rs[0] if rs.count() else None,
                               runner_number = tag["runnerNumber"],
                               video = video,
                               time = fromtimestamp(tag["time"]),
                               distance = tag["position"],
                               latitude = tag["lat"],
                               longitude = tag["lon"],
                                       )
                except Exception as e:
                    ""
                    #print "Error with tag %s: %s"%(tag["_id"], e)
            
            print "Now %d tags in database"%(RunnerTag.objects.count())
        