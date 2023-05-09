import re
import time
import ipaddress
from datetime import datetime

from patterns import ipv4_pattern, ipv6_pattern, shortening_services


def having_ip_address(url):
    """ checks if the URL has an IP address in it, 
    returns -1 if the URL has an IP address, otherwise 1"""

    ip_address_pattern = ipv4_pattern + "|" + ipv6_pattern
    match = re.search(ip_address_pattern, url)
    return -1 if match else 1


def url_length(url):
    """ Returns -1 if the length of the URL is greater than 75 characters, 
    0 if it is between 54 and 75 characters, and 1 otherwise 
    """

    if len(url) < 54:
        return 1
    elif 54 <= len(url) <= 75:
        return 0
    return -1


def shortening_service(url):
    """Returns -1 if the URL is a known shortening service URL, and 1 otherwise"""

    match = re.search(shortening_services, url)
    return -1 if match else 1


def having_at_symbol(url):
    """# Returns -1 if the URL contains an @ symbol (which is not allowed in URLs), 
    and 1 otherwise"""

    match = re.search('@', url)
    return -1 if match else 1


def double_slash_redirecting(url):
    # since the position starts from 0, we have given 6 and not 7 which is according to the document.
    # It is convenient and easier to just use string search here to search the last occurrence instead of re.
    last_double_slash = url.rfind('//')
    return -1 if last_double_slash > 6 else 1


def prefix_suffix(domain):
    match = re.search('-', domain)
    return -1 if match else 1


def having_sub_domain(url):
    # Here, instead of greater than 1 we will take greater than 3 since the greater than 1 condition is when www and
    # country domain dots are skipped
    # Accordingly other dots will increase by 1
    if having_ip_address(url) == -1:
        match = re.search(
            '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
            '([01]?\\d\\d?|2[0-4]\\d|25[0-5]))|(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}',
            url)
        pos = match.end()
        url = url[pos:]
    num_dots = [x.start() for x in re.finditer(r'\.', url)]
    if len(num_dots) <= 3:
        return 1
    elif len(num_dots) == 4:
        return 0
    else:
        return -1


def domain_registration_length(domain):
    expiration_date = domain.expiration_date
    today = time.strftime('%Y-%m-%d')
    today = datetime.strptime(today, '%Y-%m-%d')

    registration_length = 0
    # Some domains do not have expiration dates. This if condition makes sure that the expiration date is used only
    # when it is present.
    if expiration_date:
        registration_length = abs((expiration_date - today).days)
    return -1 if registration_length / 365 <= 1 else 1


def favicon(wiki, soup, domain):
    for head in soup.find_all('head'):
        for head.link in soup.find_all('link', href=True):
            dots = [x.start() for x in re.finditer(r'\.', head.link['href'])]
            return 1 if wiki in head.link['href'] or len(dots) == 1 or domain in head.link['href'] else -1
    return 1


def https_token(url):
    match = re.search(http_https, url)
    if match and match.start() == 0:
        url = url[match.end():]
    match = re.search('http|https', url)
    return -1 if match else 1


def get_hostname_from_url(url):
    hostname = url
    pattern = "https://|http://|www.|https://www.|http://www."
    pre_pattern_match = re.search(pattern, hostname)

    if pre_pattern_match:
        hostname = hostname[pre_pattern_match.end():]
        post_pattern_match = re.search("/", hostname)
        if post_pattern_match:
            hostname = hostname[:post_pattern_match.start()]

    return hostname


def extractFeature(url, html):
    features = []
    hostname = get_hostname_from_url(url)

    features.append(having_ip_address(url))
    features.append(url_length(url))
    features.append(shortening_service(url))
    features.append(having_at_symbol(url))
    features.append(double_slash_redirecting(url))
    features.append(prefix_suffix(hostname))
    features.append(having_sub_domain(url))

    print(features)

    return features
