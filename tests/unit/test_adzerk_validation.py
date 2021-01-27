from unittest import TestCase

from app.adzerk.validation import validate_image_url


class TestAdZerkValidation(TestCase):

    def test_valid_urls(self):
        self.assertTrue(validate_image_url('https://s.zkcdn.net/Advertisers/3a781523241f4e1293caad4ffbf2e2cb.jpg'))

    def test_invalid_urls(self):
        with self.assertRaises(Exception):
            self.assertFalse(validate_image_url('http://s.zkcdn.net/Advertisers/3a.jpg'))

        with self.assertRaises(Exception):
            self.assertFalse(validate_image_url('https://example.com/Advertisers/3a.jpg'))

        with self.assertRaises(Exception):
            self.assertFalse(validate_image_url('https://sxzkcdn.net/https://s.zkcdn.net/Advertisers/3a.jpg'))
