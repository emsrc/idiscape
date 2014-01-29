# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem


class ValidateItem(object):
    
    def process_item(self, item, spider):
        if not item["bibtex"]:
            raise DropItem("no bibtex in item %s" % item)
        return item


