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
OSCAR_URL = 'https://groups.google.com/forum/#!forum/django-oscar'
ARTICLE_URL = 'https://groups.google.com/d/msg/jbrout' + \
    '/xNwoVmC07KI/OfpRHFscUkwJ'


class TestGGScrapperFunctional(unittest.TestCase):
    @staticmethod
    def msg_wo_From(inmsg):
        if gg_scraper.py3k and isinstance(inmsg, bytes):
            inmsg = inmsg.decode()
        out = inmsg.replace('\r\n', '\n').split('\n')[1:]
        return '\n'.join(out)

    @staticmethod
    def dired(x):
        return os.path.join(os.path.dirname(__file__), x)

    def test_collecting_topics(self):
        page = gg_scraper.Group(IN_URL)
        topics = page.get_topics()
        self.assertGreater(len(topics), 0)

    def test_collecting_oscar_topics(self):
        page = gg_scraper.Group(OSCAR_URL)
        topics = page.get_topics()
        self.assertGreater(len(topics), 0)

    def test_collecting_articles(self):
        logging.debug('topic = URL {0}'.format(TOPIC_URL))
        topic = gg_scraper.Topic(TOPIC_URL,
                                 'repo version incompatible with ' +
                                 'ubuntu 11.04 ?')
        articles = topic.get_articles()
        article_count = topic.get_count_articles()
        self.assertEqual(len(articles), article_count)

    def test_get_raw_article(self):
        self.maxDiff = None
        article = gg_scraper.Article(ARTICLE_URL)

        with io.open(self.dired('message.eml'), 'r',
                     encoding='utf8') as exp_f:
            self.assertEqual(self.msg_wo_From(article.collect_message()),
                             exp_f.read())

    def test_py26_unicode_raw_article(self):
        self.maxDiff = None
        URL = 'https://groups.google.com/forum/message/raw?' + \
            'msg=django-oscar/BbBiMWwolf0/gn-s0sFYEhkJ'
        article = self.msg_wo_From(gg_scraper.Article(URL).collect_message())
        with io.open(self.dired('py26_unicode.eml'), 'r',
                     encoding='utf8') as exp_f:
            expected = exp_f.read()
            self.assertEqual(article, expected)


if __name__ == '__main__':
    unittest.main()
