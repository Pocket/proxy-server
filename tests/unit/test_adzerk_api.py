import os
from unittest import TestCase
from unittest.mock import patch, Mock
import responses
import requests.exceptions

from app.adzerk.api import Api
from tests.fixtures.mock_placements import mock_placements, mock_spocs_placement


class TestAdZerkApi(TestCase):

    def setUp(self):
        # Reset cache expiration time
        Api.priority_cache_expires_at = None

    @responses.activate
    def test_delete_user(self):
        url = 'https://e-10250.adzerk.net/udb/10250/?userKey=%7B123%7D'
        responses.add(responses.DELETE, url, status=200)

        api = Api(pocket_id="{123}", api_key="DUMMY_123")
        api.delete_user()

        self.assertEqual(1, len(responses.calls))

        request = responses.calls[0].request
        self.assertEqual(url, request.url)
        self.assertEqual('DUMMY_123', request.headers['X-Adzerk-ApiKey'])

    @responses.activate
    def test_update_api_key(self):
        url = 'https://e-10250.adzerk.net/udb/10250/?userKey=%7B123%7D'
        responses.add(responses.DELETE, url, status=401)

        api = Api(pocket_id="{123}", api_key="OUT_OF_DATE_123")
        # Exception is raised when AdZerk responds with a bad status code.
        with self.assertRaises(requests.exceptions.HTTPError):
            api.delete_user()

        self.assertEqual(1, len(responses.calls))

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
            self.assertEqual(10, p['count'])
            self.assertEqual([5000], p['zoneIds'])

    def test_default_zone(self):
        api = Api(pocket_id="{123}", placements=mock_spocs_placement)
        body = api.get_decision_body()
        self.assertTrue(1, len(body['placements']))
        for p in body['placements']:
            self.assertEqual([217995], p['zoneIds'])

    @responses.activate
    def test_site_is_not_stored_in_conf(self):
        api = Api(pocket_id="{123}", country='US', region='CA', site=1084367)
        body = api.get_decision_body()
        self.assertEqual(1084367, body['placements'][0]['siteId'])

        api = Api(pocket_id="{123}", country='US', region='CA')
        body = api.get_decision_body()
        self.assertEqual(1070098, body['placements'][0]['siteId'])
