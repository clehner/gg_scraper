import os
import tempfile
import yaml
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import gg_scraper
from gg_scraper import Group, Topic, Article  # noqa

IN_URL = 'https://groups.google.com/forum/#!forum/jbrout'
ORIG_URL = 'http://groups.google.com/d/forum/jbrout'
EXP_URL = 'https://groups.google.com/forum/' + \
    '?_escaped_fragment_=forum/jbrout'


class TestGGScrapper(unittest.TestCase):
    def test_URL_conversion(self):
        obs_URL = gg_scraper.Group.unenscape_Google_bang_URL(IN_URL)
        self.assertEqual(obs_URL, EXP_URL)


class TestMBOX(unittest.TestCase):
    def setUp(self):
        group_file_name = 'test/group.yaml'
        with open(group_file_name, 'r') as group_f:
            self.group = yaml.load(group_f)

    @unittest.skipIf(sys.version_info[:2] < (2, 7),
                     'Formatting on 2.6 is different')
    def test_create_mbox(self):
        '''Create a mbox file from (YAMLed) Group
        '''
        mbx_file = tempfile.NamedTemporaryFile('w', delete=False)
        mbx = gg_scraper.MBOX(mbx_file.name)
        mbx.write_group(self.group)

        with open('test/mbox.mbx') as exp_f:
            with open(mbx_file.name) as mbx_f:
                self.assertEqual(exp_f.read().strip(),
                                 mbx_f.read().strip())

        os.unlink(mbx_file.name)

    def test_generate_list_mangled_addrs(self):
        self.maxDiff = None
        with open('test/mangled_address.cnf') as exp_addr_f:
            exp_str = exp_addr_f.read()

        self.group.collect_mangled_addrs()

        with open('{0}.cnf'.format(self.group.name)) as obs_f:
            mang_addres = obs_f.read()
        self.assertEqual(exp_str, mang_addres)


class TestDemangle(unittest.TestCase):
    def test_demangle(self):
        self.maxDiff = None
        gg_scraper.demangle('test/unmangled_address.cnf',
                            'test/mbox.mbx', 'unmangled.mbx')

        with open('unmangled.mbx') as obs_mbx_f:
            with open('test/mbox_unmangled.mbx') as exp_mbx_f:
                self.assertAlmostEqual(len(obs_mbx_f.read()),
                                       len(exp_mbx_f.read()),
                                       delta=100)

if __name__ == '__main__':
    unittest.main()
