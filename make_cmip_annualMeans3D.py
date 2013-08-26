#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 13:16:50 2012

Paul J. Durack 31 May 2012

File created to generate 3D annual mean files
Sourced from Pete G, annual_means.py

PJD 31 May 2012     - Added gc.collect statements
PJD 31 May 2012     - BNU-ESM.piControl.r1i1p1.mo.so.ver-v20120503 using 95% RAM @ nyrs=25yrs, without writing a single file - drop back to 10yrs
PJD 31 May 2012     - Corrected pathin to take var as path argument
PJD 31 May 2012     - Even with nyrs=10 BNU-ESM.piControl.r1i1p1.mo.thetao.ver-v20120503 is using 47% RAM and bombed due to memory
PJD 31 May 2012     - BNU-ESM.piControl.r1i1p1.mo.so.ver-v20120503 is using 90% RAM nyrs=10
                    BNU-ESM.historical.r1i1p1.mo.so.ver-v20120504 ~4% nyrs=10;
                    BNU-ESM.historical.r1i1p1.mo.thetao.ver-v20120504 ~4% nyrs=10
PJD 31 May 2012     - Added code to drop BNU**piControl calculations to consider nyrs=5 all else nyrs=25
PJD 31 May 2012     - Even with nyrs=5, BNU-ESM.piControl.r1i1p1.mo.so.ver-v20120503 ~43%,
                    BNU-ESM.piControl.r1i1p1.mo.thetao.ver-v20120503 ~46%
                    With nyrs=25, BNU-ESM.historical.r1i1p1.mo.so.ver-v20120504 ~8%,
                    BNU-ESM.historical.r1i1p1.mo.thetao.ver-v20120504 ~8%
PJD 31 May 2012     - nyrs=25, BNU-ESM.historical.r1i1p1.mo.so.ver-v20120504 ~8%
                    BNU-ESM.historical.r1i1p1.mo.thetao.ver-v20120504 ~8%
                    CCSM4.piControl.r1i1p1.mo.so.ver-v20120220 ~17%
                    CCSM4.piControl.r1i1p1.mo.thetao.ver-v20120220 ~17%
