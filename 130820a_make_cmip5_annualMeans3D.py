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
PJD  7 May 2013     - TODO: Add file existence check before writing, just to make sure that duplicate (reversed) jobs don't overwrite one another
PJD  7 May 2013     - TODO: Fix issue with final years of 3D files being +1 (HadGEM-AO/CC are good models to validate these fixes)
PJD  7 May 2013     - TODO: Add sanity checks, so first month is Jan, 12th month is December, 12th-last month is Jan and last month is December - otherwise sub-index
                      Test with Had* files as these are often the most problematic
PJD  7 May 2013     - TODO: Consider adding masking of eta variable using input 'dan' variable
PJD  7 May 2013     - TODO: Consider reporting and logging memory usage resource.getrusage(resource.RUSAGE_SELF).ru_maxrss should return this

@author: durack1
"""

import cdms2 as cdms
import os,string,cdtime,cdutil,sys,datetime,argparse,gc,pytz,cdat_info
from socket import gethostname
from string import replace

if 'e' in locals():
    del(e,pi,sctypeNA,typeNA)
    gc.collect()

# Set nc classic as outputs
cdms.setNetcdfShuffleFlag(0)
cdms.setNetcdfDeflateFlag(0)
cdms.setNetcdfDeflateLevelFlag(0)
#cdms.setAutoBounds('on') ; # Set off 120619_0624 as could cause issues with non-gregorian calendars

# Set directories
host_name = gethostname()
if host_name in {'crunchy.llnl.gov','oceanonly.llnl.gov'}:
    trim_host = replace(host_name,'.llnl.gov','')
    host_path   = '/work/durack1/Shared/cmip5/' ; # crunchy 120119
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

# Get script arguments
parser = argparse.ArgumentParser()
parser.add_argument('variable',metavar='str',type=str,help='include \'variable\' as a command line argument')
parser.add_argument('experiment',metavar='str',type=str,help='include \'experiment\' as a command line argument')
parser.add_argument('order',metavar='str',type=str,nargs='?',default='',help='include \'order\' keyword \'reverse\' to reverse model ordering - run in parallel')
args = parser.parse_args()
if (args.variable == ''):
    print "** No variables passed, exiting **"
    sys.exit()
else:
    var = args.variable
    exp = args.experiment
    print "".join(['** Processing for variable: ',var,' and experiment: ',exp,' **'])
if args.order == 'reverse':
    print '** Models processed in reverse order **'
    reverse = True
else:
    reverse = False

# For testing
'''
var = 'uo' ; ###TEST_MODE
exp = 'historical' ; ###TEST_MODE
'''

# Set xml paths
pathin = '/work/cmip5'
#pathin = '/work/durack1/Shared/cmip5/tmp' ; ###TEST_MODE

# Create logfile
time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
logfile = os.path.join(host_path,"".join([time_format,'_make_cmip5_an3D-',exp,'-',var,'-',trim_host,'.log']))
# Log disk usage info for $machine:/work
os.chdir('/work')
cmd = 'df -h | grep work'
o = os.popen(cmd).readlines()
oj = "".join(o)
# Open logfile to write
logfile_handle = open(logfile,'w')
logfile_handle.write("".join(['TIME: ',time_format,'\n']))
logfile_handle.write("".join(['HOSTNAME: ',host_name,'\n']))
logfile_handle.write("".join(['WORKDISK: ',oj]))
logfile_handle.close()

# Set inputs
indir = os.path.join(pathin,exp,'ocn/mo',var) # *.xmls
outdir = os.path.join(host_path,exp,'ocn/an',var,'ncs')

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
    f = cdms.open(os.path.join(indir,l))
    # Validate that data is online - also consider cdms_filemap/directory combination for existing files
    try:
        d = f[var][0,0,0,0] ; # Assuming 4D variable get single data value
        del(d); gc.collect()
    except:
        print "".join(['** DATA NOT ONLINE: ',l,' **'])
        logfile_handle = open(logfile,'a')
        logfile_handle.write("".join(['** DATA NOT ONLINE: ',l,' **']))
        logfile_handle.close()
        continue
    t = f[var].getTime()
    c = t.asComponentTime()
    # Extract info from filename
    mod = string.split(l,'.')[1]
    run = string.split(l,'.')[3]
    #ver = string.split(l,'.')[7] ; ###TEST_MODE
    ver = string.split(l,'.')[8] ; # Using /tmp subdir ###TEST_MODE
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
    #n = 0
    #for i in range(len(yrsX)-1):
    for i,yrval in enumerate(yrsX[0:-1]):
        lb = yrsX[i] ; # swapped n variable for i
        ub = yrsX[i+1] ; # swapped n variable for i
        #n = n + 1 ; # Increment counter
        # Create output filename - pay attention to last year
        if ub == yrsX[-1]:
            # Case of last file
            #cmip5.CNRM-CM5.historical.r1i1p1.an.so.ver-v20111021.1850-2005.nc - example
            fout = "".join(['cmip5.',mod,'.',exp,'.',run,'.an.',var,'.',ver,'.',format(lb,"04d"),'-',format(ub,"04d"),'.nc'])
        else:
            #fout = "".join(['cmip5.',mod,'.',exp,'.',run,'.an.',var,'.',ver,'.',format(lb,"04d"),'-',format(ub-1,"04d"),'.nc'])
            fout = "".join(['cmip5.',mod,'.',exp,'.',run,'.an.',var,'.',ver,'.',format(lb,"04d"),'-',format(ub-1,"04d"),'.nc']) ; # Correct for off by one last year
        # Check if file already exists and write
        if os.path.isfile(os.path.join(outdir,mod,run,ver,fout)) == False:
            # Report if file is being processed
            print "".join(['** Outfile: ',fout,' being processed **'])
            logfile_handle = open(logfile,'a')
            logfile_handle.write("".join(['** Outfile: ',fout,' being processed **\n']))
            logfile_handle.close()
            # Debugging code
            d = f[var]
            print cdtime.comptime(lb),cdtime.comptime(ub)
            print d.getTime().mapInterval((cdtime.comptime(lb),cdtime.comptime(ub)))
            logfile_handle = open(logfile,'a')
            logfile_handle.write("".join([str(cdtime.comptime(lb)),' ',str(cdtime.comptime(ub)),'\n']))
            logfile_handle.write("".join([str(d.getTime().mapInterval((cdtime.comptime(lb),cdtime.comptime(ub)))),'\n']))
            logfile_handle.close()
            del(d); gc.collect()
            # Read data considering bounds
            if ub == yrsX[-1]:
                d = f(var,time=(cdtime.comptime(lb),cdtime.comptime(ub))) ; # Include last year
            else:
                d = f(var,time=(cdtime.comptime(lb),cdtime.comptime(ub),'co')) ; # Exclude last year
            print "".join(['** Processing annual means for ',str(lb),' to ',str(ub),' **'])
            print d.shape
            print d.getTime()
            t = d.getTime()
            mon = 1
            for ind,val in enumerate(t):
                if ind == 0:
                    print [format(ind,'03d'),format(mon,'02d'),t.asComponentTime()[ind]]
                    logfile_handle = open(logfile,'a')
                    logfile_handle.write("".join(['Start: ',str([format(ind,'03d'),format(mon,'02d'),t.asComponentTime()[ind]]),'\n']))
                    logfile_handle.close()
                elif ind == d.shape[0]-1:
                    print [format(ind,'03d'),format(mon,'02d'),t.asComponentTime()[ind]]
                    logfile_handle = open(logfile,'a')
                    logfile_handle.write("".join(['Start: ',str([format(ind,'03d'),format(mon,'02d'),t.asComponentTime()[ind]]),'\n']))
                    logfile_handle.close()
                mon = mon + 1
                if mon == 13:
                    mon = 1
            cdutil.setTimeBoundsMonthly(d) ; # Correct CCSM4 bounds
            # Check units and correct in case of salinity
            if var == 'so' or var == 'sos':
                if d.max() < 1. and d.mean() < 1.:
                    print "".join(["** Correcting units for: ",l," **"])
                    print "".join(['SO mean:     {:+06.2f}'.format(d.mean()),'; min: {:+06.2f}'.format(d.min().astype('float64')),'; max: {:+06.2f}'.format(d.max().astype('float64'))])
                    d_              = d*1000
                    d_.id           = d.id
                    d_.name         = d_.id
                    for k in d.attributes.keys():
                        setattr(d_,k,d.attributes[k])
                    d               = d_
                    print "".join(['SO mean:     {:+06.2f}'.format(d.mean()),'; min: {:+06.2f}'.format(d.min().astype('float64')),'; max: {:+06.2f}'.format(d.max().astype('float64'))])
                    del(d_) ; gc.collect()
            
            dan = cdutil.YEAR(d)
            dan = dan.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            print "".join(['Start time: ',str(lb),' End time: ',str(ub),' input shape: ',str(d.shape),' output shape: ',str(dan.shape)])
            logfile_handle = open(logfile,'a')
            logfile_handle.write("".join(['Start time: ',str(lb),' End time: ',str(ub),' input shape: ',str(d.shape),' output shape: ',str(dan.shape),'\n']))
            logfile_handle.close()
            # Open outfile to write
            g = cdms.open(os.path.join(outdir,mod,run,ver,fout),'w+')
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
            # Write new file global atts
            g.institution = "Program for Climate Model Diagnosis and Intercomparison (LLNL)"
            g.data_contact = "Paul J. Durack; pauldurack@llnl.gov; +1 925 422 5208"
            # Create timestamp, corrected to UTC for history
            local           = pytz.timezone("America/Los_Angeles")
            time_now        = datetime.datetime.now();
            local_time_now  = time_now.replace(tzinfo = local)
            utc_time_now    = local_time_now.astimezone(pytz.utc)
            time_format     = utc_time_now.strftime("%d-%m-%Y %H:%M:%S %p")
            g.history       = "".join([history,'\n','File processed: ',time_format,' UTC; San Francisco, CA, USA'])
            g.host          = "".join([host_name,'; CDAT version: ',"".join(["%s" % el for el in cdat_info.version()]),'; Python version: ',string.replace(string.replace(sys.version,'\n','; '),') ;',');')])
            # Write new variable atts
            dan.comment     = "Converted to annual from monthly mean data" 
            g.write(dan)
            # Deal with eta and depth variables in sigma-coord files
            if 'eta' in f.variables.keys():
                if ub == yrsX[-1]:
                    d = f('eta',time=(cdtime.comptime(lb),cdtime.comptime(ub))) ; # Include last year
                else:
                    d = f('eta',time=(cdtime.comptime(lb),cdtime.comptime(ub),'co')) ; # Exclude last year
                etaan = cdutil.YEAR(d)
                etaan = etaan.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
                # Write variable attributes back out to new variable
                for k in d.attributes.keys():
                    setattr(etaan,k,d.attributes[k])  
                # Write new variable atts
                etaan.comment     = "Converted to annual from monthly mean data"
                depth = f('depth')
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
            logfile_handle = open(logfile,'a')
            logfile_handle.write("".join(['** Outfile: ',os.path.join(outdir,mod,run,fout),' already exists.. Skipping to next model.. **\n']))
            logfile_handle.close()
        #if os.path.isfile(os.path.join(outdir
    #for i in range(len(yrsX)
    f.close()
    # Cleanup
    del(f,t,c,mod,run,ver,yrs,yr,yrsX,nyrs)
    gc.collect()
#for l in lst
