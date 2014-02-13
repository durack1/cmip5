#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 10:26:47 2012

Paul J. Durack 30th January 2012

This script builds annual files

PJD 30 Jan 2012     - Finalised to create annual files from monthly means
PJD 31 Jan 2012     - Considering multithreading code, particularly for 3D file creation (demo code added and commented)
PJD  3 Feb 2012     - Added logging code and corrected format so that first and last year will always be 04d
PJD  3 Feb 2012     - Added code to report skipping 3D files, previously these were unreported
PJD  6 Feb 2012     - Added error reporting code, bombed on file:
                    /work/durack1/Shared/cmip5/rcp45/atm/mo/tas/cmip5.NorESM1-M.rcp45.r1i1p1.mo.tas.ver-v20110901.xml
PJD  6 Feb 2012     - Problem above due to no timeBounds, use cdutil.setTimeBoundsMonthly(var) to resolve issue
PJD  6 Feb 2012     - Converting d=f_in[var] to d=f_in(var) has improved cdutil.YEAR timing by between 10x and 2x,
                      this now explicitly reads the whole array into memory and calcs annual in memory
PJD  6 Feb 2012     - Added missing_value flag correction for d and ann variable
PJD  6 Feb 2012     - Added code to exclude non pr/tas historical data
PJD  6 Feb 2012     - Using latest run 528 files are contained in filelist 120206 1635
PJD  7 Feb 2012     - Have another go at dealing with grids and missing data
PJD  8 Feb 2012     - CDAT Issues too numerous with grids and variable attributes, so wrote code to skip any
                      write issues and skip to next file in loop. Issue with creating:
                      /work/durack1/Shared/cmip5/1pctCO2/ocn/an/sos/cmip5.GFDL-ESM2M.1pctCO2.r1i1p1.an.sos.ver-v1.0001-0200.nc
                      logged to bugzilla: http://uv-cdat.llnl.gov/bugzilla/show_bug.cgi?id=64
PJD 14 Feb 2012     - Charles implemented a type casting fix for bug64, uvcdat/latest includes this fix
PJD 15 Feb 2012     - [durack1@crunchy cmip5]$ ls */*/an/*/*.nc | wc -l = 394 (pre-rerunning on new xmls)
PJD 15 Feb 2012     - Added some gc.collect() calls to tighten memory usage
PJD 15 Feb 2012     - Added code to reapply d.attributes to new ann variable (same with global atts)
PJD 15 Feb 2012     - [durack1@crunchy cmip5]$ ls */*/an/*/*.nc | wc -l = XXX (post-rerunning on new xmls)
PJD 16 Feb 2012     - Considerable file cleanup, due to UVCDAT6.0beta bug fixes resolving many cludgy partially implemented
                      code below
PJD 16 Feb 2012     - Added writing of "completion" logfile statement
PJD 16 Feb 2012     - Latest run (120215_163849) produced 436 *an* output files increased from 394 (120208_162520)
PJD 19 Feb 2012     - Problem using cdutil.YEAR on cmip5.MIROC-ESM.historical.r1i1p1.mo.tas.ver-v20110929.xml - time axis issue?
PJD 19 Feb 2012     - Added try-except around cdutil.YEAR to catch above issue
PJD 19 Feb 2012     - 120219_090047: 571 an*.nc files generated
PJD 28 Feb 2012     - an_nc count 120228_2147: 571  120229_xxxx:
                      [durack1@crunchy cmip5]$ ls */*/an/*/*.nc | wc -l
PJD  2 Mar 2012     - Updated cdat_path as ['/bin/sh: /usr/local/cdat/2012-01-12/bin/cdscan: No such file or directory\n']
PJD  2 Mar 2012     - an nc count 120302_0921: 575
PJD  8 Mar 2012     - an nc count 120308_1851: 784
PJD  9 Mar 2012     - an nc count 120309_1052: 846
PJD 18 Mar 2012     - Added 'zos' to xml creation, so added 'zos' to the vars_exclude list below
PJD 16 Apr 2012     - Updated to log info for nc_good & nc_bad files
PJD 17 Apr 2012     - Updated nc_$ counters to 0, added try statement for file read due to axis length issues with
                    /work/durack1/Shared/cmip5/rcp26/atm/mo/tas/cmip5.CCSM4.rcp26.r1i1p1.mo.tas.ver-v20120203.xml
