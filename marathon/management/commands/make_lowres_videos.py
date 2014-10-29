# -*- coding: utf-8 -*-

from marathon.models import Video
from django.core.management.base import NoArgsCommand
from django.conf import settings
import subprocess, os, urllib, re

class Command(NoArgsCommand):
    
    help = "Import a spectator description file"
    
    def handle(self, *args, **options):
                
        vqs = Video.objects.filter(online=True, lowres_video_url__iexact="")
        
        print "%d videos to process"%vqs.count()
        
        tmpsrc = os.path.join(settings.MEDIA_ROOT,"tmp/tempsource.mp4")
        
        for v in vqs:
             
            print "Retrieving %s"%v.url
            
            urllib.urlretrieve(v.url, tmpsrc)
            
            cmdline = '%s "%s"'%(
                                              settings.VIDEO_PROBE_CMD,
                                              tmpsrc
                                              )
            probelines = subprocess.check_output(cmdline, shell=True)
            
            width = None
            height = None
            for l in re.split("[\n\r]+",probelines):
                if "Video:" in l:
                    res = re.findall("(\d+)x(\d+)",l)
                    if res:
                        width = int(res[0])
                        height = int(res[1])
                        break
            
            if width and height:
                if width > height:
                    ow = "240"
                    oh = "%d"%(240.*float(height)/float(width))
                else:
                    oh = "240"
                    ow = "%d"%(240.*float(width)/float(height))
            else:
                ow = "iw"
                oh = "ih"
            
            destfilebase = "videos/video_%d.mp4"%v.id
            
            destfile = os.path.join(settings.MEDIA_ROOT,destfilebase)
            desturl = os.path.join(settings.MEDIA_URL,destfilebase)
            
            try:
                cmdline = '%s -i "%s" -codec:v libx264 -codec:a aac -b:v 200k -b:a 32k -y -tune zerolatency -strict experimental -vf scale="%s:%s" "%s"'%(
                                                                      settings.VIDEO_CONV_CMD,
                                                                      tmpsrc,
                                                                      ow,
                                                                      oh,
                                                                      destfile
                                                                      )
                subprocess.call(cmdline, shell=True)
                
                v.lowres_video_url = desturl
                v.save()
                
            except Exception:
                print "Error while processing video"
            
            os.remove(tmpsrc)
            

            
        