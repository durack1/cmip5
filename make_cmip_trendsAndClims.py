# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 13:16:50 2012

Paul J. Durack 30th January 2012

This script builds trends and 50-yr climatologies from annual files

PJD 31 Jan 2012     - Began writing
PJD  1 Feb 2012     - Finalised code to write without looping, quick!
PJD  3 Feb 2012     - Added log code and temporal specifics dependent on experiment
PJD 10 Feb 2012     - Added log code, created additional out dir an_trends
PJD 10 Feb 2012     - Problem with temporal index for /work/durack1/Shared/cmip5/rcp45/atm/an/pr/cmip5.HadCM3.rcp45.r10i1p1.an.pr.ver-v20110905.2006-2035.nc
PJD 16 Feb 2012     - Latest run (120216_061434) produced 349 *an_trend* output files increased from 308 (120210_114950)
PJD  2 Mar 2012     - an_trends nc files 120302_1443: 482
                      [durack1@crunchy cmip5]$ ls */*/an_trends/*/*.nc | wc -l
PJD  2 Mar 2012     - Updated uvcdat path
PJD  2 Mar 2012     - an_trends nc files 120302_2108: 693
PJD  9 Mar 2012     - an_trends nc files 120309_1247: 751
PJD 18 Apr 2012     - Added count and purge code
                      an_trends nc files 120418_1257: 751
