#!/usr/bin/env python3
#utf8

# Jérôme COUSSANES
# 22 october 2012


import re


def parse_filedat(filename):
    '''Read the file and return all data in a list of dictionary.'''

    re_section=re.compile("(\S+)\s*{")
    re_content=re.compile("(\S+)\s*=\s*(\S+)")
    data_list=[]
    i=-1

    with open(filename,"r") as filedat:
        for line in filedat:
            line=line.strip()

            section=re_section.match(line)

            if section:
                # New section
                i+=1
                data_list.append({"section":section.group(1),"content":{}})
            else:
                # New content line in the current section
                content=re_content.match(line)
                if content:
                    data_list[i]["content"][content.group(1)]=content.group(2)

    return l_fichier
