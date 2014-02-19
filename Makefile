#≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈
# 
# IDISCAPE
#
# Erwin Marsi - 2014
#
#≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈

.PHONY: crawl_idi crawl_citeseer download extract annot vector cloud webpage

all: crawl_idi crawl_citeseer download extract annot vector cloud webpage

clean: clean_crawl_idi clean_citeseer clean_download clean_extract \
clean_annot clean_vector clean_webpage


#------------------------------------------------------------------------------
# Step 1: Crawl IDI website
#------------------------------------------------------------------------------
#
# Crawl http://www.idi.ntnu.no/ for info on scientific staff

IDI_DIR=crawl_idi
IDI_OUTPUT=$(IDI_DIR)/IDISpider.xml
IDI_LOG=$(IDI_DIR)/crawl_idi.log
IMG_DIR=$(IDI_DIR)/img

crawl_idi:
	rm -f $(IDI_OUTPUT) # Scrappy writes in append mode, so remove old file 
	mkdir -p $(IMG_DIR)
	cd $(IDI_DIR); scrapy crawl IDISpider |tee $(IDI_LOG)
	xmllint --format --output $(IDI_OUTPUT) $(IDI_OUTPUT)

clean_crawl_idi:
	rm -vf $(IDI_OUTPUT) $(IDI_LOG)
	rm -vrf $(IMG_DIR)


#------------------------------------------------------------------------------
# Step 2: Crawl CiteSeerX for publications by authors
#------------------------------------------------------------------------------
#
# Crawl http://citeseer.ist.psu.edu for publications by scientific staff

CSX_DIR=crawl_citeseer
CSX_OUTPUT=$(CSX_DIR)/CiteSeerXSpider.xml
CSX_LOG=$(CSX_DIR)/crawl_siteseer.log

crawl_citeseer:
	rm -f $(CSX_OUTPUT) # Scrappy writes in append mode, so remove old file 
	cd $(CSX_DIR); scrapy crawl CiteSeerXSpider |tee $(CSX_LOG)
	xmllint --format --output $(CSX_OUTPUT) $(CSX_OUTPUT)

clean_crawl_citeseer:
	rm -vf $(CSX_OUTPUT) $(CSX_LOG)

#------------------------------------------------------------------------------
# STEP 3: Download full-text publications
#------------------------------------------------------------------------------
#
# Download full-text PDF files following links on CiteSeerX page where
# 'CiteSeerXSpider.xml' is the output from the CiteSeerX crawl and 'docs' is the
# destination directory for PDF files.
#
# Documents are stored under their DOI. If a file {DOI}.pdf already
# exists, its download is skipped.
#
# Known issue: script sometimes hangs for no apparent reason; if so,
# restart.

DOWNLOAD_DIR=download
PDF_DIR=$(DOWNLOAD_DIR)/pdf
DOWNLOAD_LOG=$(DOWNLOAD_DIR)/download.log

download:
	mkdir -p $(PDF_DIR)
	$(DOWNLOAD_DIR)/download_fulltext.py $(CSX_OUTPUT) $(PDF_DIR) \
		|tee $(DOWNLOAD_LOG)

clean_download:
	rm -rvf $(PDF_DIR)
	rm -vf $(DOWNLOAD_LOG)


#------------------------------------------------------------------------------
# STEP 4: Extract text from PDFs
#------------------------------------------------------------------------------
#
# Extract text from PDF files, skipping
# - PDF files with more than 50 pages
# - converted text consisting mainly of garbage
# - converted text not containing the author name
#
# Also deletes illegal XML chars. 
# Assumes command line tools 'pdfinfo' and 'pdftotext' are on shell PATH.

EXTRACT_DIR=extract
TXT_DIR=$(EXTRACT_DIR)/txt
EXTRACT_LOG=$(EXTRACT_DIR)/extract.log

extract:
	mkdir -p $(TXT_DIR)
	$(EXTRACT_DIR)/extract_text.py $(CSX_OUTPUT) $(PDF_DIR) $(TXT_DIR) \
		|tee $(EXTRACT_LOG)

clean_extract:
	rm -rvf $(TXT_DIR)
	rm -vf $(EXTRACT_LOG)


#------------------------------------------------------------------------------
# STEP 5: Annotation
#------------------------------------------------------------------------------
#
# Tokenize, POS tag and lemmatize with Stanford CoreNLP
# tools. Increase Java heap size when you encounter out-of-memory
# errors.
# Afterwards extract lemma (and optionally POS tag) from XML output.

