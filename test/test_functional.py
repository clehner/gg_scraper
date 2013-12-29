# -*- coding: utf-8 -*-

import logging
import unittest
import gg_scrapper

IN_URL = 'https://groups.google.com/forum/#!forum/jbrout'
ORIG_URL = 'http://groups.google.com/d/forum/jbrout'
EXP_URL = 'https://groups.google.com/forum/' + \
    '?_escaped_fragment_=forum/jbrout'
TOPIC_URL = 'https://groups.google.com/forum/#!topic/jbrout/xNwoVmC07KI'


class TestGGScrapperFunctional(unittest.TestCase):
    def test_collecting_topics(self):
        page = gg_scrapper.Group(IN_URL)
        topics = page.get_topics()
        logging.debug("number of topics = %d", len(topics))
        self.assertGreater(len(topics), 0)

    def test_collecting_articles(self):
        logging.debug('topic = URL {}'.format(TOPIC_URL))
        topic = gg_scrapper.Topic(TOPIC_URL,
                                  'repo version incompatible with ' +
                                  'ubuntu 11.04 ?')
        articles = topic.get_articles()
        article_count = topic.get_count_articles()
        logging.debug('article_count = {0:d}'.format(article_count))
        logging.debug('articles = len {0:d}'.format(len(articles)))
        self.assertEqual(len(articles), article_count)

if __name__ == '__main__':
    unittest.main()
