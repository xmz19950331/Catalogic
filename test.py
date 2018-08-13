import json
import os
basedir = os.path.abspath(os.path.dirname(__file__))
with open(basedir + '/logfiles/JobLog_vmware_SLAVM_1528731600187_1528731683585.csv', 'r') as f:
	lines = []
	for l in f:
		lines.append(l)

with open(basedir + '/logfiles/test.csv', 'a+') as f:
	for l in lines:
		f.write(l)