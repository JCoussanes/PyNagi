#!/bin/env python
#utf8

from datetime import datetime

class DatObjectManager:

    def __init__(self):
        self.dolist = {"service": {}, "host": {}}

    def getHost(self, hostname):
        if hostname not in self.dolist["host"]:
            self.dolist["host"][hostname] = Host(hostname)
        return self.dolist["host"][hostname]

    def setHost(self, obj):
        self.dolist["host"][obj.hostname] = obj
    
    def getService(self, hostname, description):
        if hostname not in self.dolist["service"]:
            self.dolist["service"][hostname] = {}
        if description not in self.dolist["service"][hostname]:
            self.dolist["service"][hostname][description] = Service(hostname, description)
        return self.dolist["service"][hostname][description]

    def setService(self, obj):
        if obj.hostname not in self.dolist["service"]:
            self.dolist["service"][obj.hostname] = {}
        self.dolist["service"][obj.hostname][obj.description] = obj
    
    def hostStateChanged(self, obj):
        oldHost = self.getHost(obj.hostname)
        return oldHost.stateChanged(obj)
    
    def serviceStateChanged(self, obj):
        oldService = self.getService(obj.hostname, obj.description)
        return oldService.stateChanged(obj)

    def updateAllAndGetDiff(self, hostlist, servicelist):
        for host in hostlist:
            if self.hostStateChanged(host):
                yield host
            self.setHost(host)
        for service in servicelist:
            if self.serviceStateChanged(service):
                yield service
            self.setService(service)

    def getIssues(self):
        for obj in self.dolist["host"]:
            host = self.dolist["host"][obj]
            if host.state > 0:
                yield host
            else:
                for service in self.dolist["service"][host.hostname]:
                    if self.dolist["service"][host.hostname][service].state > 0:
                        yield self.dolist["service"][host.hostname][service]

class DatObject:
    
    def stateChanged(self, other):
        if self.state != other.state:
            return True
        return False

    def status(self):
        raise NotImplementedError
    
    def strState(self):
        raise NotImplementedError
        

class Service(DatObject):
    '''Data structure which contain all service usefull information'''

    def __init__(self, hostname="", description=""):
        self.hostname=hostname
        self.description=description
        self.state=0
        self.plugin=""

    def strState(self):

        if self.state==0:
            return "OK"
        elif self.state==1:
            return "WARNING"
        elif self.state==2:
            return "CRITICAL"

    def status(self):
        return "[%s][%s %s][%s] %s" % (datetime.now().strftime("%d/%m/%Y %H:%M"), self.hostname, self.description, self.strState(), self.plugin)


class Host(DatObject):
    '''Data structure which contain all host usefull information'''

    def __init__(self, hostname=""):
        self.hostname=hostname
        self.state=0
        self.plugin=""

    def strState(self):

        if self.state==0:
            return "UP"
        elif self.state==1:
            return "DOWN"
        elif self.state==2:
            return "UNREACHABLE"
        elif self.state==3:
            return "PENDING"
    
    def status(self):
        return "[%s][%s][%s] %s" % (datetime.now().strftime("%d/%m/%Y %H:%M"), self.hostname, self.strState(), self.plugin)


