import base64
import gzip
import json

from unittest import TestCase
from unittest.mock import patch, call
from telemetry.handler import handle_message, ping_adzerk


class TestTelemetryHandler(TestCase):
    @patch('telemetry.handler.ping_adzerk')
    def test_handle_message(self, mock_ping_adzerk):
        telemetry = {'tiles': [{'shim': '0,foo,bar'}, {'shim': '1,1,2'}, {'shim': '2,a,b'}]}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))

        handle_message(event={'data': data}, context={})
        mock_ping_adzerk.assert_has_calls([
            call('0,foo,bar'),
            call('1,1,2'),
            call('2,a,b'),
        ])

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_r(self, mock_urlopen):
        ping_adzerk('0,foo,bar')
        mock_urlopen.assert_called_once_with("https://e-10250.adzerk.net/r?e=foo&s=bar")

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_i(self, mock_urlopen):
        ping_adzerk('1,foo,bar')
        mock_urlopen.assert_called_once_with("https://e-10250.adzerk.net/i.gif?e=foo&s=bar")

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_e(self, mock_urlopen):
        ping_adzerk('2,foo,bar')
        mock_urlopen.assert_called_once_with("https://e-10250.adzerk.net/e.gif?e=foo&s=bar")
