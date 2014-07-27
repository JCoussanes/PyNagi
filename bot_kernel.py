#!/bin/env python2.7
# -*- coding: utf8 -*-

import irclib
import ircbot
import re
from parse import *
import thread
import time
import signal

class Pynagi(ircbot.SingleServerIRCBot):

    def __init__(self,server,port,channel,nickname,dat_file,global_check_interval,global_announcement):
        """Constructor of PyNagi."""

        ircbot.SingleServerIRCBot.__init__(self, [(server, port)],nickname, "Icinga checker bot",0)
        self.chan = channel
        self.server = server
        self.nickname = nickname
        self.port = port
        self.file_name = dat_file
        self.global_check_interval = global_check_interval
        self.global_announcement = global_announcement
        self.lh=[]
        self.ls=[]
        self.prev_stats=""
        self.toShow=1
        self.re_to_me=re.compile(nickname+".*(-\S+)$")
        self.run=True
        self.global_run=False
        signal.signal(signal.SIGINT,self.handler)

    def on_welcome(self, serv, ev):
        """Method called when PyNagi is connected to a server."""
        serv.join(self.chan)
        thread.start_new_thread(self.global_check,(serv, self.chan))
        self.global_run=True

    def on_pubmsg(self, serv, ev):
        """Method called when a public message is catch by PyNagi on the chan. It check if someone ask something to PyNagi"""
        auteur = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]

        to_me=self.re_to_me.match(message)
        if to_me:
            cmd=to_me.group(1)
            self.answers(self.chan,cmd,serv)

    def on_privmsg(self, serv, ev):
        """Method called when someone query PyNagi."""
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]
        self.answers(author,message,serv)

    def answers(self, author, message, serv):
        """Method called to set the output according with the user input"""

        if "-resend"==message:
            self.check_nagios_status(serv,author)

        elif "-stats"==message:
            serv.privmsg(author,self.prev_stats)

        elif "-reload"==message:
            self.lh,self.ls = parse_dat_file(self.file_name)
            self.prev_stats=calc_stat(self.lh,self.ls,datetime.now())
            serv.privmsg(author,"PyNagi status are reloaded.")

        elif "-check"==message:
            serv.privmsg(author,"OK, je check.")

        elif "-all"==message:
            self.toShow=1
            serv.privmsg(self.chan,"From now PyNagi will show all.")

        elif "-critical"==message:
            self.toShow=2
            serv.privmsg(author,"From now PyNagi will show critical only.")

        elif "-help"==message:
            serv.privmsg(author,"""        -resend: Resend the last known problems""")
            serv.privmsg(author,"""        -stats: Returns the number of criticals/warnings/etc""")
            serv.privmsg(author,"""        -reload: Completely forced reload the nagios status""")
            serv.privmsg(author,"""        -check: Check if nagios is still running""")
            serv.privmsg(author,"""        -critical: Change the type of errors shown to critical only""")
            serv.privmsg(author,"""        -all: Change the type of errors shown to all""")
        else:
            serv.privmsg(author,"""Unknown comand. Use "-help" to see all command. """)

    def global_check(self,serv,chan):
        while self.run==True:
            self.lh,self.ls = parse_dat_file(self.file_name)
            self.prev_stats=calc_stat(self.lh,self.ls,datetime.now())
            self.check_nagios_status(serv,chan)
            if self.global_announcement:
                serv.privmsg(chan,self.prev_stats)
            time.sleep(self.global_check_interval)
        self.global_run=False

    def check_nagios_status(self,serv,author):

        for e in self.lh:
            if should_i_show(e,self.toShow):
                serv.privmsg(author,e.status(datetime.now()))
        for e in self.ls:
            if should_i_show(e,self.toShow):
                serv.privmsg(author,e.status(datetime.now()))

    def handler(self,signum,frame):
        self.run=False
        while self.global_run==True:
            time.sleep(1)


if __name__ == "__main__":
    Pynagi("irc.rivlink.net",6667,"#testRivIRC","pynagi","resource/status_icinga.dat",5,True).start()

