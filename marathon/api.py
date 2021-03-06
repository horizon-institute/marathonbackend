from tastypie import resources, fields
from tastypie.authentication import MultiAuthentication, SessionAuthentication, ApiKeyAuthentication, BasicAuthentication
from tastypie.authorization import Authorization
from oauth2_tastypie.authentication import OAuth20Authentication
from marathon.models import Spectator, Video, RunnerTag, PositionUpdate, Event, ContentFlag
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.conf.urls import url
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

def api_detail_auth_logger(detailfunc):
    def loggedfunc(self, object_list, bundle):
        request = bundle.request
        is_authorised = detailfunc(self, object_list, bundle)
        logstr = "Request authorised=%r, Username=%s, Superuser=%r"%(
                                                          is_authorised,
                                                          request.user.username,
                                                          request.user.is_superuser)
        if hasattr(bundle, "obj"):
            logstr += " %s id=%r"%(bundle.obj.__class__.__name__, getattr(bundle.obj,"id",None))
        logger.debug(logstr)
        return is_authorised
    return loggedfunc
    
class LoggedMultiAuthentication(MultiAuthentication):

    def __init__(self, *backends, **kwargs):
        backendz = [ SessionAuthentication(), OAuth20Authentication(), ApiKeyAuthentication() ]
        for b in backends:
            backendz.append(b)
        super(LoggedMultiAuthentication, self).__init__(*backendz, **kwargs)
    
    def is_authenticated(self, request, **kwargs):
        result = super(LoggedMultiAuthentication, self).is_authenticated(request, **kwargs)
        logger.debug("Request authenticated=%r"%(result is True))
        return result

# Found on https://gist.github.com/vmihailenco/2382901
class LoggedMixin(object):
    
    def dispatch(self, request_type, request, **kwargs):
        
        logger.debug(" ------ API REQUEST ------ ")
        logger.debug('%s %s %s' % (request.method, request.get_full_path(), request.body))
        logger.debug("Cookie Session ID=%s, Cookie CSRF Token=%s, CSRF Token Header=%s"%(
                                        request.COOKIES.get("sessionid",None),
                                        request.COOKIES.get("csrftoken",None),
                                        request.META.get("HTTP_X_CSRFTOKEN",None),
                                    ))
        try:
            response = super(LoggedMixin, self).dispatch(request_type, request, **kwargs)
        except Exception, e:
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                logger.debug('Response %r' %(e.response.status_code))
            else:
                logger.debug('Other error')
            raise
        logger.debug('Response %s' % (response.status_code))
        return response

class SpectatorAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_superuser:
            return object_list
        return object_list.filter(user_id=current_user.id)

    @api_detail_auth_logger
    def read_detail(self, object_list, bundle):
        if bundle.request.method == "GET" and bundle.obj.user is None:
            return True
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)
    
    @api_detail_auth_logger
    def create_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)
    
    @api_detail_auth_logger
    def update_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)
    
    @api_detail_auth_logger
    def delete_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.user == bundle.request.user)

class SpectatorResource(LoggedMixin, resources.ModelResource):
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
        if ("user" not in bundle.data) and (not hasattr(bundle.obj, "user")):
            bundle.obj.user_id = bundle.data.get("user_id", bundle.request.user.id)
        return bundle
    
    class Meta:
        queryset = Spectator.objects.all()
        resource_name = 'spectator'
        fields = ['id', 'guid', 'name']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = LoggedMultiAuthentication()
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

    @api_detail_auth_logger
    def read_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser or bundle.obj.public)

class EventResource(LoggedMixin, resources.ModelResource):
    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        fields = ['id', 'name', 'date', 'public', 'is_current']
        allowed_methods = ['get']
        authentication = LoggedMultiAuthentication()
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
    
    @api_detail_auth_logger
    def read_detail(self, object_list, bundle):
        current_video = bundle.obj
        current_user = bundle.request.user
        if bundle.request.method == "GET" and not hasattr(current_video, "spectator"): #This would be a schema documentation request
            return True
        if current_user.is_superuser:
            return True
        return ((current_video.spectator.user == current_user) or (current_video.public and current_video.event.public))
    
    @api_detail_auth_logger
    def create_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
    @api_detail_auth_logger
    def update_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
    @api_detail_auth_logger
    def delete_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)

