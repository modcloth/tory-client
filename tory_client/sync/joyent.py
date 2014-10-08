# vim:fileencoding=utf-8

from ..client import put_host
from ..junkdrawer import stringified_dict


def sync_machine(log, server, auth_token, machine):
    machine = machine.copy()
    host_def = machine.copy()
    for key in ('id', 'ips'):
        host_def.pop(key)

    interpreter = '/usr/bin/python'
    user = 'ubuntu'
    if machine.get('type') == 'smartmachine':
        interpreter = '/opt/local/bin/python'
        user = 'root'

    hostname = machine['name']
    ip = machine.pop('ips')[0]
    host_def.update({
        'ip': ip,
        'name': hostname,
        'vars': {
            'ansible_python_interpreter': interpreter,
            'ansible_ssh_host': ip,
            'ansible_ssh_user': user,
            'ansible_inventory_hostname': hostname,
            'disk': str(machine.pop('disk')),
            'joyent_id': str(machine.pop('id')),
            'memory': str(machine.pop('memory')),
        },
        'tags': stringified_dict(machine.pop('tags')),
    })

    status = put_host(server, auth_token, host_def)
    if status == 201:
        log.info('Added host %s', hostname)
    elif status == 200:
        log.info('Updated host %s', hostname)
    else:
        log.warn('Failed to create or update host %s: %s',
                 hostname, status)
