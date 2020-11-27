from services import ListServers, DeleteServers

servers_info, status_code = ListServers.call(limit=50, name='debug-dxwind-compute-node')
print(servers_info['count'])
# Dropping servers
dropping_server_ids = [{'id': s['id']} for s in servers_info['servers']]
deleting_result, status_code = DeleteServers.call(dropping_server_ids, delete_publicip=True, delete_volume=True)
print(deleting_result)

