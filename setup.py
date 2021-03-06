# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys
from distutils.core import setup, Command
import io
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import gg_scraper


class RunTests(Command):
    """New setup.py command to run all tests for the package.
    """
    description = "run all tests for the package"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        tests = unittest.TestLoader().discover('test')
        runner = unittest.TextTestRunner(verbosity=2)
        res = runner.run(tests)
        sys.exit(int(not res.wasSuccessful()))


classifiers = [
    'Development Status :: 3 - Alpha',
    'Operating System :: OS Independent',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Communications :: Email',
    'Topic :: Communications :: Conferencing']


def get_long_description():
    lines = io.open('README.rst', encoding='utf8').read().splitlines(False)
    return '\n' + '\n'.join(lines) + '\n'

setup(name='gg_scraper',
      version=gg_scraper.__version__,
      description='Download a Google Group to MBOX',
      long_description=get_long_description(),
      author='Matěj Cepl',
      author_email='mcepl@cepl.eu',
      url='http://luther.ceplovi.cz/git/gg_scraper.git',
      scripts=['gg_scraper.py'],
      keywords=['email', 'Google Groups', 'scrap', 'backup'],
      license='GNU GPL',
      classifiers=classifiers,
      cmdclass={
          'test': RunTests,
      },
      requires=['beautifulsoup4', 'PyYAML'])
