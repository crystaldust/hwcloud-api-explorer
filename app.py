import requests
from apig_sdk import signer
from os import environ


AK = environ['AK'] if 'AK' in environ else 'YOUR_AK'
SK = environ['SK'] if 'SK' in environ else 'YOUR_SK'
project_id = environ['project_id'] if 'project_id' in environ else 'YOUR_project_id'
region = environ['region'] if 'region' in environ else 'YOUR_region'
sig = signer.Signer()
sig.Key = AK
sig.Secret = SK


class BasicService:
    schema = 'https'
    _singleton = None

    def construct_querystring(self, *args):
        pass

    @classmethod
    def call(cls, *args):
        if not cls._singleton:
            cls._singleton = cls()

        cls._singleton.construct_querystring(*args)
        request_url = f'{cls._singleton.__class__.url_base}{cls._singleton.canonical_uri}'
        if cls._singleton.canonical_qs:
            request_url = f'{request_url}?{cls._singleton.canonical_qs}'

        r = signer.HttpRequest(cls._singleton.http_method, request_url)
        sig.Sign(r)
        r.headers['X-Project-Id'] = project_id
        # If uri already takes query string, then don't pass r.query to 'params' argument
        # or it will be handled twice, the value becomes a list with 2 same elements.
        res = requests.request(r.method, request_url, headers=r.headers, data=r.body)
        return res.json()


class EcsService(BasicService):
    schema = 'https'
    endpoint = f'ecs.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'

    # def construct_querystring(self, *args):
    #     pass


class ListServers(EcsService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v1/{project_id}/cloudservers/detail'
        self.canonical_qs = ''

    def construct_querystring(self, limit=10, offset=0):
        self.canonical_qs = f'limit={limit}&offset={offset}'



# Instance specs:
# https://support.huaweicloud.com/productdesc-ecs/ecs_01_0008.html


class CreateOnDemandServer(EcsService):

    def __init__(self):
        self.http_method = 'POST'
        self.canonical_uri = f'/v1/{project_id}/cloudservers'
        self.canonical_qs = ''

    def construct_querystring(self, name, vpc_id, nics, root_vol, az, image_ref='67f433d8-ed0e-4321-a8a2-a71838539e09',
                              flavor_ref='c6.16xlarge.2', dry_run=True):
        pass


class ImageService(BasicService):
    schema = 'https'
    endpoint = f'ims.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'

    def construct_querystring(self, *args):
        pass


class ListImages(ImageService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v2/cloudimages'
        self.canonical_qs = ''

    def construct_querystring(self, imagetype='gold', visibility='public', protected='true'):
        self.canonical_qs = f'__imagetype={imagetype}&visibility={visibility}&protected={protected}'


class VpcService(BasicService):
    schema = 'https'
    endpoint = f'vpc.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'

class ListVpcs(VpcService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'{self.__class__.endpoint}/v1/{project_id}/vpcs'
        self.canonical_qs = ''

    def construct_querystring(self, limit=10):
        self.canonical_qs = f'limit={limit}'

# Sample, list servers
# servers_info = ListServers.call()
# print(len(servers_info['servers']))
# 67f433d8-ed0e-4321-a8a2-a71838539e09 CentOS 7.6 64bit

# images_info = ListImages.call()
# images = images_info['images']
# for img in images[:10]:
#     print(img['id'], img['name'])

ListVpcs.call()
