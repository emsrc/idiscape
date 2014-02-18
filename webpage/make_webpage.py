#!/usr/bin/env python

"""
make webpage with word cloud images
"""

from os.path import exists, join, basename, splitext, abspath
from os import makedirs, symlink, remove
from codecs import open

from lxml import etree


menu_template = u"""
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8">
<link rel="stylesheet" type="text/css" href="{style}" />
</head>
<body>
<h1>IDISCAPE</h1>
<p class="author">
<a href="about.html" target="cloud">About</a>
</p>
{authors}
</body>
</html>
"""

author_template = u"""
<p class="author">
<a href="{cloud}" target="cloud">
<img class="face" src="{img}">
</a>
<br>
<a href="{url}" target="cloud">{name}</a><br>
{position}<br>
{group}<br>
</p>
"""

cloud_template = u"""
<!DOCTYPE html>
<html>
<head>
<title>{name}</title>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8">
<link rel="stylesheet" type="text/css" href="{style}" />
</head>
<body class="cloud">
<img class="cloud" src="{cloud_href}">
</body>
</html>
"""


def make_webpage(crawl_fname, index_fname, style_fname, photo_dir, cloud_dir,
                 out_dir, photo_subdir="photo", cloud_subdir="cloud", 
                 menu_fname="menu.htm"):
    if not exists(out_dir):
        makedirs(out_dir)
        
    link(abspath(index_fname), join(out_dir, basename(index_fname)))    
    link(abspath(style_fname), join(out_dir, basename(style_fname)))
    link(abspath(photo_dir), join(out_dir, photo_subdir))
    link(abspath(cloud_dir), join(out_dir, cloud_subdir))

    tree = etree.parse(crawl_fname)
    authors = []

    for item in tree.findall("//item"):
        url, position, group, name, img = [e.text for e in item]
        cloud_fname = join(cloud_subdir, name + u".png")
        
        if exists(join(out_dir, cloud_fname)):            
            html = author_template.format(
                style=basename(style_fname),
                img=join(photo_subdir, basename(img)),
                name = name,
                url=url,
                position=position,
                group=group,
                cloud=join(name + ".htm")
            )
            authors.append((name, html))
            
            with open(join(out_dir, join(name + ".htm")), "w", "utf8") as f:
                html = cloud_template.format(name=name,
                                             style=basename(style_fname), 
                                             cloud_href=cloud_fname)
                f.write(html)
        
    authors.sort()
    authors = "".join(html for _, html in authors)
    
    with open(join(out_dir, menu_fname), "w", "utf8") as f:
        f.write(menu_template.format(style=basename(style_fname), 
                                     authors=authors))    
        
        
def link(source, dest):
    print source, dest
    if exists(dest):
        remove(dest)
    symlink(source, dest)
    
        
if __name__ == "__main__":
    from sys import argv    
    make_webpage(*argv[1:])
        

        


    