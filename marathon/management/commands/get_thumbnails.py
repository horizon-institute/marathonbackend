# -*- coding: utf-8 -*-

from marathon.models import Video, RunnerTag
from django.core.management.base import NoArgsCommand
from django.conf import settings
import subprocess
import os
import urllib
import re

class Command(NoArgsCommand):
    
    help = "Import a spectator description file"
    
    def handle(self, *args, **options):
        
        urldict = {}
        
        vqs = Video.objects.filter(thumbnail__iexact="", online=True)
        
        print "%d videos to process"%vqs.count()
        
        for v in vqs:
            if v.url not in urldict:
                urldict[v.url] = []
            urldict[v.url].append(v)
            
        rtqs = RunnerTag.objects.select_related("video").filter(thumbnail__iexact="", video__online=True)
        
        print "%d tags to process"%rtqs.count()
        
        for rt in rtqs:
            if rt.video.url not in urldict:
                urldict[rt.video.url] = []
            urldict[rt.video.url].append(rt)
        
        tmpfilename = os.path.join(settings.MEDIA_ROOT,"temp.mp4")
        
        for url in urldict:
            
            urllib.urlretrieve(url, tmpfilename)
            
            print "Retrieving %s"%url
            
            for obj in urldict[url]:
                
                
                if obj.__class__.__name__ == "Video":
                    frametime = obj.duration/2
                else:
                    frametime = obj.video_time
                
                jpgfile = os.path.join(settings.MEDIA_ROOT,"%s.jpg"%obj.guid)
                
                try:
                    
                    cmdline = 'ffmpeg -vf scale=225:-1 -ss %d -i "%s" -vframes 1 -y "%s"'%(frametime, tmpfilename, jpgfile)
                    obj.thumbnail = "%s.jpg"%obj.guid
                    obj.save()
                    subprocess.call(cmdline, shell=True)
                    
                except Exception, e:
                    print "ERROR WHEN PROCESSING THUMBNAIL"
            
            os.remove(tmpfilename)
            

            
        