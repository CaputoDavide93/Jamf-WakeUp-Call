"""Classic API records keep id and name under `general`; flat records keep them on top"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import main  # noqa: E402


def _client():
    client = MagicMock()
    client.extract_user_info.return_value = {'full_name': '', 'username': '', 'position': ''}
    return client


def test_classic_api_record_shows_id_and_name():
    record = {'general': {'id': 101, 'name': 'MBP-101'}}
    line = main.format_computer_display(record, _client())
    assert '101' in line and 'MBP-101' in line
    assert 'N/A' not in line and 'Unknown' not in line


def test_flat_record_still_works():
    line = main.format_computer_display({'id': 7, 'name': 'MBP-7'}, _client())
    assert '7' in line and 'MBP-7' in line
    assert 'N/A' not in line and 'Unknown' not in line


def test_computer_field_prefers_general_and_falls_back_to_flat():
    assert main.computer_field({'general': {'name': 'a'}, 'name': 'b'}, 'name') == 'a'
    assert main.computer_field({'name': 'b'}, 'name') == 'b'
    assert main.computer_field({}, 'name', 'x') == 'x'
