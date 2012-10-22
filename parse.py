#!/usr/bin/env python3
#utf8

# Jérôme COUSSANES
# 22 october 2012


import re

# Read the file and return all data in a list of dictionary.
def parse_filedat(filename):
    re_section=re.compile("(\S+)\s+{")
    re_content=re.compile("(\S+)\s*=\s*(\S+)$")
    data_list=[] # Create an empty list which will contain all data
    i=-1

    with open(filename,"r") as filedat: # Open the file named "filename" to read only as filedat
        for line in filedat:
            line=line.strip()

            section=re_section.match(line) # Check if line matches to re_section

            # New section
            if section:
                i+=1
                data_list.append({"section":section.group(1),"content":{}})
            else:
                content=re_content.match(line) # Check if the line matches to re_content

            # New content line in the current section
            if content:
                data_list[i]["content"][content.group(1)]=content.group(2)

    return l_fichier
