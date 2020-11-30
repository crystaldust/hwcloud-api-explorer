from services import StopServers, ListServers

prefix = 'dxwind-compute-node'

servers_info, status_code = ListServers.call(limit=50, name=prefix)
if not servers_info['count']:
    print('No servers found, skip stopping')
    exit(0)

# Dropping servers
server_ids = [{'id': s['id']} for s in servers_info['servers']]
stop_result, status_code = StopServers.call(server_ids, type='SOFT')
print(stop_result)

