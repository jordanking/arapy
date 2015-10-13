#!/usr/bin/env python
# coding: utf-8

### Purpose: Arabic word thesaurus simulation tools
# Dependant on goslate for translation
# Big huge labs query code from https://gist.github.com/hugorodgerbrown/3134709

from __future__ import absolute_import
from __future__ import print_function

import logging
import sys
import json
import requests
import goslate


API_KEY = '80901dbb851efc07b4bd747ba3ead0ae' # API key is available from here - http://words.bighugelabs.com/getkey.php
URL_MASK = 'http://words.bighugelabs.com/api/2/{1}/{0}/json'
RELATIONSHIP_ABBR = {'syn':'Synonyms','ant':'Antonyms','rel':'Related terms','sim':'Similar terms','usr':'User suggestions', None:'All'}

def thesaurus(word, relation=None, ngram=0, ar=0):
    """
    Takes in a word and
    retreives a list of ngrams (filtered by ngram, 0 for all) matching the relationship given by one key from 
    {'syn':'Synonyms','ant':'Antonyms','rel':'Related terms','sim':'Similar terms','usr':'User suggestions', None:'All'}
    If ar = 0, the word is translated before and after from arabic
    """

    gs = None
    if ar == 1:
        gs = goslate.Goslate()
        word = gs.translate(word, 'en', 'ar')

    print(word)

    url = URL_MASK.format(word, API_KEY)
    result = requests.get(url)
    json_result = json.loads(result.text)

    words = []
    for pos in json_result:
        for rel in json_result[pos]:
            if relation == None or relation == rel:
                for w in json_result[pos][rel]:

                    # if ar == 1:
                    #     w = gs.translate(w, 'ar', 'en')

                    if ngram == 0 or len(w.split(" ")) == ngram:
                        words.append([w,rel])
    return words