#!/usr/bin/env python
# coding: utf-8

### Purpose: Madamira output processing tools

from __future__ import absolute_import
from __future__ import print_function
from xml.etree.cElementTree import iterparse

import arapy
import arapy.normalization as norm
import codecs
import csv
import numpy as np
import os
import re
import requests
import socket
import StringIO
import subprocess
import time


class Madamira:
    url="http://localhost:8223"
    headers = {'Content-Type': 'application/xml'}
    xml_prefix="""<?xml version="1.0" encoding="UTF-8"?>
    <!--
      ~ Copyright (c) 2013. The Trustees of Columbia University in the City of New York.
      ~ The copyright owner has no objection to the reproduction of this work by anyone for
      ~ non-commercial use, but otherwise reserves all rights whatsoever.  For avoidance of
      ~ doubt, this work may not be reproduced, or modified, in whole or in part, for commercial
      ~ use without the prior written consent of the copyright owner.
      -->

    <madamira_input xmlns="urn:edu.columbia.ccls.madamira.configuration:0.1">
        <madamira_configuration>
            <preprocessing sentence_ids="false" separate_punct="true" input_encoding="UTF8"/>
            <overall_vars output_encoding="UTF8" dialect="MSA" output_analyses="TOP" morph_backoff="NONE"/>
            <requested_output>
                <req_variable name="PREPROCESSED" value="true" />

                <req_variable name="STEM" value="true" />
                <req_variable name="GLOSS" value="true" />
                <req_variable name="LEMMA" value="true" />
                <req_variable name="DIAC" value="true" />

                <req_variable name="ASP" value="true" />
                <req_variable name="CAS" value="true" />
                <req_variable name="ENC0" value="true" />
                <req_variable name="ENC1" value="false" />
                <req_variable name="ENC2" value="false" />
                <req_variable name="GEN" value="true" />
                <req_variable name="MOD" value="true" />
                <req_variable name="NUM" value="true" />
                <req_variable name="PER" value="true" />
                <req_variable name="POS" value="true" />
                <req_variable name="PRC0" value="true" />
                <req_variable name="PRC1" value="true" />
                <req_variable name="PRC2" value="true" />
                <req_variable name="PRC3" value="true" />
                <req_variable name="STT" value="true" />
                <req_variable name="VOX" value="true" />

                <req_variable name="BW" value="false" />
                <req_variable name="SOURCE" value="false" />

            </requested_output>
            <tokenization>
                <scheme alias="ATB" />
                <scheme alias="ATB4MT" />
                <scheme alias="MyD3">
                    <!-- Same as D3 -->
                    <scheme_override alias="MyD3"
                                     form_delimiter="\u00B7"
                                     include_non_arabic="true"
                                     mark_no_analysis="false"
                                     token_delimiter=" "
                                     tokenize_from_BW="false">
                        <split_term_spec term="PRC3"/>
                        <split_term_spec term="PRC2"/>
                        <split_term_spec term="PART"/>
                        <split_term_spec term="PRC0"/>
                        <split_term_spec term="REST"/>
                        <split_term_spec term="ENC0"/>
                        <token_form_spec enclitic_mark="+"
                                         proclitic_mark="+"
                                         token_form_base="WORD"
                                         transliteration="UTF8">
                            <normalization type="ALEF"/>
                            <normalization type="YAA"/>
                            <normalization type="DIAC"/>
                            <normalization type="LEFTPAREN"/>
                            <normalization type="RIGHTPAREN"/>
                        </token_form_spec>
                    </scheme_override>
                </scheme>
            </tokenization>
        </madamira_configuration>

        <in_doc id="in_doc">\n"""
    xml_seg_start = """<in_seg id="in_seg">\n"""
    xml_seg_end = """\n</in_seg>\n"""
    xml_suffix = """</in_doc>

    </madamira_input>"""
    config_prefix="{urn:edu.columbia.ccls.madamira.configuration:0.1}"

    def __enter__(self):
        self.start_server()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_server()

    def start_server(self):
        cwd = os.getcwd()
        os.chdir(os.path.dirname(arapy.__file__)+"/resources/MADAMIRA-release-20140825-1.0/")

        self.pid = subprocess.Popen(['java', 
                                     '-Xmx2500m', 
                                     '-Xms2500m', 
                                     '-XX:NewRatio=3', '-jar', 
                                     'MADAMIRA-release-20140825-1.0.jar', 
                                     '-s', 
                                     '-msaonly'])

        print("Waiting for madamira to initialize.")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost',8223))
        while(result != 0):
            sock.close()
            time.sleep(1)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost',8223))

        os.chdir(cwd)

    def stop_server(self):
        self.pid.kill()

    def process(self, text):
        """ Returns madamira xml output for a string input """

        query = StringIO.StringIO()
        query.write(Madamira.xml_prefix)
        for sentence in text:
            query.write(Madamira.xml_seg_start)
            query.write(sentence)
            query.write(Madamira.xml_seg_end)
        query.write(Madamira.xml_suffix)
        query.seek(0)

        response = requests.post(Madamira.url, headers=Madamira.headers, data=query.read())

        response.encoding = "utf8"

        return MadamiraOutput(response.text)

