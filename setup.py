# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from distutils.core import setup, Command
import unittest

import gg_scrapper


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
        runner.run(tests)


classifiers = [
    'Development Status :: 3 - Alpha',
    'Operating System :: OS Independent',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Programming Language :: Python :: 3',
    'Topic :: Communications :: Email',
    'Topic :: Communications :: Conferencing']


def get_long_description():
    lines = open('README.rst').read().splitlines(False)
    return '\n' + '\n'.join(lines) + '\n'

setup(name='gg_scrapper',
      version=gg_scrapper.__version__,
      description='Download a Google Group to MBOX',
      long_description=get_long_description(),
      author='Matěj Cepl',
      author_email='mcepl@cepl.eu',
      url='http://luther.ceplovi.cz/git/gg_scrapper.git',
      scripts=['gg_scrapper.py'],
      keywords=['email', 'Google Groups', 'scrap', 'backup'],
      license='GNU GPL',
      classifiers=classifiers,
      cmdclass={
          'test': RunTests,
      },
      requires=['beautifulsoup4', 'PyYAML'])
