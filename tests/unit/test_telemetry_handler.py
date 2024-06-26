import base64
import gzip
import json
import logging
import os
import random

from datetime import datetime, timezone
from unittest import mock, TestCase
from unittest.mock import patch, call
from app.telemetry.handler import handle_message, ping_adzerk, record_metrics


def make_encoded_shim(timestamp_millis):
    kevel_shim = f'{{"v":"1.11","av":1963769,"at":3617,"bt":0,"cm":56469793,"ch":36848,"ck":{{}},"cr":340374584,"di":"f9bee25375f147888123a33bfdf871c8","dj":0,"ii":"80740184383e4e5793ec76705421b78a","dm":3,"fc":515667491,"fl":2000,"ip":"34.105.7.247","kw":"us,us-ct","mk":"us","nw":10250,"pc":0.93,"op":0.93,"ec":0,"gm":0,"ep":null,"pr":147518,"rt":2,"rs":500,"sa":"55","sb":"i-0983b4c7d16eabe85","sp":172421,"st":1070098,"uk":"{{4ef12475-fb03-4ac8-881f-8637bfbc76a7}}","zn":217758,"ts":{timestamp_millis},"pn":"spocs","gc":true,"gC":true,"gs":"none","dc":1,"tz":"UTC","ba":1,"fq":1}}'
    return base64.b64encode(bytes(kevel_shim, 'utf-8')).rstrip(b'=').decode()

