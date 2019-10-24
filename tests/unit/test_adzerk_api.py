from unittest import TestCase
from unittest.mock import patch
import responses

from adzerk.api import Api
from tests.fixtures.mock_placements import mock_placements


class TestAdZerkApi(TestCase):

    @patch.dict('conf.adzerk', {"api_key": "DUMMY_123"})
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

    @patch.dict('conf.adzerk', {"api_key": "OUT_OF_DATE_456"})
    @patch('adzerk.secret.get_api_key', return_value="DUMMY_123")
    @responses.activate
    def test_update_api_key(self, mock_get_api_key):
        url = 'https://e-10250.adzerk.net/udb/10250/?userKey=%7B123%7D'
        responses.add(responses.DELETE, url, status=401)
        responses.add(responses.DELETE, url, status=200)

        api = Api(pocket_id="{123}")
        api.delete_user()

        self.assertEqual(2, len(responses.calls))

        request = responses.calls[0].request
        self.assertEqual(url, request.url)
        self.assertEqual('OUT_OF_DATE_456', request.headers['X-Adzerk-ApiKey'])

        request = responses.calls[1].request
        self.assertEqual(url, request.url)
        self.assertEqual('DUMMY_123', request.headers['X-Adzerk-ApiKey'])

    def test_keywords(self):
        api = Api(pocket_id="{123}", country='USA', region='CA')
        body = api.get_decision_body()
        self.assertTrue('country-USA' in body['keywords'])
        self.assertTrue('region-CA' in body['keywords'])

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

    @patch.dict('conf.adzerk', {"api_key": "DUMMY_123"})
    @responses.activate
    def test_site_is_not_stored_in_conf(self):
        api = Api(pocket_id="{123}", country='USA', region='CA', site=1084367)
        body = api.get_decision_body()
        self.assertEqual(1084367, body['placements'][0]['siteId'])

        api = Api(pocket_id="{123}", country='USA', region='CA')
        body = api.get_decision_body()
        self.assertEqual(1070098, body['placements'][0]['siteId'])


