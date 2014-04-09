from tastypie import resources, fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.http import HttpGone
from oauth2_tastypie.authentication import OAuth20Authentication
from marathon.models import Spectator, Finisher, Video, RunnerTag
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.conf.urls import url

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
        ]
    
    event_name = fields.CharField(attribute='race__event__name', readonly=True)
    race_name = fields.CharField(attribute='race__name', readonly=True)
    race_type = fields.CharField(attribute='race__racetype__name', readonly=True)
    race_distance = fields.FloatField(attribute='race__racetype__distance', readonly=True)
    race_start_time = fields.DateTimeField(attribute='race__start_time', readonly=True)
    average_speed = fields.FloatField(attribute='average_speed')
    average_speed_kph = fields.FloatField(attribute='average_speed_kph')
    average_speed_mph = fields.FloatField(attribute='average_speed_mph')
    mile_pace = fields.TimeField(attribute='mile_pace')
    km_pace = fields.TimeField(attribute='km_pace')
    
    def get_runnertags(self, request, **kwargs):
        bundle = self.build_bundle(data=kwargs, request=request)
        obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
        request.GET = request.GET.copy()
        request.GET["finisher__id"] = obj.id
        nested_resource = RunnerTagResource()
        return nested_resource.get_list(request)
    
    class Meta:
        queryset = Finisher.objects.select_related('race', 'race__event', 'race__racetype')
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
        queryset = Video.objects.select_related('spectator','event')
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
    video_time = fields.DateTimeField(attribute='video_time', readonly=True)
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
        