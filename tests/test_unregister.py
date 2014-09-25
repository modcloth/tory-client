# vim:fileencoding=utf-8

import os

from tory_client import unregister


def fake_delete_host(server, auth_token, hostname):
    return 204


def fake_delete_host_fail(server, auth_token, hostname):
    return 400


def setup():
    os.environ.clear()


def test_main(monkeypatch):
    monkeypatch.setattr(unregister, 'delete_host', fake_delete_host)
    assert unregister.main([
        'tory-unregister',
        '-n', 'whatever.example.com'
    ]) == 0

    assert unregister.main([
        'tory-unregister',
        '-n', 'whatever.example.com', 'another.example.com'
    ]) == 0

    monkeypatch.setattr(unregister, 'delete_host', fake_delete_host_fail)
    assert unregister.main([
        'tory-unregister', '-n', 'whatever.example.com'
    ]) == 1

    monkeypatch.setattr(unregister, 'delete_host', fake_delete_host_fail)
    assert unregister.main([
        'tory-unregister',
        '-n', 'whatever.example.com', 'another.example.com'
    ]) == 2
