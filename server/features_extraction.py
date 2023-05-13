import re
import time
import bs4
#import whois
import urllib
import socket
import ipaddress
from datetime import datetime
from bs4 import BeautifulSoup
from googlesearch import search
from urllib.request import Request, urlopen

from patterns import ipv4_pattern, ipv6_pattern, shortening_services, http_https


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
    """Checks whether a given URL has an IP address in it or not. 
    If the URL has an IP address, the function removes the IP address portion from the URL. 
    Then, it counts the number of dots in the remaining URL. If the number of dots is less than or equal to 3,
    it returns 1, indicating that the URL is a domain name. If the number of dots is 4, 
    it returns 0, indicating that the URL is an IP address. 
    If the number of dots is greater than 4, it returns -1, indicating that the URL is not valid. """

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
    """Returns 1 if the head contains an href of the same domain or the href with single dot,
    else -1 """
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


def request_url(wiki, soup, domain):
    i = 0
    success = 0
    for img in soup.find_all('img', src=True):
        dots = [x.start() for x in re.finditer(r'\.', img['src'])]
        if wiki in img['src'] or domain in img['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    for audio in soup.find_all('audio', src=True):
        dots = [x.start() for x in re.finditer(r'\.', audio['src'])]
        if wiki in audio['src'] or domain in audio['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    for embed in soup.find_all('embed', src=True):
        dots = [x.start() for x in re.finditer(r'\.', embed['src'])]
        if wiki in embed['src'] or domain in embed['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    for i_frame in soup.find_all('i_frame', src=True):
        dots = [x.start() for x in re.finditer(r'\.', i_frame['src'])]
        if wiki in i_frame['src'] or domain in i_frame['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    try:
        percentage = success / float(i) * 100
    except:
        return -1

    if percentage < 22.0:
        return -1
    elif 22.0 <= percentage < 61.0:
        return 0
    else:
        return 1


def url_of_anchor(wiki, soup, domain):
    i = 0
    unsafe = 0
    for a in soup.find_all('a', href=True):
        # 2nd condition was 'JavaScript ::void(0)' but we put JavaScript because the space between javascript and ::
        # might not be
        # there in the actual a['href']
        if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (
                wiki in a['href'] or domain in a['href']):
            unsafe = unsafe + 1
        i = i + 1
        # print a['href']
    try:
        percentage = unsafe / float(i) * 100
    except:
        return 1
    if percentage < 31.0:
        return 1
        # return percentage
    elif 31.0 <= percentage < 67.0:
        return 0
    else:
        return -1


# Links in <Script> and <Link> tags
def links_in_tags(wiki, soup, domain):
    i = 0
    success = 0
    for link in soup.find_all('link', href=True):
        dots = [x.start() for x in re.finditer(r'\.', link['href'])]
        if wiki in link['href'] or domain in link['href'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    for script in soup.find_all('script', src=True):
        dots = [x.start() for x in re.finditer(r'\.', script['src'])]
        if wiki in script['src'] or domain in script['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1
    try:
        percentage = success / float(i) * 100
    except:
        return -1

    if percentage < 17.0:
        return -1
    elif 17.0 <= percentage < 81.0:
        return 0
    else:
        return 1


# Server Form Handler (SFH)
# Have written conditions directly from word file..as there are no sites to test ######
def sfh(wiki, soup, domain):
    for form in soup.find_all('form', action=True):
        if form['action'] == "" or form['action'] == "about:blank":
            return -1
        elif wiki not in form['action'] and domain not in form['action']:
            return 0
        else:
            return 1
    return 1


# Mail Function
# PHP mail() function is difficult to retrieve, hence the following function is based on mailto
def submitting_to_email(soup):
    for form in soup.find_all('form', action=True):
        return -1 if "mailto:" in form['action'] else 1
    # In case there is no form in the soup, then it is safe to return 1.
    return 1


def abnormal_url(domain, url):
    hostname = domain.name
    match = re.search(hostname, url)
    return 1 if match else -1


# IFrame Redirection
def i_frame(soup):
    for i_frame in soup.find_all('i_frame', width=True, height=True, frameBorder=True):
        # Even if one iFrame satisfies the below conditions, it is safe to return -1 for this method.
        if i_frame['width'] == "0" and i_frame['height'] == "0" and i_frame['frameBorder'] == "0":
            return -1
        if i_frame['width'] == "0" or i_frame['height'] == "0" or i_frame['frameBorder'] == "0":
            return 0
    # If none of the iframes have a width or height of zero or a frameBorder of size 0, then it is safe to return 1.
    return 1


def age_of_domain(domain):
    creation_date = domain.creation_date
    expiration_date = domain.expiration_date
    ageofdomain = 0
    if expiration_date:
        ageofdomain = abs((expiration_date - creation_date).days)
    return -1 if ageofdomain / 30 < 6 else 1


def web_traffic(url):
    try:
        rank = \
            bs4.BeautifulSoup(urllib.request("http://data.alexa.com/data?cli=10&dat=s&url=" + url).read(), "xml").find(
                "REACH")['RANK']
    except TypeError:
        return -1
    rank = int(rank)
    return 1 if rank < 100000 else 0


def google_index(url):
    site = search(url, 5)
    return 1 if site else -1


def statistical_report(url, hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        return -1
    url_match = re.search(
        r'at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweddy\.com|myjino\.ru|96\.lt|ow\.ly', url)
    ip_match = re.search(
        '146\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|'
        '107\.151\.148\.44|107\.151\.148\.107|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|52\.69\.166\.231|216\.58\.192\.225|'
        '118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
        '216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|'
        '34\.196\.13\.28|103\.224\.212\.222|172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|'
        '216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42',
        ip_address)
    if url_match:
        return -1
    elif ip_match:
        return -1
    else:
        return 1


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
    req = Request(url,
                  headers={'User-Agent': 'Mozilla/5.0'})

    html_page = urlopen(req).read()
    soup = BeautifulSoup(html_page, 'html.parser')

    hostname = get_hostname_from_url(url)
    dns = 1
    try:
        domain = whois.query(hostname)
        print('Domain from whois', domain)
    except Exception as e:
        # print("An error occurred while checking domain using whois", type(e).__name__)
        dns = -1

    phishigFeatures = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -
                       -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,]

    features = [
        ('Having IP address', having_ip_address(url)),
        ('URL Length', url_length(url)),
        ('URL Shortening service', shortening_service(url)),
        ('Having @ symbol', having_at_symbol(url)),
        ('Having double slash', double_slash_redirecting(url)),
        ('Having dash symbol(Prefix Suffix)', prefix_suffix(hostname)),
        ('Having multiple subdomains', having_sub_domain(url)),
        # ('SSL Final State', -1 if dns == -1 else ssl_final_state(url)),
        # ('SSL Final State', -1 if dns == -1 else 1),
        ('Domain Registration Length', -1 if dns == - \
         1 else domain_registration_length(domain)),
        ('Favicon', favicon(url, soup, hostname)),
        ('HTTP or HTTPS token in domain name', https_token(url)),
        ('Request URL', request_url(url, soup, hostname)),
        ('URL of Anchor', url_of_anchor(url, soup, hostname)),
        ('Links in tags', links_in_tags(url, soup, hostname)),
        ('SFH', sfh(url, soup, hostname)),
        ('Submitting to email', submitting_to_email(soup)),
        ('Abnormal URL', -1 if dns == -1 else abnormal_url(domain, url)),
        ('IFrame', i_frame(soup)),
        ('Age of Domain', -1 if dns == -1 else age_of_domain(domain)),
        ('DNS Record', dns),
        ('Web Traffic', web_traffic(soup)),
        ('Google Index', google_index(url)),
        ('Statistical Reports', statistical_report(url, hostname))
    ]

    output = '\n'.join(
        [f"{i+1}. {feature[0]} - {feature[1]}" for i, feature in enumerate(features)])
    print(output)

    return [feature[1] for feature in features]
