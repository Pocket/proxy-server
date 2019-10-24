from unittest import TestCase
from unittest.mock import patch

from provider.geo_provider import GeolocationProvider
from tests.fixtures.mock_factory import get_mocked_geolocation_factory


class TestGeolocationProvider(TestCase):

    __FACTORY = get_mocked_geolocation_factory()

    @patch('boto3.session.Session.client', return_value=None)
    @patch('geolocation.factory.Factory.get_instance', return_value=__FACTORY)
    def test_geolocation_no_setattr(self, mock_s3, mock_geofactory):
        glp = GeolocationProvider()
        try:
            glp.__setattr__('__PROVIDER_INSTANCE', 'something else')
            self.fail('Should not be able to set attribute after singleton is created')
        except AttributeError as e:
            self.assertEqual(e.__str__(), 'Already instantiated')

    @patch('boto3.session.Session.client', return_value=None)
    @patch('geolocation.factory.Factory.get_instance', return_value=__FACTORY)
    def test_geolocation_valid_ip(self, mock_s3, mock_geofactory):
        glp = GeolocationProvider()
        city = glp.get_city('216.160.83.56')
        self.assertEqual('Milton', city.city.name)
        self.assertEqual('America/Los_Angeles', city.location.time_zone)
        self.assertEqual('US', glp.get_country(city))
        self.assertEqual('WA', glp.get_region(city))

    @patch('boto3.session.Session.client', return_value=None)
    @patch('geolocation.factory.Factory.get_instance', return_value=__FACTORY)
    def test_geolocation_invalid_ip(self, mock_s3, mock_geofactory):
        glp = GeolocationProvider()
        try:
            glp.get_city('127.0.0.1')
        except RuntimeError as e:
            self.assertEqual('The address 127.0.0.1 is not in the database.', e.__str__())

    @patch('boto3.session.Session.client', return_value=None)
    @patch('geolocation.factory.Factory.get_instance', return_value=__FACTORY)
    def test_geolocation_no_city(self, mock_s3, mock_geofactory):
        glp = GeolocationProvider()
        self.assertIsNone(glp.get_country(None))
        self.assertIsNone(glp.get_region(None))