PJD 18 Apr 2012     - Moved nc_good counter increment, weird it's reporting 3133, when 1453 files exist and filecount is 2091
PJD 30 May 2012     - Added MRRO/MRROS so that annual total, not mean is calculated
PJD  7 Jun 2012     - Added fx fields to var exclusion list to fix code falling over due to no 'time' attribute
PJD  7 Jun 2012     - Converted code to take experiment arg to parallelise across experiments
PJD 16 Jun 2012     - Added xml_path to source new cron xml files - needed to update file.split calls from 8 to 6
PJD 17 Jun 2012     - Added correction to outfile path, so /work/cmip5/ in is converted to /work/durack1/Shared/cmip5/
PJD 17 Jun 2012     - Calculated an files were being written at float64 precision - recast back to float32, reducing file sizes by half
PJD 18 Jun 2012     - TOCHECK: If issues appear with missing masks, set missing as float32: $VAR.setMissing(numpy.float32(1e20))
PJD 10 Jul 2012     - Issues with agessc files, removed agessc + others and 3D files from processing loop
PJD 10 Jul 2012     - Added exclusion list for each realm (atm, land, ocn, seaIce)
PJD 11 Jul 2012     - Added hus,hur,ta,ua,va to atm exclusion list, should do so for all 3D atm/ocn vars
PJD 25 Jul 2012     - Added clisccp to excluded vars
PJD 25 Jul 2012     - There appears no need to reorder realms, outfile is generated from the xml name, so all will be propagated
PJD 16 Aug 2012     - Added check for rsds/ocn 3Dvariable as this is causing the script to bomb:
		      /work/cmip5/historical/ocn/mo/rsds/cmip5.GFDL-ESM2M.historical.r1i1p1.mo.ocn.rsds.ver-1.xml
PJD 19 Aug 2012     - Fixed issue with mo_new files being indexed (piControl) '_new/' string being searched and excluded
PJD 20 Aug 2012     - Added historicalNat to valid experiment list
PJD 23 Oct 2012     - Corrected an/mo with leading folder '/'
PJD 23 Oct 2012     - Corrected issue with file years not agreeing outfile log created
PJD 15 Nov 2012     - INVALID: Add depth and eta variables to sigma (terrain-following) files - cmip5.inmcm4; cmip5.MIROC* - not valid for 2D
PJD 10 Dec 2012     - Added an_start_year & an_end_year as global attributes to speed up branch_time code
PJD 17 Dec 2012     - Corrected issue with *.mo.* sneaking through into an filenames
PJD 19 Feb 2013     - General code tidyup following prompts from pyflakes and rope
PJD 19 Feb 2013     - Edited code to use *cmip5/tmp/ xml tree while new xmls/directories are building
PJD 20 Feb 2013     - Added fudge to correct xml_path to host_path
PJD 21 Feb 2013     - Edited code to use /work/cmip5/ and not *cmip5/tmp/ - xml tree rebuilt and issue with amip/abrupt4xCO2/PiControl/rcp26
                      appear to have disappeared - Check email to Charles dated this morning for details
PJD 21 Feb 2013     - Added sanity checks, so first month is Jan, 12th month is December, 12th-last month is Jan and last month is December - otherwise sub-index
                      Test with Had* files as these are often the most problematic
                      /cmip5_gdo2/data/cmip5/output1/MOHC/HadGEM2-A/amip/mon/atmos/Amon/r1i1p1/evspsbl/1/evspsbl_Amon_HadGEM2-A_amip_r1i1p1_197809-200811.nc
