#!/usr/bin/env python
# coding: utf-8

### Purpose: Arabic word embedding tools

from __future__ import absolute_import
from __future__ import print_function

from gensim.models import Word2Vec
import logging
import sys

def train_embeddings(infile, sg=1, size=100, window=8, min_count=5, sample=1e-4, hs=0, negative=25, iter=15):
    """
    Saves the model to a file with
    Uses gensim's training parameters:

    Initialize the model from an iterable of `sentences`. Each sentence is a
    list of words (unicode strings) that will be used for training.

    The `sentences` iterable can be simply a list, but for larger corpora,
    consider an iterable that streams the sentences directly from disk/network.
    See :class:`BrownCorpus`, :class:`Text8Corpus` or :class:`LineSentence` in
    this module for such examples.

    If you don't supply `sentences`, the model is left uninitialized -- use if
    you plan to initialize it in some other way.

    `sg` defines the training algorithm. By default (`sg=1`), skip-gram is used. Otherwise, `cbow` is employed.

    `size` is the dimensionality of the feature vectors.

    `window` is the maximum distance between the current and predicted word within a sentence.

    `alpha` is the initial learning rate (will linearly drop to zero as training progresses).

    `seed` = for the random number generator. Initial vectors for each
    word are seeded with a hash of the concatenation of word + str(seed).

    `min_count` = ignore all words with total frequency lower than this.

    `sample` = threshold for configuring which higher-frequency words are randomly downsampled;
        default is 0 (off), useful value is 1e-5.

    `workers` = use this many worker threads to train the model (=faster training with multicore machines).

    `hs` = if 1 (default), hierarchical sampling will be used for model training (else set to 0).

    `negative` = if > 0, negative sampling will be used, the int for negative
    specifies how many "noise words" should be drawn (usually between 5-20).

    `cbow_mean` = if 0 (default), use the sum of the context word vectors. If 1, use the mean.
    Only applies when cbow is used.

    `hashfxn` = hash function to use to randomly initialize weights, for increased
    training reproducibility. Default is Python's rudimentary built in hash function.

    `iter` = number of iterations (epochs) over the corpus.
    """

    # if (len(sys.argv) < 2):
    #     print("Please use this script with an input path and output path as args.")
    #     print("In: Text file with 1 sentence per line")
    #     print("Out: Binary word vector file")

    # infile = sys.argv[1]
    # outfile = sys.argv[2]
    outfile = infile.split()[0]+
              "_sg"+str(sg)+
              "_size"+str(size)+
              "_window"+str(window)+
              "_min_count"+str(min_count)+
              "_sample"+str(sample)+
              "_hs"+str(hs)+
              "_negative"+str(negative)+
              "_iter"+str(iter)+
              ".bin"

    print("Files opened!")
    
    # set up logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)

    # files are iterated over with this object
    class MySentences(object):
        def __init__(self, fname):
            self.fname = fname
            self.errors = 0

        def __iter__(self):
            for line in open(self.fname):
                yield line.split()

    sentences = MySentences(infile)
    
    model = Word2Vec(sentences, 
                     sg = 0, 
                     size = 100, 
                     window = 8, 
                     min_count = 5, 
                     hs = 0, 
                     workers = 4, 
                     sample = 1e-4, 
                     negative = 25, 
                     iter = 15)

    model.save_word2vec_format(outfile, binary = True)

    return outfile

def start_test_suite():
    """
    Loads a model, then allows interactive tests of:
    ac - not interactive, rather loads an analogy file and outputs the results
    one word most similar queries
    two word similarity measures
    three word analogy queries
    four+ word odd one out queries
    """

    output_spacing = 25

    modelfile = raw_input('Please enter the binary model file path: ')# (or gn/en/ar): ')
    modelfile = modelfile.strip()

    # if modelfile == 'gn':
    #     modelfile = '/Users/king96/Documents/Word2Vec/Models/google_news_vecs.bin'
    # elif modelfile == 'ar':
    #     modelfile = '/Users/king96/Documents/Word2Vec/Models/ar_wiki_seg_vecs.bin'
    # elif modelfile == 'en':
    #     modelfile = '/Users/king96/Documents/Word2Vec/Models/en_wiki_vecs.bin'

    # set up logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)

    # load model
    model = Word2Vec.load_word2vec_format(modelfile, binary=True)

    while True:
        
        # offer the menu
        print '\n'
        print 'Type ac to run accuracy tests.'
        print 'Enter one word for neighbors, two for distance,'
        print 'three for analogy, more for matching, q to quit.'
        words = raw_input('Word: ')

        words = words.decode('UTF-8', 'replace')
        
        if words == 'q':
            break

        if words == 'ac':
            print 'Please enter the questions file to test on:'

            questions = raw_input('File: ').strip()

            model.accuracy(questions, restrict_vocab = 30000, tries = 5)
            continue

        # the remaining options take 0 < n query words
        words = words.split(' ')

        if len(words) == 0:
            continue

        # top 10 words
        elif len(words) == 1:
            try:
                candidates = model.most_similar(words[0], topn=10)
                print 'Candidates'.rjust(output_spacing), 'Cos Distance'.rjust(output_spacing)
                for word in candidates:
                    print str(word[0].encode('UTF-8','replace')).rjust(output_spacing), str(word[1]).rjust(output_spacing)
            except KeyError as ke:
                print ke.message.encode('utf-8','replace')


        # pair similarity
        elif len(words) == 2:
            try:
                print 'Similarity is : ' + str(model.similarity(words[0],words[1]))
            except KeyError as ke:
                print ke.message.encode('utf-8','replace')

        # analogy
        elif len(words) == 3:
            try:
                candidates = model.most_similar(positive=[words[2], words[1]], 
                                                negative = [words[0]], 
                                                topn=10)

                print 'Candidates'.rjust(output_spacing), 'Cos Distance'.rjust(output_spacing)
                for word in candidates:
                    print str(word[0].encode('UTF-8', 'replace')).rjust(output_spacing), str(word[1]).rjust(output_spacing)
            except KeyError as ke:
                print ke.message.encode('utf-8','replace')

        # odd one out
        else:
            try:
                print 'Odd one out: ' + str(model.doesnt_match(words).encode('utf-8', 'replace'))
            except KeyError as ke:
                print ke.message.encode('utf-8','replace')

def start_query_expander():
    modelfile = raw_input('Please enter the binary model file path: ')
    modelfile = modelfile.strip()

    # if modelfile == 'gn':
    #     modelfile = '/Users/king96/Documents/Word2Vec/Models/google_news_vecs.bin'

    # set up logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)

    # load model
    model = Word2Vec.load_word2vec_format(modelfile, binary=True)

    while True:
        
        print 
        words = raw_input('\nEnter words to expand, q to quit: ')

        words = words.decode('UTF-8', 'replace')
        
        if words == 'q':
            break

        words = words.split(' ')

        if len(words) == 0:
            continue

        # top 10 words
        else:
            expansion = set()

            for word in words:
                try:
                    expansion = expansion | set([x[0] for x in model.most_similar(word, topn=10)])
                except KeyError as ke:
                    print ke.message.encode('utf-8','replace')

            print 'Expansion'
            for word in expansion:
                print str(word.encode('UTF-8','replace'))