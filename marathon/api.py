from tastypie import resources, fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.http import HttpGone, HttpForbidden
from tastypie.bundle import Bundle
from oauth2_tastypie.authentication import OAuth20Authentication
from marathon.models import Spectator, Finisher, Video, RunnerTag
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.conf.urls import url
from django.db.models import Count
import re
import datetime

class SpectatorResource(resources.ModelResource):
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/runnertags/$" % self._meta.resource_name, self.wrap_view('get_runnertags'), name="api_get_runnertags"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/runnertags/$" % self._meta.resource_name, self.wrap_view('get_runnertags'), name="api_get_runnertags"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/videos/$" % self._meta.resource_name, self.wrap_view('get_videos'), name="api_get_videos"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/videos/$" % self._meta.resource_name, self.wrap_view('get_videos'), name="api_get_videos"),
        ]
    
    def get_runnertags(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        request.GET = request.GET.copy()
        request.GET["video__spectator__id"] = obj.id
        nested_resource = RunnerTagResource()
        return nested_resource.get_list(request)
    
    def get_videos(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        request.GET = request.GET.copy()
        request.GET["spectator__id"] = obj.id
        nested_resource = VideoResource()
        return nested_resource.get_list(request)
    
    class Meta:
        queryset = Spectator.objects.all()
        resource_name = 'spectator'
        fields = ['id', 'guid', 'name']
        allowed_methods = ['get']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = DjangoAuthorization()
        filtering = {
             "id": ("exact",),
             "name": ALL,
             "guid": ("exact",),
        }

class FinisherAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        if bundle.request.user.has_perm('can_view_private_events'):
            return object_list
        return object_list.filter(race__event__public=True)

    def read_detail(self, object_list, bundle):
        if bundle.request.user.has_perm('can_view_private_events'):
            return True
        return not bundle.obj.race.event.private

class FinisherResource(resources.ModelResource):
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/bib_number/(?P<bib_number>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/runnertags/$" % self._meta.resource_name, self.wrap_view('get_runnertags'), name="api_get_runnertags"),
            url(r"^(?P<resource_name>%s)/bib_number/(?P<bib_number>[\w\d_.-]+)/runnertags/$" % self._meta.resource_name, self.wrap_view('get_runnertags'), name="api_get_runnertags"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/potentialtags/$" % self._meta.resource_name, self.wrap_view('get_potentialtags'), name="api_get_potentialtags"),
            url(r"^(?P<resource_name>%s)/bib_number/(?P<bib_number>[\w\d_.-]+)/potentialtags/$" % self._meta.resource_name, self.wrap_view('get_potentialtags'), name="api_get_potentialtags"),
        ]
    
    event_name = fields.CharField(attribute='race__event__name', readonly=True)
    race_name = fields.CharField(attribute='race__name', readonly=True)
    race_type = fields.CharField(attribute='race__racetype__name', readonly=True)
    race_distance = fields.FloatField(attribute='race__racetype__distance', readonly=True)
    race_start_time = fields.DateTimeField(attribute='race__start_time', readonly=True)
    average_speed = fields.FloatField(attribute='average_speed')
    average_speed_kph = fields.FloatField(attribute='average_speed_kph')
    average_speed_mph = fields.FloatField(attribute='average_speed_mph')
    mile_pace_seconds = fields.FloatField(attribute='mile_pace')
    km_pace_seconds = fields.FloatField(attribute='km_pace')
    mile_pace = fields.CharField(attribute='mile_pace')
    km_pace = fields.CharField(attribute='km_pace')
    chip_time_seconds = fields.FloatField(attribute='chip_time')
    gun_time_seconds = fields.FloatField(attribute='gun_time')
    chip_time = fields.CharField(attribute='chip_time')
    gun_time = fields.CharField(attribute='gun_time')
    tag_count = fields.IntegerField(attribute='runnertag_count', readonly=True)
    
    def get_runnertags(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        request.GET = request.GET.copy()
        request.GET["finisher__id"] = obj.id
        nested_resource = RunnerTagResource()
        return nested_resource.get_list(request)
    
    def get_potentialtags(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        request.GET = request.GET.copy()
        request.GET["finisher_id"] = obj.id
        nested_resource = PotentialTagResource()
        return nested_resource.get_list(request)
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(FinisherResource, self).build_filters(filters)
        
        query = filters.get('q', filters.get('term', None))
        if query is not None:
            f = {}
            if re.match("^\d+$", query):
                f["bib_number__startswith"] = query
            else:
                f["name__icontains"] = query
            orm_filters.update({'custom': f})
    
        return orm_filters
    
    def apply_filters(self, request, applicable_filters):
        if 'custom' in applicable_filters:
            custom = applicable_filters.pop('custom')
        else:
            custom = None
        semi_filtered = super(FinisherResource, self).apply_filters(request, applicable_filters)
        return semi_filtered.filter(**custom) if custom else semi_filtered
    
    class Meta:
        queryset = Finisher.objects.select_related('race', 'race__event', 'race__racetype').annotate(runnertag_count=Count('runnertags'))
        resource_name = 'finisher'
        fields = ['id', 'start_time', 'finish_time', 'name', 'bib_number']
        allowed_methods = ['get']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = FinisherAuthorization()
        filtering = {
             "id": ("exact",),
             "name": ALL,
             "bib_number": ALL,
             "race": ALL_WITH_RELATIONS,
        }

class VideoAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        if bundle.request.user.has_perm('can_view_private_events'):
            return object_list
        return object_list.filter(event__public=True)

    def read_detail(self, object_list, bundle):
        if bundle.request.user.has_perm('can_view_private_events'):
            return True
        return not bundle.obj.event.private

class VideoResource(resources.ModelResource):
    spectator = fields.ToOneField(SpectatorResource, 'spectator')
    spectator_guid = fields.CharField(attribute='spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='spectator__name', readonly=True)
    event_name = fields.CharField(attribute='event__name', readonly=True)
    distance_miles = fields.FloatField(attribute='distance_miles')
    distance_km = fields.FloatField(attribute='distance_km')
    end_time = fields.DateTimeField(attribute='end_time', readonly=True)
    tag_count = fields.IntegerField(attribute='runnertag_count', readonly=True)
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/runnertags/$" % self._meta.resource_name, self.wrap_view('get_runnertags'), name="api_get_runnertags"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/runnertags/$" % self._meta.resource_name, self.wrap_view('get_runnertags'), name="api_get_runnertags"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/spectator/$" % self._meta.resource_name, self.wrap_view('get_spectator'), name="api_get_spectator"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/spectator/$" % self._meta.resource_name, self.wrap_view('get_spectator'), name="api_get_spectator"),
        ]
    
    def get_runnertags(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        request.GET = request.GET.copy()
        request.GET["video__id"] = obj.id
        nested_resource = RunnerTagResource()
        return nested_resource.get_list(request)
    
    def get_spectator(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        nested_resource = SpectatorResource()
        return nested_resource.get_detail(request, pk=obj.spectator_id)
    
    class Meta:
        queryset = Video.objects.select_related('spectator','event').annotate(runnertag_count=Count('runnertags'))
        resource_name = 'video'
        fields = ['id', 'guid', 'distance', 'latitude', 'longitude', 'start_time', 'duration']
        allowed_methods = ['get']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = VideoAuthorization()
        filtering = {
             "id": ("exact",),
             "distance": ALL,
             "start_time": ALL,
             "duration": ALL,
             "guid": ("exact",),
             "event": ALL_WITH_RELATIONS,
             "spectator": ALL_WITH_RELATIONS,
        }

class RunnerTagAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        if bundle.request.user.has_perm('can_view_private_events'):
            return object_list
        return object_list.filter(video__event__public=True)

    def read_detail(self, object_list, bundle):
        if bundle.request.user.has_perm('can_view_private_events'):
            return True
        return not bundle.obj.video.event.private

class RunnerTagResource(resources.ModelResource):
    video = fields.ToOneField(VideoResource, 'video')
    video_guid = fields.CharField(attribute='video__guid', readonly=True)
    video_time = fields.IntegerField(attribute='video_time', readonly=True)
    event_name = fields.CharField(attribute='video__event__name', readonly=True)
    spectator = fields.ToOneField(SpectatorResource, 'video__spectator', readonly=True)
    spectator_guid = fields.CharField(attribute='video__spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='video__spectator__name', readonly=True)
    finisher = fields.ToOneField(FinisherResource, 'finisher', null=True, blank=True)
    finisher_name = fields.CharField(attribute='finisher__name', null=True)
    distance_miles = fields.FloatField(attribute='distance_miles')
    distance_km = fields.FloatField(attribute='distance_km')
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/video/$" % self._meta.resource_name, self.wrap_view('get_video'), name="api_get_video"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/video/$" % self._meta.resource_name, self.wrap_view('get_video'), name="api_get_video"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/spectator/$" % self._meta.resource_name, self.wrap_view('get_spectator'), name="api_get_spectator"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/spectator/$" % self._meta.resource_name, self.wrap_view('get_spectator'), name="api_get_spectator"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/finisher/$" % self._meta.resource_name, self.wrap_view('get_finisher'), name="api_get_finisher"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/finisher/$" % self._meta.resource_name, self.wrap_view('get_finisher'), name="api_get_finisher"),
        ]
    
    def get_video(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        nested_resource = VideoResource()
        return nested_resource.get_detail(request, pk=obj.video_id)
    
    def get_spectator(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        nested_resource = SpectatorResource()
        return nested_resource.get_detail(request, pk=obj.video.spectator_id)
    
    def get_finisher(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        if obj.finisher_id is None:
            return HttpGone()
        nested_resource = FinisherResource()
        return nested_resource.get_detail(request, pk=obj.finisher_id)
    
    class Meta:
        queryset = RunnerTag.objects.select_related('video','video__spectator','finisher','video__event')
        resource_name = 'runnertag'
        fields = ['id', 'guid', 'runner_number', 'distance', 'latitude', 'longitude', 'time', 'video_id', 'video']
        allowed_methods = ['get']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = RunnerTagAuthorization()
        filtering = {
             "id": ("exact",),
             "distance": ALL,
             "time": ALL,
             "runner_number": ("exact",),
             "duration": ALL,
             "guid": ("exact",),
             "video": ALL_WITH_RELATIONS,
             "finisher": ALL_WITH_RELATIONS,
        }

class PotentialTag(object):
     
    already_tagged = False
    margin = None
    video_time = None
     
    def _calculate_position(self):
        if self._tagqueryset is not None:
            tqs = self._tagqueryset
        else:
            tqs = RunnerTag.objects.filter(video__event=self._video.event)
        tqs = tqs.filter(finisher=self._finisher)
        tvqs = tqs.filter(video=self._video)
        if tvqs.count():
            self.already_tagged = True
            self.margin = 0
            self.video_time = tvqs[0].video_time
            self.estimated_time = tvqs[0].time
        else:
            segments = [(self._finisher.start_time,0),(self._finisher.finish_time, self._finisher.race.racetype.distance)]
            segments += [(tag.time, tag.distance) for tag in tqs]
            segments.sort(key=lambda t: t[1])
            for i in range(len(segments)-1):
                if self._video.distance >= segments[i][1] and self._video.distance < segments[i+1][1] and segments[i][1] != segments[i+1][1]:
                    self.estimated_time = segments[i][0] + datetime.timedelta(0, (segments[i+1][0] - segments[i][0]).total_seconds() * (self._video.distance - segments[i][1]) / (segments[i+1][1] - segments[i][1]))
                    video_time = (self.estimated_time - self._video.start_time).total_seconds()
                    if video_time < 0:
                        self.video_time = 0
                        self.margin = abs(video_time)
                    else:
                        if video_time > self._video.duration:
                            self.video_time = self._video.duration
                            self.margin = (video_time - self._video.duration)
                        else:
                            self.video_time = video_time
                            self.margin = 0
    
    def __init__(self, finisher, video, **kwargs):
        self._finisher = finisher
        self._video = video
        self._tagqueryset = kwargs.get("tagqueryset", None)
        self._calculate_position()
    
    def __getattribute__(self,name):
        if "__" in name:
            attrs = name.split("__",1)
            return getattr(object.__getattribute__(self,attrs[0],None),attrs[1],None)
        else:
            return object.__getattribute__(self, name)
     
    @property
    def video(self):
        return self._video
     
    @video.setter
    def video(self, video):
        self._video = video
        self._calculate_position()
         
    @property
    def finisher(self):
        return self._finisher
     
    @finisher.setter
    def finisher(self, finisher):
        self._finisher = finisher
        self._calculate_position()
    
    @property
    def pk(self):
        return "%d_%d"%(self._finisher.id, self._video.id)
     
class PotentialTagResource(resources.Resource):
     
    video = fields.ToOneField(VideoResource, 'video')
    finisher = fields.ToOneField(FinisherResource, 'finisher')
    finisher_name = fields.CharField(attribute='finisher__name', readonly=True)
    bib_number = fields.IntegerField(attribute='finisher__bib_number', readonly=True)
    video_time = fields.IntegerField(attribute='video_time', readonly=True, null=True)
    estimated_time = fields.DateTimeField(attribute='estimated_time', readonly=True, null=True)
    video_guid = fields.CharField(attribute='video__guid', readonly=True, null=True)
    video_duration = fields.IntegerField(attribute='video__duration', readonly=True, null=True)
    video_start_time = fields.DateTimeField(attribute='video__start_time', readonly=True, null=True)
    video_end_time = fields.DateTimeField(attribute='video__end_time', readonly=True, null=True)
    distance = fields.IntegerField(attribute='video__distance', readonly=True)
    distance_km = fields.IntegerField(attribute='video__distance_km', readonly=True)
    distance_miles = fields.IntegerField(attribute='video__distance_miles', readonly=True)
    margin = fields.IntegerField(attribute='margin', readonly=True, null=True)
    
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.pk
        else:
            kwargs['pk'] = bundle_or_obj.pk
        return kwargs
    
    def obj_get_list(self, bundle, **kwargs):
        results = []
        margin = bundle.request.GET.get("margin", 600)
        getkeys = {}
        if "finisher_id" in bundle.request.GET:
            getkeys["id"] = bundle.request.GET["finisher_id"]
        if "bib_number" in bundle.request.GET:
            getkeys["bib_number"] = bundle.request.GET["bib_number"]
        finisher = Finisher.objects.get(**getkeys)
        event = finisher.race.event
        if not event.public and not bundle.request.user.has_perm('can_view_private_events'):
            return []
        vqs = Video.objects.filter(event=event)
        tqs = RunnerTag.objects.filter(video__event=event)
        for video in vqs:
            pt = PotentialTag(finisher, video, tag_queryset=tqs)
            if pt.margin is not None and pt.margin <= margin:
                results.append(pt)
        return results
     
    class Meta:
        resource_name = 'potentialtag'
        allowed_methods = ['get']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = RunnerTagAuthorization()