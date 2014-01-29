from scrapy.item import Item, Field

class IdiItem(Item):
    name = Field()
    position = Field()
    group = Field()
    img = Field()
    url = Field()
    
    
