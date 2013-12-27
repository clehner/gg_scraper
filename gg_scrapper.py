#!/usr/bin/python

import re
import urllib2
from bs4 import BeautifulSoup
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)

TOPIC_COUNT_RE = re.compile(r'\D+ \d+ - \d+ \D+ (\d+) \D+$')


class Topic(object):
    def __init__(self, URL, name):
        self.name = name
        self.root = URL  # root of the discussion

    def __unicode__(self):
        return "%s: %s" % (self.root, self.name)


class GooglePage(object):
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
        res = self.opener.open(self.do_redirect(URL))
        in_str = res.read()
        bs = BeautifulSoup(in_str)
        res.close()
        return bs

    def get_count_topics(self, BS):
        '''Get total number of topics from the number on the page
        itself.

        Which would be awesome for control, except it is wrong on all
        pages in various and different ways. :(
        '''
        i_elem = BS.find_all('i')
        if len(i_elem) <= 0:
            raise ValueError('Cannot find count of topics!')

        i_str = i_elem[0].string
        return int(TOPIC_COUNT_RE.match(i_str).group(1))

    def get_topics(self, BS):
        '''Recursively[?] get all topic (as special objects)
        Also return (for error checking) number of topics from the head
        of the topic page.
        '''
        out = []
        other = []
        for a_elem in BS.find_all('a'):
            if 'title' in a_elem.attrs:
                # filter out all-non-topic <a>s
                logging.debug('href = %s', a_elem['href'])
                logging.debug('title = %s', a_elem['title'])
                out.append(Topic(a_elem['href'], a_elem['title']))
            else:
                logging.debug('other = %s', a_elem)
                other.append(a_elem)

        if len(other) == 1:
            new_bs = BeautifulSoup(self.opener.open(other[0]['href']).read())
            out.extend(self.get_topics(new_bs))
        elif len(other) != 0:
            raise ValueError(
                'There must be either one or none link to the next page!')

        return out
