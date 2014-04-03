# -*- coding: utf-8 -*-

from marathon.models import RaceType
from django.core.management.base import BaseCommand
from optparse import make_option
import csv

class Command(BaseCommand):
    
    help = "Import a race description file"
    
    option_list = BaseCommand.option_list + (
        make_option('-c', '--clear',
            dest= 'clear',
            action= 'store_true',
            default= False,
            help= 'Clear all race types'
        ),
        make_option('-f','--file_name',
            dest= 'file_name',
            default= None,
            help= 'CSV File name'
        ),
    )
    
    def handle(self, *args, **options):
        
        if options["clear"]:
            RaceType.objects.all().delete()
            
        if not options["file_name"]:
            print "Please give a CSV file name"
            return
            
        with open(options["file_name"],'rb') as csv_file:
            dialect = csv.Sniffer().sniff(csv_file.read(1024))
            csv_file.seek(0)
            
            reader = csv.DictReader(csv_file, dialect=dialect)
            
            for line in reader:
                RaceType.objects.create(**line)
        