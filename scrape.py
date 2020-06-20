import bs4
import os
import requests
import sys
import urllib.parse

from requests.exceptions import ConnectionError

log_stdout = False

def log(string: str):
	if log_stdout:
		print(string)

class Page:
			
	def __init__(self, url: str):
		if not url.startswith("http://") and not url.startswith("https://"):
			raise Exception("URL requires a protocol")

		# cut off the URL fragment (if any)
		(defragged_url, frag) = urllib.parse.urldefrag(url)
		# split the URL into its components
		split_url = urllib.parse.urlparse(defragged_url)

		# the URL that was passed in
		self.raw_url = url
		self.normalised_url = split_url.geturl()

		# this page's protocol
		self.protocol = split_url.scheme
		# this page's domain
		self.domain = split_url.netloc
		# this page's path (bit after the domain)
		self.path = split_url.path

		self.children = []

		# if there is a :portnum
		if ':' in self.domain:
			log("Dealing with port number in URL")
			# slice it off
			self.domain = ''.join(self.domain.split(':')[:-1])

		# deal with absence or presence of trailing slash
		if self.path == '' or self.path == '/':
			log("Dealing with lack of path")
			self.path = 'index.html'
	
	def get_domain(self):
		"""
		Get the domain that this page is from.
		"""
		return self.domain

	def are_domains_same(self, domain: str):
		"""
		Whether the passed domain is the same as the current domain.
		"""
		# TODO: check for trailing :portnum in domain?
		return self.get_domain() == domain
		
	def should_process_page(self, url: str):
		"""
		Whether this page should be processed. Only process pages that are on the same domain as the first requested page.
		"""
		# parse the URL in question
		split_url = urllib.parse.urlparse(url)

		is_same_domain = self.are_domains_same(split_url.netloc)

		if is_same_domain:
			log("Page is on " + split_url.netloc + " so it should be processed")
		else:
			log("Page is on " + split_url.netloc + " so it not should be processed")

		return is_same_domain

	def _download_item(self, url: str):
		"""
		Download the item at the URL.
		"""
		try:
			log("Downloading " + url)
			response = requests.get(url)
		except ConnectionError:
			log("ConnectionError when connecting to " + url)
			return None
		
		if not response.ok:
			log("Could not access " + url)

			return None
		
		if 'content-type' in response.headers:
			split_url = urllib.parse.urlparse(url)
			path = split_url.path
			if path == '' or path == '/':
				path = 'index.html'
			if path[0] == '/':
				path = path[1:]
			directory = self.get_domain() + "/" + os.path.dirname(path)
			if directory != "" and not os.path.exists(os.path.abspath(directory)):
				log("Creating directory " + directory)
				os.makedirs(directory)
			log("Saving " + path + " in " + self.get_domain())
			item = open(self.get_domain() + "/" + path, 'wb')
			item.write(response.content)
			item.close()

			return response.content
		else:
			log("No content-type in response headers")
			return None
	
	def _download_children(self):
		"""
		Download the child pages
		"""
		if len(self.children) == 0:
			# look at all the links on the page
			for link in self.links:
				# pull out the URL
				url = link.get('href')
				# if the URL is on the same domain
				if self.should_process_page(url):
					# add it to the list of pages to download
					self.children.append(Page(url))

		for child in self.children:
			child.save()

	def _process_html(self, html: str):
		# parse the response HTML
		soup = bs4.BeautifulSoup(html, "html.parser")

		# find all links and media
		self.links = soup.find_all("a")
		self.sounds = soup.find_all("audio")
		self.images = soup.find_all("img")
		self.scripts = soup.find_all("script")
		self.stylesheets = soup.find_all("link")
		self.videos = soup.find_all("video")
		self.embeds = soup.find_all("embed")
		self.objects = soup.find_all("object")

	def _get_full_url(self, url: str):
		full_url = url
		parsed_url = urllib.parse.urlparse(url)

		# if the URL is a relative path
		if parsed_url.netloc == "":
			# TODO: deal with port?
			full_url = self.protocol + "://" + self.get_domain() + "/" + url

		return full_url

	def save(self):
		log("Saving site")

		if not os.path.exists(self.get_domain()):
			log("Creating directory " + self.get_domain() + " in " + os.getcwd())
			os.makedirs(self.get_domain())

		html = self._download_item(self.raw_url)

		if html is None:
			log("Got no content")
			return

		self._process_html(html)
		self._download_children()

		for image in self.images:
			url = self._get_full_url(image['src'])

			self._download_item(url)

		for sound in self.sounds:
			pass

		for script in self.scripts:
			if script.get('src', None) is not None:
				url = self._get_full_url(script['src'])

				self._download_item(url)
			else:
				log("Skipping inline script tag")

		for stylesheet in self.stylesheets:
			if stylesheet.get('rel', None) == ['stylesheet']:
				url = self._get_full_url(stylesheet['href'])

				log("Downloading " + url)
			else:
				log("Skipping link tag that isn't for a stylesheet")
		
		for video in self.videos:
			pass
		
		for embed in self.embeds:
			pass
		
		for object in self.objects:
			pass

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("No site specified")
		sys.exit()

	if len(sys.argv) > 2 and sys.argv[2] == "-v":
		log_stdout = True

	try:
		page = Page(sys.argv[1])
		page.save()
	except Exception as e:
		print("Encountered an error of type " + e.__class__.__name__ + ": " + str(e))
		if log_stdout:
			print(traceback.format_exc())
		sys.exit()