PJD 18 Apr 2012     - Added institution global att
PJD 18 Apr 2012     - Added exclusion of variables and experiments (not amip)
PJD 15 Jun 2012     - Added filelist2, which searches for an/*/*.xml files - 3D annual means - filelist1 & 2 then added to filelist
PJD 16 Jun 2012     - Corrected issue with 3D.xml input files, output file must have extension *.nc (not *.xml) to write, otherwise an error is returned
PJD 18 Jun 2012     - Changed var_mean and var_change* fields to float32 (are float64), reorder so var_mean is written then var_change*
PJD 18 Jun 2012     - Added dob global_atts to files from source file, version info should copy, global atts are then rewritten if required
PJD 18 Jun 2012     - Added 'experiment' argument to parallelise runs
PJD 13 Jul 2012     - Added additional variables to exclude
PJD 30 Jul 2012     - Like rcp check, added time check to historical - files which don't include 1950-2000 period fallover
PJD 21 Aug 2012     - Added historicalNat to valid experiment list
PJD 21 Nov 2012     - Added checks to correct units (salinity files CCSM4 & CESM)
PJD 21 Nov 2012     - Added time slicing as memory was an issue for 3D fields
PJD 22 Nov 2012     - 'cob' was returning a 51,depth,y,x array, so changed end bounds from 2000->1999 and 2100->2099
PJD 22 Nov 2012     - Added d load even if not a so/sos variable - corrected to load as well if doesn't satisfy units test
PJD 22 Nov 2012     - TOCHECK: If issues appear with missing masks, set missing as float32: $VAR.setMissing(numpy.float32(1e20))
PJD 28 Nov 2012     - Magnitude of trends is too small - rewrote time_axis for passing to linearregression
PJD 28 Nov 2012     - Tidied up a bunch of explicit calls, and resolves non-loaded module issues (when testing use notation [-2:])
PJD 10 Dec 2012     - Added calendar attribute to newd variable before passing to linearregression
PJD 10 Dec 2012     - Trends were reporting 1-year values, inflated these by length of passed (annual) variable to give 50-year (or equiv.) values
PJD 10 Dec 2012     - Updated to just change time axis, saving memory usage (rather than duplicating variable)
PJD 10 Dec 2012     - Update cdms indicator from 'cob' to 'con' and end year 2000 (replacing 1999; n=contained within interval)
PJD 14 Jan 2013     - Added 'uo' to excluded variables
PJD 29 Jan 2013     - Added historicalGHG to experiment checks
PJD  7 Mar 2013     - Commented drift code, need to update files first
PJD  7 Mar 2013     - Added historicalGHG to valid experiments
PJD  8 Mar 2013     - Added .xml to .nc conversion for rcp and CO2 experiments additional to historical
PJD 12 May 2013     - Added oceanonly to known host list
PJD 15 May 2013     - Added historicalExt to experiment checks
PJD 15 May 2013     - Removed historicalExt from experiment lists as this doesn't exist over the 1950-2000 period
PJD  4 Jun 2013     - Updated to use global_att_write from durolib
PJD  4 Jun 2013     - Turned on a tweaked drift estimation
PJD 10 Jun 2013     - Fixed issue with drift change estimates overwriting slope variable
PJD 11 Jun 2013     - Hit issues with linearregression from full timeseries - removed from current code
PJD 11 Jun 2013     - Added in estimates of drift (looping for 3D files), using cmip5_branch_time_dict.pickle
PJD 12 Jun 2013     - Fixed issue with *_drift2 variables being written into *_drift1 variables
PJD 12 Jun 2013     - Added start, end and length attributes to drift clim variables
PJD 12 Jun 2013     - Added realm to script args
PJD 12 Jun 2013     - Simplified code to copy accross file global attributes
PJD 12 Jun 2013     - Added writeToLog function and tidied up log calls
PJD 13 Jun 2013     - Moved writeToLog function into durolib, renamed globalAttWrite function
PJD 18 Jun 2013     - Added cdat_info and ping reporting set off - attempt to speed up spyder
PJD 24 Jun 2013     - Added drift start/end years to drift variable (was only listed on clim variables)
PJD 24 Jun 2013     - Added drift correction back to 50-year equivalent
PJD 24 Jun 2013     - Implemented per variable processing - realms are taking too long
PJD 17 Jul 2013     - Added fixInterpAxis to load statements and implemented code replacement for trend estimates
PJD 17 Jul 2013     - Added conditional level_count test for MPI-ESM-MR
                    Below using 95% of RAM:
                    ** Processing: 000291 cmip5/historical/ocn/an/so/cmip5.MPI-ESM-MR.historical.r1i1p1.an.ocn.so.ver-1.1850-2005.xml **
                    drift_file:        cmip5/piControl/ocn/an/so/cmip5.MPI-ESM-MR.piControl.r1i1p1.an.ocn.so.ver-1.1850-2849.xml
PJD 17 Jul 2013     - Adjusted cmds.setNetcdf flags to ensure files are written with compression
PJD 17 Jul 2013     - Cleaned up commented code relating to fixInterpAxis code replacement for CO2 and rcp experiments
PJD 18 Jul 2013     - Added temporal (1955-2005) subdir before variables as with an_clims for historical only
PJD 23 Jul 2013     - Added tas to variable list
PJD 25 Jul 2013     - Reduced MPI-ESM-MR back to 2 levels (was 3 using ~70% of RAM)
PJD 25 Jul 2013     - Added fixVarUnits function to correct so data and undertook general code tidyup
PJD 25 Jul 2013     - Removed try/except around drift creation
PJD 29 Jul 2013     - Added trip_try to replace continue which is skipping file without branch_dict entries
PJD 30 Jul 2013     - Check for 150-yr drift estimate, if not achieved, skip drift calculation
PJD  5 Aug 2013     - Added test for exception to catch issues with invalid data length (not spanning target years: cmip5.EC-EARTH.historical.r13i1p1.an.ocn.so.ver-v20120503.1850-1915.xml)
PJD  7 Aug 2013     - Corrected exception above to use str(err)
PJD 12 Aug 2013     - Tweaked exception code - cached version caused issues
PJD 19 Aug 2013     - Added catch code for negative dimensions cmip5.MIROC4h.historical.r1i1p1.an.ocn.so.ver-1.1950-2005.xml
PJD 19 Aug 2013     - Added model_suite to argument list
PJD 19 Aug 2013     - Added both cmip3 & 5 support to this script through arguments - new file validation required
PJD 19 Aug 2013     - Added driftcorrect argument
                    - TODO: Remove drift calculation from historical if statement - make standalone test (so works with all experiments)
                    - TODO: Consider using latest (by date) and longest piControl file in drift calculation - currently using first indexed
                      Code appears to mimic source file numbers
                    - TODO: Check behaviours to ensure models aren't being skipped:
                    - Ensure files with no corresponding piControl are created without drift variables and not skipped
                    ** cmip5.CESM1-CAM5-1-FV2.historical.r1i1p1.an.ocn.so.ver-1.1850-2005.xml **
                    ** cmip5.CanCM4.historical.r10i1p1.an.ocn.thetao.ver-1.1961-2005.xml **
                    ** cmip5.FGOALS-g2.historical.r1i1p1.an.ocn.thetao.ver-v1.1850-2005.xml **
                    ** cmip5.HadGEM2-ES.historical.r1i1p1.an.atm.Amon.tas.ver-1.1860-2004.nc **
                    ** cmip5.HadCM3.historical.r7i1p1.an.atm.Amon.tas.ver-1.1860-2005.nc ** 
                    - TODO: CCSM4 now includes years 250-1300, so may need to be subsetted like MPI-ESM-MR
                    - TODO: Using Kate M's parallel code - mpiexec - files copied to /work/durack1/Shared/cmip5/_obsolete/parallel/DistArray/ParaRMT.py from crunchy
                      Consider rk (rank - 0-indexed) nproc (# processors) to determine how jobs are distributed
                    - TODO: Consider alternative methods of drift calculation
                      1. Determine quadratic fit to full timeseries and then take a linear trend from contemporaneous portion - also allows extrapolation beyond overlap
                      2. Determine fit from decadally-averaged timeseries - hammer down noise by using longer temporal averaging window
                      3. Add higher order fits - quadratic & cubic - numpy.polyfit is an alternative to linearregression
                    - TOREPORT: '/work/durack1/Shared/cmip5/historical/seaIce/an/pr/cmip5.BNU-ESM.historical.r1i1p1.an.seaIce.OImon.pr.ver-1.1850-2005.nc'
                      Has an issue with gridded lat/lon in historical and vector in piControl files - these are different when attempting to write file
                      with variables derived from both - either map dimensions from historical across all vars or ignore
                    - TODO: Create function for picontrol file pairing
                    - TODO: Add depth and calculated mean eta variables to sigma (terrain-following) files - cmip5.inmcm4; cmip5.MIROC*

@author: durack1
"""
import argparse,cdat_info,cdtime,cdutil,datetime,gc,glob,os,pickle,re,sys,time
import cdms2 as cdm
import numpy as np
from durolib import fixInterpAxis,fixVarUnits,globalAttWrite,writeToLog
from genutil.statistics import linearregression
from socket import gethostname
from string import replace
#from matplotlib.pyplot import pause
#from numpy import float32

if 'e' in locals():
    del(e,pi,sctypeNA,typeNA)
    gc.collect()

# Turn off cdat ping reporting - Does this speed up Spyder?
cdat_info.ping = False

# Set nc classic as outputs
cdm.setCompressionWarnings(0) ; # Suppress warnings
cdm.setNetcdfShuffleFlag(0)
cdm.setNetcdfDeflateFlag(1) ; # was 0 130717
cdm.setNetcdfDeflateLevelFlag(9) ; # was 0 130717
cdm.setAutoBounds(1) ; # Ensure bounds on time and depth axes are generated

start_time = time.time() ; # Set time counter

# Set conditional whether files are created or just numbers are calculated
parser = argparse.ArgumentParser()
parser.add_argument('model_suite',metavar='str',type=str,help='include \'cmip3/5\' as a command line argument')
parser.add_argument('experiment',nargs='?',default='all',metavar='str',type=str,help='including \'experiment\' will select one experiment to process')
parser.add_argument('realm',nargs='?',default='all',metavar='str',type=str,help='including \'realm\' will select one realm to process')
parser.add_argument('variable',nargs='?',default='all',metavar='str',type=str,help='including \'variable\' will select one variable to process')
parser.add_argument('driftcorrect',nargs='?',default='False',metavar='str',type=str,help='including \'driftcorrect\' will attempt to calculate drift estimate')
args = parser.parse_args()
# First check provided arguments
if (args.model_suite not in ['cmip3','cmip5']):
    print "** No valid model suite specified - no *.nc files will be written **"
    sys.exit()
if (args.experiment not in ['all','1pctCO2','abrupt4xCO2','amip','historical','historicalGHG','historicalNat','piControl','rcp26','rcp45','rcp60','rcp85',
                            '1pctto2x','1pctto4x','20c3m','picntrl','sresa1b','sresa2','sresb1']):
    print "** No valid experiment specified - no *.nc files will be written **"
    sys.exit()
if (args.realm not in ['all','atm','land','ocn','seaIce']):
    print "** No valid realm specified - no *.nc files will be written **"
    sys.exit()
if (args.variable not in ['all','pr','so','tas','thetao']):
    print "** No valid variable specified - no *.nc files will be written **"
    sys.exit()
if (args.driftcorrect in ['True','False']):
    driftcorrect = args.driftcorrect
    if driftcorrect in 'True':
        drift = 'driftcorrect'
        driftcorrect = True
    elif driftcorrect in 'False':
        drift = 'nodriftcorrect'
        driftcorrect = False
else:
   print "** Invalid arguments - no *.nc files will be written **"
    
# Now use provide args
all_files = False
all_realms = False
model_suite = args.model_suite
experiment = args.experiment
realm = args.realm
variable = args.variable
if (args.experiment in 'all') and (args.realm in 'all'):
    print "".join(['** Processing files from ALL experiments and ALL realms for *ClimAndSlope.nc file generation **'])
    all_files = True
    all_realms = True
elif (args.experiment in 'all'):
    print "".join(['** Processing files from ALL experiments and ',realm,' realm for *ClimAndSlope.nc file generation **'])
    all_files = True
    all_realms = False
elif (args.realm in 'all'):
    print "".join(['** Processing files from ',experiment,' experiment and ALL realms for *ClimAndSlope.nc file generation **'])
    all_files = False
    all_realms = True
elif args.variable not in 'all':
    print "".join(['** Processing files from ',experiment,' experiment, ',realm,' realm and ',variable,' variable for *ClimAndSlope.nc file generation **'])
    all_files = False
    all_realms = False
    variable = args.variable    
else:
    print "".join(['** Processing files from ',experiment,' experiment and ',realm,' realm for *ClimAndSlope.nc file generation **'])
    all_files = False
    all_realms = False

# Set host information and directories
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
        # Load drift dictionary
        cmip5_branch_time_dict = pickle.load(open(os.path.join(host_path,"".join([model_suite,'_branch_time_dict.pickle'])),'rb'))
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

# Set logfile attributes
time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
#logfile = os.path.join(host_path,"".join([time_format,'_make_',model_suite,'_trendsAndClims-',experiment,'-',realm,'-',variable,'-',trim_host,'.log']))
logfile = os.path.join(host_path,'tmp',"".join([time_format,'_make_',model_suite,'_trendsAndClims-',experiment,'-',realm,'-',variable,'-',trim_host,'.log'])) ; ## TEST ##
# Create logfile
writeToLog(logfile,"".join(['TIME: ',time_format]))
writeToLog(logfile,"".join(['HOSTNAME: ',host_name]))
del(time_format,time_now) ; gc.collect()

'''
## TEST ##
all_files = False
all_realms = False

model_suite = 'cmip5'
experiment = 'historical'
realm = 'ocn'
variable = 'so'
drift = 'nodriftcorrect'
driftcorrect = False

experiment = 'rcp85'
variable = 'thetao'

model_suite = 'cmip3'
experiment = '20c3m'
realm = 'atm'
variable = 'tas'
driftcorrect = 'False'
'''

# Get list of infiles (*.nc) and 3D (*.xml)
if all_files and all_realms:
    print 'all_files and all_realms'
    filelist1 = glob.glob(os.path.join(host_path,'*/*/an/*/*.nc'))
    filelist2 = glob.glob(os.path.join(host_path,'*/*/an/*/*.xml'))
elif all_realms:
    print 'all_realms'
    filelist1 = glob.glob(os.path.join(host_path,experiment,'*/an/*/*.nc'))
    filelist2 = glob.glob(os.path.join(host_path,experiment,'*/an/*/*.xml'))
elif variable not in 'all':
    print ''.join(['variable: ',variable])
    filelist1 = glob.glob(os.path.join(host_path,experiment,'*/an',variable,'*.nc'))
    filelist2 = glob.glob(os.path.join(host_path,experiment,'*/an',variable,'*.xml'))
