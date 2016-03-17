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
import sys
import threading 
import pynotify
from moeplayer import MoePlayer

class MainFrame():
    def __init__(self,player):
        self.player=player
        gr=threading.Thread(target=self.player.GetRadio,args=()) 
        gr.start()
        message=""
        pynotify.init(u"萌否电台")
        self.n = pynotify.Notification(u"萌否电台")
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_default_size(576, 192)
        self.window.connect('destroy', gtk.main_quit, 'WM destroy')
        self.window.set_resizable(False)
        self.window.set_icon_from_file(sys.path[0]+"/pic/icon.jpg")
        
        #CD cover widget
        self.image=gtk.Image()
        response=urllib2.urlopen(player.piclist[player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        self.image.show()
        
        #Start music button widget
        sebox=gtk.EventBox()
        self.startpic=gtk.Image()
        self.startpic.set_from_file(sys.path[0]+'/pic/play.png')
        self.startpic.show()
        sebox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        sebox.add(self.startpic) 
        sebox.show()
        sebox.connect("button_press_event", lambda w,e: self.Play_click())
        
        #Next music button widget
        nebox=gtk.EventBox()
        nextpic=gtk.Image()
        nextpic.set_from_file(sys.path[0]+'/pic/next.png')
        nextpic.show()
        nebox.add(nextpic) 
        nebox.show()
        nebox.connect("button_press_event", lambda w,e: self.Next_click())
        
        #Download music button widget
        debox=gtk.EventBox()
        dlpic=gtk.Image()
        dlpic.set_from_file(sys.path[0]+'/pic/save.png')
        dlpic.show()
        debox.add(dlpic) 
        debox.show()
        debox.connect("button_press_event", lambda w,e: self.Download_click())
        
        #Next radio button widget
        nrebox=gtk.EventBox()
        npic=gtk.Image()
        npic.set_from_file(sys.path[0]+'/pic/change.png')
        npic.show()
        nrebox.add(npic) 
        nrebox.show()
        nrebox.connect("button_press_event", lambda w,e:self.Nextr_click())
        
        #Previous radio button widget
        prebox=gtk.EventBox()
        ppic=gtk.Image()
        ppic.set_from_file(sys.path[0]+'/pic/back.png')
        ppic.show()
        prebox.add(ppic) 
        prebox.show()
        prebox.connect("button_press_event", lambda w,e:self.Previousr_click())
        
        #A label to display radio channel
        rbebox=gtk.EventBox()
        bpic=gtk.Image()
        bpic.set_from_file(sys.path[0]+'/pic/return.png')
        bpic.show()
        rbebox.add(bpic) 
        rbebox.show()
        rbebox.connect("button_press_event", lambda w,e:self.Back_click())
        
        mebox=gtk.EventBox()
        ipic=gtk.Image()
        ipic.set_from_file(sys.path[0]+'/pic/info.png')
        ipic.show()
        mebox.add(ipic) 
        mebox.show()
        mebox.connect("button_press_event", lambda w,e:self.Info_click())

        mainbox = gtk.HBox()
        controlbox = gtk.VBox()
        lowbox = gtk.HBox()
        upbox = gtk.HBox()
        midbox = gtk.HBox()
        self.window.add(mainbox)
        
        #Box composition
        mainbox.pack_start(self.image, False)
        mainbox.pack_start(controlbox, False)
        
        controlbox.pack_start(upbox, False)
        controlbox.pack_start(midbox, False)
        controlbox.pack_start(lowbox, False)
        
        upbox.pack_start(prebox, False)
        upbox.pack_start(mebox, False)
        
        midbox.pack_start(rbebox, False)
        midbox.pack_start(nrebox, False)
        
        lowbox.pack_start(sebox, False)
        lowbox.pack_start(nebox, False)
        lowbox.pack_start(debox, False)
        
        #Create a bus
        bus=self.player.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)
        if self.player.isconnect:
            self.window.set_title('萌否电台——'+player.radiolist[player.rindex])
        else:
            self.window.set_title('萌否电台——网络不稳定')
        self.window.show_all()
    
    def Play_click(self):
        #Get current play states
        states=self.player.player.get_state()
        #To judge the play state 
        isPaused=gst.STATE_PAUSED in states
        isPlay=gst.STATE_PLAYING in states
        self.player.Play(isPaused,isPlay)
        if isPaused:
            self.startpic.set_from_file(sys.path[0]+'/pic/play.png')
            self.Info_click()
        elif isPlay:
            self.startpic.set_from_file(sys.path[0]+'/pic/pause.png')
        self.Checknet()
            
    def Next_click(self):
        self.player.Next()
        self.Change()
        self.Checknet()
        
    def Download_click(self):
        if not self.player.isconnect:
            message=u"网络不稳定，无法下载"
            self.Checknet(message)
            return
        #Make a dir in '~'
        home = os.path.expanduser('~')
        if not(os.path.exists(home+"/MoefouDownload")):
            os.mkdir(home+"/MoefouDownload")
        m=u"正在下载"+self.player.namelist[self.player.index]+".mp3"
        self.n.update(u"萌否电台", m)
        self.n.show()
        #Create a thread to download music
        th=threading.Thread(target=self.Download,args=()) 
        th.start()
    
    def Download(self):
        home = os.path.expanduser('~')
        filename=home+"/MoefouDownload/"+self.player.namelist[self.player.index]+".mp3"
        if os.path.exists(filename):
            return
        #Get and save the data from Moefou
        try:
            fp=urllib2.urlopen(self.player.list[self.player.index],timeout=2)
        except urllib2.URLError, e:
            self.player.isconnect=False
            message=u"网络不稳定，无法下载"
            self.Checknet(message)
            return
        data = fp.read()
        fp.close()
        file=open(filename,'w+b')
        file.write(data)
        file.close()    
        m=self.player.namelist[self.player.index]+u".mp3 已保存至"+home+u"/MoefouDownload/"
        self.n.update(u"萌否电台", m)
        n.show()
        
    def Nextr_click(self):
        self.player.NextRadio()
        self.Change()
        self.Checknet()
        
    def Previousr_click(self):
        self.player.PreviousRadio()
        self.Change()
        self.Checknet()
        
    def Back_click(self):
        self.player.rindex=0
        self.player.index=0
        self.player.InitList()
        self.Change()
        self.Checknet()
        
    def Info_click(self):
        if self.player.isconnect:
            message=u"正在播放："+self.player.namelist[self.player.index]+"\n"
            message=message+u"当前电台："+self.player.radiolist[self.player.rindex]+"\n"
            message=message+u"歌手："+self.player.artlist[self.player.index]+"\n"
            message=message+u"曲目专辑："+self.player.wikilist[self.player.index]
            self.n.update(u"萌否电台", message)
            self.n.show()
        else:
            message=u"网络不稳定，无法获取曲目信息。"
            self.Checknet(message)
    
    def Change(self):
        if not self.player.isconnect:
            return
        self.window.set_title('萌否电台——'+self.player.radiolist[self.player.rindex])
        self.Info_click()
        #Get new CD cover and change the old one
        try:
            response=urllib2.urlopen(self.player.piclist[self.player.index],timeout=2)
        except urllib2.URLError, e:
            self.player.isconnect=False
            self.Checknet()
            return
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        
    def Checknet(self,message=u"网络不稳定，无法播放"):
        if not self.player.isconnect:
            self.window.set_title('萌否电台——网络不稳定')
            self.n.update(u"萌否电台", message)
            self.n.show()
    
    def on_message(self, bus, message):
        e=gtk.gdk.Event(gtk.gdk.NOTHING)
        t = message.type
        if t == gst.MESSAGE_ERROR:
            self.Next_click()
        elif t == gst.MESSAGE_EOS:
            self.Next_click()
            
player=MoePlayer()
MainFrame(player)
gtk.gdk.threads_init()
gtk.main()


