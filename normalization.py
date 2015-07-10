#!/usr/bin/env python
# coding: utf-8

### Purpose: Arabic script normalization tools

from __future__ import absolute_import
from __future__ import print_function

import re as re
import codecs

def normalize(text):
    """
    Normalizes arabic text
    Normalizes alif, hamza, and yaa
    Removes supplementary diacritics
    """
    text = normalize_alif(text)
    text = normalize_hamza(text)
    text = normalize_yaa(text)

    text = remove_tashkil(text)

    return text

def remove_tashkil(text):
    """ removes set of arabic supplementary diacritics """
    text = remove_harakat(text)
    text = remove_tanwin(text)
    text = remove_shaddah(text)
    text = remove_kashida(text)
    return text

#####################
### Normalization ###
#####################

def normalize_alif(text):
    """ replaces all forms of alif with ا """
    return re.sub(ur'[إأٱآا]', ur'ا', text)

def normalize_yaa(text):
    """ replaces ى with ي """
    return re.sub(ur'ى', ur'ي', text)

def normalize_hamza(text, normalize_alif = False):
    """
    replaces hamza on seats with ء
    does not include alif seats by default
    set normalize_alif=True to replace إأ with hamza
    """
    if normalize_alif:
        return re.sub(ur'[ؤئإأ]', ur'ء', text)
    else:
        return re.sub(ur'[ؤئ]', ur'ء', text)

#######################
### Tashkil removal ###
#######################

def remove_harakat(text):
    """
    removes short vowel marks
    does not normalize alif forms
    does not remove tanwin (ًٌٍ) (use remove_tanwin)
    """
    return re.sub(ur'[َُِْ]', ur'', text)

def remove_tanwin(text):
    """
    removes tanwin vowel marks
    does not normalize alif forms
    """
    return re.sub(ur'[ًٌٍ]', ur'', text)

def remove_shaddah(text):
    """
    removes the shaddah mark (tashdid)
    """
    return re.sub(ur'[ّ]', ur'', text)

def remove_kashida(text):
    """
    removes the kashida elongation mark (tatwil)
    """
    return re.sub(ur'[ـ]', ur'', text)

    text = re.sub(noise, '', text)
    return text




