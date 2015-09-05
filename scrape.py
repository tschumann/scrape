import bs4
import requests
import sys
import urlparse

home_url = None
visited_urls = []

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
