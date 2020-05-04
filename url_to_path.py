import os
import re
from urllib.parse import urlparse

def url_to_path(url):
    parsed = urlparse(url)
    path = re.sub(r'^\/|\/$', '', parsed.path)
    return os.path.join(parsed.netloc, path)
