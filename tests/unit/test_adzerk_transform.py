from unittest import TestCase
from unittest.mock import patch

from adzerk.transform import to_spoc, tracking_url_to_shim
from tests.fixtures.mock_spoc import mock_spoc_2, mock_spoc_3_cta
from tests.fixtures.mock_decision import mock_decision_2, mock_decision_3_cta


class TestAdZerkTransform(TestCase):
    @patch.dict('conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_to_spoc(self):
        self.assertEqual(mock_spoc_2, to_spoc(mock_decision_2))

    @patch.dict('conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_to_spoc_cta(self):
        self.assertEqual(mock_spoc_3_cta, to_spoc(mock_decision_3_cta))

    def test_tracking_url_to_shim(self):
        self.assertEqual('0,eyJ,Zz', tracking_url_to_shim('https://e-10250.adzerk.net/r?e=eyJ&s=Zz'))
        self.assertEqual('1,a,b', tracking_url_to_shim('https://e-10250.adzerk.net/i.gif?s=b&e=a'))
        self.assertEqual('2,123,1', tracking_url_to_shim('https://e-10250.adzerk.net/e.gif?e=123&s=1'))

        with self.assertRaises(Exception):
            tracking_url_to_shim('https://e-10250.adzerk.net/x.gif?e=123&s=1')
