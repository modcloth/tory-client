# vim:fileencoding=utf-8

import json
import os
import sys

from io import BytesIO

import pytest

from tory_client.sync import joyent
from tory_client import sync_from_joyent


@pytest.fixture
def sdc_listmachines_json_stream(sampledata):
    sdc_bytes = json.dumps(sampledata['joyent']['sdc_listmachines'])
    if sys.version >= '3':
        sdc_bytes = sdc_bytes.encode('utf-8')
    return BytesIO(sdc_bytes)


def fake_sync_machine(log, server, auth_token, host_def):
    pass


def setup():
    os.environ.clear()


def test_main(monkeypatch, sdc_listmachines_json_stream):
    monkeypatch.setattr(joyent, 'sync_machine', fake_sync_machine)
    monkeypatch.setattr('sys.stdin', sdc_listmachines_json_stream)
    ret = sync_from_joyent.main(['tory-sync-from-joyent'])
    assert ret == 0
