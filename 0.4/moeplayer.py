#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  未命名.py
#  
#  Copyright 2012 sbin <sbin@sbin-Aspire-4520>
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
import gtk
import os
import sys
import threading 
import pynotify


class MoePlayer:
    def __init__(self):
        self.channel=0
        self.list=[]
        self.ridlist=[]
        self.piclist=[]
        self.namelist=[]
        self.wikilist=[]
        self.artlist=[]
        self.radiolist=[]
        self.index=0
        self.rindex=0
        self.isconnect=False
        self.player=gst.element_factory_make("playbin", "player")
        self.GetList()
        
    def GetURL(self, type, rpage, channel):
        if type=="song":
            if channel==0:
                #To get random musics from Moefou
                url="http://moe.fm/listen/playlist?api=json&api_key=ec8fd84d73ba19810b162b4999528da904fe50066"
            else:
                #To get random musics with named channel from Moefou
                url="http://moe.fm/listen/playlist?api=json&api_key=ec8fd84d73ba19810b162b4999528da904fe50066&radio="+str(channel)
        #if type=="radio":
            #To get radio channel from Moefou
            #url="http://api.moefou.org/wikis.json?wiki_type=radio&perpage=20&api_key=ec8fd84d73ba19810b162b4999528da904fe50066&page=1"
        return url
    
    #To get musics' information from Moefou and load them to arrays
    def GetList(self):
        url=self.GetURL("song",0, self.channel)
        proxy_info = { 'host' : '122.96.59.106', 'port' : 843 }
        proxy_support = urllib2.ProxyHandler({"http" : "http://%(host)s:%(port)d" % proxy_info})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        try:
            response=urllib2.urlopen(url,timeout=2)
        except urllib2.URLError, e:
            self.isconnect=False
            return
        data=response.read()
        moe=json.loads(data)
        i=0
        while i< len(moe['response']['playlist']):
            #Load music list
            self.list.append(moe['response']['playlist'][i]["url"])
            #Load the cd cover list
            self.piclist.append(moe['response']['playlist'][i]["cover"]["square"])
            #Load the music name list
            self.namelist.append(moe['response']['playlist'][i]['sub_title'])
            #Load the CD name
            self.wikilist.append(moe['response']['playlist'][i]['wiki_title'])
            #Load the singer name
            self.artlist.append(moe['response']['playlist'][i]['artist'])
            i=i+1
        self.isconnect=True
    
    #To get radio channels' information from Moefou and load them to arrays
    def GetRadio(self):
        #Set the first radio channel
        self.ridlist.append('0')
        self.radiolist.append(u'随便听听')
        #Get the first page of radio channels
        url=self.GetURL('radio', 1 , self.channel)
        proxy_info = { 'host' : '122.96.59.106', 'port' : 843 }
        proxy_support = urllib2.ProxyHandler({"http" : "http://%(host)s:%(port)d" % proxy_info})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        try:
            response=urllib2.urlopen(url,timeout=2)
        except urllib2.URLError, e:
            self.isconnect=False
            return
        data=response.read()
        moe=json.loads(data)
        i=0
        while i<len(moe["response"]["wikis"]):
            #Load the radio id list
            self.ridlist.append(moe["response"]["wikis"][i]["wiki_id"])
            #Load the radio name list
            self.radiolist.append(moe["response"]["wikis"][i]["wiki_title"])
            i=i+1
        self.isconnect=True
     
    #To get next radio channel
    def NextRadio(self):
        length=len(self.radiolist)-1
        if self.rindex<length:
            self.rindex=self.rindex+1
        elif self.rindex>=length:
            self.rindex=0
        self.channel=self.ridlist[self.rindex]
        self.InitList()
    
    #To get previous radio channel
    def PreviousRadio(self):
        length=len(self.radiolist)-1
        if self.rindex>0:
            self.rindex=self.rindex-1
        elif self.rindex<=0:
            self.rindex=length
        self.channel=self.ridlist[self.rindex]
        self.InitList()
    
    #To get next music
    def Next(self):
        length=len(self.list)-1
        if self.index<length:
            self.index=self.index+1
            self.SimPlay()
        else:
            self.InitList()
            
    #Clear arraies to avoid play repeated musics        
    def InitList(self):
        self.list=[]
        self.piclist=[]
        self.namelist=[]
        self.wikilist=[]
        self.artlist=[]
        self.GetList()
        self.index=0
        self.channel=0
        self.SimPlay()
            
    #To judge whether need to play or pause        
    def Play(self,Pause,Play):
        isPaused=Pause
        isPlay=Play
        if isPaused:
            self.player.set_state(gst.STATE_PLAYING)
        elif isPlay:
            self.player.set_state(gst.STATE_PAUSED)
        else:
            self.SimPlay()
    
    #Only to play music    
    def SimPlay(self):
        if self.isconnect:
            stream=self.list[self.index]
            self.player.set_state(gst.STATE_NULL)
            self.player.set_property('uri', stream)
            self.player.set_state(gst.STATE_PLAYING)

