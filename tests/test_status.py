# vim:fileencoding=utf-8
from __future__ import unicode_literals

import os

from tory_client import status


def fake_fetch_inventory(url):
    return b'{"_meta":{"hostvars":{}}}'


def setup():
    os.environ.clear()


def test_main(monkeypatch):
    captured = []

    def fake_print_inventory_with_status(inventory, cb, debug=False):
        captured.append(inventory)

    monkeypatch.setattr(status, '_fetch_inventory', fake_fetch_inventory)
    monkeypatch.setattr(
        status, '_print_inventory_with_status',
        fake_print_inventory_with_status
    )
    ret = status.main(['tory-status'])
    assert ret == 0
    assert len(captured) == 1