ANNOT_DIR=annot
XML_DIR=$(ANNOT_DIR)/xml
LEMTAG_DIR=$(ANNOT_DIR)/lemtag
ANNOT_LOG=$(ANNOT_DIR)/annot.log
SCNLP_DIR=$(ANNOT_DIR)/stanford-corenlp-full-2014-01-04
SCNLP_CP=$(SCNLP_DIR)/stanford-corenlp-3.3.1.jar:$(SCNLP_DIR)/stanford-corenlp-3.3.1-models.jar:$(SCNLP_DIR)/xom.jar
HEAP_SIZE=3g
FILELIST=$(ANNOT_DIR)/text_files

annot:
	ls -1 $(TXT_DIR)/*.txt > $(FILELIST) 
	mkdir -p $(XML_DIR)
	java \
		-cp $(SCNLP_CP) \
		-Xmx$(HEAP_SIZE) \
		edu.stanford.nlp.pipeline.StanfordCoreNLP  \
		-annotators tokenize,ssplit,pos,lemma \
		-outputDirectory $(XML_DIR) \
		-replaceExtension \
		-outputFormat xml \
		-filelist $(FILELIST) \
		|tee $(ANNOT_LOG)
	rm $(FILELIST)
	mkdir -p $(LEMTAG_DIR)
	$(ANNOT_DIR)/lemtag.py \
		"$(XML_DIR)/*.xml" \
		$(LEMTAG_DIR) \
		|tee -a $(ANNOT_LOG)


clean_annot:
	rm -rvf $(XML_DIR)
	rm -rvf $(LEMTAG_DIR)
	rm -vf $(ANNOT_LOG)


#------------------------------------------------------------------------------
# STEP 6: Vectorize
# ------------------------------------------------------------------------------
#
# Create document vectors by vectorizing document as bag-of-n-grams
# Create author vectors by summing the document vectors of their publications

VECTOR_DIR=vector
DOC_VECS=$(VECTOR_DIR)/docvecs.npz
AUTH_VECS=$(VECTOR_DIR)/authvecs.npz
VECTOR_LOG=$(VECTOR_DIR)/vector.log

vector:
	$(VECTOR_DIR)/make_doc_vectors.py  "$(LEMTAG_DIR)/*.lemtag" $(DOC_VECS)
	$(VECTOR_DIR)/make_author_vecs.py  $(CSX_OUTPUT) $(DOC_VECS) $(AUTH_VECS) \
		|tee $(VECTOR_LOG)

clean_vector:
	rm -vf $(DOC_VECS) $(AUTH_VECS) $(VECTOR_LOG) \
		$(VECTOR_DIR)\*.mtx $(VECTOR_DIR)\*.txt


#------------------------------------------------------------------------------
# STEP 7: Make word clouds
#------------------------------------------------------------------------------
#
# Make word clouds consisting of 200 most frequent words from the
# author vector.

CLOUD_DIR=cloud
CLOUD_IMG_DIR=$(CLOUD_DIR)/img
CLOUD_LOG=$(CLOUD_DIR)/cloud.log

cloud:
	mkdir -p $(CLOUD_IMG_DIR)
	$(CLOUD_DIR)/make_clouds.py \
		$(AUTH_VECS) \
		$(IDI_OUTPUT) \
		$(CLOUD_IMG_DIR) \
		|tee $(CLOUD_LOG)


clean_cloud:
	rm -frv $(CLOUD_IMG_DIR) $(CLOUD_LOG)


#------------------------------------------------------------------------------
# STEP 8: Make webpage
#------------------------------------------------------------------------------
#
# Create webpage is self-contained dir, symlinking photos and cloud images

WEB_DIR=webpage
HTML_DIR=$(WEB_DIR)/html
BUILD_DIR=$(WEB_DIR)/build


webpage:
	$(WEB_DIR)/make_webpage.py \
		$(IDI_OUTPUT) \
		$(HTML_DIR) \
		$(IMG_DIR) \
		$(CLOUD_IMG_DIR) \
		$(BUILD_DIR)
		
clean_webpage:
	rm -vrf $(BUILD_DIR)
	
	

#------------------------------------------------------------------------------
# Pack data
#------------------------------------------------------------------------------

# Pack matrices, labels and features. Move tarball to webpage. 

TARBALL=idiscape-data-v1.tar.bz2

pack:
	tar cvyf $(TARBALL) $(VECTOR_DIR)/*.mtx $(VECTOR_DIR)/*.txt
	mv -v $(TARBALL) $(BUILD_DIR)