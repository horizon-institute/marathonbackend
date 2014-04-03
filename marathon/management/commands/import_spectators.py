# -*- coding: utf-8 -*-

from marathon.models import Spectator
from django.core.management.base import BaseCommand
from optparse import make_option
import json

class Command(BaseCommand):
    
    help = "Import a spectator description file"
    
    option_list = BaseCommand.option_list + (
        make_option('-c', '--clear',
            dest= 'clear',
            action= 'store_true',
            default= False,
            help= 'Clear all spectators'
        ),
        make_option('-f','--file_name',
            dest= 'file_name',
            default= None,
            help= 'JSON File name'
        ),
    )
    
    def handle(self, *args, **options):
        
        if options["clear"]:
            print "Deleting ALL spectators"
            Spectator.objects.all().delete()
            
        if not options["file_name"]:
            print "Please give a JSON file name"
            return
        
        with open(options["file_name"],'r') as json_file:
            spectator_data = json.load(json_file)
            for guid in spectator_data:
                data = spectator_data[guid]
                Spectator.objects.create(
                     guid = guid,
                     name = data["p_no"],
                     user = None,
                )
        