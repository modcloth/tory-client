# vim:fileencoding=utf-8

import argparse
import json
import logging
import os
import sys

try:
    from urlparse import urlparse
    import httplib as httpclient
except ImportError:
    from urllib.parse import urlparse
    import http.client as httpclient


from . import __version__

USAGE = """%(prog)s [options]

populate tory inventory from Joyent listmachines json
"""
DEFAULT_TORY_SERVER = 'http://localhost:9462/ansible/hosts'


def main(sysargs=sys.argv[:]):
    default_json_input = sys.stdin
    json_infile = os.environ.get('TORY_SYNC_SDC_LISTMACHINES_JSON')
    if json_infile:
        default_json_input = open(json_infile)

    parser = argparse.ArgumentParser(
        usage=USAGE,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    if sys.version >= '3':
        parser.add_argument('--version', action='version', version=__version__)
    else:
        parser.version = __version__

    parser.add_argument(
        '-s', '--tory-server',
        default=os.environ.get('TORY_SERVER', DEFAULT_TORY_SERVER),
        help='tory inventory server (including path)'
    )
    parser.add_argument(
        '-j', '--sdc-listmachines-json',
        default=default_json_input,
        metavar='TORY_SYNC_SDC_LISTMACHINES_JSON',
        type=argparse.FileType('r'),
        help='joyent listmachines input json'
    )
    parser.add_argument(
        '-A', '--auth-token',
        default=os.environ.get('TORY_AUTH_TOKEN', 'swordfish'),
        metavar='TORY_AUTH_TOKEN',
        help='tory server auth token'
    )

    args = parser.parse_args(sysargs[1:])
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    log = logging.getLogger('tory-sync-from-joyent')

    json_string = args.sdc_listmachines_json.read()
    if sys.version >= '3':
        json_string = json_string.decode('utf-8')

    machines = json.loads(json_string)
    if hasattr(machines, 'keys'):
        machines = [machines]

    for machine in machines:
        try:
            _sync_one_machine(log, args.tory_server, args.auth_token, machine)
        except Exception:
            log.exception('failed to sync machine %s', machine['name'])

    return 0


def _sync_one_machine(log, server, auth_token, machine):
    host_def = machine.copy()
    for key in ('id', 'ips'):
        host_def.pop(key)

    interpreter = '/usr/bin/python'
    if machine.get('type') == 'smartmachine':
        interpreter = '/opt/local/bin/python'

    hostname = machine['name']
    host_def.update({
        'ip': machine.pop('ips')[0],
        'name': hostname,
        'vars': {
            'ansible_python_interpreter': interpreter,
            'disk': str(machine.pop('disk')),
            'joyent_id': str(machine.pop('id')),
            'memory': str(machine.pop('memory')),
        },
        'tags': _stringified_dict(machine.pop('tags')),
    })

    status = _put_host(server, auth_token, host_def)
    if status == 201:
        log.info('Added host %s', hostname)
    elif status == 200:
        log.info('Updated host %s', hostname)
    else:
        log.warn('Failed to create or update host %s: %s',
                 hostname, status)


def _stringified_dict(indict):
    return dict(
        ((str(key), str(value)) for key, value in indict.items())
    )


def _put_host(server, auth_token, host_def):
    url = urlparse(server)
    conn = httpclient.HTTPConnection(
        url.netloc.split(':')[0], int(url.port or 80)
    )
    conn.request(
        'PUT',
        '{}/{}'.format(url.path, host_def['name']),
        json.dumps({'host': host_def}),
        {
            'Content-Type': 'application/json',
            'Authorization': 'token {}'.format(auth_token)
        }
    )
    resp = conn.getresponse()
    return resp.status


if __name__ == '__main__':
    sys.exit(main())
