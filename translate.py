#!/usr/bin/env python
# coding: utf-8

### Purpose: Arabic word translation tools for google translate api: https://cloud.google.com/translate/v2/pricing

from __future__ import absolute_import
from __future__ import print_function

import logging
import sys
import json
import requests
import urllib2


GOOGLE_API_KEY = 'AIzaSyAAScZ3-Ut-1sxn5gsSLzxzXJgzn3jGsN4'
URL_MASK = 'https://www.googleapis.com/language/translate/v2?key={0}{1}&source={2}&target={3}'

def translate_list(words, target, source='en'):
    """
    Translates a word with the google translate api
    Requires an API key from the google developers console
    """

    # format the words for the url
    formatted_words=""
    for word in words:
        formatted_words += "&q=" + urllib2.quote(word)

    # format the url for the get
    url = URL_MASK.format(GOOGLE_API_KEY, formatted_words, source, target)
    result = requests.get(url)

    if not result.text:
        logging.info("Google responded with no translations")
        return []

    json_result = json.loads(result.text)

    if not 'data' in json_result:
        logging.info("Google result had no data element.")
        return []

    # parse the result
    translations = []
    for translation in json_result['data']['translations']:
        trans_word = translation['translatedText']
        logging.info("Translated "+str(word)+ " to "+trans_word.encode('utf-8'))
        translations.append(trans_word)

    return translations