PJD 21 Feb 2013     - Added oceanonly to known hosts
PJD 21 Feb 2013     - General code tidyup, updated reporting of sub-sampled data to generate annual means, reordered problem codes
PJD 21 Feb 2013     - Added 'historicalGHG' to experiment list
PJD 26 Feb 2013     - Added 'evspsbl' to vars_exclude_atm exclusion list, will need to purge these data prior to rerunning - disk space issues!
PJD  1 Mar 2013     - Added clivi, clwvi, ... to exclusion list - after historical run update to full list, and rerun for all experiments (purge extra variables)
PJD  2 Mar 2013     - Inverted logic, so list variables for inclusion, rather than an exclusion list - removed vars_exclude references
PJD  2 Mar 2013     - TOCHECK: Log counters have been reordered and some inconsistencies fixed, check logging code to confirm numbers are correctly reporting
PJD  5 Mar 2013     - TOCHECK: Added print statements to verify warning sub-indexing message is valid for mostly all files - likely linked to off by
                      one issue, so index is 0-based, length/shape is 1-based
PJD  5 Mar 2013     - Historical was taking too long to process, chopped further into realms using optional arguments
PJD  5 Mar 2013     - Removed 'evspsbl','hfls','hfss','tauu','tauv','uas','vas' from atm_vars and purged existing files off disk (disk space issues)
PJD 18 Mar 2013     - Migrated files to oceanonly from crunch
PJD 18 Mar 2013     - Updated path to xmls - was set for /tmp subdir on crunchy for testing
PJD 19 Mar 2013     - Added 'historicalExt' to experiment list
PJD 31 Jul 2013     - Updated reference to file variable and replaced globalAtt code with globalAttWrite function
PJD 31 Jul 2013     - Code using writeToLog function; updated call to cdms and cdutil
PJD 31 Jul 2013     - Cleaned up glob statements to only index */mo/* subdirs (not mo_new)
PJD 31 Jul 2013     - Updated cdm criterion to use compression and setAutoBounds
PJD 31 Jul 2013     - Replaced all unit fixes with fixVarUnits function
PJD  4 Aug 2013     - Fixed problem with str to int casting in filelist loop
PJD  4 Aug 2013     - Removed del(time_format,time_now) as hangovers from globalAttWrite pre-function call
PJD  9 Sep 2013     - Added both cmip3 & 5 support to this script through arguments - new file validation required
                    - TODO: Add EC-EARTH mask fix (and other model issues to be resolved)
                    - TODO: Start correcting issued files, use /work/cmip5/12xxxx_cmip5_pathologies.txt to document and deal with these
                    - TODO: Consider reporting and logging memory usage resource.getrusage(resource.RUSAGE_SELF).ru_maxrss should return this
                    - TODO: Consider multiplying WFO/PR by 86400 to get to correct comparable units (cmip3) code commented below
"""

import os,sys,datetime,time,glob,gc,argparse
from string import replace
from socket import gethostname
import cdms2 as cdm
import cdutil as cdu
from durolib import fixVarUnits,globalAttWrite,writeToLog
from numpy import mod
from numpy.core import shape

if 'e' in locals():
    del(e,pi,sctypeNA,typeNA)
    gc.collect()

# Set netcdf file criterion - turned on from default 0s
cdm.setCompressionWarnings(0) ; # Suppress warnings
cdm.setNetcdfShuffleFlag(0)
cdm.setNetcdfDeflateFlag(1)
cdm.setNetcdfDeflateLevelFlag(9)
# Hi compression: 1.4Gb file ; # Single salt variable
# No compression: 5.6Gb ; Standard (compression/shuffling): 1.5Gb ; Hi compression w/ shuffling: 1.5Gb
cdm.setAutoBounds(1) ; # Ensure bounds on time and depth axes are generated

start_time = time.time() ; # Set time counter

# Set conditional whether files are created or just numbers are calculated
parser = argparse.ArgumentParser()
parser.add_argument('model_suite',metavar='str',type=str,help='include \'cmip3/5\' as a command line argument')
parser.add_argument('experiment',metavar='str',type=str,help='including \'experiment\' will select one experiment to process')
parser.add_argument('realm',nargs='?',default='',metavar='str',type=str,help='including optional argument \'realm\' will subprocess variables')
args = parser.parse_args()

# Get realm and experiment
all_experiments = False ; all_realms = False ; # Preset variables before testing
if (args.model_suite not in ['cmip3','cmip5']):
    print "** No valid model suite specified - no *.nc files will be written **"
    sys.exit()
if (args.experiment in ['all','1pctCO2','abrupt4xCO2','amip','historical','historicalExt','historicalGHG','historicalNat','piControl','rcp26','rcp45','rcp60','rcp85',
                        '1pctto2x','1pctto4x','20c3m','picntrl','sresa1b','sresa2','sresb1']):
    model_suite = args.model_suite    
    experiment = args.experiment ; # 1 = make files
    if (args.realm in ['','all','atm','land','ocn','seaIce']):
        realm = args.realm ; # 1 = make files
        if ( realm == '' or realm == 'all' ) and experiment == 'all':
            all_experiments = True
            all_realms = True
            realm = 'all' ; # for logfile handling
            print "".join(['** Processing *.xml files from ALL experiments and realms for *an.nc file generation **'])
        elif realm == '' or realm == 'all':
            all_realms = True
            realm = 'all' ; # for logfile handling
            print "".join(['** Processing *.xml files from ',model_suite,',',experiment,' and all realms for *an.nc file generation **'])
        elif realm != '' and experiment == 'all':
            all_experiments = True
            print "".join(['** Processing *.xml files from ALL experiments and ',realm,' for *an.nc file generation **'])
        elif realm != '':
            print "".join(['** Processing *.xml files from ',model_suite,',',experiment,',',realm,' for *an.nc file generation **'])
    else:
        print "** Invalid realm specified - no *.nc files will be written **"
        sys.exit()
else:
    print "** Invalid experiment specified - no *.nc files will be written **"
    sys.exit()

## TEST ## 
'''
experiment = 'amip'
realm = 'all'
all_experiments = False
all_realms = True
'''

# Set host information and directories
host_name = gethostname()
if host_name in {'crunchy.llnl.gov','oceanonly.llnl.gov'}:
    trim_host = replace(host_name,'.llnl.gov','')
    if 'cmip3' in model_suite:
        host_path   = '/work/durack1/Shared/cmip3/'
        xml_path    = '/work/cmip3/'
        xml_count   = 6
    elif 'cmip5' in model_suite:
        host_path   = '/work/durack1/Shared/cmip5/'
        xml_path    = '/work/cmip5/' ; # set xml paths
        xml_count   = 6
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

# Set logfile attributes
time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
logfile = os.path.join(host_path,"".join([time_format,'_make_cmip5_an-',experiment,'-',realm,'-',trim_host,'.log']))
# Create logfile
if 'logfile' in locals():
    writeToLog(logfile,"".join(['TIME: ',time_format]))
    writeToLog(logfile,"".join(['HOSTNAME: ',host_name]))

# Get list of infiles (xml)
if all_experiments and all_realms:
    filelist = glob.glob("".join([xml_path,'*/*/mo/*/*.xml'])) ; filelist.sort()
    #print "all both"
elif all_experiments and not all_realms:
    filelist = glob.glob("".join([xml_path,'*/',realm,'/mo/*/*.xml'])) ; filelist.sort()
    #print "all experiments"
elif all_realms and not all_experiments:
    filelist = glob.glob("".join([xml_path,experiment,'/*/mo/*/*.xml'])) ; filelist.sort()
    #print "all realms"
else:
    filelist = glob.glob("".join([xml_path,experiment,'/',realm,'/mo/*/*.xml'])) ; filelist.sort()
    #print "else"

