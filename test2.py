from multiprocessing.pool import ThreadPool
from time import time as timer
from urllib.request import urlopen

urls = ["https://www.google.com",
        "https://www.apple.com",
        "https://www.microsoft.com",
        "https://www.amazon.com",
        "https://www.facebook.com"]


def fetch_url(url1):
    try:
        response = urlopen(url1)
        return url, response.read(), None
    except Exception as e:
        return url1, None, e


start = timer()
results = ThreadPool(20).imap_unordered(fetch_url, urls)
for url, html, error in results:
    if error is None:
        print("%r fetched in %ss" % (url, timer() - start))
    else:
        print("error fetching %r: %s" % (url, error))
print("Elapsed Time: %s" % (timer() - start,))
