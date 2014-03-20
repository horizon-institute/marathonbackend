from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from marathon.api import UserResource
from tastypie.api import Api

admin.autodiscover()

api = Api(api_name='api')
api.register(UserResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'marathonbackend.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include(auth_urls)),
    url(r'^auth/', include('social_auth.urls')),
    url(r'^oauth/', include('oauth_provider.urls')),
    url(r'', include(api.urls)),
)
