import os

from unittest import TestCase
from unittest.mock import patch
import responses
import time

from adzerk.api import Api
from tests.fixtures.mock_placements import mock_placements, mock_spocs_placement


class TestAdZerkApi(TestCase):

    def setUp(self):
        # Reset cache expiration time
        Api.priority_cache_expires_at = None

    @patch.dict(os.environ, {"ADZERK_API_KEY": "DUMMY_123"})
    @responses.activate
    def test_delete_user(self):

        url = 'https://e-10250.adzerk.net/udb/10250/?userKey=%7B123%7D'
        responses.add(responses.DELETE, url, status=200)

        api = Api(pocket_id="{123}")
        api.delete_user()

        self.assertEqual(1, len(responses.calls))

        request = responses.calls[0].request
        self.assertEqual(url, request.url)
        self.assertEqual('DUMMY_123', request.headers['X-Adzerk-ApiKey'])

    @patch('adzerk.secret.get_api_key')
    @responses.activate
    def test_update_api_key(self, mock_get_api_key):
        url = 'https://e-10250.adzerk.net/udb/10250/?userKey=%7B123%7D'
        responses.add(responses.DELETE, url, status=401)
        responses.add(responses.DELETE, url, status=200)
        call_values = [, "DUMMY_123"]
        return_values = ["OUT_OF_DATE_456", "DUMMY_123"]
        mock_get_api_key.return_value = lambda: return_values.pop()
        mock_get_api_key.side_effect = lambda: call_values.pop()

        api = Api(pocket_id="{123}")
        api.delete_user(retry_count=10) # Arbitrarily high number of retry attempts. It's expected to only retry once.

        self.assertEqual(2, len(responses.calls))

        request = responses.calls[0].request
        self.assertEqual(url, request.url)
        self.assertEqual('OUT_OF_DATE_456', request.headers['X-Adzerk-ApiKey'])

        request = responses.calls[1].request
        self.assertEqual(url, request.url)
        self.assertEqual('DUMMY_123', request.headers['X-Adzerk-ApiKey'])

    def test_keywords(self):
        api = Api(pocket_id="{123}", country='US', region='CA')
        body = api.get_decision_body()
        self.assertTrue('US' in body['keywords'])
        self.assertTrue('US-CA' in body['keywords'])

    def test_missing_region(self):
        api = Api(pocket_id="{123}", country='US', region='')
        body = api.get_decision_body()
        self.assertEqual(['US'], body['keywords'])

    def test_keywords_empty(self):
        api = Api(pocket_id="{123}")
        body = api.get_decision_body()
        self.assertFalse('keywords' in body)

    def test_new_placements(self):
        api = Api(pocket_id="{123}", placements=mock_placements)
        body = api.get_decision_body()
        self.assertTrue(2, len(body['placements']))
        for p in body['placements']:
            self.assertEqual(10250, p['networkId'])
            self.assertEqual(1070098, p['siteId'])
            self.assertEqual(20, p['count'])
            self.assertEqual([5000], p['zoneIds'])

    def test_default_zone(self):
        api = Api(pocket_id="{123}", placements=mock_spocs_placement)
        body = api.get_decision_body()
        self.assertTrue(1, len(body['placements']))
        for p in body['placements']:
            self.assertEqual([217995], p['zoneIds'])

    @patch.dict(os.environ, {"ADZERK_API_KEY": "DUMMY_123"})
    @responses.activate
    def test_site_is_not_stored_in_conf(self):
        api = Api(pocket_id="{123}", country='US', region='CA', site=1084367)
        body = api.get_decision_body()
        self.assertEqual(1084367, body['placements'][0]['siteId'])

        api = Api(pocket_id="{123}", country='US', region='CA')
        body = api.get_decision_body()
        self.assertEqual(1070098, body['placements'][0]['siteId'])

    @patch('adzerk.secret.get_api_key', return_value="DUMMY_123")
    @responses.activate
    def test_get_priorities(self, mock_get_api_key):
        url = 'https://api.adzerk.net/v1/priority'
        responses.add(responses.GET, url, status=200, body='{"items": [{"Id": 123, "Weight": 9}]}')

        api = Api(pocket_id=None)
        result = api.get_cached_priorty_id_to_weights()

        self.assertEqual({123: 9}, result)

        # Check that the cache expiration time was updated correctly, with 1 second precision.
        self.assertAlmostEqual(
            api.priority_cache_expires_at,
            time.time() + api.PRIORITY_CACHE_DURATION,
            delta=1.0)

        self.assertEqual(1, len(responses.calls))

        request = responses.calls[0].request
        self.assertEqual(url, request.url)
        self.assertEqual('DUMMY_123', request.headers['X-Adzerk-ApiKey'])

    @patch('adzerk.secret.get_api_key', return_value="DUMMY_123")
    @responses.activate
    def test_get_priorities_retries_on_401(self, mock_get_api_key):
        url = 'https://api.adzerk.net/v1/priority'
        responses.add(responses.GET, url, status=401, body='')
        responses.add(responses.GET, url, status=200, body='{"items": [{"Id": 123, "Weight": 9}]}')

        api = Api(pocket_id=None)
        result = api.get_cached_priorty_id_to_weights()

        self.assertEqual({123: 9}, result)
        self.assertEqual(2, len(responses.calls))

    @patch('adzerk.secret.get_api_key', return_value="DUMMY_123")
    @responses.activate
    def test_get_priorities_cache(self, mock_get_api_key):
        url = 'https://api.adzerk.net/v1/priority'
        responses.add(responses.GET, url, status=200, body='{"items": [{"Id": 123, "Weight": 9}]}')

        api = Api(pocket_id=None)

        for i in range(20):
            result = api.get_cached_priorty_id_to_weights()
            self.assertEqual({123: 9}, result)

        # Check that only a single request is made to AdZerk.
        self.assertEqual(1, len(responses.calls))
