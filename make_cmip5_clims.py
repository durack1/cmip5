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

@author: durack1
"""
import cdutil,os,datetime,time,glob,re,pytz,cdat_info,sys,gc,string,argparse
import cdms2 as cdms
from socket import gethostname
from string import replace

if 'e' in locals():
    del(e,pi,sctypeNA,typeNA)
    gc.collect()

# Set nc classic as outputs
cdms.setNetcdfShuffleFlag(0)
cdms.setNetcdfDeflateFlag(0)
cdms.setNetcdfDeflateLevelFlag(0)

start_time = time.time() ; # Set time counter

# Set conditional whether files are created or just numbers are calculated
parser = argparse.ArgumentParser()
parser.add_argument('experiment',metavar='str',type=str,help='including \'experiment\' as a command line argument will select one experiment to process')
parser.add_argument('variable',metavar='str',type=str,help='including \'variable\' as a command line argument will select one variable to process')
parser.add_argument('start_yr',nargs='?',default=1975,metavar='int',type=int,help='including \'start_yr\' as a command line argument set a start year from which to process')
parser.add_argument('end_yr',nargs='?',default=2005,metavar='int',type=int,help='including \'end_yr\' as a command line argument set an end year from which to process')
args = parser.parse_args()
# Test and validate experiment
if (args.experiment in ['1pctCO2','abrupt4xCO2','amip','historical','historicalNat','piControl','rcp26','rcp45','rcp60','rcp85']):
    experiment = args.experiment ; # 1 = make files
    variable = args.variable
    start_yr = args.start_yr
    start_yr_s = str(start_yr)
    end_yr = args.end_yr
    end_yr_s = str(end_yr)
    print "".join(['** Processing ',variable,' files from ',experiment ,' for ',start_yr_s,'-',end_yr_s,'-Clim.nc file generation **'])
else:
    print "** No valid experiment specified - no *.nc files will be written **"
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
    host_path = '/work/durack1/Shared/cmip5/' ; # crunchy 120119
    cdat_path = '/usr/local/uvcdat/latest/bin/'
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

# Set logfile attributes
time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
logfile = os.path.join(host_path,"".join([time_format,'_make_cmip5_clims-',experiment,'-',variable,'-',trim_host,'.log']))
# Create logfile
logfile_handle = open(logfile,'w')
logfile_handle.write("".join(['TIME: ',time_format,'\n']))
logfile_handle.write("".join(['HOSTNAME: ',host_name,'\n']))
logfile_handle.close()

# Get list of infiles (*.nc) and 3D (*.xml)
filelist1 = glob.glob("".join([host_path,experiment,'/*/an/*/*.nc']))
filelist2 = glob.glob("".join([host_path,experiment,'/*/an/*/*.xml']))

filelist = list(filelist1)
filelist.extend(filelist2) ; filelist.sort()
del(filelist1,filelist2)
gc.collect()

# Purge entries matching atm_vars_exclude by index
i = 0
filelist2 = []
for file in filelist:
    if (file.split('/')[8] in variable) and (file.split('/')[5] in experiment):
        filelist2.insert(i,file)
        i = i + 1

del(filelist,i,file)
filelist = filelist2
del(filelist2)
gc.collect()

# Report total file count to logfile
if 'logfile' in locals():
    logfile_handle = open(logfile,'a')
    logfile_handle.write("".join([host_path,': ',format(len(filelist),"06d"),' nc files found to process\n']))
    logfile_handle.close()

# Count and purge code
# Deal with existing *.nc files
ii,o,e = os.popen3("".join(['ls ',host_path,experiment,'/*/an_clims/',str(start_yr),'-',str(end_yr),'/',variable,'/*.nc | wc -l']))
nc_count = o.read();
print "".join(['** Purging ',nc_count.strip(),' existing *.nc files **'])
logfile_handle = open(logfile,'a')
logfile_handle.write("".join(['** Purging ',nc_count.strip(),' existing *.nc files **\n']))
logfile_handle.close()
cmd = "".join(['rm -f ',host_path,experiment,'/*/an_clims/',str(start_yr),'-',str(end_yr),'/',variable,'/*.nc'])
# Catch errors with system commands
ii,o,e = os.popen3(cmd) ; # os.popen3 splits results into input, output and error - consider subprocess function in future
print "** *.nc files purged **"
logfile_handle = open(logfile,'a')
logfile_handle.write("** *.nc files purged **\n")
logfile_handle.close()
print "** Generating new *.nc files **"
logfile_handle = open(logfile,'a')
logfile_handle.write("** Generating new *.nc files **\n")
logfile_handle.close()

filecount = 0
# Loop through files
for l in filelist:
    filecount = filecount + 1; filecount_s = '%06d' % filecount
    print "".join(["** Processing: ",l," **"])
    var = l.split('/')[8] ; # Get variable name from filename
    f_in = cdms.open(l) ; # Open file
    d = f_in[var] ; # Create variable object - square brackets indicates cdms "file object" and it's associated axes
    # Determine experiment
    time_calc_start = time.time()
    if experiment == 'piControl':
        # Case of piControl files, need to consider spawning time of subsequent experiment
        logtime_now = datetime.datetime.now()
        logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
        time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
        logfile_handle = open(logfile,'a')        
        logfile_handle.write("".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; piControl file skipped        : ',l,' **\n']))
        logfile_handle.close()        
        continue
    else:
        try:
            clim = cdutil.YEAR.climatology(d(time=(start_yr_s,end_yr_s,"cob")))
            clim = clim.astype('float32') ; # Recast from float64 back to float32 precision - half output file sizes
            clim.comment = "".join([start_yr_s,'-',end_yr_s,' climatological mean'])
            outfile = re.sub("[0-9]{4}-[0-9]{4}","".join([start_yr_s,'-',end_yr_s,'_anClim']),l)
            outfile = re.sub(".xml",".nc",outfile) ; # Correct for 3D an.xml files
        except:
            logtime_now = datetime.datetime.now()
            logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
            time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
            logfile_handle = open(logfile,'a')
            logfile_handle.write("".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; PROBLEM file skipped          : ',l,' **\n']))
            logfile_handle.close()
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
    f_out = cdms.open(outfile,'w')
    # Copy across global attributes from source file - do this first, then write again so new info overwrites
    att_keys = f_in.attributes.keys()
    att_dic = {}
    for i in range(len(att_keys)):
        att_dic[i]=att_keys[i],f_in.attributes[att_keys[i]]
        to_out = att_dic[i]
        setattr(f_out,to_out[0],to_out[1])    
    # Write new outfile global atts
    f_out.institution = "Program for Climate Model Diagnosis and Intercomparison (LLNL)"
    f_out.data_contact = "Paul J. Durack; pauldurack@llnl.gov; +1 925 422 5208"
    # Create timestamp, corrected to UTC for history
    local           = pytz.timezone("America/Los_Angeles")
    time_now        = datetime.datetime.now();
    local_time_now  = time_now.replace(tzinfo = local)
    utc_time_now    = local_time_now.astimezone(pytz.utc)
    time_format     = utc_time_now.strftime("%d-%m-%Y %H:%M:%S %p")
    f_out.history   = "".join(['File processed: ',time_format,' UTC; San Francisco, CA, USA'])
    f_out.host      = "".join([host_name,'; CDAT version: ',"".join(["%s" % el for el in cdat_info.version()]),'; Python version: ',string.replace(string.replace(sys.version,'\n','; '),') ;',');')])    
    # Write to output file    
    f_out.write(clim) ; # Write clim first as it has all grid stuff
    # Close all files
    f_in.close()
    f_out.close()
    # Log success to file        
    logtime_now = datetime.datetime.now()
    logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
    time_since_start = time.time() - start_time ; time_since_start_s = '%09.2f' % time_since_start
    logfile_handle = open(logfile,'a')        
    logfile_handle.write("".join(['** ',filecount_s,': ',logtime_format,' ',time_since_start_s,'s; slope&clim: ',time_calc_end_s,'s; created: ',outfile,' **\n']))
    logfile_handle.close()
    # Cleanup
    del(clim,filecount_s,local_time_now,logtime_format,logtime_now,outfile)
    del(time_calc_end,time_calc_end_s,time_calc_start,time_format,time_now)
    del(time_since_start,time_since_start_s,utc_time_now,var)
    # Garbage collection before next file iteration
    gc.collect()
# Log success to file
logfile_handle = open(logfile,'a')
logfile_handle.write("** make_cmip5_clims.py complete **")
logfile_handle.close()
