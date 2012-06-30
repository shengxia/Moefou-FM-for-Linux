#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  moefou.py
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
import threading 


class MoePlayer:
    def __init__(self):
        self.channel=0
        self.radiocount=0
        self.list=[]
        self.ridlist=[]
        self.piclist=[]
        self.namelist=[]
        self.radiolist=[]
        self.index=0
        self.rindex=0
        self.player=gst.element_factory_make("playbin", "player")
        self.GetRadio()
        self.GetList()
        
    def GetURL(self, type, rpage, channel):
        if type=="song":
            if channel==0:
                url="http://moe.fm/listen/playlist?api=json&api_key=ec8fd84d73ba19810b162b4999528da904fe50066"
            else:
                url="http://moe.fm/listen/playlist?api=json&api_key=ec8fd84d73ba19810b162b4999528da904fe50066&radio="+str(channel)
        if type=="radio":
            url="http://api.moefou.org/wikis.json?wiki_type=radio&perpage=50&api_key=ec8fd84d73ba19810b162b4999528da904fe50066&page="+str(rpage)
        return url
        
    def GetList(self):
        url=self.GetURL("song",0, self.channel)
        response=urllib2.urlopen(url)
        data=response.read()
        moe=json.loads(data)
        if moe['response']['information']['item_count']==0:
            url=GetURL("song",0, self.channel)
            response=urllib2.urlopen(url)
            data=response.read()
            moe=json.loads(data)
        i=0
        while i< len(moe['response']['playlist']):
            self.list.append(moe['response']['playlist'][i]["url"])
            self.piclist.append(moe['response']['playlist'][i]["cover"]["square"])
            self.namelist.append(moe['response']['playlist'][i]['title'])
            i=i+1
    
    def GetRadio(self):
        self.ridlist.append('0')
        self.radiolist.append(u'随便听听')
        url=self.GetURL('radio', 1 , self.channel)
        response=urllib2.urlopen(url)
        data=response.read()
        moe=json.loads(data)
        self.radiocount=moe['response']['information']['count']
        i=0
        while i<len(moe["response"]["wikis"]):
            self.ridlist.append(moe["response"]["wikis"][i]["wiki_id"])
            self.radiolist.append(moe["response"]["wikis"][i]["wiki_title"])
            i=i+1
                
    def NextRadio(self):
        length=len(self.radiolist)-1
        if self.rindex<length:
            self.rindex=self.rindex+1
        elif self.rindex>=length:
            self.rindex=0
        self.channel=self.ridlist[self.rindex]
        self.list=[]
        self.piclist=[]
        self.namelist=[]
        self.GetList()
        self.index=0
        self.SimPlay()
    
    def PreviousRadio(self):
        length=len(self.radiolist)-1
        if self.rindex>0:
            self.rindex=self.rindex-1
        elif self.rindex<=0:
            self.rindex=length
        self.channel=self.ridlist[self.rindex]
        self.list=[]
        self.piclist=[]
        self.namelist=[]
        self.GetList()
        self.index=0
        self.SimPlay()
    
    def Next(self):
        length=len(self.list)-1
        if self.index<length:
            self.index=self.index+1
            self.SimPlay()
        else:
            self.list=[]
            self.piclist=[]
            self.namelist=[]
            self.GetList()
            self.index=0
            self.SimPlay()
            
            
    def Play(self,Pause,Play):
        isPaused=Pause
        isPlay=Play
        if isPaused:
            self.player.set_state(gst.STATE_PLAYING)
        elif isPlay:
            self.player.set_state(gst.STATE_PAUSED)
        else:
            self.SimPlay()
        
    def SimPlay(self):
        music_stream_uri=self.list[self.index]
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property('uri', music_stream_uri)
        self.player.set_state(gst.STATE_PLAYING)
        

