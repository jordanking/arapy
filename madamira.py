#!/usr/bin/env python
# coding: utf-8

### Purpose: Madamira output processing tools

from __future__ import absolute_import
from __future__ import print_function
from xml.etree.cElementTree import iterparse

import numpy as np
import re
import codecs
import arapy.normalization as norm
import csv

# window = 5

def save_lemmatization(xml_mada_fn, out_fn):
    """
    Saves a lemmatization from a madamira xml output file
    """

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
    """
    Saves noun phrases from a madamira xml output file
    """

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
    """ 
    TODO figure out how expensive this is, implement in scala/spark next
    Saves a noun phrase graph from a madamira xml output file
    """

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

def raw_save_lemmatization(raw_mada_fn, out_fn):
    """
    Saves a lemmatization from a madamira raw output file
    """
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

def raw_save_noun_phrase_graph(raw_bpcbio_fn, out_fn, window = 5):
    """
    TODO figure out how expensive this is, implement in scala/spark next
    Saves a noun phrase graph from a madamira raw output file
    """

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

    # get an iterable
    context = codecs.open(raw_bpcbio_fn, 'r', 'utf-8')

    # document token tracking
    tokens_so_far = 0

    # keep track of NP construction
    noun_phrase = ''
    noun_phrase_start = 0
    noun_phrase_end = 0

    # count sentences if not broken into docs
    sentence_idx = 1

    # count docs
    doc_count = 1

    with codecs.open('raw_edges.csv', 'a') as edge_file:
        with codecs.open(raw_bpcbio_fn, 'r', 'utf-8') as context:
            while True:
                line = context.readline()

                if not line or sentence_idx % 100 == 0:

                    sentence_idx = 1
                    print('Doc: ', doc_count, 'Vertices: ', len(vertices))
                    doc_count += 1

                    if noun_phrase != '':
                        noun_phrase = noun_phrase.strip('_')
                        noun_phrase_end = tokens_so_far - 1
                        np_hash = hash(noun_phrase)
                        vertices[np_hash] = noun_phrase
                        mentions_list.append([np_hash, noun_phrase_start, noun_phrase_end])
                        noun_phrase = ''

                    # edge_count = 0

                    # add edges from last document
                    for start in range(0, len(mentions_list) - 10):
                        # end = start + 10
                        head = start
                        tail = start + 1
                        in_range = True
                        while in_range and tail < len(mentions_list):
                            if abs(mentions_list[tail][1] - mentions_list[head][2]) <= distance:
                                if (mentions_list[tail][1]-mentions_list[head][2] > 0):
                                    dist = mentions_list[tail][1]-mentions_list[head][2]
                                else:
                                    dist = 0
                                
                                edges.append([mentions_list[head][0], mentions_list[tail][0], dist])
                                edges.append([mentions_list[tail][0], mentions_list[head][0], dist])

                                # edge_count += 2
                                tail += 1

                            else:
                                in_range = False    

                    # print('Adding: ', edge_count, ' edges.')     

                    np.savetxt(edge_file, np.array(edges), delimiter=",", fmt='%i')
                    

                    edges = []
                    mentions_list = []

                    if not line:
                        writer = csv.writer(open('raw_vertices.csv','wb'))
                        for key, value in vertices.items():
                            writer.writerow([key, value.encode('utf-8')])
                        break


                if line.strip() == "":

                    # end of sentence
                    sentence_idx += 1

                else:

                    tokens_so_far += 1

                    text, bpc_type = line.strip().split("\t")

                    if (bpc_type == 'B-NP' or bpc_type != 'I-NP') and noun_phrase != '':

                        noun_phrase = noun_phrase.strip('_')
                        noun_phrase_end = tokens_so_far - 1
                        np_hash = hash(noun_phrase)
                        vertices[np_hash] = noun_phrase
                        mentions_list.append([np_hash, noun_phrase_start, noun_phrase_end])
                        noun_phrase = ''

                    if bpc_type == 'B-NP':

                        # noun phrase starts on this token
                        noun_phrase_start = tokens_so_far

                        if text[-1] == '+':
                            noun_phrase += text[:-1]
                        elif text[0] == '+':
                                noun_phrase = text[1:]
                        else:
                            noun_phrase += text + '_'

                    elif bpc_type == 'I-NP':

                        if text[-1] == '+':
                            noun_phrase += text[:-1]
                        elif text[0] == '+':
                            # if it is a suffix prep, attach it to prev token
                            if len(noun_phrase) > 0:
                                noun_phrase = noun_phrase[:-1] + text[1:]
                            else:
                                noun_phrase = text[1:]
                        else:
                            noun_phrase += text + '_'              