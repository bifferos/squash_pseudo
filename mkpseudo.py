#!/usr/bin/env python3

"""
   Process the output of unsquashfs -li type of command from squashfstools, to produce a list of pseudo-file definitions.

   Usage:   
   unsquashfs -lln <image> | mkpseudo.py > spec.txt
"""

import re
import sys


ATTRIBS = r"(?P<attribs>[-rwxstST]{9}) (?P<uid>\d+)/(?P<gid>\d+)"
DATE = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\s+(?P<hour>\d{2}):(?P<minute>\d{2})"
match_types = {
  "s" : re.compile("^l" + ATTRIBS + r"\s+\d+\s+" + DATE + r" squashfs-root(?P<path>.*) -> (?P<target>.*)$"),
  "d" : re.compile("^d" + ATTRIBS + r"\s+\d+\s+" + DATE + r" squashfs-root(?P<path>.*)$"),
  "f" : re.compile("^-" + ATTRIBS + r"\s+\d+\s+" + DATE + r" squashfs-root(?P<path>.*)$"), 
}


def parse(txt):
    for ftype in match_types.keys():
        m = match_types[ftype].match(txt)
        if m:
            d = m.groupdict()
            if d["path"] == '':
                d["path"] = '/'
            d["ftype"] = ftype
            attr = d["attribs"]
            d["chmod"] = eval("0b" + attr[2::3].translate("".maketrans("x-stST","001111")) + attr.translate("".maketrans("rwxst-ST","11111000")))
            return d
    return {"ftype" : None}


if __name__ == "__main__":
    while True:
        line = sys.stdin.readline()
        if line == '':
            break
        d = parse(line.strip())
        ftype = d["ftype"]
        
        if ftype == "f":
            print("%(path)s f %(chmod)04o %(uid)s %(gid)s cat squashfs-root%(path)s" % d)
        elif ftype == "d":
            print("%(path)s d %(chmod)04o %(uid)s %(gid)s" % d)
        elif ftype == "s":
            print("%(path)s s 0 %(uid)s %(gid)s %(target)s" % d)

