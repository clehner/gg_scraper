A small script as a replacement of `the old PHP script`_ for downloading messages stored in the black hole of the Google Groups.

.. _`the old PHP script`:
    http://saturnboy.com/2010/03/scraping-google-groups/

I would never start without an inspiration from the comment_ on my previous post on the theme of locked down nature of Google Groups.

.. _comment:
    http://matej.ceplovi.cz/blog/2013/09/we-should-stop-even-pretending-google-is-trying-to-do-the-right-thing/#comment-482

Current bugs are filled at my bugzilla_ and new ones can be reported via
email (one of many of my addresses are available on my `Github page`_ )

.. _bugzilla:
    https://luther.ceplovi.cz/bugzilla/buglist.cgi?quicksearch=product%3Agg_scraper
.. _`Github page`:
    https://github.com/mcepl

Of course pull requests are more than welcome in the same places as well.  Currently all development is done with Python 3.3, but tests are run on Travis-CI for 2.7 and pypy as well.

.. image:: https://secure.travis-ci.org/mcepl/gg_scraper.png
   :alt: Build Status
