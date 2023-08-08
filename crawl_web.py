import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import csv
import time

# create a dictionary to store crawled source links as keys and corresponding internal and external links as values
data = {}

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):
    """
    Returns all URLs that are found on `url` and belong to the same website.
    """
    # all URLs of `url`
    urls = set()
    time.sleep(1)
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's a relative link (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if 'mailto:' in href or 'tel:' in href:
            # skip email and phone links
            continue

        if href in internal_urls:
            # skip duplicate internal links within the same website
            continue

        if domain_name not in href:
            # external link
            if href not in external_urls:
                external_urls.add(href)
                data.setdefault(url, []).append(href)
            continue
        
        try:
            response = requests.get(href)
        except requests.exceptions.RequestException as e:
            error_urls.add(href)            
            data.setdefault(url, []).append(href)
            continue
        if response.status_code != 200:
            error_urls.add(href)            
            data.setdefault(url, []).append(href)
            continue
        urls.add(href)
        internal_urls.add(href)
        # add edge from current node to internal node
        data.setdefault(url, []).append(href)
    return urls

def crawl(url, max_urls=100):
    if url in visited_urls:  # skip already visited URLs
        return
    visited_urls.add(url)

    data.setdefault(url, [])

    # reset sets of internal before crawling a new web page
    internal_urls.clear()

    links = get_all_website_links(url)
    for link in links:
        if len(visited_urls) > max_urls:
            break
        crawl(link, max_urls=max_urls)

def write_data_to_csv(data, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Source Link', 'Target', 'Color'])
        rows = []
        for source_link, links in data.items():
            for link in links:
                if link in external_urls:
                    rows.append([source_link, link, 'gray'])
                elif link in error_urls:
                    rows.append([source_link, link, 'red'])
                else:
                    rows.append([source_link, link, 'green'])
        writer.writerows(rows)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Link Extractor Tool with Python")
    parser.add_argument("url", help="The URL to extract links from.")
    parser.add_argument("-m", "--max-urls", help="Number of max URLs to crawl, default is 30.", default=30, type=int)

    args = parser.parse_args()
    url = args.url
    max_urls = args.max_urls
    # Get domain name from the input URL
    domain_name = urlparse(url).netloc

    visited_urls = set()
    internal_urls = set()
    external_urls = set()
    error_urls = set()
    data = {}
    
    crawl(url, max_urls=max_urls)
    
    write_data_to_csv(data, 'database.csv')
    
    print("Data written to database.csv file.")