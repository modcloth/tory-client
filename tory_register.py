#!/usr/bin/env python
# vim:fileencoding=utf-8

import argparse
import httplib
import json
import logging
import os
import re
import socket
import sys
import time

from itertools import ifilter
from urlparse import urlparse

HAS_NETIFACES = False

try:
    import netifaces
    HAS_NETIFACES = True
except ImportError:
    pass


USAGE = """%(prog)s [options]

Register a given host in tory.
"""
DEFAULT_TORY_SERVER = 'http://localhost:9462/ansible/hosts'
DEFAULT_IFNAME = 'eth0'
if sys.platform == 'darwin':
    DEFAULT_IFNAME = 'en0'
DEFAULT_HOST_TAGS_FILES = (
    '/etc/host-tags.json',
    '/usr/local/etc/host-tags.json',
    'host-tags.json'
)
HOSTNAME_RE = re.compile(
    "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]*" +
    "[a-zA-Z0-9])\\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\\-]*[A-Za-z0-9])$"
)
IPADDR_RE = re.compile("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\\.|$)){4}$")


def main(sysargs=sys.argv[:]):
    parser = argparse.ArgumentParser(
        usage=USAGE,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-H', '--hostname',
        metavar='TORY_HOSTNAME',
        default=os.environ.get(
            'TORY_HOSTNAME', os.environ.get('HOSTNAME', socket.getfqdn())
        ),
        help='hostname to register (also accepts $HOSTNAME)',
    )
    parser.add_argument(
        '-i', '--ipv4',
        metavar='TORY_IPV4',
        default=os.environ.get('TORY_IPV4', _get_local_ipv4()),
        help='host ipv4 address to register',
    )
    parser.add_argument(
        '-j', '--host-tags-json',
        metavar='TORY_HOST_TAGS_JSON',
        default=os.environ.get(
            'TORY_HOST_TAGS_JSON', DEFAULT_HOST_TAGS_FILES[0]
        ),
        help='json file from which tags will be read',
    )
    parser.add_argument(
        '-t', '--tag',
        metavar='TORY_TAGS',
        dest='tags', type=_kvpair, action='append',
        default=list(ifilter(lambda pair: len(pair) == 2, [
            _kvpair(s) for s in os.environ.get('TORY_TAGS', '').split(':')
        ])),
        help='tags assigned to host (as key=value pairs)',
    )
    parser.add_argument(
        '-s', '--tory-server',
        default=os.environ.get('TORY_SERVER', DEFAULT_TORY_SERVER),
        help='tory inventory server (including path)'
    )
    parser.add_argument(
        '-A', '--auth-token',
        default=os.environ.get('TORY_AUTH_TOKEN', 'swordfish'),
        metavar='TORY_AUTH_TOKEN',
        help='tory server auth token'
    )
    parser.add_argument(
        '-L', '--loop-seconds',
        type=int, default=int(os.environ.get('TORY_LOOP_SECONDS', '0')),
        metavar='TORY_LOOP_SECONDS',
        help='register repeatedly at an interval of seconds if non-zero',
    )
    parser.add_argument(
        '--once',
        action='store_true',
        default=os.environ.get('TORY_ONCE') is not None,
        help='only run registration once (equivalent to --loop-seconds=0)'
    )

    args = parser.parse_args(sysargs[1:])
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    log = logging.getLogger('tory-register')

    tags = dict(_get_local_tags())
    tags.update(dict(_get_local_tags([args.host_tags_json])))
    tags.update(dict(args.tags))

    host_def = {
        'name': args.hostname,
        'ip': args.ipv4,
        'tags': tags,
    }

    errors = _validate_host_def(host_def)
    if errors:
        for error in errors:
            log.error(error)
        return 1

    while True:
        status = _put_host(args.tory_server, args.auth_token, host_def)
        if status == 201:
            log.info('Added host %s', host_def['name'])
        elif status == 200:
            log.info('Updated host %s', host_def['name'])
        else:
            log.warn('Failed to create or update host %s: %s',
                     host_def['name'], status)
        if args.once or args.loop_seconds == 0:
            return 0

        log.info('Sleeping %s seconds', args.loop_seconds)
        time.sleep(args.loop_seconds)


def _kvpair(string):
    return string.strip().split('=', 1)


def _get_local_ipv4(ifname=DEFAULT_IFNAME):
    if HAS_NETIFACES:
        try:
            return netifaces.ifaddresses(ifname)[netifaces.AF_INET][0]['addr']
        except ValueError:
            return ''
    return ''


def _get_local_tags(files=DEFAULT_HOST_TAGS_FILES):
    tagdict = {}
    for filename in files:
        if not os.path.exists(filename):
            continue
        with open(filename) as infile:
            tagdict.update(json.load(infile))

    return [[str(key), str(value)] for key, value in tagdict.items()]


def _validate_host_def(host_def):
    errors = []

    for key in ('name', 'ip', 'tags'):
        if key not in host_def:
            errors.append('Missing required key {!r}'.format(key))

    if not HOSTNAME_RE.match(host_def.get('name', '')):
        errors.append('Invalid hostname')

    if not IPADDR_RE.match(host_def.get('ip', '')):
        errors.append('Invalid ipv4 address')

    return errors


def _put_host(server, auth_token, host_def):
    url = urlparse(server)
    conn = httplib.HTTPConnection(
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
