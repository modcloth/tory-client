# vim:fileencoding=utf-8

import os

from _pytest.monkeypatch import monkeypatch

from conftest import fake_put_host, fake_get_local_ipv4

from tory_client import register


def setup():
    os.environ.clear()
    mp = monkeypatch()
    mp.setattr(register, 'put_host', fake_put_host)
    mp.setattr(register, '_get_local_ipv4', fake_get_local_ipv4)


def test_main():
    ret = register.main(['tory-register'])
    assert ret == 0


def test_once_overrides_loop_seconds_env_var():
    os.environ['TORY_LOOP_SECONDS'] = '3600'
    ret = register.main(['tory-register', '--once'])
    assert ret == 0


def test_once_overrides_loop_seconds_flag():
    ret = register.main([
        'tory-register', '--once', '--loop-seconds=3600'
    ])
    assert ret == 0
