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

    if normalised_url in visited_urls:
        return
    else:
        visited_urls.append(visited_urls)

    response = requests.get(url)

    # TODO: handle redirects and things that aren't errors
    if response.status_code != 200:
        print("Could not access", url)
        return

    # TODO: check mimetype here? parse HTML, download otherwise?

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

    for link in links:
        process_page(link.href)

if len(sys.argv) < 2:
    print("No site specified")
    sys.exit()

# remember the home page
home_url = urlparse.urlparse(sys.argv[1])

process_page(sys.argv[1])
