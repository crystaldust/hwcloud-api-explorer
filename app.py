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

    def construct_request_params(self, *args):
        pass

    @classmethod
    def call(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = cls()
        cls._singleton.req_body = ''
        cls._singleton.construct_request_params(*args, **kwargs)
        request_url = f'{cls._singleton.__class__.url_base}{cls._singleton.canonical_uri}'
        if cls._singleton.canonical_qs:
            request_url = f'{request_url}?{cls._singleton.canonical_qs}'

        r = signer.HttpRequest(cls._singleton.http_method, request_url,
                               body=cls._singleton.req_body)
        sig.Sign(r)
        r.headers['X-Project-Id'] = project_id
        r.headers['Content-Type'] = 'application/json'
        # If uri already takes query string, then don't pass r.query to 'params' argument
        # or it will be handled twice, the value becomes a list with 2 same elements.
        res = requests.request(r.method, request_url, headers=r.headers, data=r.body)
        return res.json(), res.status_code


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

    def construct_request_params(self, limit=10, offset=0):
        self.canonical_qs = f'limit={limit}&offset={offset}'


# Instance specs:
# https://support.huaweicloud.com/productdesc-ecs/ecs_01_0008.html
class CreateOnDemandServer(EcsService):

    def __init__(self):
        self.http_method = 'POST'
        self.canonical_uri = f'/v1/{project_id}/cloudservers'
        self.canonical_qs = ''
        self.req_body = ''

    def construct_request_params(self, name, vpc_id, nics, root_vol, az='cn-north-4a',
                                 security_groups=[], image_ref='67f433d8-ed0e-4321-a8a2-a71838539e09',
                                 flavor_ref='c6.16xlarge.4', dry_run=True, public_ip='', count=1):
        req_payload = {
            'server': {
                'imageRef': image_ref,
                'flavorRef': flavor_ref,
                'name': name,
                'vpcid': vpc_id,
                'nics': nics,
                'root_volume': root_vol,
                'count': count,
                'security_groups': security_groups,
                'availability_zone': az,
            },
            'dry_run': 'true' if dry_run else 'false',
        }
        if public_ip:
            req_payload['publicip'] = public_ip

        self.req_body = json.dumps(req_payload)
        print(json.dumps(req_payload, indent=2))


class ImageService(BasicService):
    schema = 'https'
    endpoint = f'ims.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'

    def construct_request_params(self, *args):
        pass


class ListImages(ImageService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v2/cloudimages'
        self.canonical_qs = ''

    def construct_request_params(self, imagetype='gold', visibility='public', protected='true'):
        self.canonical_qs = f'__imagetype={imagetype}&visibility={visibility}&protected={protected}'


class VpcService(BasicService):
    schema = 'https'
    endpoint = f'vpc.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'

class ListVpcs(VpcService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v1/{project_id}/vpcs'
        self.canonical_qs = ''

    def construct_request_params(self, limit=10):
        self.canonical_qs = f'limit={limit}'


class ListSubnets(VpcService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v1/{project_id}/subnets'
        self.canonical_qs = ''

    def construct_request_params(self, limit=10, marker='', vpc_id=''):
        self.canonical_qs = f'limit={limit}'
        if marker:
            self.canonical_qs += f'&marker={marker}'
        if vpc_id:
            self.canonical_qs += f'&vpc_id={vpc_id}'


# Sample, list servers
# servers_info = ListServers.call(limit=2)
# print(len(servers_info['servers']))
# 67f433d8-ed0e-4321-a8a2-a71838539e09 CentOS 7.6 64bit

# images_info = ListImages.call()
# images = images_info['images']
# for img in images[:10]:
#     print(img['id'], img['name'])

# vpcs_info = ListVpcs.call(limit=2)
# import json
# print(json.dumps(vpcs_info, indent=2))
# VPC: "id": "6de3f8c3-fa9c-40e6-ba12-52d6c5e31db0",
# Subnet id: bb64d226-14a4-4e13-afcb-ccda97cdf4e5
# Security group id: 08bc3b69-08e8-449d-ab55-0f7d141c07a0 # For XiangJi
import json
# subnets_info = ListSubnets.call()
# print(json.dumps(subnets_info, indent=2))

root_volume = {
    'volumetype': 'SSD', # One of 'SSD', 'GPSSD', 'SAS'
    'size': 256, # Unit: GB
}

# name, vpc_id, nics, root_vol, az='cn-north-4a',
#                               security_group=[], image_ref='67f433d8-ed0e-4321-a8a2-a71838539e09',
#                               flavor_ref='c6.16xlarge.2', dry_run=True, public_ip='', count=1
nics = [
    {
        'subnet_id': 'bb64d226-14a4-4e13-afcb-ccda97cdf4e5'
    }
]
security_groups = [
    {
        'id': '08bc3b69-08e8-449d-ab55-0f7d141c07a0'
    }
]

create_result, status_code = CreateOnDemandServer.call('compute-node-',
                                                       '6de3f8c3-fa9c-40e6-ba12-52d6c5e31db0',
                                                       nics, root_volume,
                                                       security_groups=security_groups,
                                                       flavor_ref='c6.large.2',
                                                       dry_run=False)

print(json.dumps(create_result, indent=4), status_code)
