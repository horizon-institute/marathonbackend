from tastypie import resources, fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication, ApiKeyAuthentication
from tastypie.authorization import Authorization
from oauth2_tastypie.authentication import OAuth20Authentication
from marathon.models import Spectator, Video, RunnerTag, PositionUpdate, Event
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.conf.urls import url
from django.db.models import Q

class SpectatorAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_superuser:
            return object_list
        return object_list.filter(user_id=current_user.id)

    def read_detail(self, object_list, bundle):
        if bundle.request.method == "GET" and bundle.obj.user is None:
            return True
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)
    
    def create_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)
    
    def update_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)
    
    def delete_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)

class SpectatorResource(resources.ModelResource):
    last_position = fields.ToOneField('marathon.api.PositionUpdateResource', 'last_position', related_name='last_position', null=True, full=True, readonly=True)

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
    
    def hydrate(self, bundle):
        if "user" not in bundle.data:
            bundle.obj.user_id = bundle.data.get("user_id", bundle.request.user.id)
        return bundle
    
    class Meta:
        queryset = Spectator.objects.all()
        resource_name = 'spectator'
        fields = ['id', 'guid', 'name']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication(), ApiKeyAuthentication())
        authorization = SpectatorAuthorization()
        filtering = {
             "id": ("exact",),
             "name": ALL,
             "guid": ("exact",),
        }

class EventAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return object_list
        return object_list.filter(public=True)

    def read_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser or bundle.obj.public)

class EventResource(resources.ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        fields = ['id', 'name', 'date', 'public', 'is_current']
        allowed_methods = ['get']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication(), ApiKeyAuthentication())
        authorization = EventAuthorization()
        filtering = {
             "id": ("exact",),
             "name": ALL,
             "date": ALL,
             "public": ("exact",),
             "is_current": ("exact",),
        }

class VideoAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_superuser:
            return object_list
        return object_list.filter(Q(spectator__user_id=current_user.id) | (Q(public=True) & Q(event__public=True)))

    def read_detail(self, object_list, bundle):
        current_video = bundle.obj
        current_user = bundle.request.user
        if bundle.request.method == "GET" and not hasattr(current_video, "spectator"): #This would be a schema documentation request
            return True
        if current_user.is_superuser:
            return True
        return ((current_video.spectator.user == current_user) or (current_video.public and current_video.event.public))
    
    def create_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
    def update_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
    def delete_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)

class VideoResource(resources.ModelResource):
    spectator = fields.ToOneField(SpectatorResource, 'spectator')
    spectator_guid = fields.CharField(attribute='spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='spectator__name', readonly=True)
    event_name = fields.CharField(attribute='event__name', readonly=True)
    event_id = fields.CharField(attribute='event_id', readonly=True)
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
    
    def hydrate(self, bundle):
        if "spectator" not in bundle.data:
            if "spectator_id" in bundle.data:
                bundle.obj.spectator_id = bundle.data["spectator_id"]
            elif "spectator_guid" in bundle.data:
                bundle.obj.spectator = Spectator.objects.get(guid=bundle.data["spectator_guid"])
            else:
                bundle.obj.spectator, created = Spectator.objects.get_or_create(user=bundle.request.user, defaults={"name":"Participant %d"%bundle.request.user.id})
        if "event" not in bundle.data:
            if "event_id" in bundle.data:
                bundle.obj.event_id = bundle.data["event_id"]
            else:
                bundle.obj.event = Event.objects.get(is_current=True)
        return bundle
    
    class Meta:
        queryset = Video.objects.select_related('spectator','event')
        resource_name = 'video'
        fields = ['id', 'guid', 'start_time', 'duration', 'public']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication(), ApiKeyAuthentication())
        authorization = VideoAuthorization()
        filtering = {
             "id": ("exact",),
             "start_time": ALL,
             "duration": ALL,
             "guid": ("exact",),
             "event": ALL_WITH_RELATIONS,
             "spectator": ALL_WITH_RELATIONS,
        }
        
class PositionUpdateAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_superuser:
            return object_list
        return object_list.filter(spectator__user_id=current_user.id)

    def read_detail(self, object_list, bundle):
        if bundle.request.method == "GET" and not hasattr(bundle.obj, "spectator"): #This would be a schema documentation request
            return True
        if bundle.request.user.is_superuser:
            return True
        return (bundle.obj.spectator.user == bundle.request.user)
    
    def create_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
    def update_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
    def delete_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
