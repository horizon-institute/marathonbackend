from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.contrib.auth.decorators import login_required
from marathon.api import SpectatorResource, EventResource, VideoResource, PositionUpdateResource, RunnerTagResource, FlaggedContentResource
from marathon.views import register, home, RunnerTagList, MyVideoList, AllVideosList, MyTagList, AllTagsList, searchrunner, customlogin, VideoDetail
from marathon.models import Video
from tastypie.api import Api
from django.views.generic import TemplateView
from haystack.views import FacetedSearchView, search_view_factory
from haystack.query import SearchQuerySet
from haystack.forms import FacetedSearchForm

admin.autodiscover()

api = Api(api_name='v1')
api.register(SpectatorResource())
api.register(VideoResource())
api.register(RunnerTagResource())
api.register(PositionUpdateResource())
api.register(EventResource())
api.register(FlaggedContentResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'marathonbackend.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', TemplateView.as_view(template_name='landing.html'), name='landing'),
    url(r'^search-runner/', login_required(searchrunner), name='search_runner'),
    url(r'^videos/', login_required(MyVideoList.as_view()), name='my_video_list'),
    url(r'^admin/videos/', login_required(AllVideosList.as_view()), name='all_videos'),
    url(r'^admin/tags/', login_required(AllTagsList.as_view()), name='all_tags'),
    url(r'^tags/', login_required(MyTagList.as_view()), name='my_tag_list'),
    url(r'^(?P<tagtype>(runner|hot))-tags/', login_required(MyTagList.as_view()), name='my_tag_list'),
    url(r'^event/(?P<event>\d+)/runner/(?P<runner_number>\d+)/', login_required(RunnerTagList.as_view()), name='runner_results'),
    url(r'^home/', login_required(home), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(auth_urls)),
    url(r'^login/', customlogin, name='login'),
    url(r'^signup/', register, name='signup'),
    url(r'^social-auth/', include('social_auth.urls')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace = 'oauth2')),
    url(r'^api/', include(api.urls)),
    url(r'^about/faq/', TemplateView.as_view(template_name='faq.html'), name='about_faq'),
    url(r'^about/consent/', TemplateView.as_view(template_name='consent.html'), name='about_consent'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
                                  content_type='text/plain')),
    url(r'^video/(?P<pk>\d+)/', VideoDetail.as_view(), name="video_detail"),
    url(r'^search-video/', search_view_factory(
        view_class=FacetedSearchView,
        template='search/search.html',
        searchqueryset=SearchQuerySet().facet("event"),
        form_class=FacetedSearchForm
    ), name='haystack_search_video'),
   
)
