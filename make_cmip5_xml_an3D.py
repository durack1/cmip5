# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 10:44:35 2012

Paul J. Durack 215th June 2012

This script builds *.xml files for 3D model variables

PJD 15 Jun 2012     - Created hard coded, however it'll work..
PJD 15 Jun 2012     - Sorting date with more rigorously with picntrl files:
                    cmip5.CCSM4.piControl.r1i1p1.an.so.ver-v20120220.1000-999.xml
                    cmip5.GFDL-CM3.piControl.r1i1p1.an.so.ver-v20110601.1-100.xml
PJD 10 Jul 2012     - Regenerated new data, pointing to new directories and rerunning
PJD 10 Jul 2012     - Added realm to xml name
PJD 20 Aug 2012     - Added code to pre-purge xml tree
PJD 19 Feb 2013     - General code tidyup following prompts from pyflakes and rope
PJD  8 May 2013     - Added oceanonly to known host list and added replace loading from string module
PJD 30 May 2013     - Updated counter from 50 to 250 as much larger number of files now exist ~3050
PJD 13 Jun 2013     - Added permissions wash
PJD 13 Jun 2013     - TODO: Figure out what code is purging historical+piControl/ocn/an/so+thetao/*.xml files

@author: durack1
"""

import gc,os,subprocess,sys
from socket import gethostname
from string import replace

# Set directories
host_name = gethostname()
if host_name in {'crunchy.llnl.gov','oceanonly.llnl.gov'}:
    trim_host = replace(host_name,'.llnl.gov','')
    host_path = '/work/durack1/Shared/cmip5/' ; # crunchy 120119
    cdat_path = '/usr/local/uvcdat/latest/bin/'
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

# Change directory to host
os.chdir(host_path)

# Mine source directory and create pathnames
i1 = 0
list_an3D_data_paths = []
for (path, dirs, files) in os.walk(host_path,'false'):
    if files != [] and dirs == [] and (path.find('/ncs/') != -1):
        # Append to list variable
        list_an3D_data_paths += [path]
        if i1 == 0:
            print 'an3D_data:'
        if i1 % 250 == 0:
            print "%03d--" % i1
        i1 = i1 + 1 ; # Increment counter

list_an3D_data_paths.sort() ; # Sort so process alphabetically
del(i1,path,dirs,files)
gc.collect()

# Purge all existing xml files before building below
del_paths = []
for file in list_an3D_data_paths:
    if os.path.join('/'.join(file.split('/')[0:9]),'*.xml') not in del_paths:
        del_paths.append(os.path.join('/'.join(file.split('/')[0:9]),'*.xml'))

for delpath in del_paths:
    cmd = "".join(['rm -f ',delpath])
    print cmd
    # Catch errors with file generation
    ii,o,e = os.popen3(cmd) ;

# Loop through input files
for l in list_an3D_data_paths:
    outfile_bits    = l.split('/')
    #print outfile_bits
    experiment      = outfile_bits[5]
    realm           = outfile_bits[6]
    variable        = outfile_bits[8]
    model           = outfile_bits[10]
    realisation     = outfile_bits[11]
    version         = outfile_bits[12]
    # List files in directory
    files = os.listdir(l); files.sort()
    # piControl files causing grief with year scraping
    years1 = []; years2 = [];
    for l2 in files:
        l3 = l2.split('.')[7]
        years1.append(int(l3.split('-')[0]))
        years2.append(int(l3.split('-')[1]))
    years1.sort(); years2.sort()
    startyr     = min(years1)
    endyr       = max(years2)  
    outfilename     = "".join(['cmip5.',model,'.',experiment,'.',realisation,'.an.',realm,'.',variable,'.',version,'.',str(startyr),'-',str(endyr),'.xml'])
    #print outfilename
    #print years1,years2
    outpath         = os.path.join(host_path,experiment,'ocn','an',variable)
    del(outfile_bits,experiment,variable,model,realisation,version,years1,years2,l2,startyr,endyr)
    gc.collect()
    # Check for path and create if required
    if os.path.exists(outpath) != 1:
        # At first run create output directories
        os.makedirs(outpath)
    if os.path.isfile(os.path.join(outpath,outfilename)) == 1:
        # Purge file if exists
        os.remove(os.path.join(outpath,outfilename))
        print "".join(['** purged: ',outfilename,' **'])
    print "".join(['** Processing ',outfilename,' creation.. **'])
    cmd = "".join([cdat_path,'cdscan -x ',os.path.join(outpath,outfilename),' ',os.path.join(l,'*.nc')])
    # Catch errors with file generation
    ii,o,e = os.popen3(cmd) ; # os.popen3 splits results into input, output and error - consider subprocess function in future
    st = o.read()
    if st.find('Warning:') > -1:
        errstart = st.find('Warning:')
        errend = st.find(':',errstart+8)
        errorcode = st[errstart:errend]
        fileerror = True
        print "".join(['** Error with ',outfilename,' creation.. quitting **'])
        sys.exit()
    del(outfilename,outpath,l,cmd,ii,o,e,st)
    gc.collect()

# Wash permissions
cmd = ''.join(['chmod 755 -R ',host_path])
fnull = open(os.devnull,'w')
p = subprocess.call(cmd,stdout=fnull,shell=True)
fnull.close()