import base64
import gzip
import json

from unittest import TestCase
from unittest.mock import patch, call
from app.telemetry.handler import handle_message, ping_adzerk


class TestTelemetryHandler(TestCase):
    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_legacy_ping(self, mock_ping_adzerk):
        telemetry = {'tiles': [{'shim': '0,foo,bar'}, {'shim': '1,1,2'}, {'shim': '2,a,b'}]}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'activity-stream', 'document_type': 'impression-stats',
                      'user_agent_version': 121}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_has_calls([
            call('0,foo,bar'),
            call('1,1,2'),
            call('2,a,b'),
        ])

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_android_spoc_ping(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.spoc_shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'org-mozilla-firefox', 'document_type': 'spoc',
                      'user_agent_version': 121}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_called_with('0,foo,bar')

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_desktop_spoc_ping(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-desktop', 'document_type': 'spoc',
                      'user_agent_version': 122}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_called_with('0,foo,bar')

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_unknown_namespace(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-temp', 'document_type': 'spoc',
                      'user_agent_version': 122}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_not_called()

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_unknown_doctype(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-desktop', 'document_type': 'temp',
                      'user_agent_version': 122}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_not_called()

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
