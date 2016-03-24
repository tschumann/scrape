import bs4
import imp
import sys
import urlparse

using_beautifulsoup = False
using_requests = False

if imp.find_module('bs4'):
	import bs4
	using_beautifulsoup = True
else:
	import HTMLParser
	using_beautifulsoup = False

if imp.find_module('requests'):
	import requests
	using_requests = True
else:
	import urllib2
	using_requests = False

visited_urls = []

class Page:
	raw_url = ''
	normalised_url = ''
	domain = ''
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
		split_url = urlparse.urlparse(url)
		# TODO: look at urlparse.urldefrag
		# normalise the URL by clearing the fragment
		split_url.fragment = ''

		self.normalised_url = split_url.geturl()
		self.raw_url = url
		# TODO: clean up the domain as there may be a trailing :portnum
		self.domain = split_url.netloc
		
		self._get_page()

	def get_url(self):
		"""
		"""
		return self.normalised_url
	
	def get_domain(self):
		"""
		Get the domain that this page is from.
		"""
		return self.normalised_url.netloc
		
	def should_process_page(self, url):
		"""
		Whether this page should be processed.
		"""
		split_url = urlparse.urlparse(url)
		
		# TODO: clean up the domain as there may be a trailing :portnum
		return domain == split_url.netloc
	
	def _download(self):
		"""
		Download the page.
		"""
		global using_requests
		
		if using_requests:
			response = requests.get(self.raw_url)
			
			if not response.ok:
				print("Could not access ", self.raw_url)
				
				return None
			
			if 'content-type' in response.headers:
				content_type = response.headers['content-type']
			else:
				# TODO: possible to not have a mime-type? check if it looks like HTML?
				pass
		else:
			response = urllib2.Request(self.raw_url)
			
			# TODO: check response status code
			
			return response.read()
	
	def _download_children(self):
		"""
		"""
		for link in self.links:
			# TODO: call should_process_page on each link
			pass
		
	def _get_page(self):
		self.html = self._download(self.raw_url)
		
		if using_beautifulsoup:
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
			
def process_page(url):
    global traversed_links

    # if we've already visited this page
    if normalised_url in visited_urls:
        return
    else:
        # remember that we visited the page
        visited_urls.append(visited_urls)

    # download the page itself
    response = requests.get(url)

    if not response.ok:
        print("Could not access", url)
        return

    if 'content-type' in response.headers:
        content_type = response.headers['content-type']

        if content_type == 'text/html':
            # parse the response HTML
            soup = bs4.BeautifulSoup(response.text)

            page = open(split_url.path or 'index.html')
            page.write(response.text)

            # process all child pages
            for link in links:
                process_page(link.href)
        else:
            asset = open(split_url.path)
            asset.write(response.text)

if len(sys.argv) < 2:
    print("No site specified")
    sys.exit()

home_url = urlparse.urlparse(sys.argv[1])

page = Page(home_url)

# at this point add page.get_url to visited_urls, then recursively do this using a method to get all child pages