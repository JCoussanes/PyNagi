#!/bin/env python2.7
# -*- coding: utf8 -*-

import irclib
import ircbot
import re

class Pynagi(ircbot.SingleServerIRCBot):

    def __init__(self,server,port,channel,nickname):
        """Constructeur qui pourrait prendre des paramètres dans un "vrai" programme."""

        ircbot.SingleServerIRCBot.__init__(self, [(server, port)],nickname, "Bot de modération réalisé en Python avec ircbot",0)
        self.chan = channel
        self.server = server
        self.nickname = nickname
        self.port = port
        self.re_to_me=re.compile(nickname+".*(-\S+)")

    def on_welcome(self, serv, ev):
        """Méthode appelée une fois connecté et identifié. Notez qu'on ne peut rejoindre les canaux auparavant."""
        serv.join(self.chan)

    def on_pubmsg(self, serv, ev):
        """Méthode appelée à la réception d'un message, elle analyse si une commande est entrée à son intention et y réagit."""
        auteur = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]

        to_me=self.re_to_me.match(message)
        if to_me:
            cmd=to_me.group(1)
            if cmd=="-resend":
                serv.privmsg(self.chan,"OK, je resend.")#resend_nagios_status
            elif cmd=="-stat":
                serv.privmsg(self.chan,"OK, je stat.")#calc_statistics()
            elif cmd=="-reload":
                serv.privmsg(self.chan,"OK, je reload.")#reload_statuslog()
            elif cmd=="-check":
                serv.privmsg(self.chan,"OK, je check.")#check_nagios()
            elif cmd=="-show-all":
                serv.privmsg(self.chan,"OK, je show all.")
            elif cmd=="-show-critical":
                serv.privmsg(self.chan,"OK, je show critical.")
            elif cmd=="-help":
                serv.privmsg(self.chan,"""        -resend: Resend the last known problems""")
                serv.privmsg(self.chan,"""        -stat: Returns the number of criticals/warnings/etc""")
                serv.privmsg(self.chan,"""        -reload: Completely forced reload the nagios status""")
                serv.privmsg(self.chan,"""        -check: Check if nagios is still running""")
                serv.privmsg(self.chan,"""        -show-critical: Change the type of errors shown to critical only""")
                serv.privmsg(self.chan,"""        -show-all: Change the type of errors shown to all""")
            else:
                serv.privmsg(self.chan,"""Unknown comand. Use "-help" to see all command. """)

    def on_privmsg(self, serv, ev):
        """Méthode appelée à la réception d'un message privé, elle réagit en fonction de la comande envoyée."""
        author = irclib.nm_to_n(ev.source())
        message = ev.arguments()[0]

        if "-resend"==message:
            serv.privmsg(author,"OK, je resend.")
        elif "-statistics"==message:
            serv.privmsg(author,"OK, je stat.")
        elif "-reload"==message:
            serv.privmsg(author,"OK, je reload.")
        elif "-check"==message:
            serv.privmsg(author,"OK, je check.")
        elif "-show-all"==message:
            serv.privmsg(self.chan,"OK, je show all.")
        elif "-show-critical"==message:
            serv.privmsg(author,"OK, je show critical.")
        elif "-help"==message:
            serv.privmsg(author,"""        -resend: Resend the last known problems""")
            serv.privmsg(author,"""        -statistics: Returns the number of criticals/warnings/etc""")
            serv.privmsg(author,"""        -reload: Completely forced reload the nagios status""")
            serv.privmsg(author,"""        -check: Check if nagios is still running""")
            serv.privmsg(author,"""        -show-critical: Change the type of errors shown to critical only""")
            serv.privmsg(author,"""        -show-all: Change the type of errors shown to all""")
        else:
            serv.privmsg(author,"""Unknown comand. Use "-help" to see all command. """)


if __name__ == "__main__":
    Pynagi("irc.rivlink.net",6667,"#testRivIRC","pynagi").start()

