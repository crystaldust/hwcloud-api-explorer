import platform
import re
import subprocess
import spur
from spur.ssh import MissingHostKey
from os.path import exists
from services import ListServers
from services import vpc_id
from pathlib import Path

hostname = platform.node()
cat_process = subprocess.Popen(['cat', '/etc/hosts'], stdout=subprocess.PIPE)
grep_process = subprocess.Popen(['grep', hostname], stdin=cat_process.stdout, stdout=subprocess.PIPE)
stdout, _ = grep_process.communicate()
compute_node_hosts_content = ''
manage_node_hosts_content = stdout.decode('utf-8').strip() + '\n'  # start with the host ip line

prefix = 'dxwind-compute-node'

user_already_exists_pattern = re.compile("useradd: user '.*' already exists")
home = str(Path.home())

# Make sure we have the password
if not exists('./passwd'):
    raise Exception("No password file!")

passwd = ''
with open('./passwd', 'r') as f:
    passwd = f.read()
if not passwd:
    raise Exception("Password empty")


servers_info, status_code = ListServers.call(limit=50, name=prefix)
print(servers_info, status_code)

target_ips = []
for s in servers_info['servers']:
    server_addr = s['addresses'][vpc_id][0]['addr']
    server_name = s['name']
    compute_node_hosts_content += f'{server_addr}\t{server_name}\n'
    target_ips.append(server_addr)

pubkey = ''
with open(f'{home}/.ssh/id_rsa.pub', 'r') as f:
    pubkey = f.read()

if not pubkey:
    raise Exception('Failed to read pubkey, make sure $HOME/.ssh/id_rsa.pub exits!')


for ip in target_ips:
    # # Test locally
    # from subprocess import Popen, PIPE
    # p = Popen(['sh', '-c', f'echo "{hosts_content}" >> /tmp/foo'],
    #           stdout=PIPE, stderr=PIPE)
    # stdout, stderr = p.communicate()

    # Configure the hosts
    shell = spur.SshShell(hostname=ip, username='root', password=passwd, missing_host_key=MissingHostKey.accept)
    result = shell.run(['sh', '-c', f'echo "{manage_node_hosts_content + compute_node_hosts_content}" >> /etc/hosts'])
    print(result.output.decode('utf-8'))

    # Configure user 'op'
    shell = spur.SshShell(hostname=ip, username='root', password=passwd, missing_host_key=MissingHostKey.accept)
    result = shell.run(['sh', '-c', 'useradd -m -G root op'], allow_error=True)
    if result.return_code != 0 and not re.match(user_already_exists_pattern, result.stderr_output.decode('utf-8')):
        raise Exception(result.stderr_output.decode('utf-8'))
    else:
        print(result.output.decode('utf-8'))

    result = shell.run(['sh', '-c', 'mkdir /home/op/.ssh -p'])
    print(result.output.decode('utf-8'))

    result = shell.run(['sh', '-c', f'echo "{pubkey}" >> /home/op/.ssh/authorized_keys'])
    print(result.output.decode('utf-8'))

    result = shell.run(['sh', '-c', f'echo "{pubkey}" > /home/op/.ssh/id_rsa.pub'])
    print(result.output.decode('utf-8'))

    result = shell.run(['sh', '-c', 'systemctl start munge'])
    print(result.output.decode('utf-8'))

    result = shell.run(['sh', '-c', 'systemctl start munge'])
    print(result.output.decode('utf-8'))

    result = shell.run(['sh', '-c', 'systemctl start slurmd'])
    print(result.output.decode('utf-8'))

    result = shell.run(['sh', '-c', 'systemctl restart slurmd'])
    print(result.output.decode('utf-8'))

    # Create 


subprocess.Popen(['sh', '-c', f'echo "{compute_node_hosts_content}" >> /etc/hosts'])

subprocess.Popen(['systemctl', 'start', 'munge'])
subprocess.Popen(['systemctl', 'restart', 'munge'])
subprocess.Popen(['systemctl', 'start', 'slurmd'])
subprocess.Popen(['systemctl', 'restart', 'munge'])