# -*- coding: utf-8 -*-

from marathon.models import RacePoint, LocationName, LocationDistance
from django.core.management.base import BaseCommand
from django.db.models import Avg
from marathon.utils import calculate_easting_delta, get_event_from_options
from optparse import make_option
import json, urllib2

class Command(BaseCommand):
    
    help = "Importing OpenStreetMap data"
    
    option_list = BaseCommand.option_list + (
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
        make_option('-r', '--data-radius',
            dest= 'data_radius',
            default= 20,
            help= 'Radius to look for OSM data around points'
        ),
        make_option('-e', '--endpoint-url',
            dest= 'endpoint_url',
            default= "http://www.overpass-api.de/api/interpreter",
            help= 'Overpass API endpoint URL'
        ),
        make_option('-s', '--use-ssl',
            dest= 'use_ssl',
            action= 'store_true',
            default= False,
            help= 'Use an SSL connection to gather OSM data'
        ),
    )
    
    
    def handle(self, *args, **options):
        
        event = get_event_from_options(options)
        
        rpqs = RacePoint.objects.filter(event=event)
        
        i = 0
        n = rpqs.count()
        
        if not n:
            print "No race points for this event. You may import a course using import_race_course"
            return
        
        meanlat = rpqs.aggregate(Avg("latitude"))["latitude__avg"]
        
        osmdataradius = int(options["data_radius"])
        osmlongdelta = calculate_easting_delta(meanlat, osmdataradius)
        osmlatdelta = osmdataradius * 90./10000000.
        osmendpoint = options["endpoint_url"]
        if options["use_ssl"]:
            osmendpoint = osmendpoint.replace("http://","https://")
        
        for rp in rpqs:
            i += 1
            print "Fetching data for point %d/%d"%(i,n)
            try:
                query = '[out:json];way(%.6f,%.6f,%.6f,%.6f)["name"];out meta;'%(
                                                            rp.latitude-osmlatdelta,
                                                            rp.longitude-osmlongdelta,
                                                            rp.latitude+osmlatdelta,
                                                            rp.longitude+osmlongdelta)
                result = urllib2.urlopen(osmendpoint, query)
                jsondata = json.loads(result.read())
                
                elements = []
                
                for element in jsondata["elements"]:
                    
                    tags = element["tags"]
                    
                    elementtype = tags.get("amenity", "unknown")
                    
                    for key in [
                                ("building","building"),
                                ("highway","road"),
                                ("shop","shop"),
                                ("leisure","leisure"),
                                ("tourism","tourism"),
                                ("waterway","waterway")]:
                        if key[0] in tags:
                            elementtype = key[1]
                    
                    if ([tags["name"], elementtype] not in elements):
                        elements.append([tags["name"], elementtype])
                        
                    postcode = tags.get("postal_code", tags.get("addr:postcode","")).split(" ")[0]
                    if postcode and ([postcode,"postcode"] not in elements):
                        elements.append([postcode,"postcode"])
                
                print ", ".join([e[0] for e in elements])
                
                LocationDistance.objects.filter(reference_point=rp).exclude(location_name__type="race marker").delete()
                
                for element in elements:
                    
                    locname, created = LocationName.objects.get_or_create(
                                                                          name = element[0],
                                                                          type = element[1])
                    LocationDistance.objects.create(
                                              location_name = locname,
                                              accuracy = osmdataradius,
                                              reference_point = rp)
                
            except Exception, e:
                print "Error", e
        
        
            
        