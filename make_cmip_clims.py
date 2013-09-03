#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 13:16:50 2012

Paul J. Durack 30th January 2012

This script builds 30-yr climatologies from annual files

PJD 13 Jul 2012     - Copied from make_cmip5_trendsAndClims.py and updated input
PJD 13 Jul 2012     - TOCHECK: If issues appear with missing masks, set missing as float32: $VAR.setMissing(numpy.float32(1e20))
PJD 19 Feb 2013     - General code tidyup following prompts from pyflakes and rope
PJD 19 Feb 2013     - Updated paths from 'clims' to 'an_clims'
PJD  8 Mar 2013     - Added argument defaults for start_yr and end_yr
PJD  8 Mar 2013     - Corrected reporting and purge paths
PJD 18 Mar 2013     - Migrated files to oceanonly from crunch
PJD 22 Mar 2013     - Added oceanonly to known host list
PJD  2 Sep 2013     - Added both cmip3 & 5 support to this script through arguments - new file validation required
PJD  2 Sep 2013     - Adjusted cmds.setNetcdf flags to ensure files are written with compression
PJD  2 Sep 2013     - Code tidyup and use of functions in durolib
PJD  2 Sep 2013     - Added shebang for local and remote dir execution
PJD  2 Sep 2013     - Added realm argument to prevent across realm file generation (pr = atm/ocn/seaIce)
PJD  2 Sep 2013     - Script is dependent upon an files existing, added test for graceful exit

