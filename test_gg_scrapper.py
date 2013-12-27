# -*- coding: utf-8 -*-

import logging
import unittest
import gg_scrapper

IN_URL = 'https://groups.google.com/forum/#!forum/jbrout'
ORIG_URL = 'http://groups.google.com/d/forum/jbrout'
EXP_URL = 'https://groups.google.com/forum/' + \
    '?_escaped_fragment_=forum/jbrout'


class TestGGScrapper(unittest.TestCase):
    def test_URL_conversion(self):
        obs_URL = gg_scrapper.Group.unenscape_Google_bang_URL(IN_URL)
        self.assertEqual(obs_URL, EXP_URL)

    def test_do_redirect(self):
        obs_URL = gg_scrapper.Group.do_redirect(ORIG_URL)
        self.assertEqual(obs_URL, EXP_URL)

    def test_collecting_topics(self):
        page = gg_scrapper.Group(IN_URL)
        topics = page.get_topics()
        logging.debug("number of topics = %d", len(topics))
        self.assertGreater(len(topics), 0)

if __name__ == '__main__':
    unittest.main()
