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

class Site:

	def __init__(self, url: str):
		if not url.startswith("http://") and not url.startswith("https://"):
			raise Exception("URL requires a valid protocol")

		# keep track of the initial URL so we can check the domain
		self.url = self.normalise_url(url, url)

		# insert the initial URL into the processing queue
		self.pages = {
			url: {
				"processed": False
			}
		}

	def get_url_components(self, url: str, context: str) -> dict:
		"""
		Split the given URL into a normalised scheme, network location and path.
		"""

		# if it's a relative URL
		if (not url.startswith("http://")) and (not url.startswith("https://")):
			# recursive but shouldn't fail as the constructor makes sure the initial URL starts with a scheme
			initial_url_components = self.get_url_components(self.url, context)

			# if it's a relative URL
			if not url.startswith("/"):
				# add the path of the current page to make it an absolute URL
				url = context + "/" + url
			else:
				url = initial_url_components.get("scheme") + initial_url_components.get("netloc") + url

		# cut off the URL fragment (if any)
		(defragged_url, frag) = urllib.parse.urldefrag(url)
		# split the URL into its components
		parsed_url = urllib.parse.urlparse(defragged_url)

		# do extra processing of netloc
		netloc = parsed_url.netloc

		# if there is a port specified as part of the URL
		if ":" in netloc:
			# this assumes there is only one : in the netloc
			netloc = "".join(netloc.split(":")[:-1])

		# do extra processing of path
		path = parsed_url.path

		# if the path has a trailing /
		if path.endswith("/"):
			path = path[:-1]

		# ignore query string and fragment
		return {
			"scheme": parsed_url.scheme + "://",
			"netloc": netloc,
			"path": path
		}

	def normalise_url(self, url: str, context: str) -> str:
		"""
		Return a normalised version of the given URL.
		This is so that different versions of the same URL aren't processed multiple times.
		"""
		url_components = self.get_url_components(url, context)

		return url_components.get("scheme") + url_components.get("netloc") + url_components.get("path")

	def get_directory_for_url(self, url: str, content_type: str) -> str:
		"""
		Return a filesystem directory equivalent of the given URL.
		"""
		url_components = self.get_url_components(url, None)

		directory = url_components.get("netloc") + url_components.get("path")

		if content_type.startswith("text/html"):
			if directory.endswith("index.html"):
				directory = directory[:-len("index.html")]
		else:
			# treat it like a path and remove the 'file' from the 'directory'
			(directory, _) = os.path.split(directory)

		# normalise the ending
		if not directory.endswith("/"):
			directory = directory + "/"

		return directory

	def get_path_for_url(self, url: str, content_type: str) -> str:
		"""
		Return a filesystem path equivalent of the given URL.
		"""
		url_components = self.get_url_components(url, None)

		path = url_components.get("path")

		if content_type.startswith("text/html"):
			if not path.endswith("/index.html"):
				path = path + "/index.html"

		return url_components.get("netloc") + path

	def should_download_asset(self, url: str) -> bool:
		"""
		Whether this asset should be downloaded as part of this site.
		Only download pages on the same domain as the initial URL.
		"""
		site_netloc = self.get_url_components(self.url, None).get("netloc")
		asset_netloc = self.get_url_components(url, None).get("netloc")
		should_download = (site_netloc == asset_netloc)

		log("should_download_asset " + url + " " + str(should_download))

		return should_download

	def download_asset(self, url: str) -> str:
		try:
			log("Downloading " + url)
			response = requests.get(url)
		except ConnectionError:
			log("ConnectionError when connecting to " + url)
			return None
		
		if not response.ok:
			log("Could not get " + url)
			return None

		self.pages[url] = self.pages.get(url, {"processed": True})

		if "content-type" in response.headers:
			# TODO: content-type should be properly parsed (there may be a trailing ; charset=utf-8 for example)
			content_type = response.headers["content-type"]
			log("Got " + url + " with content-type " + content_type)

			directory = self.get_directory_for_url(url, content_type)
			path = self.get_path_for_url(url, content_type)

			# make sure the path to download to exists on the filesystem
			if not os.path.exists(os.path.abspath(directory)):
				log("Creating directory " + directory)
				os.makedirs(directory)

			log("Saving " + path)
			asset = open(path, "wb")
			asset.write(response.content)
			asset.close()

			# if it's HTML, return the HTML for further processing
			if content_type.startswith("text/html"):
				return response.content
			else:
				return None
		else:
			log("No content-type in response headers")
			return None

	def find_assets(self, html: str, context: str):
		"""
		Look through the HTML for more assets to download.
		"""
		# parse the response HTML
		soup = bs4.BeautifulSoup(html, "html.parser")

		anchors = soup.find_all("a")

		for anchor in anchors:
			url = anchor.get("href")
			normalised_url = self.normalise_url(url, context)

			if normalised_url not in self.pages:
				# only download pages that are on the same domain
				if self.should_download_asset(normalised_url):
					log("Adding " + normalised_url)
					self.pages[normalised_url] = {"processed": False}
				else:
					# keep track of external pages so they don't need to be processed each time they're found
					self.pages[normalised_url] = {"skip": True}

		sounds = soup.find_all("audio")
		images = soup.find_all("img")

		for image in images:
			url = image.get("src")

			normalised_url = self.normalise_url(url, context)

			if normalised_url not in self.pages:
				log("Adding " + normalised_url)
				self.pages[normalised_url] = {"processed": False}

		scripts = soup.find_all("script")

		for script in scripts:
			url = script.get("src")

			# only handle script tags that have an src attribute (i.e. that are not inline)
			if url:
				normalised_url = self.normalise_url(url, context)

				if normalised_url not in self.pages:
					log("Adding " + normalised_url)
					self.pages[normalised_url] = {"processed": False}

		links = soup.find_all("link")

		for link in links:
			# only handle link tags that are for stylesheets or favicons
			if ("stylesheet" in link.get("rel")) or ("icon" in link.get("rel")):
				url = link.get("href")
				normalised_url = self.normalise_url(url, context)

				if normalised_url not in self.pages:
					log("Adding " + normalised_url)
					self.pages[normalised_url] = {"processed": False}
		
		videos = soup.find_all("video")
		embeds = soup.find_all("embed")
		objects = soup.find_all("object")

	def save(self):
		should_continue = True

		while should_continue:
			has_unprocessed_urls = False

			# look at each tracked URL
			for url, value in list(self.pages.items()):
				# if the page should be skipped
				if value.get("skip") == True:
					# skip it
					continue
				# if it hasn't been processed yet
				if value.get("processed") == False:
					has_unprocessed_urls = True
					# save it and get the HTML
					html = self.download_asset(url)
					# mark it as saved
					self.pages[url].update({"processed": True})

					# if HTML was returned
					if html:
						# find more links in the HTML
						self.find_assets(html, url)

			if has_unprocessed_urls == False:
				should_continue = False

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("No site specified")
		sys.exit()

	if len(sys.argv) > 2 and sys.argv[2] == "-v":
		log_stdout = True

	try:
		site = Site(sys.argv[1])
		site.save()
	except Exception as e:
		if log_stdout == True:
			raise e
		else:
			print("Encountered an error of type " + e.__class__.__name__ + ": " + str(e))
		sys.exit()
