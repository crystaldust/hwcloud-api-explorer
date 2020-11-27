import spur
from os.path import exists
from app import ListServers
from app import vpc_id

# Make sure we have the password
if not exists('./passwd'):
    raise Exception("No password file!")

passwd = ''
with open('./passwd', 'r') as f:
    passwd = f.read()
if not passwd:
    raise Exception("Password empty")


servers_info, status_code = ListServers.call(limit=50, name='debug-dxwind-compute-node')
print(servers_info, status_code)
hosts_content = ''
target_ips = []
for s in servers_info['servers']:
    server_addr = s['addresses'][vpc_id][0]['addr']
    server_name = s['name']
    hosts_content += f'{server_addr}\t{server_name}\n'
    target_ips.append(server_addr)
for ip in target_ips:
    # # Test locally
    # from subprocess import Popen, PIPE
    # p = Popen(['sh', '-c', f'echo "{hosts_content}" >> /tmp/foo'],
    #           stdout=PIPE, stderr=PIPE)
    # stdout, stderr = p.communicate()

    # # Run on remote server
    # shell = spur.SshShell(hostname=ip, username='root', password=passwd)
    # result = shell.run(['sh', '-c', f'echo "{hosts_content}" >> /etc/hosts'])
    # print(result.output.decode('utf-8'))
    continue
