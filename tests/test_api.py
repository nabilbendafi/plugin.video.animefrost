import unittest

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
        """Tests all categories list."""
        categories = self.api.get_categories()

        self.assertIn('Martial Arts', [category['label'] for category in categories])

        for category in categories:
            self.assertNotIn('no_such_category', category['label'])

    def test_category(self):
        pass

    def test_animes(self):
        pass

    def test_anime(self):
        pass

    def test_episode(self):
        pass

    def test_search(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    #Rock'n'Roll
    unittest.main()
