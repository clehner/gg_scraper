# -*- coding: utf-8 -*-

import logging
import io
import os.path
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import gg_scraper

IN_URL = 'https://groups.google.com/forum/#!forum/jbrout'
ORIG_URL = 'http://groups.google.com/d/forum/jbrout'
EXP_URL = 'https://groups.google.com/forum/' + \
    '?_escaped_fragment_=forum/jbrout'
TOPIC_URL = 'https://groups.google.com/forum/#!topic/jbrout/xNwoVmC07KI'
ARTICLE_URL = 'https://groups.google.com/d/msg/jbrout' + \
    '/xNwoVmC07KI/OfpRHFscUkwJ'


def msg_wo_From(inmsg):
    return '\n'.join(inmsg.replace('\r\n', '\n').split('\n')[1:])


class TestGGScrapperFunctional(unittest.TestCase):
    def setUp(self):
        self.dired = lambda x: os.path.join(os.path.dirname(__file__), x)

    def test_collecting_topics(self):
        page = gg_scraper.Group(IN_URL)
        topics = page.get_topics()
        logging.debug("number of topics = %d", len(topics))
        self.assertGreater(len(topics), 0)

    def test_collecting_articles(self):
        logging.debug('topic = URL {0}'.format(TOPIC_URL))
        topic = gg_scraper.Topic(TOPIC_URL,
                                 'repo version incompatible with ' +
                                 'ubuntu 11.04 ?')
        articles = topic.get_articles()
        article_count = topic.get_count_articles()
        logging.debug('article_count = {0:d}'.format(article_count))
        logging.debug('articles = len {0:d}'.format(len(articles)))
        self.assertEqual(len(articles), article_count)

    def test_get_raw_article(self):
        self.maxDiff = None
        article = gg_scraper.Article(ARTICLE_URL)

        with io.open(self.dired('message.eml'), 'r',
                     encoding='utf8') as exp_f:
            self.assertEqual(msg_wo_From(article.collect_message()),
                             exp_f.read())

    def test_py26_unicode_raw_article(self):
        self.maxDiff = None
        URL = 'https://groups.google.com/forum/message/raw?' + \
            'msg=django-oscar/BbBiMWwolf0/gn-s0sFYEhkJ'
        article = msg_wo_From(gg_scraper.Article(URL).collect_message())
        with io.open(self.dired('py26_unicode.eml'), 'r',
                     encoding='utf8') as exp_f:
            self.assertEqual(article, exp_f.read())


if __name__ == '__main__':
    unittest.main()
