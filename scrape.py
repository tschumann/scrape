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

home_url = None
visited_urls = []

class Page:
	raw_url = ''
	normalised_url = ''
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
		# normalise the URL by clearing the fragment
		split_url.fragment = ''

		self.normalised_url = split_url.geturl()
		self.raw_url = url
		
		self._get_page()
	
	def get_domain():
		"""
		Get the domain that this page is from.
		"""
		return normalised_url.netloc
	
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
			response = urllib2.Request(self.raw_url)
			return response.read()
		
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

    # split the URL into its components
    split_url = urlparse.urlparse(url)
    # normalise the URL by clearing the fragment
    split_url.fragment = ''

    normalised_url = split_url.geturl()

    # don't go wild and start trying to download sites external to what was requested
    if split_url.netloc != home_url.netloc:
        print("Skipping external link to", url)
        return

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

            # find all links and media
            # TODO: handle embed and object
            links = soup.find_all("a")
            sounds = soup.find_all("audio")
            images = soup.find_all("img")
            scripts = soup.find_all("script")
            videos = soup.find_all("video")

            page = open(split_url.path or 'index.html')
            page.write(response.text)

            # process all child pages
            for link in links:
                process_page(link.href)
        else:
            asset = open(split_url.path)
            asset.write(response.text)
    else:
        # TODO: possible to not have a mime-type? check if it looks like HTML?
        pass

if len(sys.argv) < 2:
    print("No site specified")
    sys.exit()

# remember the home page
home_url = urlparse.urlparse(sys.argv[1])

process_page(sys.argv[1])