class MadamiraOutput:
    def __init__(self, xmltext):
        self.xml = xmltext.encode("utf8")

    def docs(self):
        # madamira config prefix
        mp=Madamira.config_prefix

        # get an iterable TODO use raw string?
        # wrapper = codecs.StreamReader(StringIO.StringIO(self.xml), "utf8")
        context = iterparse(StringIO.StringIO(self.xml), events=("start", "end"))

        # turn it into an iterator
        context = iter(context)

        # get the root element
        event, root = context.next()

        for event, elem in context:
            
            # parse each doc
            if event == 'end' and elem.tag == mp+'out_doc':

                yield MadamiraDoc(elem)

                # don't keep the doc in memory
                root.clear()#find(mp+'madamira_output').clear()

class MadamiraDoc:
    def __init__(self, elem):
        self.elem = elem

    def sentences(self):
        mp = Madamira.config_prefix

        for sentence in self.elem.iter(mp+'out_seg'):

            yield MadamiraSentence(sentence)

class MadamiraSentence:
    def __init__(self, sentence):
        self.sentence = sentence

    def words(self):
        mp = Madamira.config_prefix

        for word in self.sentence.find(mp+'word_info').iter(mp+'word'):

            yield MadamiraWord(word)

    def chunks(self):
        mp = Madamira.config_prefix

        # should just be one segment_info per out_seg
        # parse each chunk in segment, looking for noun phrases
        for chunk in sentence.find(mp+'segment_info').find(mp+'bpc').iter(mp+'chunk'):
            yield MadamiraChunk(chunk)

class MadamiraWord:
    def __init__(self, word):
        self.word = word

    def lemma(self):
        mp = Madamira.config_prefix

        # grab the lemma data
        lemma = self.word.find(mp+'svm_prediction').find(mp+'morph_feature_set').get('lemma')

        # strip down to the arabic script
        if not lemma:
            return ""
        elif len(lemma) == 0:
            return ""
        else:
            norm_lemma = norm.normalize_charset(lemma).strip()
            if len(norm_lemma) == 0:
                return lemma
            else:
                return norm_lemma

    def pos(self):
        mp = Madamira.config_prefix

        return self.word.find(mp+'svm_prediction').find(mp+'morph_feature_set').get('pos')

class MadamiraChunk:
    def __init__(self, chunk):
        self.chunk = chunk

    def type(self):
        return self.get('type')

    def tokens():
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



def transform_sentence_file(sentence_file, lemmas=True, pos=False, tokens=False):
    """returns filenames of lemmas and pos files"""
    with Madamira() as m:

        # open output files
        lemma_out = None
        lemma_buff = None
        if lemmas:
            lemma_buff = StringIO.StringIO()
            lemma_file = (sentence_file.split('.')[0]+
                          "_lemmas"+
                          ".txt")
            lemma_out = open(lemma_file, 'w')

        pos_out = None
        pos_buff = None
        if pos:
            pos_buff = StringIO.StringIO()
            pos_file = (sentence_file.split('.')[0]+
                          "_pos"+
                          ".txt")
            pos_out = open(pos_file, 'w')

        token_out = None
        token_buff = None
        if tokens:
            token_buff = StringIO.StringIO()
            token_file = (sentence_file.split('.')[0]+
                          "_token"+
                          ".txt")
            token_out = open(token_file, 'w')

        # read files into a list, or buffer the sentences one at a time, of sentences
        sentence_list = sentence_file.read().splitlines()

        out = m.process(sentence_list)

        for doc in out.docs():
            for sent in doc.sentences():

                for word in sent.words():
                    if lemmas:
                        lemma_buff.write(word.lemma())
                        lemma_buff.write(" ")
                    if pos:                        
                        pos_buff.write(word.pos())
                        pos_buff.write(" ")

                for chunk in sent.chunks()
                    if tokens:   
                        # token_list = word.tokens()
                        # for token in token_list:                    
                        #     token_buff.write(token) # TODO
                        #     token_buff.write(" ")

                if lemmas:
                    lemma_buff.seek(0)
                    lemma_out.write(lemma_buff.read().rstrip())
                    lemma_buff.close()
                    lemma_buff = StringIO.StringIO()

                if pos:
                    pos_buff.seek(0)
                    pos_out.write(pos_buff.read().rstrip())
                    pos_buff.close()
                    pos_buff = StringIO.StringIO()

                if tokens:
                    token_buff.seek(0)
                    token_out.write(token_buff.read().rstrip())
                    token_buff.close()
                    token_buff = StringIO.StringIO()

        if lemmas:
            lemma_buff.close()
            lemma_out.close()
        if pos:
            pos_buff.close()
            pos_out.close()
        if tokens:
            token_buff.close()
            token_out.close()

    return [lemma_file, pos_file, token_file]

    


