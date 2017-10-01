import bs4
import imp
import os
import requests
import sys
import urllib.parse

visited_urls = []

class Page:
	raw_url = ''
	normalised_url = ''
	# the pages that are linked from this page
	children = []
	# this page's domain
	domain = ''
	# this page's path
	path = ''
	# this page's content
	html = ''
	links = []
	sounds = []
	images = []
	scripts = []
	videos = []
	embeds = []
	objects = []
			
	def __init__(self, url):
		# split the URL into its components
		split_url = urllib.parse.urlparse(url)
		# TODO: look at urlparse.urldefrag
		# normalise the URL by clearing the fragment
		# split_url.fragment = ''

		self.normalised_url = split_url.geturl()
		self.raw_url = url
		# TODO: clean up the domain as there may be a trailing :portnum
		self.domain = split_url.netloc
		self.path = split_url.path
		
		if self.path == '/':
			self.path = 'index.html'

	def get_url(self):
		"""
		"""
		return self.normalised_url
	
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
	
	def _download(self):
		"""
		Download the page.
		"""
		response = requests.get(self.raw_url)
		
		if not response.ok:
			print("Could not access ", self.raw_url)
			
			return None
		
		if 'content-type' in response.headers:
			content_type = response.headers['content-type']
			page = open(self.domain + "/" + self.path, 'wb')
			page.write(response.content)
			page.close()
		else:
			# TODO: possible to not have a mime-type? check if it looks like HTML?
			return None
	
	def _download_children(self):
		"""
		"""
		# instantiate the children
		if not self.children:
			for link in self.links:
				self.children.append(Page(self.link.get('href')))

		for child in self.children:
			child.save()

	def _get_page(self):
		self.html = self._download()

		if self.html:
			# parse the response HTML
			soup = bs4.BeautifulSoup(self.html)

			# find all links and media
			self.links = soup.find_all("a")
			self.sounds = soup.find_all("audio")
			self.images = soup.find_all("img")
			self.scripts = soup.find_all("script")
			self.videos = soup.find_all("video")
			self.embeds = soup.find_all("embed")
			self.objects = soup.find_all("object")
		else:
			pass
			
	def save(self):
		if not os.path.exists(self.domain):
			os.makedirs(self.domain)

		self._download()

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
	pages = []

	def __init__(self, url):
		page = Page(url)
		page.save()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("No site specified")
		sys.exit()

	download_manager = DownloadManager(sys.argv[1])