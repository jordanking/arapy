#!/usr/bin/env python
# coding: utf-8

### Purpose: Madamira raw output processing tools

from __future__ import absolute_import
from __future__ import print_function

import re as re
import numpy as np
import csv as csv
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

def save_noun_phrase_graph(raw_bpcbio_fn, out_fn, window = 5):
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

    