from tastypie import resources, fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from oauth2_tastypie.authentication import OAuth20Authentication
from marathon.models import Spectator, Video, RunnerTag, PositionUpdate
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.conf.urls import url
from django.db.models import Count, Q

class SpectatorAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_superuser:
            return object_list
        return object_list.filter(user_id=current_user.id)

    def read_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)

class SpectatorResource(resources.ModelResource):
    last_position = fields.ToOneField('marathon.api.PositionUpdateResource', 'last_position', related_name='last_position', null=True, full=True)

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
    
#     def dehydrate(self, bundle):
#         bundle.data["last_position"] = bundle.obj.positionupdates.order_by("-time")[0] if bundle.obj.positionupdates.count() else None
#         return bundle
    
    class Meta:
        queryset = Spectator.objects.all()
        resource_name = 'spectator'
        fields = ['id', 'guid', 'name']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = SpectatorAuthorization()
        filtering = {
             "id": ("exact",),
             "name": ALL,
             "guid": ("exact",),
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
        if current_user.is_superuser:
            return True
        return ((current_video.spectator.user == current_user) or (current_video.public and current_video.event.public))

class VideoResource(resources.ModelResource):
    spectator = fields.ToOneField(SpectatorResource, 'spectator')
    spectator_guid = fields.CharField(attribute='spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='spectator__name', readonly=True)
    event_name = fields.CharField(attribute='event__name', readonly=True)
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
        fields = ['id', 'guid', 'start_time', 'duration']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = VideoAuthorization()
        filtering = {
             "id": ("exact",),
             "start_time": ALL,
             "duration": ALL,
             "guid": ("exact",),
             "event": ALL_WITH_RELATIONS,
             "spectator": ALL_WITH_RELATIONS,
        }

class PositionUpdateResource(resources.ModelResource):
    spectator = fields.ToOneField(SpectatorResource, 'spectator')
    spectator_guid = fields.CharField(attribute='spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='spectator__name', readonly=True)
    
    class Meta:
        queryset = PositionUpdate.objects.select_related('spectator')
        resource_name = 'positionupdate'
        fields = ['id', 'guid', 'time', 'latitude', 'longitude', 'accuracy']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = DjangoAuthorization()
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
        return object_list.filter(Q(video__spectator__user_id=current_user.id) | (Q(video__public=True) & Q(video__event__public=True)))

    def read_detail(self, object_list, bundle):
        current_user = bundle.request.user
        current_video = bundle.obj.video
        if (not current_user.is_superuser):
            return ((current_video.spectator.user == current_user) or (current_video.public and current_video.event.public))
        return True

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
        
    class Meta:
        queryset = RunnerTag.objects.select_related('video','video__spectator','video__event')
        resource_name = 'runnertag'
        fields = ['id', 'guid', 'runner_number', 'latitude', 'longitude', 'accuracy', 'time', 'video_id']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
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
