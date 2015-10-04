#!/usr/bin/env python
# coding: utf-8

### Purpose: Arabic script normalization tools

from __future__ import absolute_import
from __future__ import print_function

import re
import codecs

# regex for arabic chars
inv_arabic_charset = re.compile(ur'[^\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\u0030-\u0039\.]+', re.UNICODE)

def normalize(text, ar_only=True, digits=False, alif=True, hamza=True, yaa=True, tashkil=True):
    """
    Normalizes arabic text
    Removes non-arabic chars by default
    Changes all numerals to # if digits is true, default false
    Normalizes alif, hamza, and yaa by default
    Removes supplementary diacritics
    """
    if ar_only:
        text = normalize_charset(text)

    if digits:
        text = normalize_digits(text)

    if alif:
        text = normalize_alif(text)
    if hamza:
        text = normalize_hamza(text)
    if yaa:
        text = normalize_yaa(text)

    if tashkil:
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

def normalize_charset(text):
    return inv_arabic_charset.sub(' ', text)

def normalize_digits(text):
    """ replaces all forms of numbers with # """
    return re.sub(ur'[0123456789٠١٢٣٤٥٦٧٨٩]', ur'#', text)

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

##################################
### Buckwalter transliteration ###
##################################

def unicode_to_bw(string, reverse=0):
    """
    Given a Unicode string, transliterate into Buckwalter. 
    To go from Buckwalter back to Unicode, set reverse=1.
    Partially taken from https://github.com/andyroberts/buckwalter2unicode
    """

    buck2uni = {"'": u"\u0621", # hamza-on-the-line
                "|": u"\u0622", # madda
                ">": u"\u0623", # hamza-on-'alif
                "&": u"\u0624", # hamza-on-waaw
                "<": u"\u0625", # hamza-under-'alif
                "}": u"\u0626", # hamza-on-yaa'
                "A": u"\u0627", # bare 'alif
                "b": u"\u0628", # baa'
                "p": u"\u0629", # taa' marbuuTa
                "t": u"\u062A", # taa'
                "v": u"\u062B", # thaa'
                "j": u"\u062C", # jiim
                "H": u"\u062D", # Haa'
                "x": u"\u062E", # khaa'
                "d": u"\u062F", # daal
                "*": u"\u0630", # dhaal
                "r": u"\u0631", # raa'
                "z": u"\u0632", # zaay
                "s": u"\u0633", # siin
                "$": u"\u0634", # shiin
                "S": u"\u0635", # Saad
                "D": u"\u0636", # Daad
                "T": u"\u0637", # Taa'
                "Z": u"\u0638", # Zaa' (DHaa')
                "E": u"\u0639", # cayn
                "g": u"\u063A", # ghayn
                "_": u"\u0640", # taTwiil
                "f": u"\u0641", # faa'
                "q": u"\u0642", # qaaf
                "k": u"\u0643", # kaaf
                "l": u"\u0644", # laam
                "m": u"\u0645", # miim
                "n": u"\u0646", # nuun
                "h": u"\u0647", # haa'
                "w": u"\u0648", # waaw
                "Y": u"\u0649", # 'alif maqSuura
                "y": u"\u064A", # yaa'
                "F": u"\u064B", # fatHatayn
                "N": u"\u064C", # Dammatayn
                "K": u"\u064D", # kasratayn
                "a": u"\u064E", # fatHa
                "u": u"\u064F", # Damma
                "i": u"\u0650", # kasra
                "~": u"\u0651", # shaddah
                "o": u"\u0652", # sukuun
                "`": u"\u0670", # dagger 'alif
                "{": u"\u0671", # waSla
    }

    # For a reverse transliteration (Unicode -> Buckwalter), a dictionary
    # which is the reverse of the above buck2uni is essential.

    uni2buck = {}

    # Iterate through all the items in the buck2uni dict.
    for (key, value) in buck2uni.iteritems():
            # The value from buck2uni becomes a key in uni2buck, and vice
            # versa for the keys.
            uni2buck[value] = key

    if not reverse:     
        for k,v in buck2uni.iteritems():
            string = string.replace(v,k)

    else:     
        for k,v in buck2uni.iteritems():
            string = string.replace(k,v)

    return string