# Trim out variables of no interest
vars_include_atm    = ['pr','prw','ps','psl','tas','ts'] ; # 'evspsbl','hfls','hfss','tauu','tauv','uas','vas'
vars_include_fx     = []
vars_include_land   = ['mrro','mrros']
vars_include_ocn    = ['pr','soga','sos','tos','wfo','zos','zostoga']
vars_include_seaIce = ['pr','sic','sit']
# Generate master inclusion list from sublists
vars_include = list(vars_include_atm)
vars_include.extend(vars_include_fx)
vars_include.extend(vars_include_land)
vars_include.extend(vars_include_ocn)
vars_include.extend(vars_include_seaIce) ; vars_include.sort()
# Purge entries matching vars_include by index
filelist2 = []
for i,filename in enumerate(filelist):
    if ( (filename.split('/')[xml_count] in vars_include) or ('_new/' in filename) ):
        filelist2.insert(i,filename)

del(filelist,filename,vars_include,i)
filelist = filelist2
del(filelist2)
gc.collect()

# Report total file count to logfile
if 'logfile' in locals():
    writeToLog(logfile,"".join([xml_path,': ',format(len(filelist),"06d"),' xml files found to process']))

# Create counters for nc_good and nc_bad
nc_good = 0; nc_bad1 = 0; nc_bad2 = 0; nc_bad3 = 0; nc_bad4 = 0;
# Deal with existing *.nc files
if all_experiments and all_realms:
    exp_path = '*/*/an/*/*.nc'
    #print "all both: ",exp_path
