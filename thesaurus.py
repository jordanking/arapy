#!/usr/bin/env python
# coding: utf-8

### Purpose: Arabic word thesaurus simulation tools
# Dependant on goslate for free translation

from __future__ import absolute_import
from __future__ import print_function

import arapy.translate as trans
import logging
import sys
import json
import requests
import goslate


API_KEY = '80901dbb851efc07b4bd747ba3ead0ae' # API key is available from here - http://words.bighugelabs.com/getkey.php
URL_MASK = 'http://words.bighugelabs.com/api/2/{1}/{0}/json'
RELATIONSHIP_ABBR = {'syn':'Synonyms','ant':'Antonyms','rel':'Related terms','sim':'Similar terms','usr':'User suggestions', None:'All'}

def thesaurus(word, relation=None, ngram=0, ar=False, trans_with_google=False, target_result_count=0):
    """
    Uses bighugelabs thesaurus API
    requires the API key available http://words.bighugelabs.com/getkey.php

    Takes in a word and retreives a list of related words where
    the relationship is given by one key from {'syn':'Synonyms','ant':'Antonyms','rel':'Related terms','sim':'Similar terms','usr':'User suggestions', None:'All'}
    the words are filtered by ngram, 0 for all
    if ar = 0, the word is translated before and after from arabic
    translation is done withgoogle translate if trans_with_google is 1 and goslate otherwise
    target_result_count is the number of words to return with

    returns a dictionary where keys are the requested relationships, and values are lists of ngrams matching that relationship
    """

    gs = None
    if ar:
        if trans_with_google:
            word = trans.translate_list([word], 'en', 'ar')[0]
        else:
            gs = goslate.Goslate()
            word = gs.translate(word, 'en', 'ar')

    # format and make the request
    url = URL_MASK.format(word, API_KEY)
    result = requests.get(url)
    json_result = json.loads(result.text)

    # our relationship dictionary
    words = {}
    word_count = 0

    # for each sense of the word
    for pos in json_result:

        # we want only the requested relations 
        for rel in json_result[pos]:
            if relation == None or relation == rel:

                # each word matching the relationship
                for w in json_result[pos][rel]:

                    # we only want so many results
                    if word_count == 0 or word_count < target_result_count:

                        if ar == 1:
                            if trans_with_google:
                                w = trans.translate_list([w],'ar','en')[0]
                            else:
                                w = gs.translate(w, 'ar', 'en')

                        if ngram == 0 or len(w.split(" ")) == ngram:
                            if not rel in words:
                                words[rel] = []
                            words[rel].append(w)

                    else:
                        # we have enough results
                        return words
    return words



