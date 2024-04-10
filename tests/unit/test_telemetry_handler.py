import base64
import gzip
import json
import time

from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, call
from urllib.parse import urlencode
from app.telemetry.handler import handle_message, ping_adzerk


def make_encoded_shim(flight_id, timestamp_millis):
    kevel_shim = f'{{"v":"1.11","av":1963769,"at":3617,"bt":0,"cm":56469793,"ch":36848,"ck":{{}},"cr":340374584,"di":"f9bee25375f147888123a33bfdf871c8","dj":0,"ii":"80740184383e4e5793ec76705421b78a","dm":3,"fc":515667491,"fl":{flight_id},"ip":"34.105.7.247","kw":"us,us-ct","mk":"us","nw":10250,"pc":0.93,"op":0.93,"ec":0,"gm":0,"ep":null,"pr":147518,"rt":2,"rs":500,"sa":"55","sb":"i-0983b4c7d16eabe85","sp":172421,"st":1070098,"uk":"{{4ef12475-fb03-4ac8-881f-8637bfbc76a7}}","zn":217758,"ts":{timestamp_millis},"pn":"spocs","gc":true,"gC":true,"gs":"none","dc":1,"tz":"UTC","ba":1,"fq":1}}'
    return base64.b64encode(bytes(kevel_shim, 'utf-8')).rstrip(b'=').decode()


class TestTelemetryHandler(TestCase):
    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_legacy_ping(self, mock_ping_adzerk):
        telemetry = {'tiles': [{'shim': '0,foo,bar'}, {'shim': '1,1,2'}, {'shim': '2,a,b'}]}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'activity-stream', 'document_type': 'impression-stats',
                      'user_agent_version': 121, 'submission_timestamp': '2024-03-12T21:02:18.123456Z'}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_has_calls([
            call('0,foo,bar', '2024-03-12T21:02:18.123456Z'),
            call('1,1,2', '2024-03-12T21:02:18.123456Z'),
            call('2,a,b', '2024-03-12T21:02:18.123456Z'),
        ])

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_android_spoc_ping(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.spoc_shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'org-mozilla-firefox', 'document_type': 'spoc',
                      'user_agent_version': 121, 'submission_timestamp': '2024-03-12T21:02:18.123456Z'}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_called_with('0,foo,bar', '2024-03-12T21:02:18.123456Z')

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_desktop_spoc_ping(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-desktop', 'document_type': 'spoc',
                      'user_agent_version': 122, 'submission_timestamp': '2024-03-12T21:02:18.123456Z'}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_called_with('0,foo,bar', '2024-03-12T21:02:18.123456Z')

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_desktop_spoc_ping_old_version(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-desktop', 'document_type': 'spoc',
                      'user_agent_version': 121, 'submission_timestamp': '2024-03-12T21:02:18.123456Z'}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_not_called()

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_unknown_namespace(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-temp', 'document_type': 'spoc',
                      'user_agent_version': 122, 'submission_timestamp': '2024-03-12T21:02:18.123456Z'}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_not_called()

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_unknown_doctype(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-desktop', 'document_type': 'temp',
                      'user_agent_version': 122, 'submission_timestamp': '2024-03-12T21:02:18.123456Z'}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_not_called()

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_r(self, mock_urlopen):
        ping_adzerk('0,foo,bar', '2024-03-12T21:02:18.123456Z')
        mock_urlopen.assert_called_once_with("https://e-10250.adzerk.net/r?e=foo&s=bar")

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_i(self, mock_urlopen):
        ping_adzerk('1,foo,bar', '2024-03-12T21:02:18.123456Z')
        mock_urlopen.assert_called_once_with("https://e-10250.adzerk.net/i.gif?e=foo&s=bar")

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_e(self, mock_urlopen):
        ping_adzerk('2,foo,bar', '2024-03-12T21:02:18.123456Z')
        mock_urlopen.assert_called_once_with("https://e-10250.adzerk.net/e.gif?e=foo&s=bar")

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_pacing_test_flight_skipped(self, mock_urlopen):
        submission_timestamp = '2024-03-12T21:02:18.123456Z'
        # 35 minutes older than submission
        submission_timestamp_seconds = int(datetime.fromisoformat(submission_timestamp).timestamp())
        shim_time = (submission_timestamp_seconds - 35*60) * 1000
        shim = make_encoded_shim(5003, shim_time)
        ping_adzerk(f'2,{shim},bar', submission_timestamp)
        mock_urlopen.assert_not_called()

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_pacing_non_test_flight_not_skipped(self, mock_urlopen):
        submission_timestamp = '2024-03-12T21:02:18.123456Z'
        # 10 minutes older than submission
        submission_timestamp_seconds = int(datetime.fromisoformat(submission_timestamp).timestamp())
        shim_time = (submission_timestamp_seconds - 10*60) * 1000
        shim = make_encoded_shim(5003, shim_time)
        ping_adzerk(f'2,{shim},bar', submission_timestamp)
        params = urlencode({'e': shim, 's': 'bar'})
        mock_urlopen.assert_called_once_with(f"https://e-10250.adzerk.net/e.gif?{params}")

    @patch('urllib.request.urlopen')
    def test_ping_adzerk_pacing_test_flight_not_skipped(self, mock_urlopen):
        submission_timestamp = '2024-03-12T21:02:18.123456Z'
        # 35 minutes older than submission but not a test flight
        submission_timestamp_seconds = int(datetime.fromisoformat(submission_timestamp).timestamp())
        shim_time = (submission_timestamp_seconds - 35*60) * 1000
        shim = make_encoded_shim(504478050, shim_time)
        ping_adzerk(f'2,{shim},bar', submission_timestamp)
        params = urlencode({'e': shim, 's': 'bar'})
        mock_urlopen.assert_called_once_with(f"https://e-10250.adzerk.net/e.gif?{params}")
