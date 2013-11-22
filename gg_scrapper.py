#!/usr/bin/python

import urllib2
from bs4 import BeautifulSoup
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)


class GooglePage:
    verb_handler = urllib2.HTTPHandler()
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        verb_handler.set_http_debuglevel(2)
    redir_handler = urllib2.HTTPRedirectHandler()
    opener = urllib2.build_opener(verb_handler, redir_handler)

    def __init__(self, URL):
        self.bs_page = self.get_first_page_BS(URL)

    @staticmethod
    def unenscape_Google_bang_URL(old_URL):
        """
        See https://developers.google.com/webmasters\
                /ajax-crawling/docs/getting-started for more information
        """
        if old_URL.find('#!') != -1:
            esc_URL = old_URL.replace('#!', '?_escaped_fragment_=')
            logging.debug('esc_URL = {}'.format(esc_URL))
            return esc_URL
        else:
            return old_URL

    @classmethod
    def do_redirect(cls, URL):
        res = cls.opener.open(URL)

        if res.getcode() == 200:
            new_URL = res.geturl()
            logging.debug('url = {}'.format(new_URL))
            return cls.unenscape_Google_bang_URL(new_URL)
        else:
            raise urllib2.HTTPError('Unknown URL: {}'.format(URL))

    def get_first_page_BS(self, URL):
        with self.opener.open(self.do_redirect(URL)) as esc_res:
            return BeautifulSoup(esc_res.read())

    def get_topics(self, BS):
        'Recursively[?] get all topic (as special objects)'
        return []
