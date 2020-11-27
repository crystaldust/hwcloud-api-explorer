from services import StopServers, ListServers

servers_info, status_code = ListServers.call(limit=50, name='debug-dxwind-compute-node')
if not servers_info['count']:
    print('No servers found, skip stopping')
    exit(0)

# Dropping servers
server_ids = [{'id': s['id']} for s in servers_info['servers']]
stop_result, status_code = StopServers.call(server_ids, type='SOFT')
print(stop_result)