elif all_experiments and not all_realms:
    exp_path = "".join(['*/',realm,'/an/*/*.nc'])
    #print "all experiments: ",exp_path
elif not all_experiments and not all_realms:
    exp_path = "".join([experiment,'/',realm,'/an/*/*.nc'])
    #print "not all realms: ",exp_path
else:
    exp_path = "".join([experiment,'/*/an/*/*.nc'])
    #print "else: ",exp_path
ii,o,e = os.popen3("".join(['ls ',host_path,exp_path,' | wc -l']))
nc_count = o.read();
print "".join(['** Purging ',nc_count.strip(),' existing *.nc files **'])
#sys.exit() ; # For testing
writeToLog(logfile,"".join(['** Purging ',nc_count.strip(),' existing *.nc files **']))
cmd = "".join(['rm -f ',host_path,exp_path])
# Catch errors with system commands
ii,o,e = os.popen3(cmd) ; # os.popen3 splits results into input, output and error - consider subprocess function in future
print '** *.nc files purged **'
writeToLog(logfile,'** *.nc files purged **')
print "** Generating new *.nc files **"
writeToLog(logfile,"** Generating new *.nc files **\n")

for x,l in enumerate(filelist): # test [1265:1500] 120417 - cmip5.CCSM4.rcp26.r1i1p1.mo.tas.ver-v20120203
    filecount_s = '%07d' % int(x+1)
    print "".join(['** Processing: ',l,' **'])
    var = l.split('/')[xml_count] ; # in path var is 6th indexed
    realm = l.split('/')[xml_count-2] ; # in path realm is 4th indexed
    if var in ['rsds','so','thetao','uo','vo'] and realm in 'ocn':
        print '** NOT CREATING 3D ocean files: so/thetao/uo/vo file found and breaking to next loop entry.. **'
        # Log skip to file
        if 'logfile' in locals():
            logtime_now = datetime.datetime.now()
            logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
            time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
            writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; 3D FILE ENCOUNTERED,      skipped: ',l,' **']))
            # Cleanup
            del(logtime_now,logtime_format,time_since_start)
        del(var,filecount_s)
        gc.collect()
        continue
    # Open file
    f_in = cdm.open(l)
    # Read variable - square brackets indicates "file object", parentheses indicates variable object
    try:
       d = f_in(var)
    except:
        # Report failure to logfile
        print "** PROBLEM 1 (read var error - ann calc failed) with: " + l + " found and breaking to next loop entry.. **"
        nc_bad1 = nc_bad1 + 1;
        if 'logfile' in locals():
            logtime_now = datetime.datetime.now()
            logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
            time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
            err_text = 'PROBLEM 1 (read var error - ann calc failed) creating '
            writeToLog(logfile,"".join(['** ',format(nc_bad1,"07d"),': ',logtime_format,' ',time_since_start_s,'s; ',err_text,l,' **']))
        continue
  
    # Explicitly set timeBounds - problem with cmip5.NorESM1-M.rcp45.r1i1p1.mo.tas.ver-v20110901.xml
    cdu.setTimeBoundsMonthly(d)
    # Check units and correct in case of salinity
    if var in ['so','sos']:
        [d,_] = fixVarUnits(d,var,True,logfile)
            
    # Get time dimension and convert to component time
    dt          = d.getTime()
    dtc         = dt.asComponentTime()
    dfirstyr    = dtc[0].year
    dlastyr     = dtc[-1].year
    # Use cdutil averager functions to generate annual means
    print "** Calculating annual mean **"
    time_anncalc_start = time.time()
    try:
        # Determine first January
        for counter,compTime in enumerate(dtc):
            if compTime.month == 1:
                index_start = counter
                break
        # Determine last December
        for counter,compTime in reversed(list(enumerate(dtc))):
            if compTime.month == 12:
                index_end = counter
                break
        # Report inconsistent start/end times of data
        if (index_start != 0 or index_end != (shape(d)[0])-1) and not mod(len(range(index_start,index_end+1)),12):
            print "".join(['** WARNING: data sub-indexed to generate annual mean timeseries from: ',l,' **'])
            print "".join(['Start index: ',str(index_start),' End index: ',str(index_end),' var length: ',str(shape(d)[0]),' start ctime: ',str(dtc[index_start]),' end ctime: ',str(dtc[index_end])])         
            if 'logfile' in locals():
                writeToLog(logfile,"".join(['** WARNING: data sub-indexed to generate annual mean timeseries from: ',l,' **']))
        # Check valid number of months are being processed to create annual means
        elif mod(len(range(index_start,index_end+1)),12):
            # Report failure to logfile
            print "".join(['** PROBLEM 2 (incomplete monthly mean data) with: ',l,' found and breaking to next loop entry.. **'])
            #print "".join(['Start time: ',str(lb),' End time: ',str(ub),' input shape: ',str(d.shape),' output shape: ',str(dan.shape)])
            nc_bad2 = nc_bad2 + 1;
            if 'logfile' in locals():
                logtime_now = datetime.datetime.now()
                logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
                time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
                err_text = 'PROBLEM 2 (incomplete monthly mean data) creating '
                writeToLog(logfile,"".join(['** ',format(nc_bad2,"07d"),': ',logtime_format,' ',time_since_start_s,'s; ',err_text,l,' **']))
            continue
        #ann = cdutil.YEAR(d) # no temporal subsetting a problem for:
        #/cmip5_gdo2/data/cmip5/output1/MOHC/HadGEM2-A/amip/mon/atmos/Amon/r1i1p1/evspsbl/1/evspsbl_Amon_HadGEM2-A_amip_r1i1p1_197809-200811.nc
        ann = cdu.YEAR(d(time=(dtc[index_start],dtc[index_end],"con")))
        ann = ann.astype('float32') ; # Recast from float64 back to float32 precision
    except:
        # Report failure to logfile
        print "** PROBLEM 3 (cdutil.YEAR error - ann calc failed) with: " + l + " found and breaking to next loop entry.. **"
        nc_bad3 = nc_bad3 + 1;
        if 'logfile' in locals():
            logtime_now = datetime.datetime.now()
            logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
            time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
            err_text = 'PROBLEM 3 (cdutil.YEAR error - ann calc failed) creating '
            writeToLog(logfile,"".join(['** ',format(nc_bad3,"07d"),': ',logtime_format,' ',time_since_start_s,'s; ',err_text,l,' **']))
        continue
    time_anncalc_end = time.time() - time_anncalc_start; time_anncalc_end_s = '%08.2f' % time_anncalc_end
    print "** Annual mean calculated **"
    if var in ['pr','wfo','mrro','mrros']:
        print "** PR/WFO/MRRO/MRROS variable corrected for annual total, not mean **"
        ann*12. ; # Correct to annual sum
    
    """ 
    if var in 'wfo':
        ann*-86400 ; # Convert kg m-2 s-1 -> mm/day -> mm/month and into ocean as -ve/blue (wfo)
    if var in 'pr':
        ann*86400 ; # Convert kg m-2 s-1 -> mm/day -> mm/month
    print "** PR/WFO units corrected to mm/month **"
 
    from make_model_plots.m /work/durack1/csiro/Backup/110808/Y_dur041_linux/working/
    elseif strcmp(var,'wfo')
    varmat = (varmat*-86400).*gregorian_days; % Convert kg m-2 s-1 -> mm/day -> mm/month and into ocean as -ve/blue (wfo)
    elseif strcmp(var,'pr')
    varmat = (varmat*86400).*gregorian_days; % Convert kg m-2 s-1 -> mm/day -> mm/month        
    """    

    # Create check values for annual variable
    annt = ann.getTime()
    anntc = annt.asComponentTime()
    annfirstyr = anntc[0].year
    annlastyr = anntc[-1].year
    # Create outfile name
    outfile = replace(replace(replace(l,'.xml',"".join(['.',format(annfirstyr,"04d"),'-',format(annlastyr,"04d"),'.nc'])),'/mo','/an'),'.mo.','.an.')
    # Correct from /work/cmip5/ to /work/durack1/Shared/cmip5/
    outfile = replace(outfile,xml_path,host_path)
    print "".join(['outfile: ',outfile])
    #outfile = replace(outfile,'/work/cmip5/','/work/durack1/Shared/cmip5/')
    # FOR TESTING - write the current working directory
    """
    outfile = re.sub('rcp26/ocn/an/tos/','',outfile) ; print "".join(['outfile: ',outfile])
    """
    # Check that outfile path exists
    dirend = outfile.rfind('/')
    if os.path.exists(outfile[:dirend+1]) != 1:
        # At first run create output directories
        os.makedirs(outfile[:dirend])
    if os.path.exists(outfile):
        print "".join(['** File exists.. removing: ',outfile,' **'])
        os.remove(outfile)
    # Open outfile
    f_out = cdm.open(outfile,'w')
    # Write variable attributes back out to new variable
    for k in d.attributes.keys():
        setattr(ann,k,d.attributes[k])
    # Write out file global atts
    for k in f_in.attributes.keys():
        setattr(f_out,k,f_in.attributes[k])
    history = getattr(f_in,'history')
    # Write out start and end years
    f_out.an_start_year = annfirstyr
    f_out.an_end_year = annlastyr        
    # Global attributes
    globalAttWrite(f_out,options=None) ; # Use function to write standard global atts
    # Write new variable atts
    ann.comment 	= "Converted to annual from monthly mean data"

    # Write data to file, if successful close infile and outfile
    try:
        f_out.write(ann)
        f_out.close()
        f_in.close() ; # Source file kept open so attributes can be copied across
        nc_good = nc_good + 1 ;
    except:
        print "file write bombed onto next in loop"
        f_out.close()
        f_in.close()
        nc_bad4 = nc_bad4 + 1 ;
        if os.path.exists(outfile):
            print "".join(['** File exists.. removing: ',outfile,' **'])
            os.remove(outfile)
        # Report failure to logfile
        if 'logfile' in locals():
            logtime_now = datetime.datetime.now()
            logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
            time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
            err_text = 'PROBLEM 4 (f_out.write error - nc creation failed) creating '
            writeToLog(logfile,"".join(['** ',format(nc_bad4,"07d"),': ',logtime_format,' ',time_since_start_s,'s; ',err_text,outfile,' **']))
            
        continue

    # Log success to file
    if 'logfile' in locals():
        logtime_now = datetime.datetime.now()
        logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
        time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
        writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; cdutil.YEAR(): ',time_anncalc_end_s,'s; created: ',outfile,' **']))
        # Cleanup
        del(logtime_now,logtime_format,time_since_start,time_since_start_s)
    del(ann,annfirstyr,annlastyr,dfirstyr,dirend,dlastyr,filecount_s,history,k,outfile)
    del(time_anncalc_end,time_anncalc_end_s,time_anncalc_start)
    del(var)
    # Garbage collection before next file iteration
    gc.collect()

# Log success to file
# Create master list of xml_bad
nc_bad = nc_bad1+nc_bad2+nc_bad3+nc_bad4
if 'logfile' in locals():
    writeToLog(logfile,"** make_cmip5_annualMeans.py complete **")
    writeToLog(logfile,"".join(['** NC file count - Good: ',format(nc_good,"1d"),' **']))
    writeToLog(logfile,"".join(['** NC file count - Bad/skipped: ',format(nc_bad,"1d"),'; bad1 (read var error): ',format(nc_bad1,"1d"),'; bad2 (incomplete monthly mean data): ',format(nc_bad2,"1d"),'; bad3 (cdutil.YEAR error): ',format(nc_bad3,"1d"),'; bad4 (f_out.write error): ',format(nc_bad4,"1d")]))
