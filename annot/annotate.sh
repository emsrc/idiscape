# tokenize, tag and lemmatize text files with Stanford CoreNLP

ls -1 ../extract/text/*.txt > text_files

java -cp stanford-corenlp-full-2014-01-04/stanford-corenlp-3.3.1.jar:stanford-corenlp-full-2014-01-04/stanford-corenlp-3.3.1-models.jar:stanford-corenlp-full-2014-01-04/xom.jar -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP  -annotators tokenize,ssplit,pos,lemma -outputDirectory xml -replaceExtension -outputFormat xml -filelist text_files