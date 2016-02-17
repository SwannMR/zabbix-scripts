#!/usr/bin/env python
"""
Read the mountstats from the python pickle object
"""

import pickle
import sys

arguments = len(sys.argv)

try:
	input_pickle = open("/tmp/nfs-mountstats", "rb")
except:
	print ("Can't access /tmp/mountstats")
	sys.exit()

mountstats = pickle.load(input_pickle)

if arguments == 2:
	mountpoint = sys.argv[1]
	print mountstats[mountpoint]
if arguments == 3:
	mountpoint = sys.argv[1]
	operation = sys.argv[2]
	print mountstats[mountpoint][operation]
if arguments == 4:
	mountpoint = sys.argv[1]
	operation = sys.argv[2]
	stat = sys.argv[3]
	print mountstats[mountpoint][operation][stat]


