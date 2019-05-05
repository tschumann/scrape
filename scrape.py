import bs4
import os
import requests
import sys
import urllib.parse

from requests.exceptions import ConnectionError

class Page:
	# the URL that was passed in
	raw_url = ''
	normalised_url = ''
	# the pages that are linked from this page
	children = []
	# this page's domain
	domain = ''
	# this page's path (bit after the domain)
	path = ''
	# this page's content
	links = []
	sounds = []
	images = []
	scripts = []
	videos = []
	embeds = []
	objects = []
			
	def __init__(self, url):
		# cut off the URL fragment (if any)
		(defragged_url, frag) = urllib.parse.urldefrag(url)
		# split the URL into its components
		split_url = urllib.parse.urlparse(defragged_url)

		self.raw_url = url
		self.normalised_url = split_url.geturl()

		# TODO: clean up the domain as there may be a trailing :portnum
		self.domain = split_url.netloc
		self.path = split_url.path
		
		if self.path == '/':
			self.path = 'index.html'
	
	def get_domain(self):
		"""
		Get the domain that this page is from.
		"""
		return self.domain
		
	def should_process_page(self, url):
		"""
		Whether this page should be processed. Only process pages that are on the same domain as the first requested page.
		"""
		# parse the URL in question
		split_url = urllib.parse.urlparse(url)
		
		# TODO: clean up the domain as there may be a trailing :portnum
		return self.domain == split_url.netloc
	
	def _download_html(self):
		"""
		Download the page.
		"""
		try:
			response = requests.get(self.raw_url)
		except ConnectionError:
			print("ConnectionError when connecting to " + self.raw_url)
			return None
		
		if not response.ok:
			print("Could not access " + self.raw_url)
			
			return None
		
		if 'content-type' in response.headers:
			content_type = response.headers['content-type']
			page = open(self.domain + "/" + self.path, 'wb')
			page.write(response.content)
			page.close()

			return response.content
		else:
			print("No content-type in response headers")
			return None
	
	def _download_children(self):
		"""
		Download the child pages
		"""
		if not self.children:
			# look at all the links on the page
			for link in self.links:
				# pull out the URL
				url = self.link.get('href')
				# if the URL is on the same domain
				if self.should_process_page(url):
					# add it to the list of pages to download
					self.children.append(Page(url))

		for child in self.children:
			child.save()

	def _process_html(self, html):
		# parse the response HTML
		soup = bs4.BeautifulSoup(html, "html.parser")

		# find all links and media
		self.links = soup.find_all("a")
		self.sounds = soup.find_all("audio")
		self.images = soup.find_all("img")
		self.scripts = soup.find_all("script")
		self.videos = soup.find_all("video")
		self.embeds = soup.find_all("embed")
		self.objects = soup.find_all("object")

	def save(self):
		if not os.path.exists(self.get_domain()):
			print("Creating directory " + self.get_domain())
			os.makedirs(self.get_domain())

		html = self._download_html()
		self._process_html(html)

		for image in self.images:
			pass

		for sound in self.sounds:
			pass

		for script in self.scripts:
			pass
		
		for video in self.videos:
			pass
		
		for embed in self.embeds:
			pass
		
		for object in self.objects:
			pass

class DownloadManager:

	def __init__(self, url):
		page = Page(url)
		page.save()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("No site specified")
		sys.exit()

	download_manager = DownloadManager(sys.argv[1])
