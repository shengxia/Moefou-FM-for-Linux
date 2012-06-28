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
import urllib2
import gtk


class MoePlayer:
    def __init__(self):
        self.url="http://moe.fm/listen/playlist?api=json&api_key=ec8fd84d73ba19810b162b4999528da904fe50066"
        self.list=[]
        self.piclist=[]
        self.namelist=[]
        self.index=0
        self.player=gst.element_factory_make("playbin", "player")
        self.GetList()

    def GetList(self):
        page=urllib2.urlopen(self.url)
        data=page.read()
        moe=json.loads(data)
        i=0
        while i< len(moe['response']['playlist']):
            self.list.append(moe['response']['playlist'][i]["url"])
            self.piclist.append(moe['response']['playlist'][i]["cover"]["square"])
            self.namelist.append(moe['response']['playlist'][i]["title"])
            i=i+1
            
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
        self.window.set_title("萌否电台——"+player.namelist[self.player.index])
        self.window.set_default_size(576, 192)
        self.window.connect("destroy", gtk.main_quit, "WM destroy")
        self.window.set_resizable(False)
        self.image=gtk.Image()
        response=urllib2.urlopen(player.piclist[player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        self.image.show()
        self.start=gtk.Button()
        startpic=gtk.Image()
        startpic.set_from_file("start.jpg")
        startpic.show()
        self.start.add(startpic) 
        self.start.show()
        self.start.connect("clicked", self.Play_click)
        self.next=gtk.Button()
        nextpic=gtk.Image()
        nextpic.set_from_file("next.jpg")
        nextpic.show()
        self.next.add(nextpic) 
        self.next.show()
        self.next.connect("clicked",self.Next_click)
        hbox = gtk.HBox()
        self.window.add(hbox)
        hbox.set_border_width(10)
        hbox.pack_start(gtk.Label())
        hbox.pack_start(self.image, False)
        hbox.pack_start(self.start, False)
        hbox.pack_start(self.next, False)
        hbox.add(gtk.Label())
        bus=self.player.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        self.window.show_all()
    
    def Play_click(self,event):
        states=self.player.player.get_state()
        childimage = self.start.get_child()
        isPaused=gst.STATE_PAUSED in states
        isPlay=gst.STATE_PLAYING in states
        self.player.Play(isPaused,isPlay)
        if isPaused:
            childimage.set_from_file("start.jpg")
        elif isPlay:
            childimage.set_from_file("pause.jpg")
            
    def Next_click(self,event):
        self.player.Next()
        self.window.set_title("萌否电台——"+self.player.namelist[self.player.index])
        response=urllib2.urlopen(self.player.piclist[self.player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        
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