class VideoResource(LoggedMixin, resources.ModelResource):
    spectator = fields.ToOneField(SpectatorResource, 'spectator')
    spectator_guid = fields.CharField(attribute='spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='spectator__name', readonly=True)
    event_name = fields.CharField(attribute='event__name', readonly=True)
    event_id = fields.CharField(attribute='event_id', readonly=True)
    end_time = fields.DateTimeField(attribute='end_time', readonly=True)
    server_created_date = fields.DateTimeField(attribute='server_created_date', readonly=True)
    server_updated_date = fields.DateTimeField(attribute='server_updated_date', readonly=True)
    
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
        if ("spectator" not in bundle.data) and (not hasattr(bundle.obj, "spectator")):
            if "spectator_id" in bundle.data:
                bundle.obj.spectator_id = bundle.data["spectator_id"]
            elif "spectator_guid" in bundle.data:
                bundle.obj.spectator = Spectator.objects.get(guid=bundle.data["spectator_guid"])
            else:
                bundle.obj.spectator, created = Spectator.objects.get_or_create(user=bundle.request.user, defaults={"name":"Participant %d"%bundle.request.user.id})
        if ("event" not in bundle.data) and (not hasattr(bundle.obj, "event")):
            if "event_id" in bundle.data:
                bundle.obj.event_id = bundle.data["event_id"]
            else:
                bundle.obj.event = Event.objects.get(is_current=True)
        return bundle
    
    class Meta:
        queryset = Video.objects.select_related('spectator','event').order_by("-start_time")
        resource_name = 'video'
        fields = ['id', 'guid', 'start_time', 'duration', 'public', 'url', 
                  'latitude', 'longitude', 'accuracy', 'upload_status', 'filename', 'thumbnail', 'online']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = LoggedMultiAuthentication()
        authorization = VideoAuthorization()
        filtering = {
             "id": ("exact",),
             "start_time": ALL,
             "duration": ALL,
             "guid": ("exact",),
             "event": ALL_WITH_RELATIONS,
             "spectator": ALL_WITH_RELATIONS,
        }
        ordering = ["start_time"]
        
class PositionUpdateAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_superuser:
            return object_list
        return object_list.filter(spectator__user_id=current_user.id)

    @api_detail_auth_logger
    def read_detail(self, object_list, bundle):
        if bundle.request.method == "GET" and not hasattr(bundle.obj, "spectator"): #This would be a schema documentation request
            return True
        if bundle.request.user.is_superuser:
            return True
        return (bundle.obj.spectator.user == bundle.request.user)
    
    @api_detail_auth_logger
    def create_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
    @api_detail_auth_logger
    def update_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
    @api_detail_auth_logger
    def delete_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.spectator.user == bundle.request.user)
    
class PositionUpdateResource(LoggedMixin, resources.ModelResource):
    spectator = fields.ToOneField(SpectatorResource, 'spectator')
    spectator_guid = fields.CharField(attribute='spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='spectator__name', readonly=True)
    server_created_date = fields.DateTimeField(attribute='server_created_date', readonly=True)
    server_updated_date = fields.DateTimeField(attribute='server_updated_date', readonly=True)
    
    def hydrate(self, bundle):
        if ("spectator" not in bundle.data) and (not hasattr(bundle.obj, "spectator")):
            if "spectator_id" in bundle.data:
                bundle.obj.spectator_id = bundle.data["spectator_id"]
            elif "spectator_guid" in bundle.data:
                bundle.obj.spectator = Spectator.objects.get(guid=bundle.data["spectator_guid"])
            else:
                bundle.obj.spectator,created = Spectator.objects.get_or_create(user=bundle.request.user, defaults={"name":"Participant %d"%bundle.request.user.id})
        return bundle
    
    class Meta:
        queryset = PositionUpdate.objects.select_related('spectator').order_by("-time")
        resource_name = 'positionupdate'
        fields = ['id', 'guid', 'time', 'latitude', 'longitude', 'accuracy']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = LoggedMultiAuthentication()
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
        ordering = ["time"]

class RunnerTagAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_superuser:
            return object_list
        return object_list.filter(Q(video__spectator__user_id=current_user.id) | (Q(public=True) & Q(video__public=True) & Q(video__event__public=True)))

    @api_detail_auth_logger
    def read_detail(self, object_list, bundle):
        current_user = bundle.request.user
        if bundle.request.method == "GET" and not hasattr(bundle.obj, "video"): #This would be a schema documentation request
            return True
        current_video = bundle.obj.video
        if (not current_user.is_superuser):
            return ((current_video.spectator.user == current_user) or (bundle.obj.public and current_video.public and current_video.event.public))
        return True

    @api_detail_auth_logger
    def create_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.video.spectator.user == bundle.request.user)
    
    @api_detail_auth_logger
    def update_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.video.spectator.user == bundle.request.user)
    
    @api_detail_auth_logger
    def delete_detail(self, object_list, bundle):
        return (bundle.request.user.is_superuser) or (bundle.obj.video.spectator.user == bundle.request.user)

