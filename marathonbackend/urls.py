from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.contrib.auth.decorators import login_required
from marathon.api import Activity, SpectatorResource, EventResource, VideoResource, PositionUpdateResource, RunnerTagResource
from marathon.views import register, home, landing, RunnerTagList, MyVideoList, MyTagList, searchrunner
from tastypie.api import Api
from django.views.generic import TemplateView

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

    url(r'^$', landing, name='landing'),
    url(r'^search-runner/', searchrunner, name='search_runner'),
    url(r'^videos/', login_required(MyVideoList.as_view()), name='my_video_list'),
    url(r'^tags/', login_required(MyTagList.as_view()), name='my_tag_list'),
    url(r'^(?P<tagtype>\w+)-tags/', login_required(MyTagList.as_view()), name='my_tag_list'),
    url(r'^event/(?P<event>\d+)/runner/(?P<runner_number>\d+)/', RunnerTagList.as_view(), name='runner_results'),
    url(r'^home/', home, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(auth_urls)),
    url(r'^signup/', register, name='signup'),
    url(r'^social-auth/', include('social_auth.urls')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace = 'oauth2')),
    url(r'^api/', include(api.urls)),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
                                  content_type='text/plain'))
)
