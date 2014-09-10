from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from marathon.api import Activity, SpectatorResource, EventResource, VideoResource, PositionUpdateResource, RunnerTagResource
from marathon.views import register, home
from tastypie.api import Api

admin.autodiscover()

api = Api(api_name='v1')
api.register(SpectatorResource())
api.register(VideoResource())
api.register(RunnerTagResource())
api.register(PositionUpdateResource())
api.register(EventResource())
api.register(Activity())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'marathonbackend.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', login_required(home), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(auth_urls)),
    url(r'^signup/', register, name='signup'),
    url(r'^social-auth/', include('social_auth.urls')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace = 'oauth2')),
    url(r'^api/', include(api.urls)),
)
