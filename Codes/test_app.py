import unittest

# Import only the simple function we want to test
from .app import clean_text

class TestSimpleFunctions(unittest.TestCase):

    def test_clean_text_standard(self):
        """Tests basic cleaning with mixed case and extra spaces."""
        self.assertEqual(clean_text("  Some Text HERE   "), "some text here")

    def test_clean_text_empty(self):
        """Tests an empty string, which should remain empty."""
        self.assertEqual(clean_text(""), "")

    def test_clean_text_no_change(self):
        """Tests text that is already clean."""
        self.assertEqual(clean_text("already clean"), "already clean")
        
    def test_clean_text_non_string_input(self):
        """Tests non-string input like None, which should return an empty string."""
        self.assertEqual(clean_text(None), "")

if __name__ == '__main__':
    unittest.main()