# def save_lemmatization(xml_mada_fn, out_fn):
#     """
#     Saves a lemmatization from a madamira xml output file
#     """

#     # open the output file    
#     outfile = codecs.open(out_fn, 'w', "utf-8")

#     # madamira config prefix
#     mp='{urn:edu.columbia.ccls.madamira.configuration:0.1}'

#     # get an iterable
#     context = iterparse(xml_mada_fn, events=("start", "end"))

#     # turn it into an iterator
#     context = iter(context)

#     # get the root element
#     event, root = context.next()

#     for event, elem in context:
        
#         # parse each sentence
#         if event == 'end' and elem.tag == mp+'out_seg':

#             # construct the sentence, then write once per sentence
#             sent = ''

#             # should just be one word_info per out_seg
#             # parse each word in word_info
#             for word in elem.find(mp+'word_info').iter(mp+'word'):

#                 # grab the lemma data
#                 lemma = word.find(mp+'svm_prediction').find(mp+'morph_feature_set').get('lemma')

#                 # strip all but arabic script TODO
#                 lemma = lemma.split('_')[0]

#                 # normalize the script
#                 lemma = norm.normalize(lemma)

#                 sent += lemma
#                 sent += ' '

#             # write the sentence out (without last space)
#             outfile.write(sent[:-1]+'\n')

#             # don't keep the sentence in memory
#             root.find(mp+'out_doc').clear()

#         elif event == 'end' and elem.tag == mp+'out_doc':
#             outfile.write('#ENDDOC#\n')

# def save_noun_phrases(xml_mada_fn, out_fn):
#     """
#     Saves noun phrases from a madamira xml output file
#     """

#     # open the output file    
#     outfile = codecs.open(out_fn, 'w', "utf-8")

#     # madamira config prefix
#     mp='{urn:edu.columbia.ccls.madamira.configuration:0.1}'

#     # get an iterable
#     context = iterparse(xml_mada_fn, events=("start", "end"))

#     # turn it into an iterator
#     context = iter(context)

#     # get the root element
#     event, root = context.next()

#     for event, elem in context:
        
#         # parse each sentence
#         if event == 'end' and elem.tag == mp+'out_seg':

#             # construct the sentence, then write once per sentence
#             sent = ''

#             # should just be one segment_info per out_seg
#             # parse each chunk in segment, looking for noun phrases
#             for chunk in elem.find(mp+'segment_info').find(mp+'bpc').iter(mp+'chunk'):

#                 # identify noun phrases
#                 if chunk.get('type') == 'NP':

#                     # we build noun phrases with underscores between words
#                     noun_phrase = ''

#                     # combine tokens into phrase
#                     for tok in chunk.iter(mp+'tok'):
#                         segment = tok.get('form0')

#                         if segment[-1] == '+':
#                             noun_phrase += segment[:-1]
#                         elif segment[0] == '+':
#                             # if it is a suffix prep, attach it to prev token
#                             if len(noun_phrase) > 0:
#                                 noun_phrase = noun_phrase[:-1] + segment[1:]
#                             else:
#                                 noun_phrase = segment[1:]
#                         else:
#                             noun_phrase += segment + '_'

#                     # drop the last underscore and add to the np sentence
#                     if noun_phrase[-1] == '_':
#                         noun_phrase = noun_phrase[:-1]
#                     sent += noun_phrase+' '

#             # write the noun phrase sentence out (without last space)
#             outfile.write(sent[:-1]+'\n')

#             # don't keep the segment in memory
#             root.find(mp+'out_doc').clear()