PJD  1 Jun 2012     - Commented out second del() statement, are deleted variables tripping things over?
PJD  1 Jun 2012     - Issue appears to be with trailing time so 1960-1-1 being included/indexed twice, use 'con' to limit up to bounds?
PJD  1 Jun 2012     - Edited to include missing last year of historical/piControl etc
PJD  4 Jun 2012     - CCSM4 output is shaped 11,lev,lat,lon (doesn't appear an issue for other models: CNRM-CM5)
PJD  4 Jun 2012     - Added setTimeBoundsMonthly(d) with the hope this will fix issues with CCSM4
PJD  5 Jun 2012     - Test run of cdscan on /cmip5/scratch/cmip5/output1/BNU/BNU-ESM/piControl/mon/ocean/Omon/r1i1p1/v20120503/so yields no complaints - remove BNU catch below and rerun - problem still occurs with thetao
PJD  7 Jun 2012     - Added logging with timings, some files were written with 26 elements in a 25yr mean? Which ones?
PJD  7 Jun 2012     - Updated subsequent log write statements to use 'a', rather than 'w'
PJD  7 Jun 2012     - Updated reporting code, log if a file exists and is being skipped
PJD 17 Jun 2012     - Calculated an files were being written at float64 precision - recast back to float32, reducing file sizes by half
                    [durack1@crunchy cmip5]$ date
                    Sun Jun 17 12:15:05 PDT 2012
                    [durack1@crunchy cmip5]$ du -sch /work/durack1/Shared/cmip5/tmp
                    1.6T    /work/durack1/Shared/cmip5/tmp
                    1.6T    total
PJD 17 Jun 2012     - Added 04d formatted years,'an',var and version info to outfilename
PJD 17 Jun 2012     - Reorder logfile variables to align with an2D logfiles
PJD 17 Jun 2012     - Added df -h argument to report more meaningful numbers to logs
PJD 17 Jun 2012     - Added 'ver' to output directory build, required as GISS-E2-R.r1i1p141.ver-v20120105.850.874.nc and GISS-E2-R.r1i1p141.ver-v20120319.850.874.nc exist in same subdir
PJD 17 Jul 2012     - Updated to index ver as 7 (was 6) due to realm being added to xml files
PJD 19 Aug 2012     - Updated nyrs for MIROC4h, was 25 now 5 for this model
PJD 20 Nov 2012     - Updated indenting in file
PJD 20 Nov 2012     - TOCHECK: Added ann calculation of eta (2D: time,y,x) field and copy depth field for sigma level file usage (conversion to standard depth levels)
PJD 20 Nov 2012     - TOCHECK: Off by one end year, many models complete at YEAR-01-01
PJD 21 Nov 2012     - Added so/sos conversion to correct units
PJD  1 Dec 2012     - Corrected delete statement from etann -> etaan
PJD 10 Dec 2012     - Added an_start_year & an_end_year as global attributes to speed up branch_time code
PJD 10 Dec 2012     - Added a whole bunch of variable and global attributes
PJD 21 Dec 2012     - Added module pytz, cdat_info loading
PJD 21 Dec 2012     - Cleaned up some delete statements for non-existent variables
PJD 29 Dec 2012     - Updated etaan variable to include variable attributes from source data and comment
PJD 19 Feb 2013     - General code tidyup following prompts from pyflakes and rope
PJD  3 Mar 2013     - Updated pathin to use /tmp xmls ; ###TEST_MODE
PJD 18 Mar 2013     - Migrated files to oceanonly from crunch
PJD 19 Mar 2013     - Added oceanonly to known host list
PJD 20 Mar 2013     - Updated pathin = '/work/durack1/Shared/cmip5/tmp' to pathin = '/work/cmip5'
PJD 20 Mar 2013     - Rerun with cdms.setAutoBounds off, runs started prior to 120617_1400 all have this set on
PJD 20 Mar 2013     - Added cleanup code for spyder variables
PJD 23 Apr 2013     - Fixed issue with xml files being dead - data migrated before xml rewritten - so read attempt for single array value from file object prior to processing
PJD 26 Apr 2013     - Added write to log for "DATA NOT ONLINE" errors
PJD  1 May 2013     - Added 'order' argument to reverse ordering of file creation - run a long job in parallel from both ends of model names
PJD  3 May 2013     - Added default arg and nargs='?' to order argument
PJD  3 May 2013     - Added MPI-ESM-MR to 10-yr processing exclusion
PJD  9 Aug 2013     - Renamed to make_cmip_annualMeans3D.py (was cmip5)
PJD 12 Aug 2013     - Added try/except wrapper around file read (with time bounds)
PJD 12 Aug 2013     - Updated df call to specifically target /work - was hanging due to non-responsive CSS01
PJD 26 Aug 2013     - Added shebang for system-wide execute
                    - TODO: Add file existence check before writing, just to make sure that duplicate (reversed) jobs don't overwrite one another
                    - TODO: Fix issue with final years of 3D files being +1 (HadGEM-AO/CC are good models to validate these fixes)
                    - TODO: Add sanity checks, so first month is Jan, 12th month is December, 12th-last month is Jan and last month is December - otherwise sub-index
                      Test with Had* files as these are often the most problematic
                    - TODO: Consider adding masking of eta variable using input 'dan' variable
                    - TODO: Consider reporting and logging memory usage resource.getrusage(resource.RUSAGE_SELF).ru_maxrss should return this

@author: durack1
"""

import cdms2 as cdm
import cdtime as cdt
import cdutil as cdu
import argparse,datetime,gc,os,sys
from durolib import fixVarUnits,globalAttWrite,writeToLog
from socket import gethostname
from string import replace,split

if 'e' in locals():
    del(e,pi,sctypeNA,typeNA)
    gc.collect()

# Set nc classic as outputs
cdm.setCompressionWarnings(0)
cdm.setNetcdfShuffleFlag(0)
cdm.setNetcdfDeflateFlag(1) ; # was 0 130809
cdm.setNetcdfDeflateLevelFlag(9) ; # was 0 130809
#cdms.setAutoBounds('on') ; # Set off 120619_0624 as could cause issues with non-gregorian calendars

# Get script arguments
parser = argparse.ArgumentParser()
parser.add_argument('model_suite',metavar='str',type=str,help='include \'cmip3/5\' as a command line argument')
parser.add_argument('variable',metavar='str',type=str,help='include \'variable\' as a command line argument')
parser.add_argument('experiment',metavar='str',type=str,help='include \'experiment\' as a command line argument')
parser.add_argument('order',metavar='str',type=str,nargs='?',default='',help='include \'order\' keyword \'reverse\' to reverse model ordering - run in parallel')
args = parser.parse_args()
if (args.variable == ''):
    print "** No variables passed, exiting **"
    sys.exit()
else:
    model_suite = args.model_suite
    var         = args.variable
    exp         = args.experiment
    print "".join(['** Processing for model_suite: ',model_suite,', variable: ',var,' and experiment: ',exp,' **'])
if args.order == 'reverse':
    print '** Models processed in reverse order **'
    reverse = True
else:
    reverse = False

# Set directories
host_name = gethostname()
if host_name in {'crunchy.llnl.gov','oceanonly.llnl.gov'}:
    trim_host = replace(host_name,'.llnl.gov','')
    if 'cmip3' in model_suite:
        host_path   = '/work/durack1/Shared/cmip3/'
        pathin      = '/work/cmip3'
    elif 'cmip5' in model_suite:
        host_path   = '/work/durack1/Shared/cmip5/'
        pathin      = '/work/cmip5' ; # set xml paths
        #pathin     = '/work/durack1/Shared/cmip5/tmp' ; ###TEST_MODE
    else:
        print '** model_suite unrecognised, aborting.. **'
        sys.exit()
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

# For testing
'''
model_suite = 'cmip5' ; ##TEST_MODE##
var = 'uo' ; ##TEST_MODE##
exp = 'historical' ; ##TEST_MODE##
'''

# Create logfile
time_now    = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
logfile     = os.path.join(host_path,"".join([time_format,'_make_',model_suite,'_an3D-',exp,'-',var,'-',trim_host,'.log']))
# Log disk usage info for $machine:/work
os.chdir('/work')
cmd = 'df -h /work'
o   = os.popen(cmd).readlines()
oj  = "".join(o)
# Open logfile to write
writeToLog(logfile,"".join(['TIME: ',time_format,'\n']))
writeToLog(logfile,"".join(['HOSTNAME: ',host_name,'\n']))
writeToLog(logfile,"".join(['WORKDISK: ',oj]))

# Set inputs
indir   = os.path.join(pathin,exp,'ocn/mo',var) # *.xmls
outdir  = os.path.join(host_path,exp,'ocn/an',var,'ncs')

# Get input xml files
lst = os.listdir(indir);
if reverse:
    lst.sort(reverse=True);
else:
    lst.sort()

# Loop over inputs
for l in lst:
    print "".join(['** Processing xml: ',l])
    # Check which model is being processed and exclude if a problem - xmls are now updated so if xml exists data passes tests (BNU thetao issue resolved)
    if ( ('MODEL' in l) and ('EXPERIMENT' in exp) and ('VARIABLE' in var) ):
        print "".join(['** Known problem file, skipping annual calculation for ',l])
        continue
    elif ('MIROC4h' in l):
        print "".join(['** MIROC4h file, nyrs set to 5 (not 25) for ',l])
        nyrs = 5 
    elif ('MPI-ESM-MR' in l):
        print "".join(['** MPI-ESM-MR file, nyrs set to 10 (not 25) for ',l])
        nyrs = 10
    else:
        nyrs = 25 ; #10 ok, 25 CCSM4.historical.r2i1p1.mo.so.ver-v20120409 fails, mergeTime=duplicate/overlapping time issue
        print "".join([str(nyrs),'yr annual calculation for ',l]); #continue
    
    # Open file and get times
    f = cdm.open(os.path.join(indir,l))
    # Validate that data is online - also consider cdms_filemap/directory combination for existing files
    try:
        d = f[var][0,0,0,0] ; # Assuming 4D variable get single data value
        del(d); gc.collect()
    except:
        print "".join(['** DATA NOT ONLINE: ',l,' **'])
        writeToLog(logfile,"".join(['** DATA NOT ONLINE: ',l,' **']))
        continue
    t = f[var].getTime()
    c = t.asComponentTime()
    # Extract info from filename
    mod = split(l,'.')[1]
    run = split(l,'.')[3]
    if 'cmip3' in model_suite:
        ver = split(l,'.')[6]
    elif 'cmip5' in model_suite:
        #ver = split(l,'.')[7] ; ##TEST_MODE##
        ver = split(l,'.')[8] ; # Using /tmp subdir ##TEST_MODE##
    # Create output directories
    try:
        os.makedirs(os.path.join(outdir,mod,run,ver)) ; # was (outdir,mod)
    except:
        pass
    # Create year indexes
    yrs = []
    for cc in c:
        yr = cc.year
        if yr not in yrs:
            yrs.append(yr)
    # Set start year
    yrsX = [c[0].year]
    # Set start years
    for i in range(len(yrs)):
        yr = i*nyrs
        if (c[0].year + yr not in yrsX) and (c[0].year + yr in yrs):
            yrsX.append(c[0].year + yr)
    # Add last year to yrsX
    if c[len(c)-1].year not in yrsX:
        yrsX.append(c[len(c)-1].year)
    #for i in range(len(yrsX)-1):
    for i,yrval in enumerate(yrsX[0:-1]):
        lb = yrsX[i] ; # swapped n variable for i
        ub = yrsX[i+1] ; # swapped n variable for i
        # Create output filename - pay attention to last year
        if ub == yrsX[-1]:
            # Case of last file
            #cmip5.CNRM-CM5.historical.r1i1p1.an.so.ver-v20111021.1850-2005.nc - example
            fout = ".".join([model_suite,mod,exp,run,'an',var,ver,"-".join([format(lb,"04d"),format(ub,"04d")]),'nc'])
        else:
            #fout = "".join(['cmip5.',mod,'.',exp,'.',run,'.an.',var,'.',ver,'.',format(lb,"04d"),'-',format(ub-1,"04d"),'.nc'])
            fout = ".".join([model_suite,mod,exp,run,'an',var,ver,"-".join([format(lb,"04d"),format(ub-1,"04d")]),'nc']) ; # Correct for off by one last year
        # Check if file already exists and write
        if os.path.isfile(os.path.join(outdir,mod,run,ver,fout)) == False:
            # Report if file is being processed
            print "".join(['** Outfile: ',fout,' being processed **'])
            writeToLog(logfile,"".join(['** Outfile: ',fout,' being processed **\n']))
            # Debugging code
            d = f[var]
            print cdt.comptime(lb),cdt.comptime(ub)
            print d.getTime().mapInterval((cdt.comptime(lb),cdt.comptime(ub)))
            writeToLog(logfile,"".join([str(cdt.comptime(lb)),' ',str(cdt.comptime(ub)),'\n']))
            writeToLog(logfile,"".join([str(d.getTime().mapInterval((cdt.comptime(lb),cdt.comptime(ub)))),'\n']))
            del(d); gc.collect()
            # Read data considering bounds
            if ub == yrsX[-1]:
                try:
                    d = f(var,time=(cdt.comptime(lb),cdt.comptime(ub))) ; # Include last year
                except Exception,err:
                    print "".join(['** Problem encountered with: ',l,' ',str(err),' skipping.. **'])
                    writeToLog(logfile,"".join(['** Problem encountered with: ',l,' ',str(err),' skipping.. **']))
                    continue
            else:
                try:
                    d = f(var,time=(cdt.comptime(lb),cdt.comptime(ub),'co')) ; # Exclude last year
                except Exception,err:
                    print "".join(['** Problem encountered with: ',l,' ',str(err),' skipping.. **'])
                    writeToLog(logfile,"".join(['** Problem encountered with: ',l,' ',str(err),' skipping.. **']))
                    continue
            print "".join(['** Processing annual means for ',str(lb),' to ',str(ub),' **'])
            print d.shape
            print d.getTime()
            t = d.getTime()
            mon = 1
            for ind,val in enumerate(t):
                if ind == 0:
                    print [format(ind,'03d'),format(mon,'02d'),t.asComponentTime()[ind]]
                    writeToLog(logfile,"".join(['Start: ',str([format(ind,'03d'),format(mon,'02d'),t.asComponentTime()[ind]]),'\n']))
                elif ind == d.shape[0]-1:
                    print [format(ind,'03d'),format(mon,'02d'),t.asComponentTime()[ind]]
                    writeToLog(logfile,"".join(['Start: ',str([format(ind,'03d'),format(mon,'02d'),t.asComponentTime()[ind]]),'\n']))
                mon = mon + 1
                if mon == 13:
                    mon = 1
            cdu.setTimeBoundsMonthly(d) ; # Correct CCSM4 bounds
            # Check units and correct in case of salinity
            if var == 'so' or var == 'sos':
                [d,_] = fixVarUnits(d,var,True)
                
            dan = cdu.YEAR(d)
            dan = dan.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            print "".join(['Start time: ',str(lb),' End time: ',str(ub),' input shape: ',str(d.shape),' output shape: ',str(dan.shape)])
            writeToLog(logfile,"".join(['Start time: ',str(lb),' End time: ',str(ub),' input shape: ',str(d.shape),' output shape: ',str(dan.shape),'\n']))
            # Open outfile to write
            g = cdm.open(os.path.join(outdir,mod,run,ver,fout),'w+')
            # Copy across attributes 
            # Write variable attributes back out to new variable
            for k in d.attributes.keys():
                setattr(dan,k,d.attributes[k])
            # Write out file global atts
            for k in f.attributes.keys():
                setattr(g,k,f.attributes[k])
            history = getattr(f,'history')
            # Write out start and end years
            dt = dan.getTime().asComponentTime()
            g.an_start_year = dt[0].year
            g.an_end_year = dt[-1].year   
            # Write new outfile global atts
            globalAttWrite(g,options=None) ; # Use function to write standard global atts to output file
            # Write new variable atts
            dan.comment     = "Converted to annual from monthly mean data" 
            g.write(dan)
            # Deal with eta and depth variables in sigma-coord files
            if 'eta' in f.variables.keys():
                if ub == yrsX[-1]:
                    d = f('eta',time=(cdt.comptime(lb),cdt.comptime(ub))) ; # Include last year
                else:
                    d = f('eta',time=(cdt.comptime(lb),cdt.comptime(ub),'co')) ; # Exclude last year
                etaan = cdu.YEAR(d)
                etaan = etaan.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
                # Write variable attributes back out to new variable
                for k in d.attributes.keys():
                    setattr(etaan,k,d.attributes[k])  
                # Write new variable atts
                etaan.comment     = "Converted to annual from monthly mean data"
                depth= f('depth')
                depth = depth.astype('float32')
                g.write(etaan)
                g.write(depth)
            g.close()
            # Cleanup
            del(d,dan,g)
            if 'eta' in f.variables.keys():
                del(depth,etaan)
            gc.collect()
        else:
            print "".join([os.path.join(outdir,mod,run,fout),' already exists.. Skipping to next model.. '])
            writeToLog(logfile,"".join(['** Outfile: ',os.path.join(outdir,mod,run,fout),' already exists.. Skipping to next model.. **\n']))
        #if os.path.isfile(os.path.join(outdir
    #for i in range(len(yrsX)
    f.close()
    # Cleanup
    del(f,t,c,mod,run,ver,yrs,yr,yrsX,nyrs)
    gc.collect()
#for l in lst
