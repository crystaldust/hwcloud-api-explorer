from services import CreateOnDemandServer, ListServers, vpc_id
import json
import secrets
import os

root_volume = {
    'volumetype': 'SSD', # One of 'SSD', 'GPSSD', 'SAS'
    'size': 256, # Unit: GB
}
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

servers_info, status_code = ListServers.call(limit=50, name='debug-dxwind-compute-node')
print(servers_info['count'])
max_id = 0
total_amount = 2
for server in servers_info['servers']:
    # print(server['name'], server['id'], server['addresses'][vpc_id][0]['addr'])
    server_id_num = int(str.split(server['name'], '-')[-1])
    if max_id < server_id_num:
        max_id = server_id_num

print(max_id, servers_info['count'])
print(f'there are {total_amount-max_id} servers to create')
passwd = secrets.token_urlsafe(16)
if os.path.exists('./passwd'):
    with open('./passwd', 'r') as f:
        passwd = f.read()
else:
    with open('./passwd', 'w') as f:
        f.write(passwd)
print('create with passwd:', passwd)
num_servers_to_create = total_amount - max_id

publicip = {
    'eip': {
        'iptype': '5_bgp',
        'bandwidth': {
            'size': 300,
            'charge_mode': 'traffic',
            'share_type': 'PER'
        }

    }
}

image_ref = '0c5eea8e-b56f-410e-8a6e-c960f75320db'  # Customized image node-nwp
# image_ref = '6de3f8c3-fa9c-40e6-ba12-52d6c5e31db0'  # CentOS 7.5
if num_servers_to_create:
    name = 'debug-dxwind-compute-node'
    if num_servers_to_create == 1 and max_id != 0:
        digits = str(max_id+1).zfill(3)
        name = f'{name}-{digits}'
    try:
        create_result, status_code = CreateOnDemandServer.call(name, image_ref, nics,
                                                               root_volume, security_groups=security_groups,
                                                               flavor_ref='s6.small.1', dry_run=False, # public_ip=publicip,
                                                               count=num_servers_to_create, admin_pass=passwd)
        print(create_result)
    except Exception as e:
        print(e),ta

else:
    servers_info, status_code = ListServers.call(limit=60, name='debug-dxwind-compute-node')
    for s in servers_info['servers']:
        print(s['addresses'][vpc_id][0]['addr'], '\t', s['name'])
