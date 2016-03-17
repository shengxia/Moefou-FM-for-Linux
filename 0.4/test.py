#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test.py
#  
#  Copyright 2014 sbin <sbin@sbin-Inspiron-5420>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import gst
import json
import urllib
import urllib2

def main():
    url="http://moe.fm/listen/playlist?api=json&api_key=ec8fd84d73ba19810b162b4999528da904fe50066"
    proxy_info = { 'host' : '122.96.59.106', 'port' : 843 }
    proxy_support = urllib2.ProxyHandler({"http" : "http://%(host)s:%(port)d" % proxy_info})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)
    response=urllib2.urlopen(url)
    data=response.read()
    moe=json.loads(data)
    stream=moe['response']['playlist'][0]["url"]
    print stream
    player=gst.element_factory_make("playbin", "player")
    player.set_state(gst.STATE_NULL)
    player.set_property('uri', stream)
    player.set_state(gst.STATE_PLAYING)
    return 0

if __name__ == '__main__':
	main()

