# -*- coding: utf-8 -*-

from marathon.models import Video
from django.core.management.base import NoArgsCommand
from django.conf import settings
import subprocess
import os
import urllib2
import re

class Command(NoArgsCommand):
    
    help = "Import a spectator description file"
    
    def handle(self, *args, **options):
        
        qs = Video.objects.exclude(url__iexact="").filter(online=False)
        for v in qs:
            print '"%s"'%v.url
            try:
                mp4file = os.path.join(settings.MEDIA_ROOT,"%s.mp4"%v.guid)
                mp4data = urllib2.urlopen(v.url)
                mp4output = open(mp4file,"wb")
                mp4output.write(mp4data.read())
                mp4output.close()
                
                
                cmdline = 'ffprobe "%s" -show_format'%mp4file
                probelines = subprocess.check_output(cmdline, shell=True)
                durlines = [l for l in re.split("[\n\r]+",probelines) if l[:9] == "duration="]
                if durlines:
                    duration = int(round(float(durlines[0][9:])))
                    v.duration = duration
                else:
                    duration = 0
                v.online = True
                
                frametime = duration/2
                
                jpgfile = os.path.join(settings.MEDIA_ROOT,"%s.jpg"%v.guid)
                cmdline = 'ffmpeg -vf scale=225:-1 -ss %d -i "%s" -vframes 1 -y "%s"'%(frametime, mp4file, jpgfile)
                subprocess.call(cmdline, shell=True)
                
                if os.path.isfile(jpgfile):
                    v.thumbnail = "%s.jpg"%v.guid
                
                v.save()
                
                for t in v.runnertags.all():
                    jpgfile = os.path.join(settings.MEDIA_ROOT,"%s.jpg"%t.guid)
                    cmdline = 'ffmpeg -vf scale=225:-1 -ss %d -i "%s" -vframes 1 -y "%s"'%(t.video_time, mp4file, jpgfile)
                    subprocess.call(cmdline, shell=True)
                        
                    if os.path.isfile(jpgfile):
                        t.thumbnail = "%s.jpg"%t.guid
                        t.save()
                
                os.remove(mp4file)
                
            except urllib2.URLError:
                print "MP4 file not online"
            
        