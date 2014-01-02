#!/usr/bin/python3

import mailbox
import os.path
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
#from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)


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
        self.root = URL.replace('d/msg/', 'forum/message/raw?msg=')
        self.raw_message = ''

    def collect_message(self):
        with self.opener.open(self.root) as res:
            raw_msg = res.read()
            proc = subprocess.Popen(['/usr/bin/formail'],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True)
            result = proc.communicate(raw_msg.decode())[0]
            return result


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
        return int(re.match(r'\D+ \d+\D+\d+ \D+ (\d+) \D+$', i_str).group(1))

    def get_articles(self):
        out = []
        page = self._get_page_BS(self.root)
        for a_elem in page.find_all('a'):
            if 'href' in a_elem.attrs:
                a_href = a_elem['href']
                if re.match(r'https://groups.google.com/d/msg/',
                            a_href) is not None:
                    out.append(Article(a_href))

        return out


class Group(Page):
    def __init__(self, URL):
        super(Group, self).__init__()
        self.group_URL = URL
        self.topics = []
        match = re.match(r'https://groups.google.com/forum/#!forum/(.+)',
                         URL)
        if match is not None:
            self.name = match.group(1)

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
        return int(re.match(r'\D+ \d+ - \d+ \D+ (\d+) \D+$', i_str).group(1))

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
        self.topics = self.get_topics()
        for top in self.topics:
            arts = top.get_articles()
            top.articles = arts
            for a in arts:
                msg = a.collect_message()
                a.raw_message = msg

    def all_messages(self):
        '''Iterate over all messages in the group'''
        for top in self.topics:
            for art in top.articles:
                yield art.raw_message


class MBOX(mailbox.mbox):
    def __init__(self, filename):
        if os.path.exists(filename):
            shutil.move(filename, '{}.bak'.format(filename))
        super(MBOX, self).__init__(filename)
        self.box_name = filename

    def write_group(self, group_object):
        self.lock()
        for mbx_str in group_object.all_messages():
            self.add(mbx_str.encode())
        self.unlock()
        self.close()


def main(group_URL):
    # Collect all messages to the internal variables
    grp = Group(group_URL)
    grp.collect_group()

    import yaml
    # dump the state for debugging
    with open('group.yaml', 'w') as yf:
        yaml.dump(grp, yf)

    # Write MBOX
    mbx = MBOX("{}.mbx".format(grp.name))
    mbx.write_group(grp)

if __name__ == '__main__':
    main(sys.argv[1])
