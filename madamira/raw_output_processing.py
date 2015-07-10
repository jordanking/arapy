#!/usr/bin/env python
# coding: utf-8

### Purpose: Madamira raw output processing tools

from __future__ import absolute_import
from __future__ import print_function

import re as re
import codecs
import arapy.normalization as norm


def save_lemmatization(raw_mada_fn, out_fn):
    mada = codecs.open(mada_fn, 'r', "utf-8")

    p = re.compile(ur'lex:[^\s_]+', re.UNICODE)
    start_of_line = True

    with codecs.open(out_fn, 'w', 'utf-8') as outfile:
        for line in mada:

            if line == 'SENTENCE BREAK\n':
                outfile.write('\n')
                start_of_line = True
            elif line.startswith('*'):
                m = p.findall(line)
                if m:
                    print(m)
                    if not start_of_line:
                        outfile.write(' ')
                    outfile.write(norm.normalize(m[0][4:]))
                    start_of_line = False