class MainFrame():
    def __init__(self,player):
        self.player=player
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('萌否电台——'+player.namelist[self.player.index])
        self.window.set_default_size(576, 192)
        self.window.connect('destroy', gtk.main_quit, 'WM destroy')
        self.window.set_resizable(False)
        th_add=threading.Thread(target=self.AddRadio,args=() ) 
        th_add.start()
    
        self.image=gtk.Image()
        response=urllib2.urlopen(player.piclist[player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        self.image.show()
        
        self.start=gtk.Button()
        startpic=gtk.Image()
        startpic.set_from_file('start.png')
        startpic.show()
        self.start.add(startpic) 
        self.start.show()
        self.start.connect('clicked', self.Play_click)
        
        self.next=gtk.Button()
        nextpic=gtk.Image()
        nextpic.set_from_file('next.png')
        nextpic.show()
        self.next.add(nextpic) 
        self.next.show()
        self.next.connect('clicked',self.Next_click)
        
        self.download=gtk.Button()
        dlpic=gtk.Image()
        dlpic.set_from_file('download.png')
        dlpic.show()
        self.download.add(dlpic) 
        self.download.show()
        self.download.connect('clicked',self.Download_click)
        
        self.nradio=gtk.Button()
        npic=gtk.Image()
        npic.set_from_file('nextradio.png')
        npic.show()
        self.nradio.add(npic) 
        self.nradio.show()
        self.nradio.connect('clicked',self.Nextr_click)
        
        self.pradio=gtk.Button()
        ppic=gtk.Image()
        ppic.set_from_file('prevousradio.png')
        ppic.show()
        self.pradio.add(ppic) 
        self.pradio.show()
        self.pradio.connect('clicked',self.Previousr_click)
        self.rlabel=gtk.Label(player.radiolist[player.rindex])
        
        mainbox = gtk.HBox()
        controlbox = gtk.VBox()
        buttonbox = gtk.HBox()
        radiobox = gtk.HBox()
        self.window.add(mainbox)
        
        mainbox.pack_start(gtk.Label())
        mainbox.pack_start(self.image, False)
        mainbox.pack_start(controlbox, False)
        mainbox.add(gtk.Label())
        
        controlbox.pack_start(gtk.Label())
        controlbox.pack_start(radiobox, False)
        controlbox.pack_start(buttonbox, False)
        controlbox.add(gtk.Label())
        
        radiobox.set_border_width(10)
        radiobox.pack_start(gtk.Label())
        radiobox.pack_start(self.pradio, False)
        radiobox.pack_start(self.rlabel, False)
        radiobox.pack_start(self.nradio, False)
        radiobox.add(gtk.Label())
        
        buttonbox.set_border_width(10)
        buttonbox.pack_start(gtk.Label())
        buttonbox.pack_start(self.download, False)
        buttonbox.pack_start(self.start, False)
        buttonbox.pack_start(self.next, False)
        buttonbox.add(gtk.Label())
        
        bus=self.player.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)
        self.window.show_all()
    
    def Play_click(self,event):
        states=self.player.player.get_state()
        childimage = self.start.get_child()
        isPaused=gst.STATE_PAUSED in states
        isPlay=gst.STATE_PLAYING in states
        self.player.Play(isPaused,isPlay)
        if isPaused:
            childimage.set_from_file('start.png')
        elif isPlay:
            childimage.set_from_file('pause.png')
            
    def Next_click(self,event):
        self.player.Next()
        self.window.set_title('萌否电台——'+self.player.namelist[self.player.index])
        response=urllib2.urlopen(self.player.piclist[self.player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        
    def Download_click(self,event):
        home = os.path.expanduser('~')
        if not(os.path.exists(home+"/MoefouDownload")):
            os.mkdir(home+"/MoefouDownload")
        th=threading.Thread(target=self.Download,args=() ) 
        th.start()
    
    def Download(self):
        home = os.path.expanduser('~')
        filename=home+"/MoefouDownload/"+self.player.namelist[self.player.index]+".mp3"
        if os.path.exists(filename):
            return
        urlopen = urllib.URLopener()
        fp=urlopen.open(self.player.list[self.player.index])
        data = fp.read()
        fp.close()
        file=open(filename,'w+b')
        file.write(data)
        file.close()        
        
    def Nextr_click(self,event):
        self.player.NextRadio()
        self.rlabel.set_text(player.radiolist[player.rindex])
        self.window.set_title('萌否电台——'+self.player.namelist[self.player.index])
        response=urllib2.urlopen(self.player.piclist[self.player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        
    def Previousr_click(self,event):
        self.player.PreviousRadio()
        self.rlabel.set_text(player.radiolist[player.rindex])
        self.window.set_title('萌否电台——'+self.player.namelist[self.player.index])
        response=urllib2.urlopen(self.player.piclist[self.player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        
    def AddRadio(self):
        rpage=2
        while len(self.player.ridlist)<self.player.radiocount:
            url=self.player.GetURL('radio', rpage, self.player.channel)
            response=urllib2.urlopen(url)
            data=response.read()
            moe=json.loads(data)
            i=0
            while i<len(moe["response"]["wikis"]):
                self.player.ridlist.append(moe["response"]["wikis"][i]["wiki_id"])
                self.player.radiolist.append(moe["response"]["wikis"][i]["wiki_title"])
                i=i+1
            rpage=rpage+1
        
    def on_message(self, bus, message):
        e=gtk.gdk.Event(gtk.gdk.NOTHING)
        t = message.type
        if t == gst.MESSAGE_ERROR:
            self.Next_click(e)
        elif t == gst.MESSAGE_EOS:
            self.Next_click(e)
            
player=MoePlayer()
MainFrame(player)
gtk.gdk.threads_init()
gtk.main()


