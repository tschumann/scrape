import os
import unittest
import sys

from unittest.mock import MagicMock

# add the parent directory to the path (make it absolute to this works regardless of where it's called from)
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "..")

from scrape.scrape import Page

class TestScrape(unittest.TestCase):

	def tearDown(self):
		if os.path.exists('dev.lan'):
			os.rmdir("dev.lan")

	def test_get_url(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.get_url(), "http://dev.lan")
		
	def test_get_domain(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.get_domain(), "dev.lan")
		
	def test_should_process_page_same_domain_same_scheme(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.should_process_page("http://dev.lan/news"), True)
	
	def test_should_process_page_same_domain_different_scheme(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.should_process_page("https://dev.lan/news"), True)
		
	def test_should_process_page_different_domain(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.should_process_page("https://www.wizzle.wazzle"), False)

	def test_download_creates_directory(self):
		page = Page("http://dev.lan")
		page.save()
		self.assertEqual(os.path.exists('dev.lan'), True)

if __name__ == '__main__':
    unittest.main()