#         elif event == 'end' and elem.tag == mp+'out_doc':
#             outfile.write('#ENDDOC#\n')

# def save_noun_phrase_graph(xml_mada_fn, out_fn, window = 5):
#     """ 
#     TODO figure out how expensive this is, implement in scala/spark next
#     Saves a noun phrase graph from a madamira xml output file
#     """

#     # edges (nodeid, nodeid, dist)
#     edges = []

#     # vertices (long hash(str) : str (noun phrase))
#     vertices = {}

#     # mentions list
#     mentions_list = []

#     # distance to add edges at
#     distance = 10

#     # open the output file    
#     outfile = codecs.open(out_fn, 'w', "utf-8")

#     # madamira config prefix
#     mp='{urn:edu.columbia.ccls.madamira.configuration:0.1}'

#     # get an iterable
#     context = iterparse(xml_mada_fn, events=("start", "end"))

#     # turn it into an iterator
#     context = iter(context)

#     # get the root element
#     event, root = context.next()

#     # document token tracking
#     tokens_so_far = 0

#     for event, elem in context:
        
#         # parse each sentence
#         if event == 'end' and elem.tag == mp+'out_seg':

#             # should just be one segment_info per out_seg
#             # parse each chunk in segment, looking for noun phrases
#             for chunk in elem.find(mp+'segment_info').find(mp+'bpc').iter(mp+'chunk'):

#                 # identify noun phrases
#                 if chunk.get('type') == 'NP':

#                     # we build noun phrases with underscores between words
#                     noun_phrase = ''

#                     # noun phrase starts on next token
#                     noun_phrase_start = tokens_so_far + 1

#                     # combine tokens into phrase
#                     for tok in chunk.iter(mp+'tok'):

#                         tokens_so_far += 1

#                         segment = tok.get('form0')

#                         # builds phrase
#                         if segment[-1] == '+':
#                             noun_phrase += segment[:-1]
#                         elif segment[0] == '+':
#                             # if it is a suffix prep, attach it to prev token
#                             if len(noun_phrase) > 0:
#                                 noun_phrase = noun_phrase[:-1] + segment[1:]
#                             else:
#                                 noun_phrase = segment[1:]
#                         else:
#                             noun_phrase += segment + '_'

#                     # drop the last underscore and add to the np sentence
#                     noun_phrase = noun_phrase.strip('_')

#                     # noun phrase ended on last token
#                     noun_phrase_end = tokens_so_far

#                     np_hash = hash(noun_phrase)
#                     vertices[np_hash] = noun_phrase

#                     mentions_list.append([np_hash, noun_phrase_start, noun_phrase_end])

#                 else:
#                     for tok in chunk.iter(mp+'tok'):
#                         tokens_so_far += 1

#             # don't keep the segment in memory
#             root.find(mp+'out_doc').clear()

#         elif event == 'end' and elem.tag == mp+'out_doc':
#             # add edges from last document
#             for start in range(0, len(mentions_list) - 10):
#                 end = start + 10
#                 head = start
#                 tail = start + 1
#                 in_range = True
#                 while in_range:
#                     if abs(mentions_list[tail][1] - mentions_list[head][2]) <= distance:
#                         if (mentions_list[tail][1]-mentions_list[head][2] > 0):
#                             dist = mentions_list[tail][1]-mentions_list[head][2]
#                         else:
#                             dist = 0
                        
#                         edges.append([mentions_list[head][0], mentions_list[tail][0], dist])
#                         edges.append([mentions_list[tail][0], mentions_list[head][0], dist])

#                         tail += 1

#                     else:
#                         in_range = False

#     np.savetxt("edges.csv", np.array(edges), delimiter=",", fmt='%i')
#     writer = csv.writer(open('vertices.csv','wb'))
#     for key, value in vertices.items():
#         writer.writerow([key, value.encode('utf-8')])    

# def raw_save_lemmatization(raw_mada_fn, out_fn):
#     """
#     Saves a lemmatization from a madamira raw output file
#     """
#     mada = codecs.open(mada_fn, 'r', "utf-8")

#     p = re.compile(ur'lex:[^\s_]+', re.UNICODE)
#     start_of_line = True

#     with codecs.open(out_fn, 'w', 'utf-8') as outfile:
#         for line in mada:

#             if line == 'SENTENCE BREAK\n':
#                 outfile.write('\n')
#                 start_of_line = True
#             elif line.startswith('*'):
#                 m = p.findall(line)
#                 if m:
#                     print(m)
#                     if not start_of_line:
#                         outfile.write(' ')
#                     outfile.write(norm.normalize(m[0][4:]))
#                     start_of_line = False

