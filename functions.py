#!/usr/bin/env python3
#utf8

# Jerome COUSSANES
# 22 october 2012


import re
from classes import *
import thread
import time

def parse_dat_file(file_path):
    '''Read the file and return all data in a list of dictionary'''

    re_section=re.compile("(\S+)\s*{")
    re_content=re.compile("(\S+)\s*=\s*(.+)")
    l_host=[]
    l_service=[]
    iH=-1
    iS=-1
    H=False

    with open(file_path,"r") as dat_file:
        for line in dat_file:
            line=line.strip()

            section=re_section.match(line)

            if section:
                # New section
                if section.group(1)=="hoststatus":
                    l_host.append(Host())
                    iH+=1
                    H=True
                elif section.group(1)=="servicestatus":
                    l_service.append(Service())
                    iS+=1
                    H=False
            else:
                # New content line in the current section
                content=re_content.match(line)
                if content:
                    if content.group(1)=="current_state" and H==True:
                        l_host[iH].state=int(content.group(2))
                    elif content.group(1)=="host_name" and H==True:
                        l_host[iH].hostname=content.group(2)
                    elif content.group(1)=="current_state" and H==False:
                        l_service[iS].state=int(content.group(2))
                    elif content.group(1)=="host_name" and H==False:
                        l_service[iS].hostname=content.group(2)
                    elif content.group(1)=="plugin_output" and H==True:
                        l_host[iH].plugin=content.group(2)
                    elif content.group(1)=="plugin_output" and H==False:
                        l_service[iS].plugin=content.group(2)
                    elif content.group(1)=="service_description":
                        l_service[iS].description=content.group(2)
        return l_host,l_service

def parse_conf_file(file_path):
    ''' Read the param.comf file and extract every parameters in a dictionary '''
    re_conf=re.compile("(\S+)\s*=\s*(\S+)")
    l_param={}

    with open(file_path,"r") as conf_file:
        for line in conf_file:
            line=line.strip()

            l_tmp=line.split("--",1)

            conf=re_conf.match(l_tmp[0])
            if conf:
                if conf.group(1) in ["port","global_check_interval","icinga_check_annoucement","to_show"]:
                    l_param[conf.group(1)]=int(conf.group(2))
                elif conf.group(1)=="global_announcement" and conf.group(2)==0:
                    l_param[conf.group(1)]=False
                elif conf.group(1)=="global_announcement" and conf.group(2)==1:
                    l_param[conf.group(1)]=True
                else:
                    l_param[conf.group(1)]=conf.group(2)
    return l_param


def calc_stat(lh,ls,now):
    up=down=unre=pend=ok=warn=crit=0

    for e in lh:
        if e.state==0:
            up+=1
        elif e.state==1:
            down+=1
        elif e.state==2:
            unre+=1
        elif e.state==3:
            pend+=1

    for e in ls:
        if e.state==0:
            ok+=1
        elif e.state==1:
            warn+=1
        elif e.state==2:
            crit+=1

    return now.strftime("[%Y/%b/%d %H:%M:%S]")+" Critical: "+str(crit)+", warning: "+str(warn)+", ok: "+str(ok)+", up: "+str(up)+", down: "+str(down)+", unreachable: "+str(unre)+", pending: "+str(pend)

def should_i_show(e,shown):

    if e.state >= shown:
        return True
    return False


if __name__ == "__main__":
    l1,l2=parse_dat_file("resource/status_icinga.dat")

    print("Host list: ")
    for e in l1:
        print(e.status(datetime.now()))

    print("\nService list: ")
    for e in l2:
        print(e.status(datetime.now()))

    print("\n\n"+calc_stat(l1,l2))

