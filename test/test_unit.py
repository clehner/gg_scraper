import pickle
import unittest
import gg_scrapper

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
        group_file_name = 'test/group.pickle'
        with open(group_file_name, 'r', encoding='utf8') as group_f:
            group = pickle.load(group_f)

        mbx = gg_scrapper.MBOX()
        mbx.format_mbox(group)

        with open('test/generated_mbox.mbx') as exp_f:
            self.assertEqual(exp_f.read(), mbx.mbox_string)

if __name__ == '__main__':
    unittest.main()
