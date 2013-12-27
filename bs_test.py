#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import sys
import re

TOPIC_COUNT_RE = re.compile(r'\D+ \d+ - \d+ \D+ (\d+) \D+$')

bs = BeautifulSoup(open(sys.argv[1]))
i_str = bs.find_all('i')[0].string

print("i = %s" % i_str)
count = int(TOPIC_COUNT_RE.match(i_str).group(1))
print("match i = %d" % count)
