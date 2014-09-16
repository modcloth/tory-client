# vim:fileencoding=utf-8

import os

from _pytest.monkeypatch import monkeypatch

from tory_client import inventory


def fake_fetch_inventory(url):
    return '{"_meta":{"hostvars":{}}}'


def setup():
    os.environ.clear()
    mp = monkeypatch()
    mp.setattr(inventory, '_fetch_inventory', fake_fetch_inventory)


def test_main():
    ret = inventory.main(['tory-inventory'])
    assert ret == 0
