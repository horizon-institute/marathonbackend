from django.conf import settings
from django.http import HttpResponseForbidden
from jsonrpc import jsonrpc_method
from azure.storage import (
                            AccessPolicy, 
                            BlobService,
                            CloudStorageAccount,
                            SharedAccessPolicy,
                            SharedAccessSignature
                          )
import urllib
from datetime import datetime
import hashlib
from django.views.decorators.csrf import csrf_exempt
from provider.oauth2.models import AccessToken
from django.utils import timezone

blob_service = BlobService(
    account_name = settings.AZURE_CONFIG['account_name'],
    account_key = settings.AZURE_CONFIG['account_key'])

shared_access_signature = SharedAccessSignature(
    account_name = settings.AZURE_CONFIG['account_name'],
    account_key = settings.AZURE_CONFIG['account_key'])

def format_blob_name(user, video_guid):
    return hashlib.md5(user.username).hexdigest() + '_' + video_guid

def verify_access_token(key):
    try:
        token = AccessToken.objects.get(token=key)
        if token.expires < timezone.now():
            return None
    except AccessToken.DoesNotExist:
        return None
    return token

def rpc_authentication(method):
    @csrf_exempt
    def wrapper(request, *args, **kwargs): 
        try:
            key = request.GET.get('oauth_consumer_key')
            if not key:
                key = request.POST.get('oauth_consumer_key')
            if not key:
                auth_header_value = request.META.get('HTTP_AUTHORIZATION')
                if auth_header_value:
                    key = auth_header_value.split(' ')[1]
            if not key:
                return HttpResponseForbidden()
            token = verify_access_token(key)
            request.user = token.user
            request.META['oauth_consumer_key'] = key
        except KeyError:
            return HttpResponseForbidden()
        except Exception:
            return HttpResponseForbidden()
        return method(request, *args, **kwargs)
    return wrapper

@jsonrpc_method('marathon.request_video_upload_url(String)', validate = True)
def request_video_upload_url(request, video_guid = None):
    blob_name = format_blob_name(user = request.user, video_guid = video_guid)
    
    expiry = (datetime.utcnow() + settings.AZURE_CONFIG['relative_expiry_time']).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    ap = AccessPolicy(
        expiry = expiry,
        permission = 'w')

    qs = shared_access_signature.generate_signed_query_string(
        path = settings.AZURE_CONFIG['video_upload_container'] + '/' + blob_name,
        resource_type= 'b',
        shared_access_policy = SharedAccessPolicy(access_policy = ap))

    return blob_service.make_blob_url(
        container_name = settings.AZURE_CONFIG['video_upload_container'],
        blob_name = blob_name) + '?' + urllib.urlencode(qs) 
    
@jsonrpc_method('marathon.submit_video_encoding_job(String)', validate = True)                                
def submit_video_encoding_job(request, video_guid = None):
    
    blob_name = format_blob_name(user = request.user, video_guid = video_guid)
    
    csa = CloudStorageAccount(
        account_name = settings.AZURE_CONFIG['account_name'],
        account_key = settings.AZURE_CONFIG['account_key'])
    
    qs = csa.create_queue_service()
    
    qs.put_message(
        queue_name = settings.AZURE_CONFIG['video_encode_queue'],
        message_text = blob_name)
    
    return None

@jsonrpc_method('marathon.dummy')
def dummy(request):
    return True
                                    