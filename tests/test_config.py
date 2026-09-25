"""Placeholder detection: unedited .env.example values must not reach Jamf"""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _load_config(monkeypatch, **env):
    for key in ('JAMF_PRO_URL', 'JAMF_PRO_API_TOKEN', 'JAMF_PRO_USERNAME', 'JAMF_PRO_PASSWORD'):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import dotenv
    monkeypatch.setattr(dotenv, 'load_dotenv', lambda *a, **k: None)
    from src import config
    return importlib.reload(config)


def test_example_placeholders_are_treated_as_unset(monkeypatch):
    cfg = _load_config(
        monkeypatch,
        JAMF_PRO_URL='https://your-jamf-instance.jamfcloud.com',
        JAMF_PRO_USERNAME='your_username',
        JAMF_PRO_PASSWORD='your_password',
        JAMF_PRO_API_TOKEN='your_bearer_token',
    )
    assert cfg.JAMF_PRO_URL is None
    assert cfg.JAMF_PRO_USERNAME is None
    assert cfg.JAMF_PRO_PASSWORD is None
    assert cfg.JAMF_PRO_API_TOKEN is None


def test_url_has_no_default_tenant(monkeypatch):
    assert _load_config(monkeypatch).JAMF_PRO_URL is None


def test_real_values_pass_through(monkeypatch):
    cfg = _load_config(
        monkeypatch,
        JAMF_PRO_URL='https://example.jamfcloud.com',
        JAMF_PRO_USERNAME='svc-wakeup',
        JAMF_PRO_PASSWORD='s3cret',
    )
    assert cfg.JAMF_PRO_URL == 'https://example.jamfcloud.com'
    assert cfg.JAMF_PRO_USERNAME == 'svc-wakeup'
    assert cfg.JAMF_PRO_PASSWORD == 's3cret'