else:
    print 'else'
    filelist1 = glob.glob(os.path.join(host_path,experiment,realm,'an/*/*.nc'))
    filelist2 = glob.glob(os.path.join(host_path,experiment,realm,'an/*/*.xml'))

filelist = list(filelist1)
filelist.extend(filelist2) ; filelist.sort()
del(filelist1,filelist2) ; gc.collect()

# Trim out variables and experiments of no interest
vars_atm_exclude = ['evspsbl','hfls','hfss','hurs','huss','prw','ps','psl','rlds','rlus','rsds',
                    'rsus','sfcWind','tasmax','tasmin','tauu','tauv','ts','uas','vas']
vars_ocn_exclude = ['soga','zos','uo']
vars_exclude	 = ['sci','rsdscs','ua','rlutcs','prc','rsuscs','ta','wap''cl','hur',
                     'rlds','sbl','rsdt','zg','clt','hus','mc','rsut','rlut','rsutcs',
                     'rsus','va','rldscs','cli','clw']
vars_exclude.extend(vars_atm_exclude) ;
vars_exclude.extend(vars_ocn_exclude) ; vars_exclude.sort()

exps_exclude    = ['amip'] ; exps_exclude.sort()

# Purge entries matching atm_vars_exclude by index
filelist2 = []
for count,files in enumerate(filelist):
    if all_files:
        if not (files.split('/')[8] in vars_exclude) and not (files.split('/')[5] in exps_exclude):
            filelist2.insert(count,files)
    elif all_realms:
        if not (files.split('/')[8] in vars_exclude) and (files.split('/')[5] in experiment):
            filelist2.insert(count,files)
    else:
        if not (files.split('/')[8] in vars_exclude) and (files.split('/')[6] in realm):
            filelist2.insert(count,files)