class RunnerTagResource(LoggedMixin, resources.ModelResource):
    video = fields.ToOneField(VideoResource, 'video')
    video_guid = fields.CharField(attribute='video__guid', readonly=True)
    video_time = fields.IntegerField(attribute='video_time', readonly=True)
    event_name = fields.CharField(attribute='video__event__name', readonly=True)
    spectator = fields.ToOneField(SpectatorResource, 'video__spectator', readonly=True)
    spectator_guid = fields.CharField(attribute='video__spectator__guid', readonly=True)
    spectator_name = fields.CharField(attribute='video__spectator__name', readonly=True)
    is_hot_tag = fields.BooleanField(attribute='is_hot_tag', readonly=True)
    server_created_date = fields.DateTimeField(attribute='server_created_date', readonly=True)
    server_updated_date = fields.DateTimeField(attribute='server_updated_date', readonly=True)
    
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
        if ("video" not in bundle.data) and not (hasattr(bundle.obj, "video")):
            if "video_id" in bundle.data:
                bundle.obj.video_id = bundle.data["video_id"]
            if "video_guid" in bundle.data:
                bundle.obj.video = Video.objects.get(guid=bundle.data["video_guid"])
        return bundle
    
    class Meta:
        queryset = RunnerTag.objects.select_related('video','video__spectator','video__event').order_by("-time")
        resource_name = 'runnertag'
        fields = ['id', 'guid', 'runner_number', 'latitude', 'longitude', 'accuracy', 'time', 'video_id', 'public']
        allowed_methods = ['get', 'put', 'post', 'delete']
        authentication = LoggedMultiAuthentication()
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
        ordering = ["time", "runner_number"]

class FlaggedContentAuthorization(Authorization):
    
    def read_list(self, object_list, bundle):
        current_user = bundle.request.user
        if current_user.is_authenticated:
            if current_user.is_superuser:
                return object_list
            return object_list.filter(user_id=current_user.id)
        else:
            return None

    @api_detail_auth_logger
    def read_detail(self, object_list, bundle):
        if bundle.request.user.is_authenticated:
            if bundle.request.user.is_superuser:
                return True
            return (bundle.obj.user == bundle.request.user)
        else:
            return False
    

class AnonymousAuthentication(BasicAuthentication):
    
    def is_authenticated(self, request, **kwargs):
        if request.method == "POST":
            return True
        else:
            return super(AnonymousAuthentication, self).is_authenticated(request, **kwargs)

class FlaggedContentResource(LoggedMixin, resources.ModelResource):
    
    video = fields.ToOneField(VideoResource, attribute='video_content', null=True, full=True, readonly=True)
    positionupdate = fields.ToOneField(PositionUpdateResource, attribute='positionupdate_content', null=True, full=True, readonly=True)
    runnertag = fields.ToOneField(RunnerTagResource, attribute='runnertag_content', null=True, full=True, readonly=True),
    user_id = fields.IntegerField(attribute="user_id", null=True, blank=True, readonly=True)
    
    class Meta:
        queryset = ContentFlag.objects.order_by("-flag_date")
        resource_name = 'flaggedcontent'
        fields = ['id', 'flag_date', 'content_type', 'content_id', 'reason' ]
        allowed_methods = ['get', 'post']
        authentication = LoggedMultiAuthentication(AnonymousAuthentication())
        authorization = FlaggedContentAuthorization()
        ordering = ["flag_date"]
    
    def hydrate(self, bundle):
        if bundle.request.user.is_anonymous():
            bundle.obj.user = None
        else:
            bundle.obj.user = bundle.request.user
        return bundle
        
