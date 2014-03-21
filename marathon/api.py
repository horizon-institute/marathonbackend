from tastypie.resources import ModelResource
from tastypie.authentication import MultiAuthentication, SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from oauth2_tastypie.authentication import OAuth20Authentication
from django.contrib.auth.models import User

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'resource_uri', 'id']
        allowed_methods = ['get']
        authentication = MultiAuthentication(OAuth20Authentication(), SessionAuthentication())
        authorization = DjangoAuthorization()