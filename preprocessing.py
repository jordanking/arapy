#!/usr/bin/env python
# coding: utf-8

### Purpose: Arabic script normalization tools

from __future__ import absolute_import
from __future__ import print_function

import re
import sys
import codecs
import xml.etree.cElementTree as etree
from .normalization import normalize

def parse_wiki_dump(dump_in, dump_out, norm=False):
    """
    
    """   
    arabic = re.compile(ur'[^\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\.]+', re.UNICODE)

    with open(dump_in, 'r') as infile:
        with open(dump_out, 'w') as outfile:

            context = etree.iterparse(infile, events = ('start','end'))
            context = iter(context)
            event, root = context.next()

            for event, elem in context:

                if event == 'end' and elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text':

                    text = elem.text
                    
                    if text:              
                        text = arabic.sub(' ', text)
                        text = re.sub('\.', '\n', text)

                        if norm:
                            text = normalize(text)
                        
                        if text:
                            outfile.write(text.encode('utf8'))

                    root.clear()

