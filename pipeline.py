# add the path of arapy
from __future__ import absolute_import
from __future__ import print_function

# import sys
# sys.path.insert(0,"/home/jordan/Documents/Projects/")

from .arwiki import parse_arwiki_dump
from .arwiki import normalize_arwiki_parse
from .normalization import normalize
from .word2vec import train_embeddings
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.INFO)


wiki_file = "/media/jordan/Media/data/arabic/arwiki-20150901-pages-articles.xml"

ar_only = True
alif = True
hamza = True
yaa = True
tashkil = True

sg = 0
size = 100
window = 8
min_count = 5
sample = 1e-4
hs = 0
negative = 25
iterations = 15

logging.info("Parsing dump.")
parse_file = parse_arwiki_dump(wiki_file)

logging.info("Normalizing dump")
normalized_file = normalize_arwiki_parse(parse_file, 
                                         ar_only = ar_only, 
                                         alif = alif,
                                         hamza = hamza,
                                         yaa = yaa,
                                         tashkil = tashkil)

logging.info("Generating word vectors")
embeddings_file = train_embeddings(normalized_file,
                                   sg = sg,
                                   size = size,
                                   window = window,
                                   min_count = min_count,
                                   sample = sample,
                                   hs = hs,
                                   negative = negative,
                                   iter = iterations)

logging.info("Done!")