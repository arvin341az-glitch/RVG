from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_isolated_panel_test(source: str, tmp_path: Path) -> None:
    """Run each integration scenario without leaking panel globals or env vars."""

    env = os.environ.copy()
    env.update(
        {
            "DATA_DIR": str(tmp_path),
            "CENTRAL_URL": "",
            "RAILWAY_PUBLIC_DOMAIN": "panel.example.test",
            "RVG_API_KEY": "test-api-key",
        }
    )
    result = subprocess.run(
        [sys.executable, "-c", source],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"


def test_api_key_is_checked_before_request_body(tmp_path: Path) -> None:
    run_isolated_panel_test(
        """
from fastapi.testclient import TestClient
import main

with TestClient(main.app) as client:
    response = client.post('/api/v1/users', json={'malformed': True})
    assert response.status_code == 401
    assert response.json()['error']['code'] == 'INVALID_API_KEY'
    assert response.headers['cache-control'].startswith('no-store')
    assert main.LINKS == {}
""",
        tmp_path,
    )


def test_complete_user_lifecycle(tmp_path: Path) -> None:
    run_isolated_panel_test(
        """
import base64
from fastapi.testclient import TestClient
import main

headers = {'X-API-KEY': 'test-api-key'}
with TestClient(main.app) as client:
    created = client.post(
        '/api/v1/users',
        headers=headers,
        json={
            'username': 'alice',
            'traffic_limit_gb': 20,
            'expire_days': 30,
            'protocol': 'vless',
        },
    )
    assert created.status_code == 201
    payload = created.json()
    assert payload['success'] is True
    assert payload['error'] is None
    user = payload['data']
    assert user['username'] == 'alice'
    assert user['traffic_limit_bytes'] == 20 * 1024**3
    assert user['protocol'] == 'vless-ws'
    assert user['links']['vless'].startswith('vless://')

    duplicate = client.post(
        '/api/v1/users',
        headers=headers,
        json={
            'username': 'ALICE',
            'traffic_limit_gb': 1,
            'expire_days': 1,
            'protocol': 'vless',
        },
    )
    assert duplicate.status_code == 409
    assert duplicate.json()['error']['code'] == 'USERNAME_EXISTS'

    extended = client.patch(
        '/api/v1/users/alice/extend',
        headers=headers,
        json={'add_gb': 5, 'add_days': 10},
    )
    assert extended.status_code == 200
    assert extended.json()['data']['traffic_limit_gb'] == 25
    assert extended.json()['data']['expire_days_remaining'] == 40

    disabled = client.patch(
        '/api/v1/users/alice/status',
        headers=headers,
        json={'enabled': False},
    )
    assert disabled.status_code == 200
    assert disabled.json()['data']['enabled'] is False
    assert disabled.json()['data']['is_active'] is False

    plain = client.get(
        '/api/v1/users/alice/subscription?format=plain', headers=headers
    ).json()['data']['content']
    encoded = client.get(
        '/api/v1/users/alice/subscription?format=base64', headers=headers
    ).json()['data']['content']
    assert base64.b64decode(encoded).decode('utf-8') == plain

    uid = user['uuid']
    main.LINKS[uid]['used_bytes'] = 123
    main.LINKS[uid]['upload_bytes'] = 23
    main.LINKS[uid]['download_bytes'] = 100
    reset = client.post('/api/v1/users/alice/reset-traffic', headers=headers)
    assert reset.status_code == 200
    assert reset.json()['data']['used_traffic_bytes'] == 0
    assert reset.json()['data']['upload_bytes'] == 0
    assert reset.json()['data']['download_bytes'] == 0

    deleted = client.delete('/api/v1/users/alice', headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()['data']['deleted'] is True

    missing = client.get('/api/v1/users/alice', headers=headers)
    assert missing.status_code == 404
    assert missing.json()['error']['code'] == 'USER_NOT_FOUND'
""",
        tmp_path,
    )


def test_validation_and_system_stats_use_unified_envelope(tmp_path: Path) -> None:
    run_isolated_panel_test(
        """
from fastapi.testclient import TestClient
import main

headers = {'X-API-KEY': 'test-api-key'}
with TestClient(main.app) as client:
    invalid = client.post(
        '/api/v1/users',
        headers=headers,
        json={
            'username': 'invalid username',
            'traffic_limit_gb': '10',
            'expire_days': 30,
            'protocol': 'vmess',
        },
    )
    assert invalid.status_code == 400
    assert invalid.json()['error']['code'] == 'VALIDATION_ERROR'

    mtproto = client.post(
        '/api/v1/users',
        headers=headers,
        json={
            'username': 'telegram_proxy',
            'traffic_limit_gb': 10,
            'expire_days': 30,
            'protocol': 'mtproto',
        },
    )
    assert mtproto.status_code == 503
    assert mtproto.json()['error']['code'] == 'MTPROTO_PROXY_NOT_CONFIGURED'
    assert main.LINKS == {}

    stats = client.get('/api/v1/system/stats', headers=headers)
    assert stats.status_code == 200
    payload = stats.json()
    assert payload['success'] is True
    assert 0 <= payload['data']['cpu_percent'] <= 100
    assert payload['data']['ram_total_bytes'] >= 0
    assert payload['data']['disk_total_bytes'] > 0
""",
        tmp_path,
    )
