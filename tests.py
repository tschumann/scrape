import os
import sys
import unittest

from unittest.mock import MagicMock

# add the parent directory to the path (make it absolute to this works regardless of where it's called from)
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "..")

from scrape import Site

class TestScrape(unittest.TestCase):

	def tearDown(self):
		if os.path.exists("dev.lan"):
			os.rmdir("dev.lan")

	def test_get_url_components(self):
		site = Site("http://dev.lan")
		self.assertEqual(site.get_url_components("http://dev.lan").get("netloc"), "dev.lan")
		self.assertEqual(site.get_url_components("http://www.dev.lan").get("netloc"), "www.dev.lan")

	def test_normalise_url(self):
		site = Site("http://dev.lan")
		self.assertEqual(site.normalise_url("http://dev.lan/index.html"), "http://dev.lan/index.html")
		self.assertEqual(site.normalise_url("http://dev.lan/"), "http://dev.lan")
		self.assertEqual(site.normalise_url("http://dev.lan"), "http://dev.lan")
		self.assertEqual(site.normalise_url("http://www.dev.lan/"), "http://www.dev.lan")
		self.assertEqual(site.normalise_url("http://www.dev.lan"), "http://www.dev.lan")
		self.assertEqual(site.normalise_url("http://dev.lan:80/index.html"), "http://dev.lan/index.html")
		self.assertEqual(site.normalise_url("http://dev.lan:443/index.html"), "http://dev.lan/index.html")
		self.assertEqual(site.normalise_url("http://dev.lan/index.html#hi"), "http://dev.lan/index.html")
		self.assertEqual(site.normalise_url("http://dev.lan/index.html?test=1"), "http://dev.lan/index.html")
		self.assertEqual(site.normalise_url("http://dev.lan/index.html?test"), "http://dev.lan/index.html")
		self.assertEqual(site.normalise_url("http://dev.lan:80/index.html?test=1#test"), "http://dev.lan/index.html")
		self.assertEqual(site.normalise_url("http://dev.lan/somewhere/index.html"), "http://dev.lan/somewhere/index.html")
		self.assertEqual(site.normalise_url("http://dev.lan/somewhere"), "http://dev.lan/somewhere")
		self.assertEqual(site.normalise_url("http://dev.lan/somewhere/"), "http://dev.lan/somewhere")
		self.assertEqual(site.normalise_url("http://dev.lan/somewhere/?test=1#test"), "http://dev.lan/somewhere")
		self.assertEqual(site.normalise_url("http://dev.lan/test.pdf"), "http://dev.lan/test.pdf")
		self.assertEqual(site.normalise_url("http://dev.lan/somewhere/test.pdf"), "http://dev.lan/somewhere/test.pdf")
		self.assertEqual(site.normalise_url(""), "http://dev.lan")
		self.assertEqual(site.normalise_url("#"), "http://dev.lan")
		self.assertEqual(site.normalise_url("/"), "http://dev.lan")
		self.assertEqual(site.normalise_url("/somewhere"), "http://dev.lan/somewhere")
		self.assertEqual(site.normalise_url("/somewhere/"), "http://dev.lan/somewhere")
		self.assertEqual(site.normalise_url("js/file.js"), "http://dev.lan/js/file.js")

	def test_get_directory_for_url(self):
		site = Site("http://dev.lan")
		self.assertEqual(site.get_directory_for_url("http://dev.lan/index.html", "text/html"), "dev.lan/")
		self.assertEqual(site.get_directory_for_url("http://dev.lan/", "text/html"), "dev.lan/")
		self.assertEqual(site.get_directory_for_url("http://dev.lan/somewhere", "text/html"), "dev.lan/somewhere/")
		self.assertEqual(site.get_directory_for_url("http://dev.lan/somewhere/", "text/html"), "dev.lan/somewhere/")
		self.assertEqual(site.get_directory_for_url("http://dev.lan/test.pdf", "application/pdf"), "dev.lan/")
		self.assertEqual(site.get_directory_for_url("http://dev.lan/somewhere/test.pdf", "application/pdf"), "dev.lan/somewhere/")

	def test_get_path_for_url(self):
		site = Site("http://dev.lan")
		self.assertEqual(site.get_path_for_url("http://dev.lan/index.html", "text/html"), "dev.lan/index.html")
		self.assertEqual(site.get_path_for_url("http://dev.lan/", "text/html"), "dev.lan/index.html")
		self.assertEqual(site.get_path_for_url("http://dev.lan/somewhere", "text/html"), "dev.lan/somewhere/index.html")
		self.assertEqual(site.get_path_for_url("http://dev.lan/somewhere/", "text/html"), "dev.lan/somewhere/index.html")
		self.assertEqual(site.get_path_for_url("http://dev.lan/test.pdf", "application/pdf"), "dev.lan/test.pdf")
		self.assertEqual(site.get_path_for_url("http://dev.lan/somewhere/test.pdf", "application/pdf"), "dev.lan/somewhere/test.pdf")

	def test_should_download_asset(self):
		site = Site("http://dev.lan")
		self.assertEqual(site.should_download_asset("http://dev.lan"), True)
		self.assertEqual(site.should_download_asset("http://dev.lan/"), True)
		self.assertEqual(site.should_download_asset("http://dev.lan/test.pdf"), True)
		self.assertEqual(site.should_download_asset("http://dev.lan/somewhere/test.pdf"), True)
		self.assertEqual(site.should_download_asset("http://www.dev.lan"), False)
		self.assertEqual(site.should_download_asset("http://horse.radish"), False)

if __name__ == '__main__':
    unittest.main()
