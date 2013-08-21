# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 16:50:26 2012

Paul J. Durack 20th March 2012

This script builds *.xml files for all "interesting" model variables

PJD 21 Mar 2012     - Consider advice regarding CPU-bound tasks parallelisation with multiprocessing module 
                      http://eli.thegreenplace.net/2012/01/16/python-parallelizing-cpu-bound-tasks-with-multiprocessing/
                      also worth considering the subprocess module http://docs.python.org/library/subprocess.html

@author: durack1
"""

import cdutil,Queue,threading,time
import cdms2 as cdms

def threadAnn(variable,ilat1,ilat2):
	s = variable(latitude=slice(ilat1,ilat2),longitude=slice(0,5))
	s_ann = cdutil.YEAR(s)
	return s

# Declare things
infile =
'/work/durack1/Shared/cmip5.HadCM3.historical.r6i1p1.mo.sos.ver-v20110728.xml'
# Open file, grab variable and close
f_in = cdms.open(infile)
variable = f_in('sos')
f_in.close()
print "file opened, read and closed..\n"

# Try serial
start_time = time.time() ; # Set time counter
sos_ann = cdutil.YEAR(variable(latitude=slice(0,5),longitude=slice(0,5)))
; # Limit to a 5x5 x,y point
time_since_start = time.time() - start_time ; time_since_start_s =
'%08.8f' % time_since_start
print "".join(["time1: ",time_since_start_s,'secs'])

# Try threaded
start_time = time.time() ; # Set time counter
q = Queue.Queue() ; # Create queue for thread collection
t = threading.Thread(target=threadAnn,args=(q,(variable,0,5)));
t.daemon = True;
t.start()
sos_ann_t = q.get()
time_since_start = time.time() - start_time ; time_since_start_s =
'%08.8f' % time_since_start
print "".join(["time: ",time_since_start_s,'secs'])