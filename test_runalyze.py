import json
import os
import sys
from unittest.mock import patch, MagicMock, mock_open
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from runalyze import parse_props, load_token, make_request

@pytest.mark.parametrize("props,expected", [
    (["a=1", "b=2"], {"a": 1, "b": 2}),
    (["a=\"str\"", "b=true"], {"a": "str", "b": True}),
    (["a=invalid_json"], {"a": "invalid_json"}),
    ([], {}),
    (None, {}),
])
def test_parse_props(props, expected):
    assert parse_props(props) == expected

def test_load_token_from_env_file():
    with patch("os.path.exists", return_value=True):
        m = mock_open(read_data="RUNALYZE_AUTH_TOKEN=test_token\n")
        with patch("builtins.open", m):
            assert load_token() == "test_token"

def test_load_token_from_env_var():
    with patch("os.path.exists", return_value=False):
        with patch("os.getenv", return_value="env_token"):
            assert load_token() == "env_token"

@patch("runalyze.TOKEN", "test_token")
def test_make_request_success():
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.status = 200
    mock_response.read.return_value = b'{"status": "ok"}'
    
    with patch("runalyze.urlopen", return_value=mock_response) as mock_url_open:
        res = make_request("/test")
        assert res == {"status": "ok"}
        mock_url_open.assert_called_once()

@patch("runalyze.TOKEN", "test_token")
def test_make_request_204():
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.status = 204
    
    with patch("runalyze.urlopen", return_value=mock_response):
        res = make_request("/test")
        assert res == {"status": "success"}

@patch("runalyze.TOKEN", "test_token")
def test_make_request_http_error():
    from urllib.error import HTTPError
    
    mock_fp = MagicMock()
    mock_fp.read.return_value = b"Error details"
    err = HTTPError("http://example.com", 400, "Bad Request", {}, mock_fp)
    
    with patch("runalyze.urlopen", side_effect=err):
        with patch("sys.exit") as mock_exit:
            make_request("/test")
            mock_exit.assert_called_with(1)
