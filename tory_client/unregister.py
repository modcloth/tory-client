# vim:fileencoding=utf-8

import argparse
import logging
import os
import sys

from . import __version__
from .client import delete_host
from .junkdrawer import HelpFormatter

USAGE = """%(prog)s [options]

Unregister host(s) in tory.
"""
EPILOGUE = """\

Examples:

# Unregister a machine by name
%(prog)s --name foo-bar.example.com

# Unregister a machine by ipv4
%(prog)s --name 192.168.113.29

# Unregister a whole bunch of machines with hostnames that
# start with "generic-"
tory-inventory | \\
    jq -r '._meta | .hostvars | .[] |
           select(.hostname | startswith("generic-")) |
           .hostname' | \\
    xargs %(prog)s -n

"""
DEFAULT_TORY_SERVER = 'http://localhost:9462/ansible/hosts'


def main(sysargs=sys.argv[:]):
    parser = argparse.ArgumentParser(
        usage=USAGE,
        formatter_class=HelpFormatter,
        epilog=EPILOGUE,
    )

    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '-n', '--name',
        nargs='+',
        metavar='TORY_HOSTNAME',
        default=list(filter(lambda s: s != '', [
            _s.strip() for _s in os.environ.get('TORY_HOSTNAME', '').split()
        ])),
        help='host name(s) or ip(s) to uregister',
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

    args = parser.parse_args(sysargs[1:])
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    log = logging.getLogger('tory-unregister')

    n_failures = 0
    for identifier in args.name:
        status = delete_host(args.tory_server, args.auth_token, identifier)
        if status == 204:
            log.info('Removed host %s', identifier)
        else:
            log.warn('Failed to remove host %s: %s',
                     identifier, status)
            n_failures += 1

    return n_failures
