#!/usr/bin/env python3
#utf8

# Jérôme COUSSANES
# 22 october 2012


import re


def parse_dat_file(file_name):
    '''Read the file and return all data in a list of dictionary'''

    re_section=re.compile("(\S+)\s*{")
    re_content=re.compile("(\S+)\s*=\s*(\S+)")
    l_data=[]
    i=-1

    with open(file_name,"r") as dat_file:
        for line in dat_file:
            line=line.strip()

            section=re_section.match(line)

            if section:
                # New section
                i+=1
                l_data.append({"section":section.group(1),"content":{}})
            else:
                # New content line in the current section
                content=re_content.match(line)
                if content:
                    l_data[i]["content"][content.group(1)]=content.group(2)

    return l_data