class PositionUpdateResource(resources.ModelResource):
    spectator = fields.ToOneField(SpectatorResource, 'spectator')
    spectator_guid = fields.CharField(attribute='spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='spectator__name', readonly=True)
    
    def hydrate(self, bundle):
        if "spectator" not in bundle.data:
            if "spectator_id" in bundle.data:
                bundle.obj.spectator_id = bundle.data["spectator_id"]
            elif "spectator_guid" in bundle.data:
                bundle.obj.spectator = Spectator.objects.get(guid=bundle.data["spectator_guid"])
            else:
                bundle.obj.spectator,created = Spectator.objects.get_or_create(user=bundle.request.user, defaults={"name":"Participant %d"%bundle.request.user.id})
        return bundle
    
    class Meta:
        queryset = PositionUpdate.objects.select_related('spectator')
        resource_name = 'positionupdate'
        fields = ['id', 'guid', 'time', 'latitude', 'longitude', 'accuracy']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication(), ApiKeyAuthentication())
        authorization = PositionUpdateAuthorization()
        filtering = {
             "id": ("exact",),
             "latitude": ALL,
             "longitude": ALL,
             "accuracy": ALL,
             "time": ALL,
             "guid": ("exact",),
             "spectator": ALL_WITH_RELATIONS,
        }

class RunnerTagAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_superuser:
            return object_list
        return object_list.filter(Q(video__spectator__user_id=current_user.id) | (Q(public=True) & Q(video__public=True) & Q(video__event__public=True)))

    def read_detail(self, object_list, bundle):
        current_user = bundle.request.user
        if bundle.request.method == "GET" and not hasattr(bundle.obj, "video"): #This would be a schema documentation request
            return True
        current_video = bundle.obj.video
        if (not current_user.is_superuser):
            return ((current_video.spectator.user == current_user) or (bundle.obj.public and current_video.public and current_video.event.public))
        return True

    def create_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.video.spectator.user == bundle.request.user)
    
    def update_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.video.spectator.user == bundle.request.user)
    
    def delete_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.video.spectator.user == bundle.request.user)

class RunnerTagResource(resources.ModelResource):
    video = fields.ToOneField(VideoResource, 'video')
    video_guid = fields.CharField(attribute='video__guid', readonly=True)
    video_time = fields.IntegerField(attribute='video_time', readonly=True)
    event_name = fields.CharField(attribute='video__event__name', readonly=True)
    spectator = fields.ToOneField(SpectatorResource, 'video__spectator', readonly=True)
    spectator_guid = fields.CharField(attribute='video__spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='video__spectator__name', readonly=True)
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/video/$" % self._meta.resource_name, self.wrap_view('get_video'), name="api_get_video"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/video/$" % self._meta.resource_name, self.wrap_view('get_video'), name="api_get_video"),
            url(r"^(?P<resource_name>%s)/(?P<pk>[\w\d_.-]+)/spectator/$" % self._meta.resource_name, self.wrap_view('get_spectator'), name="api_get_spectator"),
            url(r"^(?P<resource_name>%s)/guid/(?P<guid>[\w\d_.-]+)/spectator/$" % self._meta.resource_name, self.wrap_view('get_spectator'), name="api_get_spectator"),
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
    
    def hydrate(self, bundle):
        if "video" not in bundle.data:
            if "video_id" in bundle.data:
                bundle.obj.video_id = bundle.data["video_id"]
            if "video_guid" in bundle.data:
                bundle.obj.video = Video.objects.get(guid=bundle.data["video_guid"])
        return bundle
    
    class Meta:
        queryset = RunnerTag.objects.select_related('video','video__spectator','video__event')
        resource_name = 'runnertag'
        fields = ['id', 'guid', 'runner_number', 'latitude', 'longitude', 'accuracy', 'time', 'video_id', 'public']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication(), ApiKeyAuthentication())
        authorization = RunnerTagAuthorization()
        filtering = {
             "id": ("exact",),
             "latitude": ALL,
             "longitude": ALL,
             "accuracy": ALL,
             "time": ALL,
             "runner_number": ("exact",),
             "guid": ("exact",),
             "video": ALL_WITH_RELATIONS,
        }