del(filelist,count,files)
filelist = filelist2
del(filelist2) ; gc.collect()

# Clean up lists
del(vars_atm_exclude,vars_ocn_exclude,vars_exclude,exps_exclude); gc.collect()

# Report total file count to logfile
if 'logfile' in locals():
    writeToLog(logfile,"".join([host_path,': ',format(len(filelist),"06d"),' nc files found to process']))

# Count and purge code
# Deal with existing *.nc files
if all_files:
    ii,o,e = os.popen3("".join(['ls ',host_path,'*/*/an_trends/*/*.nc | wc -l']))
elif all_realms:
    ii,o,e = os.popen3("".join(['ls ',host_path,experiment,'/*/an_trends/*/*.nc | wc -l']))
else:
    ii,o,e = os.popen3("".join(['ls ',host_path,experiment,realm,'/an_trends/*/*.nc | wc -l']))

nc_count = o.read();
print "".join(['** Purging ',nc_count.strip(),' existing *.nc files **'])
writeToLog(logfile,"".join(['** Purging ',nc_count.strip(),' existing *.nc files **']))
del(ii,o,e,nc_count) ; gc.collect()

if all_files:
    cmd = "".join(['rm -f ',host_path,'*/*/an_trends/*/*.nc'])
elif all_realms:
    cmd = "".join(['rm -f ',os.path.join(host_path,experiment,'*/an_trends/*/*.nc')])
    #cmd = re.sub('/work/durack1/Shared/cmip5/','/work/durack1/Shared/cmip5/tmp/',cmd) ; ## TEST ##
    cmd = re.sub(host_path,os.path.join(host_path,'tmp'),cmd) ; ## TEST ##
else:
    cmd = "".join(['rm -f ',os.path.join(host_path,experiment,realm,'an_trends/*/*.nc')])
    #cmd = re.sub('/work/durack1/Shared/cmip5/','/work/durack1/Shared/cmip5/tmp/',cmd) ; ## TEST ##
    cmd = re.sub(host_path,os.path.join(host_path,'tmp'),cmd) ; ## TEST ##
# Catch errors with system commands


#ii,o,e = os.popen3(cmd) ; # os.popen3 splits results into input, output and error - consider subprocess function in future ## TEST ##


print "** *.nc files purged **"
writeToLog(logfile,"** *.nc files purged **")
print "** Generating new *.nc files **"
writeToLog(logfile,"** Generating new *.nc files **")

