# vim:fileencoding=utf-8

import json

from tory_client import client

from _pytest.monkeypatch import monkeypatch


_CAPTURED_REQUESTS = []


def fake_make_authenticated_request(method, path, body, server, auth_token):
    _CAPTURED_REQUESTS.append({
        'method': method,
        'path': path,
        'body': body,
        'server': server,
        'auth_token': auth_token,
    })
    return 200


def setup():
    mp = monkeypatch()
    mp.setattr(
        client,
        '_make_authenticated_request',
        fake_make_authenticated_request
    )


def test_put_host():
    client.put_host('server', 'auth_token', {'name': 'buzz'})
    assert json.loads(
        _CAPTURED_REQUESTS[-1]['body']
    )['host']['name'] == 'buzz'


def test_delete_host():
    client.delete_host('server', 'auth_token', 'buzz')
    assert _CAPTURED_REQUESTS[-1]['body'] is None
