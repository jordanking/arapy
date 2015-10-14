#!/usr/bin/env python
# coding: utf-8

### Purpose: Tools to parse arwiki dumps

from __future__ import absolute_import
from __future__ import print_function

import arapy.normalization as norm
import re
import sys
import codecs
import xml.etree.cElementTree as etree

def parse_arwiki_dump(dump_in, split_at_punc=False, remove_non_arabic=False):
    """
    Reads in an unzipped arwiki dump.
    Saves the text of the articles in a txt file with one sentence per line.
    returns the name of the output file
    """
    dump_out = (dump_in.split('.')[0]+
                "_parsed"+
                ".txt")

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

                        if remove_non_arabic:
                            text = norm.normalize_charset(text)
                        
                        # move each sentence to a new line (rough regex)
                        if split_at_punc:
                            text = re.sub(ur'[.!?]$', '\n', text)
                        
                        if text:
                            outfile.write(text.encode('utf8'))

                    # keep memory free of previous branches of the xml tree
                    root.clear()

    return dump_out