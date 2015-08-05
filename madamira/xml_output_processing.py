#!/usr/bin/env python
# coding: utf-8

### Purpose: Madamira xml output processing tools

from __future__ import absolute_import
from __future__ import print_function
from xml.etree.cElementTree import iterparse

import numpy as np
import re as re
import codecs
import arapy.normalization as norm
import csv

# TODO import arapy?

# window = 5

def save_lemmatization(xml_mada_fn, out_fn):

    # open the output file    
    outfile = codecs.open(out_fn, 'w', "utf-8")

    # madamira config prefix
    mp='{urn:edu.columbia.ccls.madamira.configuration:0.1}'

    # get an iterable
    context = iterparse(xml_mada_fn, events=("start", "end"))

    # turn it into an iterator
    context = iter(context)

    # get the root element
    event, root = context.next()

    for event, elem in context:
        
        # parse each sentence
        if event == 'end' and elem.tag == mp+'out_seg':

            # construct the sentence, then write once per sentence
            sent = ''

            # should just be one word_info per out_seg
            # parse each word in word_info
            for word in elem.find(mp+'word_info').iter(mp+'word'):

                # grab the lemma data
                lemma = word.find(mp+'svm_prediction').find(mp+'morph_feature_set').get('lemma')

                # strip all but arabic script TODO
                lemma = lemma.split('_')[0]

                # normalize the script
                lemma = norm.normalize(lemma)

                sent += lemma
                sent += ' '

            # write the sentence out (without last space)
            outfile.write(sent[:-1]+'\n')

            # don't keep the sentence in memory
            root.find(mp+'out_doc').clear()

        elif event == 'end' and elem.tag == mp+'out_doc':
            outfile.write('#ENDDOC#\n')

def save_noun_phrases(xml_mada_fn, out_fn):

    # open the output file    
    outfile = codecs.open(out_fn, 'w', "utf-8")

    # madamira config prefix
    mp='{urn:edu.columbia.ccls.madamira.configuration:0.1}'

    # get an iterable
    context = iterparse(xml_mada_fn, events=("start", "end"))

    # turn it into an iterator
    context = iter(context)

    # get the root element
    event, root = context.next()

    for event, elem in context:
        
        # parse each sentence
        if event == 'end' and elem.tag == mp+'out_seg':

            # construct the sentence, then write once per sentence
            sent = ''

            # should just be one segment_info per out_seg
            # parse each chunk in segment, looking for noun phrases
            for chunk in elem.find(mp+'segment_info').find(mp+'bpc').iter(mp+'chunk'):

                # identify noun phrases
                if chunk.get('type') == 'NP':

                    # we build noun phrases with underscores between words
                    noun_phrase = ''

                    # combine tokens into phrase
                    for tok in chunk.iter(mp+'tok'):
                        segment = tok.get('form0')

                        if segment[-1] == '+':
                            noun_phrase += segment[:-1]
                        elif segment[0] == '+':
                            # if it is a suffix prep, attach it to prev token
                            if len(noun_phrase) > 0:
                                noun_phrase = noun_phrase[:-1] + segment[1:]
                            else:
                                noun_phrase = segment[1:]
                        else:
                            noun_phrase += segment + '_'

                    # drop the last underscore and add to the np sentence
                    if noun_phrase[-1] == '_':
                        noun_phrase = noun_phrase[:-1]
                    sent += noun_phrase+' '

            # write the noun phrase sentence out (without last space)
            outfile.write(sent[:-1]+'\n')

            # don't keep the segment in memory
            root.find(mp+'out_doc').clear()

        elif event == 'end' and elem.tag == mp+'out_doc':
            outfile.write('#ENDDOC#\n')

def save_noun_phrase_graph(xml_mada_fn, out_fn, window = 5):
    """ TODO figure out how expensive this is, implement in scala/spark next """

    # edges (nodeid, nodeid, dist)
    edges = []

    # vertices (long hash(str) : str (noun phrase))
    vertices = {}

    # mentions list
    mentions_list = []

    # distance to add edges at
    distance = 10

    # open the output file    
    outfile = codecs.open(out_fn, 'w', "utf-8")

    # madamira config prefix
    mp='{urn:edu.columbia.ccls.madamira.configuration:0.1}'

    # get an iterable
    context = iterparse(xml_mada_fn, events=("start", "end"))

    # turn it into an iterator
    context = iter(context)

    # get the root element
    event, root = context.next()

    # document token tracking
    tokens_so_far = 0

    for event, elem in context:
        
        # parse each sentence
        if event == 'end' and elem.tag == mp+'out_seg':

            # should just be one segment_info per out_seg
            # parse each chunk in segment, looking for noun phrases
            for chunk in elem.find(mp+'segment_info').find(mp+'bpc').iter(mp+'chunk'):

                # identify noun phrases
                if chunk.get('type') == 'NP':

                    # we build noun phrases with underscores between words
                    noun_phrase = ''

                    # noun phrase starts on next token
                    noun_phrase_start = tokens_so_far + 1

                    # combine tokens into phrase
                    for tok in chunk.iter(mp+'tok'):

                        tokens_so_far += 1

                        segment = tok.get('form0')

                        # builds phrase
                        if segment[-1] == '+':
                            noun_phrase += segment[:-1]
                        elif segment[0] == '+':
                            # if it is a suffix prep, attach it to prev token
                            if len(noun_phrase) > 0:
                                noun_phrase = noun_phrase[:-1] + segment[1:]
                            else:
                                noun_phrase = segment[1:]
                        else:
                            noun_phrase += segment + '_'

                    # drop the last underscore and add to the np sentence
                    noun_phrase = noun_phrase.strip('_')

                    # noun phrase ended on last token
                    noun_phrase_end = tokens_so_far

                    np_hash = hash(noun_phrase)
                    vertices[np_hash] = noun_phrase

                    mentions_list.append([np_hash, noun_phrase_start, noun_phrase_end])

                else:
                    for tok in chunk.iter(mp+'tok'):
                        tokens_so_far += 1

            # don't keep the segment in memory
            root.find(mp+'out_doc').clear()

        elif event == 'end' and elem.tag == mp+'out_doc':
            # add edges from last document
            for start in range(0, len(mentions_list) - 10):
                end = start + 10
                head = start
                tail = start + 1
                in_range = True
                while in_range:
                    if abs(mentions_list[tail][1] - mentions_list[head][2]) <= distance:
                        if (mentions_list[tail][1]-mentions_list[head][2] > 0):
                            dist = mentions_list[tail][1]-mentions_list[head][2]
                        else:
                            dist = 0
                        
                        edges.append([mentions_list[head][0], mentions_list[tail][0], dist])
                        edges.append([mentions_list[tail][0], mentions_list[head][0], dist])

                        tail += 1

                    else:
                        in_range = False

    np.savetxt("edges.csv", np.array(edges), delimiter=",", fmt='%i')
    writer = csv.writer(open('vertices.csv','wb'))
    for key, value in vertices.items():
        writer.writerow([key, value.encode('utf-8')])                  