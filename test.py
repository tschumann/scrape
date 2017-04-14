import os
import unittest
import sys

from unittest.mock import MagicMock

# deal with the confusing insanity of Python's import rules
sys.path.append('..')

from scrape.scrape import Page

class TestScrape(unittest.TestCase):

	def test_get_page_domain(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.get_url(), "http://dev.lan")

if __name__ == '__main__':
    unittest.main()
