# -*- coding: utf-8 -*-

from marathon.models import Video
from django.core.management.base import NoArgsCommand
from django.conf import settings
import subprocess, os, urllib, re, logging

class Command(NoArgsCommand):
    
    help = "Creates low resolution, web-compliant versions of videos"
    
    logger = logging.getLogger(__name__)
    
    def handle(self, *args, **options):
                
        vqs = Video.objects.filter(online=True, lowres_video_url__iexact="")
        
        print "%d videos to process"%vqs.count()
        
        tmpsrc = os.path.join(settings.MEDIA_ROOT,"tmp/tempsource.mp4")
        
        for v in vqs:
             
            print "Retrieving %s"%v.url
            
            urllib.urlretrieve(v.url, tmpsrc)
            
            cmdline = '%s -show_streams "%s"'%(
                                              settings.VIDEO_PROBE_CMD,
                                              tmpsrc
                                              )
            probelines = subprocess.check_output(cmdline, shell=True)
            
            width = None
            height = None
            for l in re.split("[\n\r]+",probelines):
                t = l.split("=")
                if t[0] == "width":
                    width = t[1]
                if t[0] == "height":
                    height = t[1] 
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
                self.logger.debug(cmdline)
                subprocess.call(cmdline, shell=True)
                
                v.lowres_video_url = desturl
                v.save()
                
                self.logger.debug("Made low res video for Video ID=%d"%v.id)
                
            except Exception:
                print "Error while processing video"
                self.logger.error("Error while processing Video ID=%d"%v.id)
            
            os.remove(tmpsrc)
            

            
        
