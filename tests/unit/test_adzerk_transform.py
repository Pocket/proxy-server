from unittest import TestCase
from unittest.mock import patch

from app.adzerk.transform import \
    to_spoc, tracking_url_to_shim, is_collection, to_collection, get_personalization_models
from tests.fixtures.mock_spoc import *
from tests.fixtures.mock_decision import *


class TestAdZerkTransform(TestCase):

    @patch.dict('app.conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_to_spoc(self):
        self.assertEqual(mock_spoc_2, to_spoc(mock_decision_2))

    @patch.dict('app.conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_to_spoc_cta(self):
        self.assertEqual(mock_spoc_3_cta, to_spoc(mock_decision_3_cta))

    @patch.dict('app.conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_to_spoc_topics(self):
        self.assertEqual(mock_spoc_5_topics, to_spoc(mock_decision_5_topics))

    @patch.dict('app.conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_to_spoc_no_sponsor(self):
        self.assertEqual(mock_spoc_6_no_sponsor, to_spoc(mock_decision_6_no_sponsor))

    @patch.dict('app.conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_to_spoc_is_video(self):
        self.assertEqual(mock_spoc_7_is_video, to_spoc(mock_decision_7_is_video))

    @patch.dict('app.conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_to_spoc_sponsored_by_override(self):
        self.assertEqual(mock_spoc_8_blank_sponsored_by_override, to_spoc(mock_decision_8_blank_sponsored_by_override))
        self.assertEqual(mock_spoc_9_sponsored_by_override, to_spoc(mock_decision_9_sponsored_by_override))

    @patch.dict('app.conf.domain_affinities', {"publishers": {'example.com': 1}})
    def test_missing_priority_id(self):
        self.assertEqual(mock_spoc_10_missing_priority, to_spoc(mock_decision_10_missing_priority))

    def test_tracking_url_to_shim(self):
        self.assertEqual('0,eyJ,Zz', tracking_url_to_shim('https://e-10250.adzerk.net/r?e=eyJ&s=Zz'))
        self.assertEqual('1,a,b', tracking_url_to_shim('https://e-10250.adzerk.net/i.gif?s=b&e=a'))
        self.assertEqual('2,123,1', tracking_url_to_shim('https://e-10250.adzerk.net/e.gif?e=123&s=1'))

        with self.assertRaises(Exception):
            tracking_url_to_shim('https://e-10250.adzerk.net/x.gif?e=123&s=1')

    def test_is_collection(self):
        self.assertEqual(False, is_collection([mock_spoc_2]))
        self.assertEqual(False, is_collection([mock_spoc_2, mock_collection_spoc_2]))
        self.assertEqual(True, is_collection([mock_collection_spoc_2]))
        self.assertEqual(True, is_collection([mock_collection_spoc_2, mock_collection_spoc_3]))

    def test_to_collection(self):
        self.assertEqual(mock_collection, to_collection([mock_collection_spoc_2, mock_collection_spoc_3]))

    def test_get_topics(self):
        self.assertEqual(
            {'business':1, 'technology': 1},
            get_personalization_models({'topic_business': 'true', 'topic_technology': True}))

        self.assertEqual(
            {},
            get_personalization_models({'topic_business': '', 'topic_technology': ''}))

        self.assertEqual(
            {'business':1},
            get_personalization_models({'topic_business': 'true', 'topic_technology': 'false'}))

        self.assertEqual(
            {'arts_and_entertainment':1},
            get_personalization_models({'other_property_business': 'true', 'topic_arts_and_entertainment': 'true'}))
