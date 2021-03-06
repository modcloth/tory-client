# vim:fileencoding=utf-8
from __future__ import print_function

import argparse
import os
import sys
import requests

try:
    import urllib.parse as urlparse
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
    import urlparse

from . import __version__
from .junkdrawer import HelpFormatter, DEFAULT_SINCE


def main(sysargs=sys.argv[:]):
    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)

    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '--debug',
        action='store_true',
        help='log the constructed URL to stderr'
    )
    parser.add_argument(
        '--host',
        dest='hostname',
        help='only show the given host'
    )
    parser.add_argument(
        '--list',
        dest='enable_error_silencing',
        action='store_true',
        help='compatibility flag for dynamic inventory, ' +
             'enables silent error handling'
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

    args = parser.parse_args(sysargs[1:])
    scheme, netloc, path, params, query, fragment = \
        urlparse.urlparse(args.tory_server)

    query_dict = urlparse.parse_qs(query)

    if args.hostname:
        path += ('/' + args.hostname)
        query_dict['vars-only'] = '1'

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
        print(_fetch_inventory(url))
        return 0
    except IOError as exc:
        if not args.debug and args.enable_error_silencing:
            print('ERROR: Could not connect to tory server: {}'.format(exc),
                  file=sys.stderr)
            print('{}')
            return 0
        raise
    except Exception as exc:
        if not args.debug and args.enable_error_silencing:
            print('ERROR: {}'.format(exc), file=sys.stderr)
            print('{}')
            return 0
        raise


def _fetch_inventory(url):
    return requests.get(url).text
