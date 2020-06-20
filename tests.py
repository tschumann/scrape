import os
import sys
import unittest

from unittest.mock import MagicMock

# add the parent directory to the path (make it absolute to this works regardless of where it's called from)
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "..")

from scrape.scrape import Page

class TestScrape(unittest.TestCase):

	def tearDown(self):
		if os.path.exists("dev.lan"):
			os.rmdir("dev.lan")
		
	def test_get_domain(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.get_domain(), "dev.lan")

	def test_get_domain_port(self):
		page = Page("http://dev.lan:80")
		self.assertEqual(page.get_domain(), "dev.lan")

	def test_get_domain_ip_address(self):
		page = Page("http://0.0.0.0")
		self.assertEqual(page.get_domain(), "0.0.0.0")

	def test_get_domain_ip_address_port(self):
		page = Page("http://0.0.0.0:80")
		self.assertEqual(page.get_domain(), "0.0.0.0")

	def test_get_domain_https(self):
		page = Page("https://dev.lan")
		self.assertEqual(page.get_domain(), "dev.lan")

	def test_get_domain_no_protocol(self):
		self.assertRaises(Exception, Page, "dev.lan")

	def test_are_domains_same_same(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.are_domains_same("dev.lan"), True)

	def test_are_domains_same_different(self):
		page = Page("http://dev.lan")
		self.assertEqual(page.are_domains_same("fake.lan"), False)
		
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
		page._download_item = self._mock_download_item
		page.save()
		self.assertEqual(os.path.exists("dev.lan"), True)

	def test_get_full_url_relative(self):
		page = Page("http://dev.lan")
		full_url = page._get_full_url("path/image.jpg")
		self.assertEqual(full_url, "http://dev.lan/path/image.jpg")

	def test_get_full_url_absolute(self):
		page = Page("http://dev.lan")
		full_url = page._get_full_url("http://some.site/path/image.jpg")
		self.assertEqual(full_url, "http://some.site/path/image.jpg")

	def _mock_download_item(self, url: str):
		return ""

if __name__ == '__main__':
    unittest.main()