@author: durack1
"""
import argparse,datetime,gc,glob,os,re,sys,time
import cdms2 as cdm
import cdutil as cdu
from durolib import globalAttWrite,writeToLog
from socket import gethostname
from string import replace

if 'e' in locals():
    del(e,pi,sctypeNA,typeNA)
    gc.collect()

# Set nc classic as outputs
cdm.setCompressionWarnings(0) ; # Suppress warnings
cdm.setNetcdfShuffleFlag(0)
cdm.setNetcdfDeflateFlag(1) ; # was 0 130717
cdm.setNetcdfDeflateLevelFlag(9) ; # was 0 130717
cdm.setAutoBounds(1) ; # Ensure bounds on time and depth axes are generated

start_time = time.time() ; # Set time counter

# Set conditional whether files are created or just numbers are calculated
parser = argparse.ArgumentParser()
parser.add_argument('model_suite',metavar='str',type=str,help='include \'cmip3/5\' as an argument')
parser.add_argument('experiment',metavar='str',type=str,help='including \'experiment\' will select one experiment to process')
parser.add_argument('realm',nargs='?',default='all',metavar='str',type=str,help='including \'realm\' will select one realm to process')
parser.add_argument('variable',metavar='str',type=str,help='including \'variable\' will select one variable to process')
parser.add_argument('start_yr',nargs='?',default=1975,metavar='int',type=int,help='including \'start_yr\' sets a start year from which to process')
parser.add_argument('end_yr',nargs='?',default=2005,metavar='int',type=int,help='including \'end_yr\' sets an end year from which to process')
args = parser.parse_args()
# Test and validate experiment
if (args.model_suite not in ['cmip3','cmip5']):
    print "** No valid model suite specified - no *.nc files will be written **"
    sys.exit()
if (args.experiment in ['1pctCO2','abrupt4xCO2','amip','historical','historicalGHG','historicalNat',
                        'piControl','rcp26','rcp45','rcp60','rcp85','1pctto2x','1pctto4x','20c3m',
                        'picntrl','sresa1b','sresa2','sresb1']):
    model_suite = args.model_suite
    experiment  = args.experiment ; # 1 = make files
else:
    print "** No valid experiment specified - no *.nc files will be written **"
    sys.exit()
if (args.realm in ['atm','land','ocn','seaIce']):
    realm       = args.realm
    variable    = args.variable
    start_yr    = args.start_yr
    start_yr_s  = str(start_yr)
    end_yr      = args.end_yr
    end_yr_s    = str(end_yr)
    print "".join(['** Processing ',variable,' files from ',experiment,' and ',realm,' for ',start_yr_s,'-',end_yr_s,'-Clim.nc file generation **'])
else:
    print "** No valid realm specified - no *.nc files will be written **"
    sys.exit()
# Test and validate variable
if (args.variable == ""):
    print "** No valid variable specified - no *.nc files will be written **"
    sys.exit()
# Test start_yr
if (args.start_yr == ""):
    print "** No valid start_yr specified - defaulting to start_yr=1950 **"
    start_yr = 1950
    start_yr_s = str(start_yr)
# Test end_dyr
if (args.end_yr == ""):
    print "** No valid end_yr specified - defaulting to end_yr=2000 **"
    end_yr = 2000
    end_yr_s = str(end_yr)

# Set host information and directories
host_name = gethostname()
if host_name in {'crunchy.llnl.gov','oceanonly.llnl.gov'}:
    trim_host = replace(host_name,'.llnl.gov','')
    cdat_path = '/usr/local/uvcdat/latest/bin/'
    if 'cmip3' in model_suite:
        host_path   = '/work/durack1/Shared/cmip3/'
        pathin      = '/work/cmip3'
    elif 'cmip5' in model_suite:
        host_path   = '/work/durack1/Shared/cmip5/'
        pathin      = '/work/cmip5' ; # set xml paths
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

'''
model_suite = 'cmip5'
experiment  = 'historical'
realm       = 'atm'
variable    = 'tas'
start_yr    = 1975
end_yr      = 2005
start_yr_s  = str(start_yr)
end_yr_s    = str(end_yr)
'''
    
# Set logfile attributes
time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
logfile = os.path.join(host_path,"".join(["_".join([time_format,'make_cmip5_clims']),"-".join(['',experiment,realm,variable,trim_host]),'.log']))
# Create logfile
writeToLog(logfile,"".join(['TIME: ',time_format]))
writeToLog(logfile,"".join(['HOSTNAME: ',host_name]))

# Get list of infiles (*.nc) and 3D (*.xml)
filelist1 = glob.glob(os.path.join(host_path,experiment,realm,'an',variable,'*.nc'))
filelist2 = glob.glob(os.path.join(host_path,experiment,realm,'an',variable,'*.xml'))

filelist = list(filelist1)
filelist.extend(filelist2) ; filelist.sort()
del(filelist1,filelist2)
gc.collect()

# Test for valid input files
if not filelist:
    print "** No valid an input files - no *.nc files will be written **"
    sys.exit()   

# Purge entries matching atm_vars_exclude by index
i = 0
filelist2 = []
for infile in filelist:
    if (infile.split('/')[8] in variable) and (infile.split('/')[5] in experiment):
        filelist2.insert(i,infile)
        i = i + 1

del(filelist,i,infile)
filelist = filelist2
del(filelist2)
gc.collect()

# Report total file count to logfile
writeToLog(logfile,"".join([host_path,': ',format(len(filelist),"06d"),' nc files found to process']))

# Count and purge code
# Deal with existing *.nc files
ii,o,e = os.popen3("".join(['ls ',os.path.join(host_path,experiment,realm,'an_clims',"-".join([str(start_yr),str(end_yr)]),variable,'*.nc'),' | wc -l']))
nc_count = o.read();
print "".join(['** Purging ',nc_count.strip(),' existing *.nc files **'])
writeToLog(logfile,"".join(['** Purging ',nc_count.strip(),' existing *.nc files **']))
cmd = "".join(['rm -f ',os.path.join(host_path,experiment,realm,'an_clims',"-".join([str(start_yr),str(end_yr)]),variable,'*.nc')])
# Catch errors with system commands
ii,o,e = os.popen3(cmd) ; # os.popen3 splits results into input, output and error - consider subprocess function in future
print "** *.nc files purged **"
writeToLog(logfile,"** *.nc files purged **")
print "** Generating new *.nc files **"
writeToLog(logfile,"** Generating new *.nc files **")

filecount = 0
# Loop through files
for l in filelist:
    filecount = filecount + 1; filecount_s = '%06d' % filecount
    print "".join(["** Processing: ",l," **"])
    var     = l.split('/')[8] ; # Get variable name from filename
    f_in    = cdm.open(l) ; # Open file
    d       = f_in[var] ; # Create variable object - square brackets indicates cdms "file object" and it's associated axes
    # Determine experiment
    time_calc_start = time.time()
    if experiment == 'piControl':
        # Case of piControl files, need to consider spawning time of subsequent experiment
        logtime_now         = datetime.datetime.now()
        logtime_format      = logtime_now.strftime("%y%m%d_%H%M%S")
        time_since_start    = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start       
        writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; piControl file skipped        : ',l,' **']))        
        continue
    else:
        try:
            clim = cdu.YEAR.climatology(d(time=(start_yr_s,end_yr_s,"cob")))
            clim = clim.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            clim.comment = "".join([start_yr_s,'-',end_yr_s,' climatological mean'])
            outfile = re.sub("[0-9]{4}-[0-9]{4}","".join([start_yr_s,'-',end_yr_s,'_anClim']),l)
            outfile = re.sub(".xml",".nc",outfile) ; # Correct for 3D an.xml files
        except:
            logtime_now         = datetime.datetime.now()
            logtime_format      = logtime_now.strftime("%y%m%d_%H%M%S")
            time_since_start    = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
            writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; PROBLEM file skipped          : ',l,' **']))
            continue
    time_calc_end = time.time() - time_calc_start; time_calc_end_s = '%08.2f' % time_calc_end
    # Rename variables
    clim.id = "".join([var,'_mean'])
    # Create output file with new path
    outfile = re.sub('/an/',"".join(['/an_clims/',start_yr_s,'-',end_yr_s,'/']),outfile)
    # Check path exists
    if os.path.exists(os.sep.join(outfile.split('/')[0:-1])) != 1:
        os.makedirs(os.sep.join(outfile.split('/')[0:-1]))
    # Check file exists
    if os.path.exists(outfile):
        print "** File exists.. removing **"
        os.remove(outfile)
    f_out = cdm.open(outfile,'w')
    # Copy across global attributes from source file - do this first, then write again so new info overwrites
    att_keys = f_in.attributes.keys()
    att_dic = {}
    for i in range(len(att_keys)):
        att_dic[i]=att_keys[i],f_in.attributes[att_keys[i]]
        to_out = att_dic[i]
        setattr(f_out,to_out[0],to_out[1]) 
    # Write new outfile global atts
    globalAttWrite(f_out,options=None) ; # Use function to write standard global atts to output file
    # Write to output file    
    f_out.write(clim) ; # Write clim first as it has all grid stuff
    # Close all files
    f_in.close()
    f_out.close()
    # Log success to file        
    logtime_now         = datetime.datetime.now()
    logtime_format      = logtime_now.strftime("%y%m%d_%H%M%S")
    time_since_start    = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start       
    writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; slope&clim: ',time_calc_end_s,'s; created: ',outfile,' **']))
    # Cleanup
    del(clim,filecount_s,logtime_format,logtime_now,outfile)
    del(time_calc_end,time_calc_end_s,time_calc_start)
    del(time_since_start,time_since_start_s,var)
    # Garbage collection before next file iteration
    gc.collect()
# Log success to file
writeToLog(logfile,"** make_cmip5_clims.py complete **")
