# -*- coding: utf-8 -*-

from marathon.models import Race, Finisher
from django.core.management.base import BaseCommand
from optparse import make_option
import re

class Command(BaseCommand):
    
    help = "Import a race result file"
    
    option_list = BaseCommand.option_list + (
        make_option('-c', '--clear',
            dest= 'clear',
            action= 'store_true',
            default= False,
            help= 'Clear finishers for the race'
        ),
        make_option('-n','--race_name',
            dest= 'race_name',
            default= None,
            help= 'Race name'
        ),
        make_option('-i','--race_id',
            dest= 'race_id',
            default= None,
            help= 'Race id'
        ),
        make_option('-f','--file_name',
            dest= 'file_name',
            default= None,
            help= 'File name'
        ),
    )
    
    def handle(self, *args, **options):
        
        if not options["file_name"]:
            print "Please choose a file"
            return
        
        if options["race_id"] is None:
            if options["race_name"]:
                race = Race.objects.get(name=options["race_name"])
            else:
                print "Please give a race name or id"
                return
        else:
            race = Race.objects.get(id=options["race_id"])
        
        print "Importing data for race %s"%(race.name)
        
        if options["clear"]:
            Finisher.objects.filter(race=race).delete()
        
        def get_secs(ts):
            t = [ int(d) for d in re.findall('\d+',ts) ]
            return 60*(60*t[0] + t[1]) + t[2]
        
        with open(options["file_name"],'r') as f:
            for line in f.readlines():
                results = re.findall('^(\d+)\s(\d+)\s([\s\w]+)\s([MF])\s[\s\w]*(\d{2}\:\d{2}\:\d{2})\s(\d+)\s(\d{2}\:\d{2}\:\d{2})',line)
                if results:
                    t = results[0]
                    Finisher.objects.create(
                          race = race,
                          bib_number = int(t[1]),
                          name = t[2],
                          gun_time = get_secs(t[4]),
                          chip_time = get_secs(t[6]),
                          )
        
        
                