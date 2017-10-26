def _parse_mako(html):
    '''gets html from mako and parses the needed text'''
    try:
        soup = BeautifulSoup(html, "html.parser")
    except:
        return None, None, None

    # Extract title
    try:
        title = [p.get_text() for p in soup.find_all("h1", text=True)][0]
    except:
        title = ''

    # Extract subtitle
    try:
        subtitle = [p.get_text() for p in soup.find_all("h2", text=True)][0]
    except:
        subtitle = ''

    # Extract paragraphs
    try:
        paragraphs = [p.get_text() for p in soup.find_all("p", text=True)]
    except:
        paragraphs = []

    return title, subtitle, paragraphs


def _parse_ynet(html):
    '''gets html from ynet and parses the needed text'''

    # Extract title
    try:
        title = re.findall(r'\"headline\": \"(.*)\"', html)[0]
    except:
        title = ''

    # Extract subtitle
    try:
        subtitle = re.findall(r'\"description\": \"(.*)\"', html)[0]
    except:
        subtitle = ''

    # Extract paragraphs
    try:
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p", text=True)]
    except:
        paragraphs = []

    return title, subtitle, paragraphs


def _parse_walla(html):
    '''gets html from walla and parses the needed text'''
    try:
        soup = BeautifulSoup(html, "html.parser")
    except:
        return None, None, None

    # Extract title
    try:
        title = [p.get_text() for p in soup.find_all("h1", text=True)][0]
    except:
        title = ''

    # Extract subtitle
    try:
        subtitle = [p.get_text() for p in soup.find_all(True, {"class": "subtitle"}, text=True)][0]
    except:
        subtitle = ''

    # Extract paragraphs
    try:
        paragraphs = [p.get_text() for p in soup.find_all("p", text=True)]
    except:
        paragraphs = []

    return title, subtitle, paragraphs


def which_domain(url):
    '''gets url and returns domain'''
    domains = ['ynet', 'walla', 'mako']
    for domain in domains:
        if domain in url:
            return domain
    return None


def parse_article(html, domain):
    '''gets html and parses it'''
    if domain is None:
        return None, None, None

    if domain == 'walla':
        parsed = _parse_walla(html)
    elif domain == 'ynet':
        parsed = _parse_ynet((html))
    elif domain == 'mako':
        parsed = _parse_mako(html)
    else:
        return None, None, None
    return parsed