#!/bin/env python2.7
# -*- coding: utf8 -*-

import irclib
import ircbot
import re
from functions import *
from classes import *
from threading import Lock, Timer
import time
import signal
import os

class Pynagi(ircbot.SingleServerIRCBot):

    def __init__(self,server,port,channel,nickname,dat_file,icinga_check_interval,to_show):
        """Constructor of PyNagi."""

        ircbot.SingleServerIRCBot.__init__(self, [(server, port)],nickname, "Icinga checker bot",0)

        self.chan = channel #The chanel PyNagi must connect
        self.server = server #The server PyNagi must connect
        self.nickname = nickname #The nickname of PyNagi
        self.port = port #The port PyNagi should use
        self.file_name = dat_file #The path of the icinga dat file
        self.icinga_check_interval = icinga_check_interval #The interval icinga take to update the dat file
        self.to_show = to_show #The state of what should be shown (1 : all problems ; 2 : critical problems)

        self.domanager = DatObjectManager()
        self.prev_stats = "" #Storage of the previous status
        self.re_to_me = re.compile("(?:^|\s+)"+nickname+":\s*(.*)$") #The regular expression to catch PyNagi highlight
        self.timer = None #Thread.Timer object for loop announcement
        self.global_run_lock = Lock() #True while the global annoucement thread is running

        signal.signal(signal.SIGINT,self.handler) #Way to be sure to close all thread before quitting

    def on_welcome(self, serv, ev):
        """Method called when PyNagi is connected to a server."""
        serv.join(self.chan)
        self.timer = Timer(1.0, self.global_check, (serv, self.chan))
        self.timer.start()

    def on_pubmsg(self, serv, ev):
        """Method called when a public message is caught by PyNagi on the chan. It check if someone ask something to PyNagi"""
        auteur = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]

        to_me = self.re_to_me.match(message)
        if to_me:
            cmd = to_me.group(1)
            self.answers(self.chan,cmd,serv)

    def on_privmsg(self, serv, ev):
        """Method called when someone query PyNagi."""
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]
        self.answers(author,message,serv)

    def answers(self, author, message, serv):
        """Method called to set the output according with the user input"""
        message = message.lower()
        if "resend"==message:
            self.check_nagios_status(serv,author,self.domanager.getIssues())

        elif "stats"==message:
            serv.privmsg(author,self.prev_stats)

        elif "check"==message:
            self.is_icinga_still_alive(serv,author)

        elif "set show all"==message:
            self.to_show=1
            serv.privmsg(self.chan,"Messages mode set to ALL.")

        elif "set show critical"==message:
            self.to_show=2
            serv.privmsg(author,"Messages mode set to CRITICAL.")

        elif "set global on"==message:
            serv.privmsg(author,"Global announcement enabled.")

        elif "set global off"==message:
            serv.privmsg(author,"Global announcement disabled.")

        elif "quit"==message:
            self.quit()

        elif "help"==message:
            serv.privmsg(author, "help : show the list of PyNagi commands")
            serv.privmsg(author, "resend : Resend the last known problems")
            serv.privmsg(author, "stats : Returns the number of criticals/warnings/etc")
            serv.privmsg(author, "reload : Force reloading the nagios/icinga status")
            serv.privmsg(author, "check : Check if nagios/icinga is still running")
            serv.privmsg(author, "set show critical/all : Change the type of errors shown to critical only/all")
            serv.privmsg(author, "set global on/off : enable/disable global announcement")
            serv.privmsg(author, "quit : shutdown the bot")

        else:
            serv.privmsg(author,"""Unknown command. Use "help" to see all commands.""")

    def global_check(self,serv,chan):
        """ Method which is run as a thread to apply the global announcement """
        with self.global_run_lock:
            lh,ls = parse_dat_file(self.file_name)
            changes = self.domanager.updateAllAndGetDiff(lh, ls)
            self.prev_stats = calc_stat(lh,ls,datetime.now())
            self.check_nagios_status(serv,chan,changes)
            self.timer = Timer(self.icinga_check_interval, self.global_check, (serv, chan))
            self.timer.start()

    def check_nagios_status(self,serv,author,changes):
        """ Method which is used to show problems on IRC """

        for change in changes:
            if change.show(self.to_show):
                serv.privmsg(author,change.status())

    def handler(self,signum,frame):
        """ Handler used to close all threads with ctrl+C"""
        self.quit()

    def quit(self):
        """ Method called to close the program properly """
        if self.timer is not None:
            self.timer.cancel()
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
            serv.privmsg(author,"Last modification was : %s" % lastModification)
            serv.privmsg(author,"It should be at most : %s" % test)
            serv.privmsg(author,"Icinga is not alive.")
        else:
            serv.privmsg(author,"Icinga is alive.")



if __name__ == "__main__":
    conf = parse_conf_file("pynagi.conf")
    Pynagi(conf.get("pynagi", "server"), conf.getint("pynagi", "port"), conf.get("pynagi", "channel"), conf.get("pynagi", "nickname"), conf.get("pynagi", "dat_file"), conf.getint("pynagi", "icinga_check_interval"), conf.getint("pynagi", "to_show")).start()

