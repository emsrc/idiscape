# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class CiteSeerXItem(Item):
    url = Field()
    author = Field()
    bibtex = Field()
    cached_links = Field()
    download_links = Field()
    abstract = Field()

