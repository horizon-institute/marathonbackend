# -*- coding: utf-8 -*-

from marathon.models import Video, RunnerTag
from django.core.management.base import NoArgsCommand
from django.conf import settings
import subprocess
import os
import urllib

class Command(NoArgsCommand):
    
    help = "Creating thumbnails for videos"
    
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
                    framedir = "video"
                else:
                    frametime = obj.video_time
                    framedir = "runnertag"
                
                filename = os.path.join("thumbnails",framedir,"%s.jpg"%obj.guid)
                jpgfile = os.path.join(settings.MEDIA_ROOT,filename)
                
                try:
                    
                    cmdline = '%s -i "%s" -vf scale=225:-1 -ss %d -vframes 1 -y "%s"'%(
                                                       settings.VIDEO_CONV_CMD,
                                                       tmpfilename,
                                                       frametime,
                                                       jpgfile
                                                       )
                    print cmdline
                    obj.thumbnail = os.path.join(settings.MEDIA_URL,filename)
                    subprocess.call(cmdline, shell=True)
                    obj.save()
                    
                except Exception, e:
                    print "ERROR WHEN PROCESSING THUMBNAIL"
            
            os.remove(tmpfilename)
            

            
        
