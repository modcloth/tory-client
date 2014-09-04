# vim:fileencoding=utf-8

import json
import os
import sys

from io import BytesIO

from _pytest.monkeypatch import monkeypatch
import pytest

import tory_sync_from_joyent


@pytest.fixture
def sdc_listmachines_json_stream(sampledata):
    sdc_bytes = json.dumps(sampledata['joyent']['sdc_listmachines'])
    if sys.version >= '3':
        sdc_bytes = sdc_bytes.encode('utf-8')
    return BytesIO(sdc_bytes)


def fake_put_host(server, auth_token, host_def):
    return 200


def setup():
    os.environ.clear()
    mp = monkeypatch()
    mp.setattr(tory_sync_from_joyent, '_put_host', fake_put_host)


def test_main(monkeypatch, sdc_listmachines_json_stream):
    monkeypatch.setattr('sys.stdin', sdc_listmachines_json_stream)
    ret = tory_sync_from_joyent.main(['tory-sync-from-joyent'])
    assert ret == 0
