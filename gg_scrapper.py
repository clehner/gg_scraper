#!/usr/bin/python3

import mailbox
import re
import subprocess
import urllib.request
import urllib.error
import urllib.parse
#from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)

TOPIC_COUNT_RE = re.compile(r'\D+ \d+ - \d+ \D+ (\d+) \D+$')
ARTICL_MSG_URL_RE = re.compile(r'https://groups.google.com/d/msg/')
ARTICLE_COUNT_RE = re.compile(r'\D+ \d+\D+\d+ \D+ (\d+) \D+$')


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
    def __init__(self, URL):
        super(Article, self).__init__()
        self.root = URL.replace('#!msg/', 'message/raw?msg=')
        self.raw_message = ''

    def collect_message(self):
        with self.opener.open(self.root) as res:
            raw_msg = res.read()
            proc = subprocess.Popen(['/usr/bin/formail'],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            result = proc.communicate(raw_msg)[0]
            return result.decode()


class Topic(Page):
    def __init__(self, URL, name):
        super(Topic, self).__init__()
        self.name = name
        self.root = self.do_redirect(URL)
        self.articles = []

    def __unicode__(self):
        return "%s: %s" % (self.root, self.name)

    @staticmethod
    def get_one_article(elem):
        return elem

    def get_count_articles(self):
        '''Get total number of articles from the number on the page
        itself.
        '''
        BS = self._get_page_BS(self.root)
        i_elem = BS.find_all('i')
        if len(i_elem) <= 0:
            raise ValueError('Cannot find count of topics!')

        i_str = i_elem[0].string
        logging.debug('i_str = {}'.format(i_str))
        logging.debug('RE = {}'.format(ARTICLE_COUNT_RE.pattern))
        return int(ARTICLE_COUNT_RE.match(i_str).group(1))

    def get_articles(self):
        out = []
        page = self._get_page_BS(self.root)
        for a_elem in page.find_all('a'):
            if 'href' in a_elem.attrs:
                a_href = a_elem['href']
                if ARTICL_MSG_URL_RE.match(a_href) is not None:
                    logging.debug('a_elem = %s', a_href)
                    out.append(Article(a_href))

        return out


class Group(Page):
    def __init__(self, URL):
        super(Group, self).__init__()
        self.group_URL = URL

    @staticmethod
    def get_count_topics(BS):
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

    @staticmethod
    def get_one_topic(elem):
        if 'title' in elem.attrs:
            # filter out all-non-topic <a>s
            logging.debug('href = %s', elem['href'])
            logging.debug('title = %s', elem['title'])
            return True, Topic(elem['href'], elem['title'])
        else:
            logging.debug('other = %s', elem)
            return False, elem

    def get_topics(self):
        '''Recursively[?] get all topic (as special objects)
        Also return (for error checking) number of topics from the head
        of the topic page.
        '''
        out = []
        other = []
        BS = self._get_page_BS(self.group_URL)
        for a_elem in BS.find_all('a'):
            is_topic, res = self.get_one_topic(a_elem)
            if is_topic:
                out.append(res)
            else:
                other.append(res)

        if len(other) == 1:
            new_bs = Group(other[0]['href'])
            out.extend(new_bs.get_topics())
        elif len(other) != 0:
            raise ValueError(
                'There must be either one or none link to the next page!')

        return out

    def collect_group(self):
        topics = self.get_topics()
        for top in topics:
            arts = top.get_articles()
            top.articles = arts
            for a in arts:
                msg = a.collect_message()
                a.raw_message = msg


class MBOX(mailbox.mbox):
    def __init__(self, filename):
        super(MBOX, self).__init__()
        self.box_name = filename

    def write_group(self, group_object):
        pass


def main(group_name, group_URL):
    # Collect all messages to the internal variables
    grp = Group(group_URL)
    grp.collect_group()

    # Write MBOX
    mbx = MBOX()
    mbx.format_mbox(grp)
    mbx.save("{}.mbx".format(group_name))
