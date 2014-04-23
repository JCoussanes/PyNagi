#!/bin/env python
#utf8

from datetime import datetime

class Service:
    '''Data structure which contain all service usefull information'''

    def __init__(self):
        self.hostname=""
        self.state=0
        self.description=""
        self.plugin=""

    def strState(self):

        if self.state==0:
            return "Ok"
        elif self.state==1:
            return "Warning"
        elif self.state==2:
            return "Critical"

    def status(self,now):
        return str(now.year)+"/"+str(now.month)+"/"+str(now.day)+"  "+str(now.hour)+":"+str(now.minute)+" "+self.strState()+" "+str(self.hostname)+" "+str(self.description)+" "+str(self.plugin)


class Host:
    '''Data structure which contain all host usefull information'''

    def __init__(self):
        self.hostname=""
        self.state=0
        self.plugin=""

    def strState(self):

        if self.state==0:
            return "Up"
        elif self.state==1:
            return "Down"
        elif self.state==2:
            return "Unreachable"
        elif self.state==3:
            return "Pending"

    def status(self,now):
        return str(now.year)+"/"+str(now.month)+"/"+str(now.day)+"  "+str(now.hour)+":"+str(now.minute)+" "+self.strState()+" "+str(self.hostname)+" "+str(self.plugin)


