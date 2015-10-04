import sys

# add the path of arapy
from .arwiki import parse_arwiki_dump
from .arwiki import normalize_arwiki_parse
from .normalization import normalize
from .word2vec import train_embeddings

wiki_file = "file.xml"

ar_only = True
alif = True
hamza = True
yaa = True
tashkil = True

sg = 0
size = 0
window = 8
min_count = 5
sample = 3
hs = 3
negative = 3
iterations = 15


parse_file = parse_arwiki_dump(wiki_file)

normalized_file = normalize_arwiki_parse(parse_file, 
                                         ar_only = ar_only, 
                                         alif = alif,
                                         hamza = hamza,
                                         yaa = yaa,
                                         tashkil = tashkil)

embeddings_file = train_embeddings(normalized_file,
                                   sg = sg,
                                   size = size,
                                   window = window,
                                   min_count = min_count,
                                   sample = sample,
                                   hs = hs,
                                   negative = negative,
                                   iter = iterations)