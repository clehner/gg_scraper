#!/usr/bin/python3

import re
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)

TOPIC_COUNT_RE = re.compile(r'\D+ \d+ - \d+ \D+ (\d+) \D+$')


class Page(object):
    verb_handler = urllib.request.HTTPHandler()
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        verb_handler.set_http_debuglevel(2)
    redir_handler = urllib.request.HTTPRedirectHandler()
    opener = urllib.request.build_opener(verb_handler, redir_handler)

    def __init__(self):
        pass

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
            raise urllib.error.HTTPError('Unknown URL: {}'.format(URL))

    def _get_page_BS(self, URL):
        res = self.opener.open(self.do_redirect(URL))
        in_str = res.read()
        bs = BeautifulSoup(in_str)
        res.close()
        return bs


class Article(Page):
    def __init__(self):
        super(Article, self).__init__()


class Topic(Page):
    def __init__(self, URL, name):
        super(Topic, self).__init__()
        self.name = name
        self.root = URL

    def __unicode__(self):
        return "%s: %s" % (self.root, self.name)

    def get_articles(self):
        page = self._get_page_BS(self.root)
        page = page


class Group(Page):
    def __init__(self, URL):
        super(Group, self).__init__()
        self.group_URL = URL

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

    def get_topics(self):
        '''Recursively[?] get all topic (as special objects)
        Also return (for error checking) number of topics from the head
        of the topic page.
        '''
        out = []
        other = []
        BS = self._get_page_BS(self.group_URL)
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
            new_bs = Group(other[0]['href'])
            out.extend(new_bs.get_topics())
        elif len(other) != 0:
            raise ValueError(
                'There must be either one or none link to the next page!')

        return out
