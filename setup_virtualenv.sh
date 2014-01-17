# create virtual python enviroment named 'idiscape' using Conda
conda create -n idi lxml pip ipython twisted lxml six requests scikit-learn pil cython unidecode

source activate idi

# install latest version of scrapy (conda installs outdated version 0.16)
pip install scrapy


