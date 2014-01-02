import os
import tempfile
import yaml
import unittest
import gg_scrapper
from gg_scrapper import Group, Topic, Article  # noqa

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


class TestMBOX(unittest.TestCase):
    def test_create_mbox(self):
        '''Create a mbox file from (pickled) Group
        '''
        group_file_name = 'test/group.yaml'
        with open(group_file_name, 'r') as group_f:
            group = yaml.load(group_f)

        mbx_file = tempfile.NamedTemporaryFile('w', delete=False)
        mbx = gg_scrapper.MBOX(mbx_file.name)
        mbx.write_group(group)

        with open('test/mbox.mbx') as exp_f:
            with open(mbx_file.name) as mbx_f:
                self.assertEqual(exp_f.read(), mbx_f.read())

        os.unlink(mbx_file.name)

if __name__ == '__main__':
    unittest.main()
