#!/usr/bin/env python

"""
make static webpage with word cloud images
"""

from os.path import exists, join, basename, splitext, abspath
from os import symlink, remove
from shutil import copytree, rmtree
from codecs import open

from lxml import etree


menu_template = u"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>About IDISCAPE</title>
<meta name="description" content="IDI staff">
<link href="{style}" rel="stylesheet">
</head>
<body>
<div class="container">
<header>
<div class="logo">IDIScape</div>
</header>
<div class="row">	
<p>
<a href="about.html" target="cloud">About IDIScape</a>
</p>
</div>
<div class="row">

{authors}

</div>
<footer>
&copy;2014 <a href="http://www.idi.ntnu.no/people/emarsi">Erwin Marsi</a>
</footer>
</div>
</body>
</html>
"""


author_template = u"""
<p class="text-center">
<a href="{cloud}" target="cloud">
<img class="center" src="{img}">
</a>
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
<body>
<img class="center" src="{cloud_href}">
</body>
</html>
"""


cloud_template = u"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>{name}</title>
<meta name="description" content="word cloud">
<link href="{style}" rel="stylesheet">
</head>
<body>
<div class="row">
<div class="col-12">
<img class="center" style="margin-top:5%" src="{cloud_href}">
</div>
</div>
</body>
</html>
"""


def make_webpage(crawl_fname, html_dir, photo_dir, cloud_dir, build_dir,
                 photo_subdir="photo", cloud_subdir="cloud", index_fname="index.htm",
                 style_fname="minimal.css", menu_fname="menu.htm", clean=False):
    if clean: rmtree(build_dir)
    # copy html skeleton
    copytree(html_dir, build_dir)
    symlink(abspath(photo_dir), join(build_dir, photo_subdir))
    symlink(abspath(cloud_dir), join(build_dir, cloud_subdir))

    tree = etree.parse(crawl_fname)
    authors = []

    for item in tree.findall("//item"):
        url, position, group, name, img = [e.text for e in item]
        cloud_fname = join(cloud_subdir, name + u".png")
        
        if exists(join(build_dir, cloud_fname)):  
            # generate menu entry
            html = author_template.format(
                style=style_fname,
                img=join(photo_subdir, basename(img)),
                name = name,
                url=url,
                position=position,
                group=group,
                cloud=join(name + ".htm")
            )
            authors.append((name, html))
            
            # generate html file with word cloud image
            with open(join(build_dir, join(name + ".htm")), "w", "utf8") as f:
                html = cloud_template.format(name=name,
                                             style=style_fname, 
                                             cloud_href=cloud_fname)
                f.write(html)
        
    authors.sort()
    authors = "".join(html for _, html in authors)
    
    with open(join(build_dir, menu_fname), "w", "utf8") as f:
        f.write(menu_template.format(style=style_fname, 
                                     authors=authors))    
        
        
    
        
if __name__ == "__main__":
    from sys import argv    
    make_webpage(*argv[1:])
        

        


    