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


class EcsService:
    schema = 'https'
    endpoint = f'ecs.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'
    _singleton = None

    def construct_querystring(self):
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


class ListServers(EcsService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v1/{project_id}/cloudservers/detail'
        self.canonical_qs = ''

    def construct_querystring(self, limit=10, offset=0):
        canonical_qs = f'limit={limit}&offset={offset}'
        self.canonical_qs = canonical_qs


# Sample, list servers
servers_info = ListServers.call()
print(len(servers_info['servers']))