class TestTelemetryHandler(TestCase):
    @patch('app.telemetry.handler.record_metrics')
    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_legacy_ping(self, mock_ping_adzerk, mock_record_metrics):
        telemetry = {'tiles': [{'shim': '0,foo,bar'}, {'shim': '1,1,2'}, {'shim': '2,a,b'}]}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        submission_timestamp = '2024-04-24T21:02:18.123456Z'
        attributes = {'document_namespace': 'activity-stream', 'document_type': 'impression-stats',
                      'user_agent_version': 121, 'submission_timestamp': submission_timestamp}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_has_calls([
            call('0,foo,bar'),
            call('1,1,2'),
            call('2,a,b'),
        ])
        mock_record_metrics.assert_has_calls([
            call('0,foo,bar', submission_timestamp, 'activity-stream', 121),
            call('1,1,2', submission_timestamp, 'activity-stream', 121),
            call('2,a,b', submission_timestamp, 'activity-stream', 121),
        ])

    @patch('app.telemetry.handler.record_metrics')
    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_legacy_ping_no_version(self, mock_ping_adzerk, mock_record_metrics):
        telemetry = {'tiles': [{'shim': '0,foo,bar'}, {'shim': '1,1,2'}, {'shim': '2,a,b'}]}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        submission_timestamp = '2024-04-24T21:02:18.123456Z'
        attributes = {'document_namespace': 'activity-stream', 'document_type': 'impression-stats',
                      'submission_timestamp': submission_timestamp}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_not_called()
        mock_record_metrics.assert_not_called()

    @patch('app.telemetry.handler.record_metrics')
    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_android_spoc_ping(self, mock_ping_adzerk, mock_record_metrics):
        telemetry = {'metrics': {'text': {'pocket.spoc_shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        submission_timestamp = '2024-04-24T21:02:18.123456Z'
        attributes = {'document_namespace': 'org-mozilla-firefox', 'document_type': 'spoc',
                      'user_agent_version': 121, 'submission_timestamp': submission_timestamp}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_called_with('0,foo,bar')
        mock_record_metrics.assert_called_with('0,foo,bar', submission_timestamp, 'org-mozilla-firefox', 121)

    @patch('app.telemetry.handler.record_metrics')
    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_desktop_spoc_ping(self, mock_ping_adzerk, mock_record_metrics):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        submission_timestamp = '2024-04-24T21:02:18.123456Z'
        attributes = {'document_namespace': 'firefox-desktop', 'document_type': 'spoc',
                      'user_agent_version': 122, 'submission_timestamp': submission_timestamp}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_called_with('0,foo,bar')
        mock_record_metrics.assert_called_with('0,foo,bar', submission_timestamp, 'firefox-desktop', 122)

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_desktop_spoc_ping_old_version(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-desktop', 'document_type': 'spoc',
                      'user_agent_version': 121}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_not_called()

    @patch('app.telemetry.handler.ping_adzerk')
    def test_handle_message_desktop_spoc_ping_no_version(self, mock_ping_adzerk):
        telemetry = {'metrics': {'text': {'pocket.shim': '0,foo,bar'}}}
        data = base64.b64encode(gzip.compress(json.dumps(telemetry).encode('utf-8')))
        attributes = {'document_namespace': 'firefox-desktop', 'document_type': 'spoc'}

        handle_message(event={'data': data, 'attributes': attributes}, context={})
        mock_ping_adzerk.assert_not_called()

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

    @patch('google.cloud.logging')
    @patch('logging.info')
    def test_record_metrics_no_sampling(self, mock_logging, mock_google_logging):
        os.environ["METRICS_SAMPLE_RATE"] = "0"
        shim = make_encoded_shim(1713971071000)
        record_metrics(f'2,{shim},bar', '2024-04-24T21:02:18.123456Z', "firefox-desktop", 125)
        mock_logging.assert_not_called()

    @patch('google.cloud.logging')
    @patch('logging.info')
    def test_record_metrics_sampling_misconfigured(self, mock_logging, mock_google_logging):
        os.environ["METRICS_SAMPLE_RATE"] = "true"
        shim = make_encoded_shim(1713971071000)
        record_metrics(f'2,{shim},bar', '2024-04-24T21:02:18.123456Z', "firefox-desktop", 125)
        mock_logging.assert_not_called()

    @patch('google.cloud.logging')
    @patch('logging.info')
    def test_record_metrics_sample_rate_excluded(self, mock_logging, mock_google_logging):
        # seed random to ensure random sample is excluded
        random.seed(0)
        os.environ["METRICS_SAMPLE_RATE"] = "500"
        shim = make_encoded_shim(1713971071000)
        record_metrics(f'2,{shim},bar', '2024-04-24T21:02:18.123456Z', "firefox-desktop", 125)
        mock_logging.assert_not_called()

    @patch('google.cloud.logging')
    @patch('logging.info')
    def test_record_metrics_shim_not_parsable(self, mock_logging, mock_google_logging):
        os.environ["METRICS_SAMPLE_RATE"] = "1000"
        record_metrics(f'2,shim,bar', '2024-04-24T21:02:18.123456Z', "firefox-desktop", 125)
        mock_logging.assert_not_called()

    @patch('google.cloud.logging')
    @patch('logging.info')
    def test_record_metrics_timestamp_not_parsable(self, mock_logging, mock_google_logging):
        os.environ["METRICS_SAMPLE_RATE"] = "1000"
        shim = make_encoded_shim(1713971071000)
        record_metrics(f'2,{shim},bar', 'invalid-timestamp', "firefox-desktop", 125)
        mock_logging.assert_not_called()

    @patch('app.telemetry.handler.get_now', mock.MagicMock(return_value=datetime(2024, 4, 25, 15, 4, 44, 686803, tzinfo=timezone.utc)))
    @patch('google.cloud.logging')
    @patch('logging.info')
    def test_log_metrics_sample_rate_included(self, mock_logging, mock_google_logging):
        # seed random to ensure random sample is included
        random.seed(0)
        os.environ["METRICS_SAMPLE_RATE"] = "900"
        shim = make_encoded_shim(1713971071000)
        record_metrics(f'2,{shim},bar', '2024-04-24T21:02:18.123456Z', "firefox-desktop", 125)
        json_fields = {
            "glean_latency": 64946563,
            "adserver_latency": 86413686,
            "namespace": "firefox-desktop",
            "user_agent_version": 125
        }
        mock_logging.assert_called_once_with("metrics", extra={"json_fields": json_fields})
