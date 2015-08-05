import arapy.madamira.xml_output_processing as mxo
import arapy.madamira.raw_output_processing as mro

print('processing xml')
mxo.save_noun_phrase_graph('/Users/king96/Documents/Sitaware/Madamira/MADAMIRA-release-20150421-2.1/samples/xml/SampleOutputFile.xml', 'out.txt')
print('processing raw')
# mro.save_noun_phrase_graph('/Users/king96/Documents/Sitaware/Madamira/MADAMIRA-release-20150421-2.1/samples/raw/SampleTextInput.txt.bpc-bio', 'out2.txt')
mro.save_noun_phrase_graph('/Users/king96/Documents/Sitaware/madatest/FINAL.bpc-bio', 'out2.txt')