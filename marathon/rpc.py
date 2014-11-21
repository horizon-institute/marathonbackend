from django.conf import settings
from jsonrpc import jsonrpc_method
from azure.storage import AccessPolicy, BlobService, SharedAccessPolicy, SharedAccessSignature
import urllib
from datetime import datetime
import hashlib

blob_service = BlobService(
    account_name = settings.AZURE_CONFIG['account_name'],
    account_key = settings.AZURE_CONFIG['account_key'])

shared_access_signature = SharedAccessSignature(
    account_name = settings.AZURE_CONFIG['account_name'],
    account_key = settings.AZURE_CONFIG['account_key'])

@jsonrpc_method('marathon.request_video_upload_url(String)', validate = True)
def request_video_upload_url(request, video_guid = None):

    blob_name = hashlib.md5(request.user.username).hexdigest() + '_' + video_guid
    
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
                                    