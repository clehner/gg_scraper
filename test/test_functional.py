# -*- coding: utf-8 -*-

import logging
import os.path
import unittest
import gg_scrapper

IN_URL = 'https://groups.google.com/forum/#!forum/jbrout'
ORIG_URL = 'http://groups.google.com/d/forum/jbrout'
EXP_URL = 'https://groups.google.com/forum/' + \
    '?_escaped_fragment_=forum/jbrout'
TOPIC_URL = 'https://groups.google.com/forum/#!topic/jbrout/xNwoVmC07KI'
ARTICLE_URL = 'https://groups.google.com/d/msg/jbrout' + \
    '/xNwoVmC07KI/OfpRHFscUkwJ'


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

    def test_get_raw_article(self):
        self.maxDiff = None
        article = gg_scrapper.Article(ARTICLE_URL)

        rfc_msg = article.collect_message().replace('\r\n', '\n')
        rfc_msg = '\n'.join(rfc_msg.split('\n')[1:])

        exp_file_name = os.path.join(os.path.dirname(__file__), 'message.eml')
        with open(exp_file_name, 'r', encoding='utf8') as exp_f:
            self.assertEqual(rfc_msg, exp_f.read())


if __name__ == '__main__':
    unittest.main()
