import inspect
import re
import os
import urllib
import urlparse

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from BeautifulSoup import BeautifulSoup
from mechanize import Browser

MAIN_URL = 'http://www.animefrost.net'
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'


class API():

    def __init__(self):
        """Constructor."""
        self.browser = Browser()
        """browser"""

        # disable robot.txt usage
        self.browser.set_handle_robots(False)
        self.browser.addheaders = [('User-agent', USER_AGENT)]

    def get_all(self, page=1):
        """Find all anime available.

        :returns: list of animes
        """
        url = 'alphabetical-image-list/page/%(page)s' % {'page': page}

        main_elem = self.get_html_tree(url)

        return self.get_animes(main_elem, page)

    def get_category(self, page=1, category=None):
        """Find all anime available from a specific category.

        :returns: list of animes
        """
        url = 'video_tag/%(category)s/page/%(page)d' % {'category': category,
                                                        'page': page}

        main_elem = self.get_html_tree(url)

        return self.get_animes(main_elem, page, category)

    def get_categories(self):
        """Find all categories available.

        :returns: list of categories
        """
        categories = []

        tags = ['Action', 'Adventure', 'Comedy', 'Demons', 'Drama',
                'Ecchi', 'Fantasy', 'Game', 'Harem', 'Historical',
                'Horror', 'Josei', 'Kids', 'Madhouse', 'Magic',
                'Martial Arts', 'Mecha', 'Military', 'Music', 'Mystery',
                'Parody', 'Police', 'Psychological', 'Romance', 'Samurai',
                'School']

        urls = ['action', 'adventure', 'comedy', 'demons', 'drama', 'ecchi',
                'fantasy', 'game', 'harem', 'historical', 'horror', 'josei',
                'kids', 'madhouse', 'magic', 'martial-arts', 'mecha',
                'military', 'music-2', 'mystery', 'parody', 'police',
                'psychological-2', 'romance', 'samurai', 'school']

        for index, tag in enumerate(tags):
            category = {'label': tag,
                        'path': urls[index]}
            categories.append(category)

        return categories

    def get_animes(self, html_elem, *args):
        animes = []
        last_page = 1

        if not html_elem:
            return animes

        # find last page index
        last_page_elem = html_elem.findAll('a', {'class': 'page-numbers'})
        if last_page_elem:
            last_page = int(last_page_elem[-1].getText())

        div_elems = html_elem.findAll('div', {'class': lambda x: x
                                                       and 'item' in x.split()})
        for div_elem in div_elems:
            a_elem = div_elem.findAll('a')[-1]
            img_elem = div_elem.find('img')

            # <scheme>://<netloc>/<path>?<query>#<fragment>
            path = urlparse.urlsplit(a_elem.get('href'))[2]
            regex = re.compile('/watch/(?P<anime>.*)/')

            anime = {'label': a_elem.getText(),
                     'path': re.search(regex, path).groupdict()['anime'],
                     'thumbnail': img_elem.get('src')}
            animes.append(anime)

        # always first arg of caller function
        args = list(args)
        page = args[0]

        # recursive call for other pages
        if page < last_page:
            stack = inspect.stack()
            parent_func = stack[1][3]
            # call caller function
            args[0] = page + 1
            # with original args (increment page number)
            animes.extend(getattr(self, parent_func)(*args))

        return animes

    def search(self, page=1, pattern=''):
        pattern = urllib.quote(pattern)

        url = 'page%(page)d?s=%(pattern)s' % {'pattern': pattern,
                                              'page': page}

        search = []

        search_elem = self.get_html_tree(url)

        if not search_elem:
            return search

        div_elem = search_elem.find('div', {'class': 'alert alert-info'})
        # no anime found matching search
        if div_elem:
            return search
        else:
            search = self.get_animes(search_elem, page, pattern)

        return search

    def get_anime(self, anime):
        """Display the list of episodes for the requested anime.

        :param anime: anime name

        :returns: list of episodes.
        """
        episodes = []

        url = 'watch/%(anime)s' % {'anime': anime}

        main_elem = self.get_html_tree(url)

        if not main_elem:
            return episodes

        ul_elem = main_elem.find('ul', {'class': 'pagination post-episode'})
        a_elems = ul_elem.findAll('a')
        for a_elem in a_elems:
            episode_num = a_elem.text
            episode = {'label': 'Episode %d' % int(episode_num),
                       'episode': episode_num}
            episodes.append(episode)

        return episodes

    def get_episode(self, anime, episode='1'):
        """Display the video link for the requested anime and episode.

        :param anime:   anime name
        :param episode: episode number

        :returns: video link.
        """
        url = 'watch/%(anime)s/?episode=%(episode)s' % {'anime': anime,
                                                        'episode': episode}

        video_url = ''

        main_elem = self.get_html_tree(url)

        if not main_elem:
            return video_url

        iframe_elem = main_elem.find('iframe')
        video_url = iframe_elem.get('src')

        # 2-step video url retrieval
        pattern = 'https?://(docs|drive).google.com/file/d/(?P<video_id>.*)/preview'
        regex = re.compile(pattern)
        video_id = re.search(regex, video_url)

        if video_id:
            video_id = video_id.groupdict()['video_id']

            url = 'https://drive.google.com/file/d/%(video_id)s/' % {'video_id': video_id}
            main_elem = self.get_html_tree(url)

            for script_elem in main_elem.findAll('script'):
                text = script_elem.text
                if 'fmt_stream_map' in text:
                    pattern = '\|(?P<link>https:[^|]*)\|https.*'
                    regex = re.compile(pattern)
                    video_url = re.findall(regex, text)[0]

                    # Some coding/decode stuff
                    video_url = video_url.decode('unicode_escape')
                    video_url = video_url.encode('utf-8')
                    break

        return video_url

    def get_featured(self):
        """Find all featured anime available."""
        animes = []

        main_elem = self.get_html_tree()

        if not main_elem:
            return animes

        feature_elem = main_elem.find('div', {'class': 'featured-wrapper'})
        item_elems = feature_elem.findAll('div', {'class': 'item-img'})
        for item_elem in item_elems:
            a_elem = item_elem.find('a')
            img_elem = a_elem.find('img')

            path = urlparse.urlsplit(a_elem.get('href'))[2]
            regex = re.compile('/watch/(?P<anime>.*)/')

            anime = {'label': a_elem.get('title'),
                     'path': re.search(regex, path).groupdict()['anime'],
                     'thumbnail': img_elem.get('src')}
            animes.append(anime)

        return animes

    def get_html_tree(self, endpoint=''):
        """Return HTML tree as url is browsed.

        :param endpoint: URL endpoint to browse

        :returns: an HTML tree
        """
        html = ""
        try:
            url = urllib.basejoin(MAIN_URL, endpoint)
            self.browser.open(url)
            # retrieve page content
            html = self.browser.response().read()
        except Exception, e:
            pass
        else:
            # soup-it
            html_tree = BeautifulSoup(
                html, convertEntities=BeautifulSoup.HTML_ENTITIES)
            return html_tree


if __name__ == '__main__':
    # Rock'n'Roll
    api = API()
