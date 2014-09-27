# vim:fileencoding=utf-8

import re
import json
from requests import request


HOSTNAME_RE = re.compile(
    "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]*" +
    "[a-zA-Z0-9])\\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\\-]*[A-Za-z0-9])$"
)
IPADDR_RE = re.compile("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\\.|$)){4}$")


def put_host(server, auth_token, host_def):
    return _make_authenticated_request(
        'PUT',
        host_def['name'],
        json.dumps({'host': host_def}),
        server,
        auth_token
    )


def delete_host(server, auth_token, host_identifier):
    return _make_authenticated_request(
        'DELETE',
        host_identifier,
        None,
        server,
        auth_token
    )


def _make_authenticated_request(method, path, body, server, auth_token):
    resp = request(method, '{}/{}'.format(server, path),
                   data=body,
                   headers={
                       'Content-Type': 'application/json',
                       'Authorization': 'token {}'.format(auth_token)
        })
    return resp.status_code


def validate_host_def(host_def):
    errors = []

    for key in ('name', 'ip', 'tags'):
        if key not in host_def:
            errors.append('Missing required key {!r}'.format(key))

    if not HOSTNAME_RE.match(host_def.get('name', '')):
        errors.append('Invalid hostname')

    if not IPADDR_RE.match(host_def.get('ip', '')):
        errors.append('Invalid ipv4 address')

    return errors
