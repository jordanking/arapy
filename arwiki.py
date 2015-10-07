#!/usr/bin/env python
# coding: utf-8

### Purpose: Tools to parse arwiki dumps

from __future__ import absolute_import
from __future__ import print_function

import re
import sys
import codecs
import xml.etree.cElementTree as etree
from .normalization import normalize

def parse_arwiki_dump(dump_in):
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
                        
                        # move each sentence to a new line (rough regex)
                        text = re.sub(ur'[.!?]$', '\n', text)
                        
                        if text:
                            outfile.write(text.encode('utf8'))

                    # keep memory free of previous branches of the xml tree
                    root.clear()

    return dump_out

def normalize_arwiki_parse(parsed_dump_file, ar_only=True, digits=True, alif=True, hamza=True, yaa=True, tashkil=True):
    """
    Normalizes a parsed wikidump and saves to a file w/ naming scheme
    returns the outfile name
    """

    dump_out = (parsed_dump_file.split('.')[0]+
               "_ar_only"+str(ar_only)+
               "_digits"+str(digits)+
               "_alif"+str(alif)+
               "_hamza"+str(hamza)+
               "_yaa"+str(yaa)+
               "_tashkil"+str(tashkil)+
               ".txt")

    with open(parsed_dump_file, 'r') as infile:
        with open(dump_out, 'w') as outfile:
            for text in infile:
                text = text.decode('utf8')

                text = normalize(text, ar_only=ar_only, digits=digits, alif=alif, hamza=hamza, yaa=yaa, tashkil=tashkil)
                
                if text:
                    outfile.write(text.encode('utf8'))

    return dump_out