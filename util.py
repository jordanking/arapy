#!/usr/bin/env python
# coding: utf-8

### Purpose: Arabic utility tools

from __future__ import absolute_import
from __future__ import print_function

import re
import sys
import codecs
import xml.etree.cElementTree as etree
from .normalization import normalize

def parse_wiki_dump(dump_in, dump_out, norm=False):
    """
    Reads in an unzipped arwiki dump.
    Saves the text of the articles in a txt file with one sentence per line.
    Norm=True normalizes the arabic script.
    """

    # regex for arabic chars
    arabic = re.compile(ur'[^\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\.]+', re.UNICODE)

    # text tag that wiki uses to identify text content blocks
    text_tag = '{http://www.mediawiki.org/xml/export-0.10/}text'

    with open(dump_in, 'r') as infile:
        with open(dump_out, 'w') as outfile:

            # iterate through the xml tree looking for tag starts
            context = etree.iterparse(infile, events = ('start','end'))
            context = iter(context)
            event, root = context.next()

            for event, elem in context:

                # if the tag matches the wiki tag for text content, we extract the text
                if event == 'end' and elem.tag == text_tag:

                    text = elem.text
                    
                    # some text tags are empty
                    if text:

                        # remove non-arabic chars              
                        text = arabic.sub(' ', text)

                        # move each sentence to a new line
                        text = re.sub('\.', '\n', text)

                        # uses the arapy default normalization
                        if norm:
                            text = normalize(text)
                        
                        if text:
                            outfile.write(text.encode('utf8'))

                    # keep memory free of previous branches of the xml tree
                    root.clear()