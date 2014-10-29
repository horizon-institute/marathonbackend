# -*- coding: utf-8 -*-

from marathon.models import Video
from django.core.management.base import NoArgsCommand
from django.conf import settings
import subprocess
from dateutil import parser
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
                
                headers = mp4data.info()
                if "Last-modified" in headers:
                    v.server_last_modified = parser.parse(headers["Last-modified"])
                                    
                mp4output = open(mp4file,"wb")
                mp4output.write(mp4data.read())
                mp4output.close()
                
                
                cmdline = '%s "%s" -show_format'%(
                                                  settings.VIDEO_PROBE_CMD,
                                                  mp4file
                                                  )
                probelines = subprocess.check_output(cmdline, shell=True)
                durlines = [l for l in re.split("[\n\r]+",probelines) if l[:9] == "duration="]
                if durlines:
                    duration = int(round(float(durlines[0][9:])))
                    v.duration = duration
                else:
                    duration = 0
                v.online = True
                
                v.save()
                
                os.remove(mp4file)
                
            except urllib2.URLError:
                print "MP4 file not online"
            
            except Exception, e:
                print e
            
        