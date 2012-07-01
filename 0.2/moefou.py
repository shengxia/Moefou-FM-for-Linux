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
                #To get random musics from Moefou
                url="http://moe.fm/listen/playlist?api=json&api_key=ec8fd84d73ba19810b162b4999528da904fe50066"
            else:
                #To get random musics with named channel from Moefou
                url="http://moe.fm/listen/playlist?api=json&api_key=ec8fd84d73ba19810b162b4999528da904fe50066&radio="+str(channel)
        if type=="radio":
            #To get radio channel from Moefou
            url="http://api.moefou.org/wikis.json?wiki_type=radio&perpage=50&api_key=ec8fd84d73ba19810b162b4999528da904fe50066&page="+str(rpage)
        return url
    
    #To get musics' information from Moefou and load them to arrays
    def GetList(self):
        url=self.GetURL("song",0, self.channel)
        response=urllib2.urlopen(url)
        data=response.read()
        moe=json.loads(data)
        i=0
        while i< len(moe['response']['playlist']):
            #Load music list
            self.list.append(moe['response']['playlist'][i]["url"])
            #Load the cd cover list
            self.piclist.append(moe['response']['playlist'][i]["cover"]["square"])
            #Load the music name list
            self.namelist.append(moe['response']['playlist'][i]['title'])
            i=i+1
    
    #To get radio channels' information from Moefou and load them to arrays
    def GetRadio(self):
        #Set the first radio channel
        self.ridlist.append('0')
        self.radiolist.append(u'随便听听')
        #Get the first page of radio channels
        url=self.GetURL('radio', 1 , self.channel)
        response=urllib2.urlopen(url)
        data=response.read()
        moe=json.loads(data)
        #Get the sum of radio channels
        self.radiocount=moe['response']['information']['count']
        i=0
        while i<len(moe["response"]["wikis"]):
            #Load the radio id list
            self.ridlist.append(moe["response"]["wikis"][i]["wiki_id"])
            #Load the radio name list
            self.radiolist.append(moe["response"]["wikis"][i]["wiki_title"])
            i=i+1
     
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
        self.GetList()
        self.index=0
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
        stream=self.list[self.index]
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property('uri', stream)
        self.player.set_state(gst.STATE_PLAYING)
        

class MainFrame():
    def __init__(self,player):
        self.player=player
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('萌否电台——'+player.namelist[self.player.index])
        self.window.set_default_size(576, 192)
        self.window.connect('destroy', gtk.main_quit, 'WM destroy')
        self.window.set_resizable(False)
        #Create a thread to load all radio channel
        th_add=threading.Thread(target=self.AddRadio,args=() ) 
        th_add.start()
        
        #CD cover widget
        self.image=gtk.Image()
        response=urllib2.urlopen(player.piclist[player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())
        self.image.show()
        
        #Start music button widget
        self.start=gtk.Button()
        startpic=gtk.Image()
        startpic.set_from_file('start.png')
        startpic.show()
        self.start.add(startpic) 
        self.start.show()
        self.start.connect('clicked', self.Play_click)
        
        #Next music button widget
        self.next=gtk.Button()
        nextpic=gtk.Image()
        nextpic.set_from_file('next.png')
        nextpic.show()
        self.next.add(nextpic) 
        self.next.show()
        self.next.connect('clicked',self.Next_click)
        
        #Download music button widget
        self.download=gtk.Button()
        dlpic=gtk.Image()
        dlpic.set_from_file('download.png')
        dlpic.show()
        self.download.add(dlpic) 
        self.download.show()
        self.download.connect('clicked',self.Download_click)
        
        #Next radio button widget
        self.nradio=gtk.Button()
        npic=gtk.Image()
        npic.set_from_file('nextradio.png')
        npic.show()
        self.nradio.add(npic) 
        self.nradio.show()
        self.nradio.connect('clicked',self.Nextr_click)
        
        #Previous radio button widget
        self.pradio=gtk.Button()
        ppic=gtk.Image()
        ppic.set_from_file('prevousradio.png')
        ppic.show()
        self.pradio.add(ppic) 
        self.pradio.show()
        self.pradio.connect('clicked',self.Previousr_click)
        
        #A label to display radio channel
        self.rlabel=gtk.Label(player.radiolist[player.rindex])
        self.rlabel.set_usize(136,64)
        ebox=gtk.EventBox()
        ebox.show()
        ebox.add(self.rlabel)
        ebox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        ebox.connect("button_press_event", lambda w,e: self.Label_click())

        mainbox = gtk.HBox()
        controlbox = gtk.VBox()
        buttonbox = gtk.HBox()
        radiobox = gtk.HBox()
        self.window.add(mainbox)
        
        #Box composition
        mainbox.pack_start(self.image, False)
        mainbox.pack_start(controlbox, False)
        
        controlbox.pack_start(radiobox, False)
        controlbox.pack_start(buttonbox, False)
        
        radiobox.set_border_width(10)
        radiobox.pack_start(self.pradio, False)
        radiobox.pack_start(ebox, False)
        radiobox.pack_start(self.nradio, False)
        
        buttonbox.set_border_width(10)
        buttonbox.pack_start(self.download, False)
        buttonbox.pack_start(self.start, False)
        buttonbox.pack_start(self.next, False)
        
        
        #Create a bus
        bus=self.player.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)
        self.window.show_all()
    
    def Play_click(self,event):
        #Get current play states
        states=self.player.player.get_state()
        #Get image on button
        childimage = self.start.get_child()
        #To judge the play state 
        isPaused=gst.STATE_PAUSED in states
        isPlay=gst.STATE_PLAYING in states
        self.player.Play(isPaused,isPlay)
        if isPaused:
            childimage.set_from_file('start.png')
        elif isPlay:
            childimage.set_from_file('pause.png')
            
    def Next_click(self,event):
        self.player.Next()
        self.Change()
        
    def Download_click(self,event):
        #Make a dir in '~'
        home = os.path.expanduser('~')
        if not(os.path.exists(home+"/MoefouDownload")):
            os.mkdir(home+"/MoefouDownload")
        #Create a thread to download music
        th=threading.Thread(target=self.Download,args=() ) 
        th.start()
    
    def Download(self):
        home = os.path.expanduser('~')
        filename=home+"/MoefouDownload/"+self.player.namelist[self.player.index]+".mp3"
        if os.path.exists(filename):
            return
        #Get and save the data from Moefou
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
        self.Change()
        
    def Previousr_click(self,event):
        self.player.PreviousRadio()
        self.rlabel.set_text(player.radiolist[player.rindex])
        self.Change()
        
    def Label_click(self):
        self.player.rindex=0
        self.player.index=0
        self.rlabel.set_text(player.radiolist[player.rindex])
        self.player.InitList()
        self.Change()
    
    def Change(self):
        self.window.set_title('萌否电台——'+self.player.namelist[self.player.index])
        #Get new CD cover and change the old one
        response=urllib2.urlopen(self.player.piclist[self.player.index])
        loader=gtk.gdk.PixbufLoader()
        loader.write(response.read())
        loader.close()  
        self.image.set_from_pixbuf(loader.get_pixbuf())

    #To add the remained radio channel in a thread
    def AddRadio(self):
        rpage=2
        #When the radio channel counts have got not equal to the sum of radio channel 
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
            #Get next page
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


