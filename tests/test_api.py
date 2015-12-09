import random
import unittest
import urlparse

from mechanize import Browser, HTTPError

import animefrost

MAIN_URL = 'http://www.animefrost.net'
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'

class AnimeFrostTestCase(unittest.TestCase):

    """Test case for Anime Frost api."""

    def setUp(self):
        self.api = animefrost.API()

    def test_instance(self):
        """Tests API instance type."""
        self.assertTrue(isinstance(self.api, animefrost.API))

    def test_browser(self):
        """Tests API's browser."""
        browser = self.api.browser

        self.assertTrue(isinstance(browser, Browser))
        for header in browser.addheaders:
            if header[0] != 'User-agent':
                continue
            print(header)
            self.assertEqual(header[1], USER_AGENT)

        url = MAIN_URL + '/no_such_url'
        self.assertRaises(HTTPError, browser.open, url)

    def test_all(self):
        """Tests all animes list."""
        all_animes = self.api.get_all(7)
        self.assertTrue(all_animes)

        no_animes = self.api.get_all(99)
        self.assertFalse(no_animes)

    def test_categories(self):
        """Tests category list."""
        categories = self.api.get_categories()

        self.assertIn('Martial Arts', [category['label'] for category in categories])

        for category in categories:
            self.assertNotIn('no_such_category', category['label'])

    def test_category(self):
        """Tests anime list."""
        categories = ['action', 'adventure', 'comedy', 'demons', 'drama', 'ecchi',
                      'fantasy', 'game', 'harem', 'historical', 'horror', 'josei',
                      'kids', 'madhouse', 'magic', 'martial-arts', 'mecha',
                      'military', 'music-2', 'mystery', 'parody', 'police',
                      'psychological-2', 'romance', 'samurai', 'school']

        category = random.choice(categories)

        animes = self.api.get_category(category=category)
        self.assertTrue(animes)

        animes = self.api.get_category(page=99, category=category)
        self.assertFalse(animes)

        animes = self.api.get_category(category='not_a_category')
        self.assertFalse(animes)

    def test_animes(self):
        pass

    def test_anime(self):
        """Tests episodes list."""
        animes = ['manyuu-hikenchou', 'bleach']

        anime = random.choice(animes)

        episodes = self.api.get_anime(anime)
        self.assertTrue(episodes)

        episodes = self.api.get_anime(anime='not_an_anime')
        self.assertFalse(episodes)

    def test_episode(self):
        """Tests video url."""
        anime = 'bleach'
        episodes = range(1, 367)

        episode = random.choice(episodes)

        video_url = self.api.get_episode(anime, str(episode))
        self.assertTrue(video_url)

        video_url = self.api.get_episode(anime='not_an_anime', episode=str(episode))
        self.assertFalse(video_url)

        video_url = self.api.get_episode(anime)
        query = urlparse.urlparse(video_url).query
        query_attrs = urlparse.parse_qs(query)
        query_attrs.pop('signature')

        another_video_url = self.api.get_episode(anime, episode='999')
        another_query = urlparse.urlparse(video_url).query
        another_query_attrs = urlparse.parse_qs(another_query)
        another_query_attrs.pop('signature')

        self.assertEqual(query_attrs, another_query_attrs)

    def test_search(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    #Rock'n'Roll
    unittest.main()
