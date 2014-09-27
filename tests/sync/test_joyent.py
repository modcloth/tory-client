# vim:fileencoding=utf-8
from tory_client.sync import joyent


def test_sync_machine(testlog, monkeypatch):
    for status in (201, 200, 400):
        captured = []

        def put_host(server, auth_token, host_def):
            captured.append((server, auth_token, host_def))
            return status

        monkeypatch.setattr(joyent, 'put_host', put_host)

        machine = {
            'id': '1',
            'name': 'some-server-{}'.format(status),
            'ips': ['2'],
            'disk': 3,
            'memory': 4,
            'tags': {
                'awesome': 'maybe',
                'foos': 5,
            },
            'type': 'smartmachine',
        }

        joyent.sync_machine(
            testlog, 'some-server-{}'.format(status), 'auth', machine
        )

        assert len(captured) > 0

        assert captured[-1][0] == 'some-server-{}'.format(status)
        assert captured[-1][1] == 'auth'

        host_def = captured[-1][2]
        assert host_def['ip'] == '2'
        assert host_def['name'] == 'some-server-{}'.format(status)
        assert host_def['vars']['ansible_python_interpreter'] == \
            '/opt/local/bin/python'
        assert host_def['vars']['disk'] == '3'
        assert host_def['vars']['memory'] == '4'
        assert host_def['vars']['joyent_id'] == '1'
        assert host_def['tags'] == {'awesome': 'maybe', 'foos': '5'}
