"""
Item processing pipelines for IDI crawler
"""

from os.path import join

import requests
import sqlite3

from scrapy import log
from scrapy.contrib.exporter import BaseItemExporter

from crawl_idi import settings



class SqliteItemExporter(BaseItemExporter):
    """
    Store items is Sqlite database

    DB filename defaults to FEED_URI as defined in crawl_idi.setting,
    unless specified through scrapy's -o command line option
    """
    
    def __init__(self, file, **kwargs):
        BaseItemExporter.__init__(self, **kwargs)
        self.file = file
        
    def start_exporting(self):
        self.db = sqlite3.connect(self.file.name)
        cursor = self.db.cursor()
        cursor.execute('CREATE TABLE authors ('
                       'id INTEGER PRIMARY KEY,' 
                       'name TEXT,' 
                       'rgroup TEXT,' 
                       'position TEXT,' 
                       'img TEXT,'
                       'url TEXT)')      
        self.db.commit()        

    def export_item(self, item):
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO authors(name, rgroup, position, img, url)'
                       'VALUES(?,?,?,?,?)', 
                       (item['name'],
                        item['group'],
                        item['position'],
                        item["img"],
                        item['url']))        
        self.db.commit()        
    
    def finish_exporting(self):
        self.db.close()



class IdiImagePipeline(object):
    """
    Save mug shots
    
    Output directory defaults to IMG_DIR as defined in crawl_idi.setting
    """

    def process_item(self, item, spider):
        log.msg("Trying imgage download from {}".format(item["img"]), log.DEBUG)
        try:
            result = requests.get(item["img"])
        except requests.RequestException as inst:
            log.msg(inst, log.ERROR)
        else:
            if result.ok:
                basename = item["img"].split("/")[-1]
                out_fname = join(spider.settings["IMG_DIR"], basename)
                log.msg("Saving image to {}".format(out_fname), log.INFO)
                open(out_fname, "wb").write(result.content)
            else:
                log.msg("Failure: {}".format(result.reason), log.ERROR)            

        return item