# Loop through files
# 130717 - 291 - cmip5.MPI-ESM-MR.historical.r2i1p1.an.ocn.so.ver-1.1850-2005.xml ~80Gb RAM in historical alone
# 130725 - 238:241 - cmip5.GISS-E2-R.historical.r6i1p2.an.ocn.so.ver-v20121015.1850-2005.xml - missing overlap years in piControl through to HadCM3 no piControl
# 130812 - 117 - cmip5.EC-EARTH.historical.r13i1p1.an.ocn.so.ver-v20120503.1850-1915.xml
# 130820 - 295 - cmip5.MPI-ESM-MR.historical.r3i1p1.an.ocn.so.ver-1.1850-2005.xml
# 130820 - 313 - cmip5.MPI-ESM-MR.historical.r3i1p1.an.ocn.thetao.ver-1.1850-2005.xml
for filecount,l in enumerate(filelist):
    filecount_s = '%06d' % (filecount+1)
    print "".join(['** Processing: ',filecount_s,' ',replace(l,'/work/durack1/Shared/',''),' **'])
    var     = l.split('/')[8] ; # Get variable name from filename
    model   = l.split('/')[9].split('.')[1] ; # Get model name from filename
    ver     = l.split('/')[9].split('.')[8] ; # Get version from filename - different for 2D (8) and 3D (7) files due to tableId
    f_in    = cdm.open(l) ; # Open file
    d       = f_in[var] ; # Create variable object - square brackets indicates cdms "file object" and it's associated axes
    # Determine experiment
    experiment = l.split('/')[-1].split('.')[2]
    time_calc_start = time.time()
    
    if experiment in {'piControl','picntrl'}:
        # Case of piControl files, need to consider spawning time of subsequent experiment
        logtime_now         = datetime.datetime.now()
        logtime_format      = logtime_now.strftime("%y%m%d_%H%M%S")
        time_since_start    = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
        writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; piControl file skipped        : ',l,' **']))    
        continue
    
    elif experiment in {'1pctCO2','abrupt4xCO2','1pctto2x','1pctto4x'}:
        d = f_in(var)
        # Check units and correct in case of salinity
        if var == 'so' or var == 'sos':
            [d,_] = fixVarUnits(d,var,True)

        # Create ~50-yr linear trend - with period dependent on experiment
        (slope),(slope_err) = linearregression(fixInterpAxis(d),error=1,nointercept=1)
        # Inflate slope from single year to length of record
        slope           = slope*len(d)
        slope_err       = slope_err*len(d)
        
        slope           = slope.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
        slope_err       = slope_err.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
        slope.comment   = 'start-end change'
        # Create ~50-yr mean climatology
        clim            = cdutil.YEAR.climatology(d())
        clim            = clim.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
        clim.comment    = 'start-end climatological mean'
        outfile         = re.sub("[0-9]{4}-[0-9]{4}","start-end_ClimAndSlope",l)
        outfile         = re.sub(host_path,os.path.join(host_path,'tmp/'),outfile) ; ## TEST ##
        outfile         = re.sub(".xml",".nc",outfile) ; # Correct for 3D an.xml files
    
    elif experiment in {'historical','historicalGHG','historicalNat','20c3m'}:
        # Set start and end year as variables
        if model_suite in 'cmip3':            
            start_yr        = "1970"
            drift_start_yr  = 1900
            end_yr          = "1999"
            drift_end_yr    = 2049
        elif model_suite in 'cmip5':
            start_yr        = "1970" #"1970"
            drift_start_yr  = 1905
            end_yr          = "2004"
            drift_end_yr    = 2055            
        time_yrs        = "".join([start_yr,'-',end_yr])
        # Attempt to load variable as some data doesn't extend 1950-2000                
        try:
            d = f_in(var,time=(start_yr,end_yr,"con"))
        
            # Check units and correct in case of salinity
            if var == 'so' or var == 'sos':
                [d,_] = fixVarUnits(d,var,True)
            
            (slope),(slope_err) = linearregression(fixInterpAxis(d),error=1,nointercept=1)
            # Inflate slope from single year to length of record
            slope           = slope*len(d)
            slope_err       = slope_err*len(d)
    
            slope           = slope.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            slope_err       = slope_err.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            slope.comment   = ''.join([time_yrs,' change'])
            clim            = cdutil.YEAR.climatology(d)
            clim            = clim.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            clim.comment    = "".join([time_yrs,' climatological mean'])
            outfile         = re.sub("[0-9]{4}-[0-9]{4}","".join([time_yrs,'_ClimAndSlope']),l)
            outfile         = re.sub(".xml",".nc",outfile) ; # Correct for 3D an.xml files
            outfile         = re.sub(host_path,os.path.join(host_path,'tmp/'),outfile) ; ## TEST ##
            outfile         = re.sub('/an/',"".join(['/an_trends/',time_yrs,'/']),outfile) ; ## TEST ##
            #print "".join(['outfile: ',outfile])
            # Delete excess variables
            del(d) ; gc.collect()
    
            if model_suite in 'cmip5' and driftcorrect:
                # Attempt drift estimate
                #if cmip5_branch_time_dict.get("ACCESS1-0",{}).get("historical",{}).has_key("r1i1p1"):
                if cmip5_branch_time_dict.get(outfile.split('/')[-1].split('.')[1],{}).get(outfile.split('/')[-1].split('.')[2],{}).has_key(outfile.split('/')[-1].split('.')[3]):
                    branch_time_comp    = cmip5_branch_time_dict[outfile.split('/')[-1].split('.')[1]][outfile.split('/')[-1].split('.')[2]][outfile.split('/')[-1].split('.')[3]]['branch_time_comp']
                    bits                = branch_time_comp.split(' ')
                    compt               = cdtime.comptime(int(bits[0].split('-')[0]),int(bits[0].split('-')[1]),int(bits[0].split('-')[2])) ; # HHMMSS are assumed
                    # Get parent_exp_rip
                    parent_exp_rip      = cmip5_branch_time_dict[outfile.split('/')[-1].split('.')[1]][outfile.split('/')[-1].split('.')[2]][outfile.split('/')[-1].split('.')[3]]['parent_exp_rip']
                    # Determine start year of historical
                    an_start_year       = np.int(f_in.an_start_year)
                    # Determine offset from historical first/last years
                    offset_start        = drift_start_yr-an_start_year ; # Case ACCESS1-0 = 50
                    offset_end          = drift_end_yr-an_start_year ; # Case ACCESS1-0 = 200
                    # Start/end drift times
                    drift_start         = compt.add(offset_start,cdtime.Year) ; # Add offsets to picontrol time
                    drift_end           = compt.add(offset_end,cdtime.Year) ; # Add offsets to picontrol time
                    #print ''.join(['pid: ',str(os.getpid())]) ; # Returns calling python instance, so master also see os.getppid() - Parent
                    
                    # Determine whether piControl file/data overlap exists
                    drift_file = os.path.join(replace(l[0:l.rfind('/')],'historical','piControl'),".".join(['cmip5',model,parent_exp_rip,'*']))
                    #print 'drift_file',drift_file
                    drift_file = glob.glob(drift_file) ; # Returns first file, not latest (by date)
                    if drift_file == []:
                        print "** No drift file found **"
                        writeToLog(logfile,"** No drift file found **")
                        trip_try #continue
                    drift_file = drift_file[0] ; # Use first indexed
                    print ''.join(['   drift_file:        ',replace(drift_file,'/work/durack1/Shared/','')])
                    writeToLog(logfile,''.join(['drift_file: ',replace(drift_file,'/work/durack1/Shared/','')]))
                    f_drift = cdm.open(drift_file);
                    # Do sanity check to ensure that calendars align
                    if f_in.calendar != f_drift.calendar:
                        # Case: cmip5/piControl/atm/an/pr/cmip5.MIROC4h.piControl.r1i1p1.an.atm.Amon.pr.ver-1.0051-0150.nc
                        # Case: 
                        print "** File calendars differ, skipping model **"
                        writeToLog(logfile,"** File calendars differ, skipping model **")
                        trip_try #continue
                    d_h = f_drift[var]
                    # Do sanity check to ensure that grids align
                    if clim.getLatitude().shape != d_h.getLatitude().shape:
                         # Case: cmip5/historical/seaIce/an/pr/cmip5.BNU-ESM.historical.r1i1p1.an.seaIce.OImon.pr.ver-1.1850-2005.nc
                        print "** File grids differ, skipping model **"
                        writeToLog(logfile,"** File grids differ, skipping model **")
                        trip_try #continue                    
        
                    # Check start and end years - skip drift if not > 150
                    t = d_h.getAxis(0)
                    picontrol_start_yr  = t.asComponentTime()[0].year
                    picontrol_end_yr    = t.asComponentTime()[-1].year
                    if drift_start.year < picontrol_start_yr:
                        drift_start = cdtime.comptime(picontrol_start_yr,1,1)
                    if drift_end.year > picontrol_end_yr:
                        drift_end = cdtime.comptime(picontrol_end_yr,12,31)
                    if drift_end.year-drift_start.year < 150:
                        yr_count = drift_end.year-drift_start.year
                        print "".join(['** Less than required 150-yrs: ',str(yr_count),' skipping model **'])
                        writeToLog(logfile,"".join(['** Less than required 150-yrs: ',str(yr_count),' skipping model **']))
                        trip_try #continue
                                
                    # Loop over vertical levels if ocean var
                    if var in ['so','thetao']:
                        # Case of 3D variables - Build output arrays
                        clim_drift1         = np.ma.zeros([1,d_h.shape[1],d_h.shape[2],d_h.shape[3]])
                        slope_drift1        = np.ma.zeros([d_h.shape[1],d_h.shape[2],d_h.shape[3]])
                        slope_err_drift1    = np.ma.zeros([d_h.shape[1],d_h.shape[2],d_h.shape[3]])
                        clim_drift2         = np.ma.zeros([1,d_h.shape[1],d_h.shape[2],d_h.shape[3]])
                        slope_drift2        = np.ma.zeros([d_h.shape[1],d_h.shape[2],d_h.shape[3]])
                        slope_err_drift2    = np.ma.zeros([d_h.shape[1],d_h.shape[2],d_h.shape[3]])
        
                        # Deal with memory limits                    
                        if model in 'MPI-ESM-MR':
                            level_count = 2; # 2: ~70Gb, 3: ~70% usage
                        else:
                            level_count = 5;
                        for depth in range(0,((d_h.shape[1])-1),level_count):
                            print "".join(['lev: ',format(depth,'02d'),' of ',str((d_h.shape[1])-1)])
                            #d_level = f_drift(var,time=(drift_start,drift_end,'con'),lev=slice(depth,depth+1,1),latitude=(-90,90,'cc'),longitude=(0,360,'cc'))
                            d_level = f_drift(var,lev=slice(depth,depth+level_count,1))
        
                            # Use 150-year window
                            d_level_150                 = d_level(time=(drift_start,drift_end,'con'))
                            (slope_lev),(slope_err_lev) = linearregression(fixInterpAxis(d_level_150),error=1,nointercept=1)
                            # Inflate slope from single year to length of record
                            slope_drift1[depth:depth+level_count,...]       = slope_lev*(50/len(d_level_150)) ; # Correct back to 50-yr equivalent
                            slope_err_drift1[depth:depth+level_count,...]   = slope_err_lev*(50/len(d_level_150))
                            clim_tmp1                                       = cdutil.YEAR.climatology(d_level_150)
                            clim_drift1[0,depth:depth+level_count,...]      = clim_tmp1
                            del(d_level_150,slope_lev,slope_err_lev) ; gc.collect()
                            
                            # Use full time window
                            (slope_lev),(slope_err_lev) = linearregression(fixInterpAxis(d_level),error=1,nointercept=1)
                            # Inflate slope from single year to length of record
                            slope_drift2[depth:depth+level_count,...]       = slope_lev*(50/len(d_level)) ; # Correct back to 50-yr equivalent
                            slope_err_drift2[depth:depth+level_count,...]   = slope_err_lev*(50/len(d_level))
                            clim_tmp2                                       = cdutil.YEAR.climatology(d_level)
                            clim_drift2[0,depth:depth+level_count,...]      = clim_tmp2
                            del(d_level,slope_lev,slope_err_lev) ; gc.collect()
                        # if depth in range ...
                            
                        # for depth in range(d_h.shape ...
                        # Redress np to cdms variables
                        slope_drift1        = cdm.createVariable(slope_drift1,id='slope_drift1')
                        slope_drift1.setAxis(0,d_h.getAxis(1))                    
                        slope_drift1.setAxis(1,d_h.getAxis(2))
                        slope_drift1.setAxis(2,d_h.getAxis(3))
                        slope_err_drift1    = cdm.createVariable(slope_err_drift1,id='slope_err_drift1')
                        slope_err_drift1.setAxis(0,d_h.getAxis(1))
                        slope_err_drift1.setAxis(1,d_h.getAxis(2))
                        slope_err_drift1.setAxis(2,d_h.getAxis(3))
                        clim_drift1         = cdm.createVariable(clim_drift1,id='clim_drift1')
                        clim_drift1.setAxis(0,clim_tmp1.getAxis(0))
                        clim_drift1.setAxis(1,d_h.getAxis(1))
                        clim_drift1.setAxis(2,d_h.getAxis(2))
                        clim_drift1.setAxis(3,d_h.getAxis(3))
                        slope_drift2        = cdm.createVariable(slope_drift2,id='slope_drift2')
                        slope_drift2.setAxis(0,d_h.getAxis(1))                    
                        slope_drift2.setAxis(1,d_h.getAxis(2))
                        slope_drift2.setAxis(2,d_h.getAxis(3))
                        slope_err_drift2    = cdm.createVariable(slope_err_drift2,id='slope_err_drift2')
                        slope_err_drift2.setAxis(0,d_h.getAxis(1))
                        slope_err_drift2.setAxis(1,d_h.getAxis(2))
                        slope_err_drift2.setAxis(2,d_h.getAxis(3))
                        clim_drift2         = cdm.createVariable(clim_drift2,id='clim_drift2')
                        clim_drift2.setAxis(0,clim_tmp2.getAxis(0))
                        clim_drift2.setAxis(1,d_h.getAxis(1))
                        clim_drift2.setAxis(2,d_h.getAxis(2))
                        clim_drift2.setAxis(3,d_h.getAxis(3))
                        
                    else:
                        # Case of 2D variables
                        d = f_drift(var)
                        # Use 150-year window
                        d1 = d(time=(drift_start,drift_end,'con'))
                        (slope_lev),(slope_err_lev) = linearregression(fixInterpAxis(d1),error=1,nointercept=1)
                        # Inflate slope from single year to length of record
                        slope_drift1                = slope_lev*len(d1)
                        slope_err_drift1            = slope_err_lev*len(d1)
                        clim_drift1                 = cdutil.YEAR.climatology(d1)
                        del(d1,slope_lev,slope_err_lev) ; gc.collect()
                        # Use full time window
                        (slope_lev),(slope_err_lev) = linearregression(fixInterpAxis(d),error=1,nointercept=1)
                        # Inflate slope from single year to length of record
                        slope_drift2                = slope_lev*len(d)
                        slope_err_drift2            = slope_err_lev*len(d)
                        clim_drift2                 = cdutil.YEAR.climatology(d)
                        del(d,slope_lev,slope_err_lev) ; gc.collect()
                        f_drift.close()
                    # if var in ['so ...
        
                    # Delete excess variables
                    del(d_h,branch_time_comp,bits,compt,parent_exp_rip,an_start_year,offset_start,offset_end) ; gc.collect()             
                    
                    # Redress variables
                    clim_drift1                 = clim_drift1.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
                    clim_drift1.id              = "".join([var,'_mean_drift1'])
                    clim_drift1.comment         = "".join([str(drift_end.year-drift_start.year),'-year piControl climatological mean'])
                    clim_drift1.file            = drift_file
                    clim_drift1.drift_start     = str(drift_start.year)
                    clim_drift1.drift_end       = str(drift_end.year)
                    clim_drift1.drift_length    = str(drift_end.year-drift_start.year)
                    slope_drift1                = slope_drift1.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
                    slope_drift1.id             = "".join([var,'_change_drift1'])
                    slope_drift1.comment        = "".join([str(drift_end.year-drift_start.year),'-year piControl linear drift'])
                    slope_drift1.file           = drift_file
                    slope_drift1.drift_start    = str(drift_start.year)
                    slope_drift1.drift_end      = str(drift_end.year)
                    slope_drift1.drift_length   = str(drift_end.year-drift_start.year)
                    del(drift_start,drift_end) ; gc.collect()
                    slope_err_drift1            = slope_err_drift1.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
                    slope_err_drift1.id         = "".join([var,'_change_error_drift1'])
                    slope_err_drift1.comment    = 'linear trend error drift1'
                    clim_drift2                 = clim_drift2.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
                    clim_drift2.id              = "".join([var,'_mean_drift2'])
                    clim_drift2.comment         = 'full piControl climatological mean'
                    clim_drift2.file            = drift_file
                    clim_drift2.drift_start     = str(picontrol_start_yr)
                    clim_drift2.drift_end       = str(picontrol_end_yr)
                    clim_drift2.drift_length    = str(picontrol_end_yr-picontrol_start_yr)
                    slope_drift2                = slope_drift2.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
                    slope_drift2.id             = "".join([var,'_change_drift2'])
                    slope_drift2.comment        = 'full piControl linear drift'
                    slope_drift2.file           = drift_file
                    slope_drift2.drift_start    = str(picontrol_start_yr)
                    slope_drift2.drift_end      = str(picontrol_end_yr)
                    slope_drift2.drift_length   = str(picontrol_end_yr-picontrol_start_yr)
                    del(picontrol_start_yr,picontrol_end_yr) ; gc.collect()
                    slope_err_drift2            = slope_err_drift2.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
                    slope_err_drift2.id         = "".join([var,'_change_error_drift2'])
                    slope_err_drift2.comment    = 'linear trend error drift2'
                    
                else:
                    print "".join(['** KeyError: ',model,' - no branch_time information exists: Drift estimate failed **'])
                    writeToLog(logfile,"".join(['** KeyError: ',model,' - no branch_time information exists: Drift estimate failed **']))  
                # if cmip5_branch_time_dict.get ...  
            
        except Exception,err:
            print 'Exception thrown: ',err
            writeToLog(logfile,"".join(['** Exception thrown: ',str(err), ' **']))
            if 'clim_drift1' in locals():
                del(clim_drift1,slope_drift1,slope_err_drift1,clim_drift2,slope_drift2,slope_err_drift2)
            if 'Coordinate interval is out of range' in re.sub('\'','',str(err)):
                # Catch issues with incomplete historical timeseries: cmip5.EC-EARTH.historical.r13i1p1.an.ocn.so.ver-v20120503.1850-1915.xml
                # trip_try will catch issues with drift estimates from piControl files
                print "".join(['** PROBLEM file skipped: ',l,' Coordinate interval out of range error **'])
                writeToLog(logfile,"".join(['** PROBLEM file skipped: ',l,' Coordinate interval out of range error **']))
                continue
            if 'slope' not in locals():
                # Catch issues with negative dimensions in historical: cmip5/historical/ocn/an/so/cmip5.MIROC4h.historical.r1i1p1.an.ocn.so.ver-1.1950-2005.xml
                print "".join(['** PROBLEM file skipped: ',l,' slope not calculated for historical **'])
                writeToLog(logfile,"".join(['** PROBLEM file skipped: ',l,' slope not calculated for historical **']))
                continue
            logtime_now = datetime.datetime.now()
            logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
            time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
            writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; PROBLEM file skipped          : ',l,' **']))
            pass #continue
    
    elif experiment in {'rcp26','rcp45','rcp60','rcp85','sresa1b','sresa2','sresb1'}:
        # Try for rcp's as some data doesn't extend 2050-2099
        try:
            # Set start and end year as variables
            start_yr    = "2050"
            end_yr      = "2099" 
            time_yrs    = "".join([start_yr,'-',end_yr])
            d = f_in(var,time=(start_yr,end_yr,"con"))
            # Check units and correct in case of salinity
            if var == 'so' or var == 'sos':
                [d,_] = fixVarUnits(d,var,True)

            # Create ~50-yr linear trend - with period dependent on experiment
            (slope),(slope_err) = linearregression(fixInterpAxis(d),error=1,nointercept=1)
            # Inflate slope from single year to length of record
            slope           = slope*len(d)
            slope_err       = slope_err*len(d)
            
            slope           = slope.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            slope_err       = slope_err.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            slope.comment   = ''.join([time_yrs,' change'])
            clim            = cdutil.YEAR.climatology(d)
            clim            = clim.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            clim.comment    = "".join([time_yrs,' climatological mean'])
            outfile         = re.sub("[0-9]{4}-[0-9]{4}","".join([time_yrs,'_ClimAndSlope']),l)
            outfile         = re.sub(".xml",".nc",outfile) ; # Correct for 3D an.xml files
            #outfile         = re.sub('/work/durack1/Shared/cmip5/','/work/durack1/Shared/cmip5/tmp/',outfile) ; ## TEST ##
            outfile         = re.sub(host_path,os.path.join(host_path,'tmp/'),outfile) ; ## TEST ##
            outfile         = re.sub('/an/',"".join(['/an_trends/',time_yrs,'/']),outfile) ; ## TEST ##
            #print "".join(['outfile: ',outfile])            
        except:
            logtime_now = datetime.datetime.now()
            logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
            time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
            writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; PROBLEM file skipped          : ',l,' **']))
            continue
    
    # Pull drift code out of historical if statement
    if driftcorrect:
        pass
    
    # Calculate time taken to process
    time_calc_end = time.time() - time_calc_start; time_calc_end_s = '%08.2f' % time_calc_end

    # Rename standard variables
    slope.id = "".join([var,'_change'])
    slope_err.id = "".join([var,'_change_error'])
    slope_err.comment = 'linear trend error'
    clim.id = "".join([var,'_mean'])

    # Create output file with new path
    outfile = re.sub('/an/','/an_trends/',outfile)
    # Check path exists
    if not os.path.exists(os.sep.join(outfile.split('/')[0:-1])):
        os.makedirs(os.sep.join(outfile.split('/')[0:-1]))
    # Check file exists
    if os.path.exists(outfile):
        print "** File exists.. removing **"
        os.remove(outfile)
    f_out = cdm.open(outfile,'w')
    # Write new outfile global atts
    globalAttWrite(f_out,options=None) ; # Use function to write standard global atts to output file
    # Copy across global attributes from source file - do this first, then write again so new info overwrites
    for i,key in enumerate(f_in.attributes.keys()):
        setattr(f_out,key,f_in.attributes.get(key))
    del(i,key) ; gc.collect()
    # Write to output file
    f_out.write(clim) ; # Write clim first as it has all grid stuff
    if 'slope_drift1' in locals():
        f_out.write(clim_drift1)
        f_out.write(clim_drift2)
    f_out.write(slope)
    f_out.write(slope_err)
    if 'slope_drift1' in locals():
        f_out.write(slope_drift1)
        f_out.write(slope_err_drift1)
        f_out.write(slope_drift2)
        f_out.write(slope_err_drift2)
    # Close all files
    f_in.close()
    f_out.close()
    # Log success to file        
    logtime_now = datetime.datetime.now()
    logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
    time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
    writeToLog(logfile,"".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; slope&clim: ',time_calc_end_s,'s; created: ',outfile,' **']))
    # Cleanup
    del(f_in,f_out)
    if 'f_drift' in locals():
        del(f_drift)
    del(clim,experiment,filecount_s,logtime_format,logtime_now,outfile)
    del(slope,slope_err,time_calc_end,time_calc_end_s,time_calc_start)
    if 'slope_drift1' in locals():
        del(clim_drift1,slope_drift1,slope_err_drift1)
        del(clim_drift2,slope_drift2,slope_err_drift2)
    del(time_since_start,time_since_start_s,var) ; gc.collect()

# Log success to file
writeToLog(logfile,"** make_cmip5_trendAndClims.py complete **")
    
'''
# Plotting tips
vcs.init()
v.plot(dannmean)
i = v.createisofill()
levs = vcs.mkscale(32,38,20)
colors = vcs.getcolors(levs)
i.levels=levs
i.fillareacolors=colors
#v.clear(); v.close()
v.plot(dannmean,i)
i.list() ; # list all attributes which can be controlled    
'''
