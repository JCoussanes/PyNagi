#!/bin/env python2.7
# -*- coding: utf8 -*-

import irclib
import ircbot
import re
from functions import *
import thread
import time
import signal
import os

class Pynagi(ircbot.SingleServerIRCBot):

    def __init__(self,server,port,channel,nickname,dat_file,global_check_interval,icinga_check_interval,to_show,global_announcement):
        """Constructor of PyNagi."""

        ircbot.SingleServerIRCBot.__init__(self, [(server, port)],nickname, "Icinga checker bot",0)

        self.chan = channel #The chanel PyNagi must connect
        self.server = server #The server PyNagi must connect
        self.nickname = nickname #The nickname of PyNagi
        self.port = port #The port PyNagi should use
        self.file_name = dat_file #The path of the icinga dat file
        self.global_check_interval = global_check_interval #The interval between two check
        self.global_announcement = global_announcement #Does PyNagi should check status automaticly? (boolean)
        self.icinga_check_interval=icinga_check_interval #The interval icinga take to update the dat file
        self.toShow=to_show #The state of what should be shown (1 : all problems ; 2 : critical problems)

        self.lh=[] #The list of hosts
        self.ls=[] #The list of services
        self.prev_stats="" #Storage of the previous status
        self.re_to_me=re.compile(nickname+":\s*(-{1,2}\S+[\s?\S+]?)$") #The regular expression to catch PyNagi highlight
        self.run=True #True if the bot is running
        self.global_run=False #True while the global annoucement thread is running

        signal.signal(signal.SIGINT,self.handler) #Way to be sure to close all thread bfore quitting

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

        if "--resend"==message or "-r"==message:
            self.check_nagios_status(serv,author)

        elif "--stats"==message or "-s"==message:
            serv.privmsg(author,self.prev_stats)

        elif "--reload"==message or "-R"==message:
            self.lh,self.ls = parse_dat_file(self.file_name)
            self.prev_stats=calc_stat(self.lh,self.ls,datetime.now())
            serv.privmsg(author,"PyNagi status are reloaded.")

        elif "--check"==message or "-c"==message:
            self.is_icinga_still_alive(serv,author)

        elif "--show all"==message or "-sa"==message:
            self.toShow=1
            serv.privmsg(self.chan,"From now PyNagi will show all.")

        elif "--show critical"==message or "-sc"==message:
            self.toShow=2
            serv.privmsg(author,"From now PyNagi will show critical only.")

        elif "--global on"==message or "-go"==message:
            self.global_run=True
            serv.privmsg(author,"Global annoucement is now enable.")

        elif "--global off"==message or "-gf"==message:
            self.global_run=False
            serv.privmsg(author,"Global annoucement is now disable.")

        elif "--quit"==message or "-q"==message:
            self.quit()

        elif "--help"==message or "-h"==message:
            serv.privmsg(author,"""        --help [-h] : show the list of PyNagi commands""")
            serv.privmsg(author,"""        --resend [-r] : Resend the last known problems""")
            serv.privmsg(author,"""        --stats [-s] : Returns the number of criticals/warnings/etc""")
            serv.privmsg(author,"""        --reload [-R] : Completely forced reload the nagios status""")
            serv.privmsg(author,"""        --check [-c] : Check if nagios is still running""")
            serv.privmsg(author,"""        --show critical/all [-sc\-sa] : Change the type of errors shown to critical only/all""")
            serv.privmsg(author,"""        --global on/off [-go\-gf] : enable/disable global annoucement""")
            serv.privmsg(author,"""        --quit [-q] : close PyNagi""")

        else:
            serv.privmsg(author,"""Unknown comand. Use "--help" or "-h" to see all command. """)

    def global_check(self,serv,chan):
        """ Method which is run as a thread to apply the global annoucement """
        self.lh,self.ls = parse_dat_file(self.file_name)
        self.prev_stats=calc_stat(self.lh,self.ls,datetime.now())
        self.check_nagios_status(serv,chan)
        serv.privmsg(chan,self.prev_stats)
        while self.run==True:
            if self.global_announcement:
                #This part has the same role as time.sleep(self.global_check_interval) but it allow the program to be quit properly
                #without waiting the end of the sleeping time. And of course if the program is quit in the middle of a loop nothing is sent to IRC.
                i=0
                while i<(self.global_check_interval*60):
                    time.sleep(1)
                    if self.run==True and self.global_run==True:
                        i=i+1
                        print(i)
                    else:
                        break;
                if i==(self.global_check_interval*60):
                    self.lh,self.ls = parse_dat_file(self.file_name)
                    self.prev_stats=calc_stat(self.lh,self.ls,datetime.now())
                    self.check_nagios_status(serv,chan)
                    serv.privmsg(chan,self.prev_stats)
        self.global_run=False

    def check_nagios_status(self,serv,author):
        """ Method which is used to show problems on IRC """

        for e in self.lh:
            if should_i_show(e,self.toShow):
                serv.privmsg(author,e.status(datetime.now()))
        for e in self.ls:
            if should_i_show(e,self.toShow):
                serv.privmsg(author,e.status(datetime.now()))

    def handler(self,signum,frame):
        """ Handler used to close all threads with ctrl+C"""
        self.quit()

    def quit(self):
        """ Method called to close the program properly """
        self.run=False
        while self.global_run==True:
            time.sleep(1)
        ircbot.SingleServerIRCBot.die(self, 'PyNagi is closed.')

    def is_icinga_still_alive(self,serv,author):
        """ Method which check if icinga is still alive by comparing the time of the call and the time of the last modification """

        lastModification = time.ctime(os.stat(self.file_name).st_mtime)
        lastModification = time.strptime(lastModification, "%a %b %d %H:%M:%S %Y")
        lastModification = time.strftime("%Y/%m/%d - %H:%M:%S", lastModification)

        test = time.ctime(time.time()-(self.icinga_check_interval*60))
        test = time.strptime(test, "%a %b %d %H:%M:%S %Y")
        test = time.strftime("%Y/%m/%d - %H:%M:%S", test)

        if lastModification < test:
            serv.privmsg(author,"Last modification was : "+lastModification)
            serv.privmsg(author,"It should be at most : "+test)
            serv.privmsg(author,"Icinga is not alive.")
        else:
            serv.privmsg(author,"Icinga is alive.")



if __name__ == "__main__":
    param=parse_conf_file("external_files/pynagi.conf")
    Pynagi(param["server"],param["port"],param["channel"],param["nickname"],param["dat_file"],param["global_check_interval"],param["icinga_check_interval"],param["to_show"],param["global_announcement"]).start()