# def raw_save_noun_phrase_graph(raw_bpcbio_fn, out_fn, window = 5):
#     """
#     TODO figure out how expensive this is, implement in scala/spark next
#     Saves a noun phrase graph from a madamira raw output file
#     """

#     # edges (nodeid, nodeid, dist)
#     edges = []

#     # vertices (long hash(str) : str (noun phrase))
#     vertices = {}

#     # mentions list
#     mentions_list = []

#     # distance to add edges at
#     distance = 10

#     # open the output file    
#     outfile = codecs.open(out_fn, 'w', "utf-8")

#     # get an iterable
#     context = codecs.open(raw_bpcbio_fn, 'r', 'utf-8')

#     # document token tracking
#     tokens_so_far = 0

#     # keep track of NP construction
#     noun_phrase = ''
#     noun_phrase_start = 0
#     noun_phrase_end = 0

#     # count sentences if not broken into docs
#     sentence_idx = 1

#     # count docs
#     doc_count = 1

#     with codecs.open('raw_edges.csv', 'a') as edge_file:
#         with codecs.open(raw_bpcbio_fn, 'r', 'utf-8') as context:
#             while True:
#                 line = context.readline()

#                 if not line or sentence_idx % 100 == 0:

#                     sentence_idx = 1
#                     print('Doc: ', doc_count, 'Vertices: ', len(vertices))
#                     doc_count += 1

#                     if noun_phrase != '':
#                         noun_phrase = noun_phrase.strip('_')
#                         noun_phrase_end = tokens_so_far - 1
#                         np_hash = hash(noun_phrase)
#                         vertices[np_hash] = noun_phrase
#                         mentions_list.append([np_hash, noun_phrase_start, noun_phrase_end])
#                         noun_phrase = ''

#                     # edge_count = 0

#                     # add edges from last document
#                     for start in range(0, len(mentions_list) - 10):
#                         # end = start + 10
#                         head = start
#                         tail = start + 1
#                         in_range = True
#                         while in_range and tail < len(mentions_list):
#                             if abs(mentions_list[tail][1] - mentions_list[head][2]) <= distance:
#                                 if (mentions_list[tail][1]-mentions_list[head][2] > 0):
#                                     dist = mentions_list[tail][1]-mentions_list[head][2]
#                                 else:
#                                     dist = 0
                                
#                                 edges.append([mentions_list[head][0], mentions_list[tail][0], dist])
#                                 edges.append([mentions_list[tail][0], mentions_list[head][0], dist])

#                                 # edge_count += 2
#                                 tail += 1

#                             else:
#                                 in_range = False    

#                     # print('Adding: ', edge_count, ' edges.')     

#                     np.savetxt(edge_file, np.array(edges), delimiter=",", fmt='%i')
                    

#                     edges = []
#                     mentions_list = []

#                     if not line:
#                         writer = csv.writer(open('raw_vertices.csv','wb'))
#                         for key, value in vertices.items():
#                             writer.writerow([key, value.encode('utf-8')])
#                         break


#                 if line.strip() == "":

#                     # end of sentence
#                     sentence_idx += 1

#                 else:

#                     tokens_so_far += 1

#                     text, bpc_type = line.strip().split("\t")

#                     if (bpc_type == 'B-NP' or bpc_type != 'I-NP') and noun_phrase != '':

#                         noun_phrase = noun_phrase.strip('_')
#                         noun_phrase_end = tokens_so_far - 1
#                         np_hash = hash(noun_phrase)
#                         vertices[np_hash] = noun_phrase
#                         mentions_list.append([np_hash, noun_phrase_start, noun_phrase_end])
#                         noun_phrase = ''

#                     if bpc_type == 'B-NP':

#                         # noun phrase starts on this token
#                         noun_phrase_start = tokens_so_far

#                         if text[-1] == '+':
#                             noun_phrase += text[:-1]
#                         elif text[0] == '+':
#                                 noun_phrase = text[1:]
#                         else:
#                             noun_phrase += text + '_'

#                     elif bpc_type == 'I-NP':

#                         if text[-1] == '+':
#                             noun_phrase += text[:-1]
#                         elif text[0] == '+':
#                             # if it is a suffix prep, attach it to prev token
#                             if len(noun_phrase) > 0:
#                                 noun_phrase = noun_phrase[:-1] + text[1:]
#                             else:
#                                 noun_phrase = text[1:]
#                         else:
#                             noun_phrase += text + '_'              