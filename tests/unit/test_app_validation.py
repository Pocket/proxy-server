from unittest import TestCase

from app.validation import is_valid_pocket_id


class TestAppValidation(TestCase):

    def test_valid_pocket_id(self):
        self.assertTrue(is_valid_pocket_id('{12347fff-00b0-aaaa-0978-189231239808}'))
        # Uppercase is allowed:
        self.assertTrue(is_valid_pocket_id('{12347fff-00F0-AAAA-0978-189231feb808}'))

    def test_invalid_pocket_id(self):
        self.assertFalse(is_valid_pocket_id('{}'))
        # 'g' not allowed:
        self.assertFalse(is_valid_pocket_id('{g2345678-0000-aaaa-0978-189231239808}'))
        # Has to be correct length:
        self.assertFalse(is_valid_pocket_id('{12345678-0000-aaaa-0978-18923123980}'))
        self.assertFalse(is_valid_pocket_id('{12345678-0000-aaaa-0978-1892312398080}'))
        # Spaces not allowed:
        self.assertFalse(is_valid_pocket_id('{12345678 0000-aaaa-0978-189231239808}'))
        # Angular brackets not allowed:
        self.assertFalse(is_valid_pocket_id('{<aaaaaa>-0000-aaaa-0978-189231239808}'))
