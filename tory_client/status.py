# vim:fileencoding=utf-8
from __future__ import print_function

import argparse
import json
import os
import requests
import sys

from datetime import datetime, timedelta

try:
    import urllib.parse as urlparse
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
    import urlparse

import humanize

from dateutil.parser import parse as parse_time

from . import __version__
from .junkdrawer import HelpFormatter, DEFAULT_SINCE


_SENTINELS = {}
_CUTOFF_HOURS_COLORS = {
    24: 'RED',
    1: 'YELLOW',
    0: 'GREEN'
}


def main(sysargs=sys.argv[:]):
    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)

    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '--debug',
        action='store_true',
        help='log the constructed URL to stderr'
    )
    parser.add_argument(
        '-s',
        '--tory-server',
        metavar='TORY_SERVER',
        help='full hostname and path to tory server',
        default=os.environ.get(
            'TORY_SERVER', 'http://localhost:9462/ansible/hosts'
        )
    )
    parser.add_argument(
        '-t',
        '--team',
        metavar='TEAM',
        help='filter hosts by the "team" tag',
        default=os.environ.get('TEAM')
    )
    parser.add_argument(
        '-e',
        '--env',
        metavar='NETWORK_ENV',
        help='filter hosts by the "env" tag',
        default=os.environ.get('NETWORK_ENV')
    )
    parser.add_argument(
        '-S',
        '--since',
        metavar='TORY_SINCE',
        help='only return hosts modified since iso8601 timestamp',
        default=os.environ.get('TORY_SINCE', DEFAULT_SINCE),
    )
    parser.add_argument(
        '-B',
        '--before',
        metavar='TORY_BEFORE',
        help='only return hosts modified before iso8601 timestamp',
        default=os.environ.get('TORY_BEFORE', ''),
    )
    parser.add_argument(
        '-f',
        '--output-format',
        help='output format of status',
        choices=['text', 'json'],
        default=os.environ.get('OUTPUT_FORMAT', 'text'),
    )

    args = parser.parse_args(sysargs[1:])
    scheme, netloc, path, params, query, fragment = \
        urlparse.urlparse(args.tory_server)

    query_dict = urlparse.parse_qs(query)

    if args.team:
        query_dict['team'] = args.team

    if args.env:
        query_dict['env'] = args.env

    if args.since:
        query_dict['since'] = args.since

    if args.before:
        query_dict['before'] = args.before

    url = urlparse.urlunparse(
        urlparse.ParseResult(
            scheme, netloc, path, params, urlencode(query_dict), fragment
        )
    )

    if args.debug:
        print('URL: {}'.format(url), file=sys.stderr)

    try:
        raw_inventory = _fetch_inventory(url)
        _print_inventory_with_status(
            json.loads(raw_inventory.decode('utf-8')),
            {
                'text': _format_text,
                'json': _format_json,
            }[args.output_format],
            debug=args.debug
        )
        return 0
    except IOError as exc:
        if not args.debug:
            print('ERROR: Could not connect to tory server: {}'.format(exc),
                  file=sys.stderr)
            return 0
        raise
    except Exception as exc:
        if not args.debug:
            print('ERROR: {}'.format(exc), file=sys.stderr)
            return 0
        raise


def _fetch_inventory(url):
    return requests.get(url).text


def _print_inventory_with_status(inventory, format_callback, debug=False):
    by_hostname = {}

    for hostvars in inventory.get('_meta', {}).get('hostvars', {}).values():
        if 'modified' not in hostvars:
            if debug:
                print(
                    'WARNING: Missing \'modified\' key in {}'.format(hostvars),
                    file=sys.stderr
                )
            continue

        hostvars = hostvars.copy()
        hostname = hostvars.get('hostname')
        if not hostname:
            if debug:
                print(
                    'WARNING: Missing \'hostname\' key in {}'.format(hostvars),
                    file=sys.stderr
                )
            continue

        by_hostname[hostname] = hostvars

    for hostvars in sorted(by_hostname.values(),
                           key=lambda hv: hv['modified']):
        format_callback(hostvars)


def _format_text(hostvars):
    now = parse_time(datetime.utcnow().isoformat() + 'Z')
    for key in ('package', 'type'):
        if not hostvars[key]:
            hostvars[key] = '???'
    print('{ago}, {hostname}, {ip}, {type}, {package}'.format(
        ago=_format_lastmod_time(now, parse_time(hostvars['modified'])),
        **hostvars
    ))


def _format_json(hostvars):
    json.dump(hostvars, sys.stdout)
    print('', file=sys.stdout)


def _format_lastmod_time(now, modified, cutoffs=_CUTOFF_HOURS_COLORS):
    import colorama

    if 'colorama' not in _SENTINELS:
        colorama.init()
        _SENTINELS['colorama'] = 1

    delta = now - modified
    humanized = humanize.naturaltime(delta)

    for hrs, color in sorted(cutoffs.items(), reverse=True):
        if delta > timedelta(hours=hrs):
            return getattr(colorama.Fore, color) + \
                humanized + colorama.Style.RESET_ALL

    return humanized
