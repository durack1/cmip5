#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 09:40:47 2012

Paul J. Durack 23rd January 2012

This script builds *.xml files for all "interesting" model variables

PJD 24 Mar 2014     - Added tauuo and tauvo variables to ocn realm
PJD 12 May 2014     - Added rluscs to the variable list (Mark Z requested)
PJD  7 Aug 2014     - Updated to include new path /cmip5_css02/cmip5
PJD  7 Aug 2014     - Added exception descriptor - '** Crash while trying to create a new directory: '
PJD  8 Aug 2014     - Updated path indexing to deal with /cmip5_css02/cmip5/data/ case
PJD  8 Aug 2014     - Added exception descriptor in pathToFile function
PJD  8 Aug 2014     - General code tidyup and increased xmlGood to 1e5 (was 4e4)
PJD  8 Aug 2014     - Current data shows 3715 (144706-140991) duplicate xml files are listed
                      presently no intelligent selection of file is done or validation that the version selected is valid
PJD  8 Aug 2014     - Removed shebang statement as new UVCDAT excludes pytz module which causes durolib load to fail
                      python version explicitly set in cron.sh file
PJD  8 Aug 2014     - Added HadGEM2-AO attempt to recover data and BESM-OA2-3 decadal skip
                    Fix HadGEM2-AO path problems - missing realm DRS component
                    pathToFile - Exception: list index out of range ->
                    /cmip5_css01/scratch/cmip5/output1/NIMR-KMA/HadGEM2-AO/rcp60/mon/atmos/ta/r3i1p1 vs
                    /cmip5_css02/data/cmip5/output1/CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/zg/1
                    Fix BEMS-OA2-3 path problems - missing realm DRS component
                    pathToFile - Exception: list index out of range ->
                    /cmip5_css02/scratch/cmip5/output1/INPE/BESM-OA2-3/decadal1990/day/seaIce/sic/r8i1p1
PJD 20 Aug 2014     - Added mkDirNoOSErr function to get around crashes with duplicate os.mkdir calls
PJD 20 Aug 2014     - Updated pathToFile function for more intelligent searching - exclusion of experiments, time frequencies and
                    data found in bad[0-9] subdirectories (Jeff's code creates these subdirs on failed download - using md5 check)
PJD 20 Aug 2014     - Updated to use scandir function in place of os.walk - requires installation on machines (not part of python std lib)
                    FUNCTION: os.walk
                    000000.10 : gdo2_scratch  scan complete.. 0      paths total; 0      output files to be written (92  vars sampled)
                    000003.80 : gdo2_data     scan complete.. 1754   paths total; 788    output files to be written (92  vars sampled)
                    000466.96 : css01_scratch scan complete.. 112587 paths total; 47017  output files to be written (92  vars sampled)
                    000002.01 : css01_data    scan complete.. 834    paths total; 708    output files to be written (92  vars sampled)
                    001100.51 : css02_scratch scan complete.. 132615 paths total; 59778  output files to be written (92  vars sampled)
                    000831.71 : css02_data    scan complete.. 69899  paths total; 32098  output files to be written (92  vars sampled)
                    000039.72 : css02_cmip5   scan complete.. 8770   paths total; 3950   output files to be written (92  vars sampled)
                    FUNCTION: scandir.walk
                    000000.10 : gdo2_scratch  scan complete.. 0      paths total; 0      output files to be written (92  vars sampled)
                    000004.96 : gdo2_data     scan complete.. 1754   paths total; 788    output files to be written (92  vars sampled)
                    000243.02 : css01_scratch scan complete.. 112587 paths total; 47017  output files to be written (92  vars sampled)
                    000002.00 : css01_data    scan complete.. 834    paths total; 708    output files to be written (92  vars sampled)
                    000789.48 : css02_scratch scan complete.. 132615 paths total; 59778  output files to be written (92  vars sampled)
                    000439.27 : css02_data    scan complete.. 69899  paths total; 32098  output files to be written (92  vars sampled)
                    000032.41 : css02_cmip5   scan complete.. 8770   paths total; 3950   output files to be written (92  vars sampled)
PJD 20 Aug 2014     - Reordered file so that function declaration is blocked up top
PJD 20 Aug 2014     - Moved mkDirNoOSErr and sysCallTimeout to durolib
PJD 21 Aug 2014     - Cleaned up module imports
PJD 21 Aug 2014     - Confirmed directory walking - exclusion code is working correctly
PJD 15 Sep 2014     - PJD 23 Jan 2012 to 18 Nov 2013: Comments purged, look in _obsolete directory for 140915a_* file
PJD 15 Sep 2014     - Updated HadGEM2-AO data recovery to use realm rather than vars to assign tableId ('pr' duplicated across tables)
PJD 15 Sep 2014     - Updated ocn_vars to include boundary fluxes
PJD 15 Sep 2014     - Added keepFile function - renames cdscan warning files '..latestX.WARNX.xml' rather than purging
PJD 19 Nov 2014     - Added 'amip4K','amip4xCO2' experiments (Chris T requested)
PJD 27 Feb 2015     - Updated to match variable to path_bits - deals with LASG-CESS/FGOALS-g2 and FIO/fio-esm published data paths
PJD  7 Mar 2015     - Disabled sysCallTimeout - uncertain what the issue is here
PJD 10 Mar 2015     - Added clcalipso to the variable list (Mark Z/Chen Z requested)
PJD  7 Jul 2015     - Fixed len_vars correctly obtained from list_vars
PJD  7 Jul 2015     - Add PID of master process to logfile contents (not just filename)/sendmail output
PJD  9 Jul 2015     - Added checkPID function
PJD 13 Jul 2015     - Added PID test before purging and regenerating xmls
                    - Generalize path indices using DRS cmip[5-6]/output[1-5] reference point
PJD 16 Jul 2015     - Added /cmip5_css02/scratch/_gc/ to search path (new scan)
PJD 17 Jul 2015     - Corrected checkPID query to skip current logFile - was terminating itself
PJD 17 Jul 2015     - Converted diagnostic file to be written using cPickle and gzipped

                    - TODO:
                    Add check to ensure CSS/GDO systems are online, if not abort - use sysCallTimeout function
                    sysCallTimeout(['ls','/cmip5_gdo2/'],5.) ; http://stackoverflow.com/questions/13685239/check-in-python-script-if-nfs-server-is-mounted-and-online
                    Add model masternodes
                    Fix issue with no valid files being recorded
                    Placing read test in pathToFile will trim out issues with 0-sized files and read permissions, so reporting may need to be relocated
                    Add counters for lat1 vs lat0
                    Report new runtimeError in cdscan - problems with overlapping times, issue in combineKeys function - Report to Jeff/Charles
                    Added demo code from Charles to convert processes and queues into lists of objects thereby subverting hard-coding and parallel limits
                    update for gdo2_data (~8k; 2.2hrs) and css02_scratch (~25k; 7hrs) to scour using multiple threads each - what is the IO vs wait difference?
                     consider using multiprocess.pool to achieve this, so full loads until job(s) are completed
                    Consider using multiprocess.pool (which loads up processes concurrently) rather than multiprocess.Process
                    Fix duplicate versions - add flag for latest or deprecated - awaiting Bob to create index file as esgquery_index wont cope with 40k queries
                     Conditionally purge xmls with earlier version number (should sort so last generated file is latest)
                    [durack1@crunchy output1]$ pwd
                    /cmip5_gdo2/data/cmip5/output1
                    [durack1@crunchy output1]$ ncdump -h NOAA-GFDL/GFDL-CM3/historical/mon/atmos/Amon/r1i1p1/tas/1/tas_Amon_GFDL-CM3_historical_r1i1p1_186001-186412.nc | grep tracking_id
                    :tracking_id = "9ab415bd-adf7-4dcf-a13c-e9530d5efe41" ;
                    # Should also test an deprecated file for "False" response
                    import urllib2
                    req = urllib2.Request(url='http://pcmdi9.llnl.gov/esg-search/search?',data='type=File&query=tracking_id:9ab415bd-adf7-4dcf-a13c-e9530d5efe41&fields=latest')
                    query = urllib2.urlopen(req)
                    print query.read()

@author: durack1
"""

import argparse,cPickle,datetime,gc,gzip,os,re,sys,time #glob,shlex,
import scandir ; # Installed locally on oceanonly and crunchy
from durolib import writeToLog #sysCallTimeout,mkDirNoOSErr,
from multiprocessing import Process,Manager
from socket import gethostname
from string import replace
from subprocess import Popen,PIPE #call,
#import cdms2 as cdm

#%% Define functions

def logWrite(logfile,time_since_start,path_name,i1,data_outfiles,len_vars):
    outfile_count = len(data_outfiles)
    time_since_start_s = '%09.2f' % time_since_start
    print "".join([path_name.ljust(13),' scan complete.. ',format(i1,"1d").ljust(6),' paths total; ',str(outfile_count).ljust(6),' output files to be written (',format(len_vars,"1d").ljust(3),' vars sampled)'])
    writeToLog(logfile,"".join([time_since_start_s,' : ',path_name.ljust(13),' scan complete.. ',format(i1,"1d").ljust(6),' paths total; ',format(outfile_count,"1d").ljust(6),' output files to be written (',format(len_vars,"1d").ljust(3),' vars sampled)']))
    return

#%%    
def pathToFile(inpath,start_time,queue1):
#$#def pathToFile(inpath,start_time): #; # Non-parallel version of code for testing
    data_paths = [] ; i1 = 0
    #for (path,dirs,files) in os.walk(inpath,topdown=True):
    for (path,dirs,files) in scandir.walk(inpath,topdown=True):

        ## IGNORE EXPERIMENTS - AT SEARCH LEVEL - SPEED UP SEARCH ##
        expExclude = set(['aqua4K','aqua4xCO2','aquaControl','esmControl','esmFdbk1','esmFixClim1',
                          'esmFixClim2','esmHistorical','esmrcp85','Igm','midHolocene','sst2030','sst2090','sst2090rcp45',
                          'sstClim','sstClim4xCO2','sstClimAerosol','sstClimSulfate','volcIn2010'])
        #timeExclude = set(['3hr','6hr','day','monClim','yr'])
        timeExclude = set(['mon','monClim','yr'])
        reDec = re.compile(r'decadal[0-9]{4}')
        reVol = re.compile(r'noVolc[0-9]{4}')
        dirs[:] = [d for d in dirs if d not in expExclude]
        dirs[:] = [d for d in dirs if d not in timeExclude and not re.search(reDec,d) and not re.search(reVol,d)]
        ## IGNORE EXPERIMENTS ##

        # Test files don't exist and we're not at the end of the directory tree
        if files == [] and dirs != []:
            continue ; #print 'files&dirs',path

        ## BAD DIRECTORIES - TRUNCATE INVALID MD5 DATA ##
        if re.search(r'bad[0-9]',path):
            continue ; #print 're.search',path
        if '-will-delete' in path:
            print '-will-delete',path
            continue
        # Iterate and purge bad[0-9] subdirs
        for dirCount,el in reversed(list(enumerate(dirs))):
            if re.match(r'bad[0-9]',el):
                del dirs[dirCount]

        #130225 1342: Pathologies to consider checking for bad data
        #badpaths = ['/bad','-old/','/output/','/ICHEC-old1/']
        #bad = GISS-E2-R, EC-EARTH ; -old = CSIRO-QCCCE-old ; /output/ = CSIRO-Mk3-6-0 ; /ICHEC-old1/ = EC-EARTH
        #paths rather than files = CNRM-CM5, FGOALS-g2, bcc-csm1-1
        #duplicates exist between /cmip5_gdo2/scratch and /cmip5_css02/scratch = CCSM4, CSIRO-Mk3-6-0
        ## BAD DIRECTORIES ##

        if files != [] and dirs == []:
            # Append to list variable
            #$#print i1,path #$#
            data_paths += [path]
            i1 = i1 + 1 ; # Increment counter

    # Create variable and realm names
    experiments = ['1pctCO2','abrupt4xCO2','amip','amip4K','amip4xCO2','amipFuture','historical','historicalExt',
                   'historicalGHG','historicalMisc','historicalNat','past1000','piControl','rcp26','rcp45','rcp60','rcp85'] ; experiments.sort()
    #temporal    = ['fx','mon'] ; # For months and fixed fields only
    temporal    = ['3hr','6hr','day'] ; # For short periods
    atm_vars    = ['cl','clcalipso','cli','clisccp','clivi','clt','clw','clwvi','evspsbl','hfls','hfss','hur','hurs',
                   'hus','huss','mc','pr','prc','prsn','prw','ps','psl','rlds','rldscs','rlus','rluscs','rlut',
                   'rlutcs','rsds','rsdscs','rsdt','rsus','rsuscs','rsut','rsutcs','sbl','sci','sfcWind',
                   'ta','tas','tasmax','tasmin','tauu','tauv','ts','ua','uas','va','vas','wap','zg'] ; atm_vars.sort()
    atmOrocn    = ['atm','ocn'] ; atmOrocn.sort()
    fx_vars     = ['areacella','areacello','basin','deptho','orog','sftlf','sftof','volcello'] ; fx_vars.sort()
    land_vars   = ['mrro','mrros','tsl'] ; land_vars.sort()
    ocn_vars    = ['agessc','cfc11','evs','ficeberg','friver','hfds','hfls','hfss','mfo','mlotst','omlmax','pr','rlds',
                   'rhopoto','sfriver','so','soga','sos','tauuo','tauvo','thetao','thetaoga','tos','uo','vo','vsf','vsfcorr',
                   'vsfevap','vsfpr','vsfriver','wfo','wfonocorr','zos','zostoga'] ; ocn_vars.sort()
    seaIce_vars = ['sic','sit'] ; seaIce_vars.sort()
    list_vars   = atm_vars+fx_vars+land_vars+ocn_vars+seaIce_vars ; # Create length counter for reporting
    
    list_vars   = ['sos']    
    
    len_vars    = len(list_vars) ; # Create length counter for reporting

    # Check for valid outputs
    if not data_paths:
        #print "** No valid data found on path.. **"
        # Create timestamp as function completes
        time_since_start = time.time() - start_time
        #$#return('','',time_since_start,i1,0,len_vars) ; # Non-parallel version of code for testing
        queue1.put_nowait(['','',time_since_start,i1,0,len_vars]) ; # Queue
        return

    # Mine inputs for info and create outfiles and paths
    data_outfiles,data_outfiles_paths = [[] for _ in range(2)] ; i2 = 0
    for path in data_paths:
        path_bits   = path.split('/')
        # Set indexing - first data/scratch
        if 'data' in path_bits:
            pathIndex = path_bits.index('data')
        elif 'scratch' in path_bits:
            pathIndex = path_bits.index('scratch')
        # Next find DRS start index
        # Naming obtained from http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf
        ActivityTest    = re.compile('cmip[5-6]$')
        ProductTest     = re.compile('^output') ; # Most conform to output[1-3], however CSIRO-Mk3-6-0 doesn't
        CMIPIndex       = [ i for i, item in enumerate(path_bits) if re.match(ActivityTest,item) ][-1] ; # Get last entry
        if re.search(ProductTest,path_bits[CMIPIndex+1]):
            DRSStartIndex = CMIPIndex+2
        else:
            print path_bits
        # Use indices to build output filenames
        try:
            #institute   = path_bits[DRSStartIndex]
            model       = path_bits[DRSStartIndex+1] ; #4,6
            experiment  = path_bits[DRSStartIndex+2] ; #5,7
            time_ax     = path_bits[DRSStartIndex+3] ; #6,8
            realm       = path_bits[DRSStartIndex+4] ; #7,9
            tableId     = path_bits[DRSStartIndex+5] ; #8,10
            # Fix realms to standard acronyms
            if (realm == 'ocean'):
                realm = 'ocn'
            elif (realm == 'atmos'):
                realm = 'atm'
            realisation = path_bits[DRSStartIndex+6] ; #9,11
            # Check for source path and order variable/version info
            if path_bits[DRSStartIndex+7] in list_vars:
                variable    = path_bits[DRSStartIndex+7] ; #10
                version     = path_bits[DRSStartIndex+8] ; #11
            elif path_bits[DRSStartIndex+8] in list_vars:
                version     = path_bits[DRSStartIndex+7] ; #10
                variable    = path_bits[DRSStartIndex+8] ; #11
                #if 'data' in path_bits:
                #    print path
            else:
                # Cases where variables are not in list_vars
                #print model,experiment,time_ax,realm,tableId,'10:',path_bits[pathIndex+10],'11:',path_bits[pathIndex+11]
                continue
            # Getting versioning/latest info
            testfile = os.listdir(path)[0]
            # Test for zero-size file before trying to open
            fileinfo = os.stat(os.path.join(path,testfile))
            checksize = fileinfo.st_size
            if checksize == 0:
                continue ; #print "".join(['Zero-sized file: ',path])
            # Read access check
            if os.access(os.path.join(path,testfile),os.R_OK) != True:
                continue ; #print "".join(['No read permissions: ',path])
            # Netcdf metadata scour
            #f_h = cdm.open(os.path.join(path,testfile))
            tracking_id     = '' ; #tracking_id     = f_h.tracking_id
            creation_date   = '' ; #creation_date   = f_h.creation_date
            #f_h.close()
            if testLatest(tracking_id,creation_date):
                lateststr = 'latestX' ; #lateststr = 'latest1' ; # Latest
            else:
                lateststr = 'latest0' ; # Not latest
        except Exception,err:
            # Case HadGEM2-AO - attempt to recover data
            if 'HadGEM2-AO' in model and experiment in ['historical','rcp26','rcp45','rcp60','rcp85']:
                variable    = path_bits[pathIndex+8]
                if realm in 'atm':
                    tableId = 'Amon'
                elif realm in 'ocn':
                    tableId = 'Omon'
                elif realm in 'land':
                    tableId = 'Lmon'
                elif realm in 'seaIce':
                    tableId = 'OImon'
                # Getting versioning/latest info
                testfile = os.listdir(path)[0]
                # Test for zero-size file before trying to open
                fileinfo = os.stat(os.path.join(path,testfile))
                version     = datetime.datetime.fromtimestamp(fileinfo.st_ctime).strftime('%Y%m%d')
            # Case BESM-OA2-3 - skip as only decadal data
            elif 'BESM-OA2-3' in model and 'decadal' in experiment:
                continue
            else:
                print 'pathToFile - Exception:',err,path
                continue
        # Test for list entry and trim experiments and variables to manageable list
        if (experiment in experiments) and (time_ax in temporal) and (variable in list_vars):
            data_outfiles.insert(i2,".".join(['cmip5',model,experiment,realisation,time_ax,realm,tableId,variable,"".join(['ver-',version]),lateststr,'xml']))
            data_outfiles_paths.insert(i2,path)
            i2 = i2 + 1

    # Create timestamp as function completes
    time_since_start = time.time() - start_time

    #$#return(data_outfiles,data_outfiles_paths,time_since_start,i1,i2,len_vars) ; # Non-parallel version of code for testing
    queue1.put_nowait([data_outfiles,data_outfiles_paths,time_since_start,i1,i2,len_vars]) ; # Queue
    return

#%%
def testLatest(tracking_id,creation_date):
    # There is a need to map models (rather than institutes) to index nodes as NSF-DOE-NCAR has multiple index nodes according to Karl T
    # User cmip5_controlled_vocab.txt file: http://esg-pcmdi.llnl.gov/internal/esg-data-node-documentation/cmip5_controlled_vocab.txt
    # This maps institute_id => (data_node, index_node)
    # where data_node is the originator of the data, and index_node is where they publish to.
    instituteDnodeMap = {
        'BCC':('bcccsm.cma.gov.cn', 'pcmdi9.llnl.gov'),
        'BNU':('esg.bnu.edu.cn', 'pcmdi9.llnl.gov'),
        'CCCMA':('dapp2p.cccma.ec.gc.ca', 'pcmdi9.llnl.gov'),
        'CCCma':('dapp2p.cccma.ec.gc.ca', 'pcmdi9.llnl.gov'),
        'CMCC':('adm07.cmcc.it', 'adm07.cmcc.it'),
        'CNRM-CERFACS':('esg.cnrm-game-meteo.fr', 'esgf-node.ipsl.fr'),
        'COLA-CFS':('esgdata1.nccs.nasa.gov', 'esgf.nccs.nasa.gov'),
        'CSIRO-BOM':('esgnode2.nci.org.au', 'esg2.nci.org.au'),
        'CSIRO-QCCCE':('esgnode2.nci.org.au', 'esg2.nci.org.au'),
        'FIO':('cmip5.fio.org.cn', 'pcmdi9.llnl.gov'),
        'ICHEC':('esg2.e-inis.ie', 'esgf-index1.ceda.ac.uk'),
        'INM':('pcmdi9.llnl.gov', 'pcmdi9.llnl.gov'),
        'IPSL':('vesg.ipsl.fr', 'esgf-node.ipsl.fr'),
        'LASG-CESS':('esg.lasg.ac.cn', 'pcmdi9.llnl.gov'),
        'LASG-IAP':('esg.lasg.ac.cn', 'pcmdi9.llnl.gov'),
        'LASF-CESS':('esg.lasg.ac.cn', 'pcmdi9.llnl.gov'),
        'MIROC':('dias-esg-nd.tkl.iis.u-tokyo.ac.jp', 'pcmdi9.llnl.gov'),
        'MOHC':('cmip-dn1.badc.rl.ac.uk', 'esgf-index1.ceda.ac.uk'),
        'MPI-M':('bmbf-ipcc-ar5.dkrz.de', 'esgf-data.dkrz.de'),
        'MRI':('dias-esg-nd.tkl.iis.u-tokyo.ac.jp', 'pcmdi9.llnl.gov'),
        'NASA GISS':('esgdata1.nccs.nasa.gov', 'esgf.nccs.nasa.gov'),
        'NASA-GISS':('esgdata1.nccs.nasa.gov', 'esgf.nccs.nasa.gov'),
        'NASA GMAO':('esgdata1.nccs.nasa.gov', 'esgf.nccs.nasa.gov'),
        'NCAR':('tds.ucar.edu', 'esg-datanode.jpl.nasa.gov'),
        'NCC':('norstore-trd-bio1.hpc.ntnu.no', 'pcmdi9.llnl.gov'),
        'NICAM':('dias-esg-nd.tkl.iis.u-tokyo.ac.jp', 'pcmdi9.llnl.gov'),
        'NIMR-KMA':('pcmdi9.llnl.gov', 'pcmdi9.llnl.gov'),
        'NOAA GFDL':('esgdata.gfdl.noaa.gov', 'pcmdi9.llnl.gov'),
        'NOAA-GFDL':('esgdata.gfdl.noaa.gov', 'pcmdi9.llnl.gov'),
        'NSF-DOE-NCAR':('tds.ucar.edu', 'esg-datanode.jpl.nasa.gov'),
    }
    masterDnodes = {
        'adm07.cmcc.it',
        'esg-datanode.jpl.nasa.gov',
        'esg2.nci.org.au',
        'esgf-data.dkrz.de',
        'esgf-index1.ceda.ac.uk',
        'esgf-node.ipsl.fr',
        'esgf.nccs.nasa.gov',
        'pcmdi9.llnl.gov',
    }
    modelInstituteMap = {
        'access1-0','CSIRO-BOM',
        'access1-3','CSIRO-BOM',
        'bcc-csm1-1','BCC',
        'noresm-l','NCC',
    }
    #cmd = ''.join(['/work/durack1/Shared/cmip5/esgquery_index.py --type f -t tracking_id:',tracking_id,' -q latest=true --fields latest'])
    # try esgquery_index --type f -t tracking_id='tracking_id',latest=true,index_node='index_node' ; # Uncertain if index_node is available
    #tmp = os.popen(cmd).readlines()
    #time.sleep(1) ; # Pause
    #latestbool = False
    #for t in tmp:
    #    if find(t,'latest'):
    #        latestbool = True
    latestbool = True

    return latestbool



#%%
##### Set batch mode processing, console printing on/off and multiprocess loading #####
batch       = True ; # True = on, False = off
batch_print = False ; # Write log messages to console - suppress from cron daemon ; True = on, False = off
threadCount = 40 ; # ~36hrs xml creation solo ; 50hrs xml creation crunchy & oceanonly in parallel
##### Set batch mode processing, console printing on/off and multiprocess loading #####

# Set time counter and grab timestamp
start_time  = time.time() ; # Set time counter
time_format = datetime.datetime.now().strftime('%y%m%d_%H%M%S')

# Set conditional whether files are created or just numbers are calculated
if batch:
    parser = argparse.ArgumentParser()
    parser.add_argument('makefiles',metavar='str',type=str,help='\'makefiles\' as a command line argument will write xml files, \'report\' will produce a logfile with path information')
    args = parser.parse_args()
    if (args.makefiles == 'makefiles'):
       make_xml = 1 ; # 1 = make files
       print time_format
       print "** Write mode - new *.xml files will be written **"
    elif (args.makefiles == 'report'):
       make_xml = 0 ; # 0 = don't make files, just report
       print time_format
       print "** Report mode - no *.xml files will be written **"
else:
    make_xml = 1
    print time_format
    print "** Non-batch mode - new *.xml files will be written **"

# Set directories
host_name = gethostname()
if host_name in {'crunchy.llnl.gov','oceanonly.llnl.gov'}:
    trim_host = replace(host_name,'.llnl.gov','')
    if batch:
        host_path = '/work/cmip5/' ; # BATCH MODE - oceanonly 130605
        log_path = os.path.join(host_path,'_logs')
    else:
        host_path = '/work/durack1/Shared/cmip5/tmp/' ; # WORK_MODE_TEST - oceanonly 130605 #TEST#
        log_path = host_path
    cdat_path = '/usr/local/uvcdat/latest/bin/'
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

# Change directory to host
os.chdir(host_path)

# Set logfile attributes
time_format = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
pypid = str(os.getpid()) ; # Returns calling python instance, so master also see os.getppid() - Parent
logfile = os.path.join(log_path,"".join([time_format,'_report_cmip5_xml-',trim_host,'-threads',str(threadCount),'-PID',pypid,'.log']))
# Logging the explicit searched data path
os.chdir('/cmip5_css02')
cmd = 'df -h | grep cmip5'
#sysCallTimeout(cmd,5) ; # Test for network connectivity and fail if /cmip5_css02 not alive
p = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)
out,err = p.communicate()
writeToLog(logfile,"".join(['TIME: ',time_format]))
writeToLog(logfile,"".join(['MASTER PID: ',pypid]))
print "".join(['master pid',pypid]) ; # Write master PID to sendmail/stdout
writeToLog(logfile,"".join(['HOSTNAME: ',host_name]))
writeToLog(logfile,"".join(['FUNCTION: ','scandir.walk']))
writeToLog(logfile,"".join(['SOURCEFILES:\n',out]))
del(trim_host,time_format,cmd,p,out,err)
gc.collect()

# Generate queue objects
manager0 = Manager()
## GDO2 data sources - Mine for paths and files
# gdo2_data
queue1 = manager0.Queue(maxsize=0)
p1 = Process(target=pathToFile,args=('/cmip5_gdo2/data/cmip5/',start_time,queue1))
p1.start() ; print "".join(['p1 pid: ',str(p1.ident)])
# gdo2_scratch
queue2 = manager0.Queue(maxsize=0)
p2 = Process(target=pathToFile,args=('/cmip5_gdo2/scratch/cmip5/',start_time,queue2))
p2.start() ; print "".join(['p2 pid: ',str(p2.ident)])
## CSS data sources - Mine for paths and files
# css02_data
queue3 = manager0.Queue(maxsize=0)
p3 = Process(target=pathToFile,args=('/cmip5_css02/data/cmip5/',start_time,queue3))
p3.start() ; print "".join(['p3 pid: ',str(p3.ident)])
# css02_scratch
queue4 = manager0.Queue(maxsize=0)
p4 = Process(target=pathToFile,args=('/cmip5_css02/scratch/cmip5/',start_time,queue4))
p4.start() ; print "".join(['p4 pid: ',str(p4.ident)])
# css01_data
queue5 = manager0.Queue(maxsize=0)
p5 = Process(target=pathToFile,args=('/cmip5_css01/data/cmip5/',start_time,queue5))
p5.start() ; print "".join(['p5 pid: ',str(p5.ident)])
# css02_scratch
queue6 = manager0.Queue(maxsize=0)
p6 = Process(target=pathToFile,args=('/cmip5_css01/scratch/cmip5/',start_time,queue6))
p6.start() ; print "".join(['p6 pid: ',str(p6.ident)])
# css02_cmip5
queue7 = manager0.Queue(maxsize=0)
p7 = Process(target=pathToFile,args=('/cmip5_css02/cmip5/data/cmip5/',start_time,queue7))
p7.start() ; print "".join(['p7 pid: ',str(p7.ident)])
# css02_\_gc
queue8 = manager0.Queue(maxsize=0)
p8 = Process(target=pathToFile,args=('/cmip5_css02/scratch/_gc/',start_time,queue8))
p8.start() ; print "".join(['p8 pid: ',str(p8.ident)])
# css01_\_gc
queue9 = manager0.Queue(maxsize=0)
p9 = Process(target=pathToFile,args=('/cmip5_css01/scratch/_gc/',start_time,queue9))
p9.start() ; print "".join(['p9 pid: ',str(p9.ident)])

# Consider parallelising css02_scratch in particular - queue object doesn't play with p.map
'''
http://stackoverflow.com/questions/7588620/os-walk-multiple-directories-at-once
http://stackoverflow.com/questions/141291/how-to-list-only-yop-level-directories-in-python
from multiprocessing import Pool
folder = '/cmip5_css02/scratch/cmip5/output1/'
paths = [os.path.join(folder,path) for path in os.listdir(folder) if os.path.isdir(os.path.join(folder,path))]
p = Pool(len(paths))
[data_outfiles,data_outfiles_paths,time_since_start,i1,i2,len_vars] = p.map(pathToFile,paths)

130227 - Charles, create a list of queues and a list of processes through which to iterate and build the full
         outfiles and outfile_paths variables - then pass this as many paths as possible

def job(path,id):
    start_time  = time.time() ; # Set time counter
    queue1      = manager0.Queue(maxsize=0)
    p1          = Process(target=pathToFile,args=(path,start_time,queue1))
    p1.start()
    print "".join(['p1 pid: ',str(p1.ident)])
    return p1,queue1

queues=[] ; processes=[]
for path,id in zip(paths,ids):
    p,q = job(path,id)
    processes.append(p)
    queues.append(q)

for i,p in enumerate(processes):
    q   = queues[i]
    id  = ids[i]
    p.join()
    [css02_scratch_outfiles,css02_scratch_outfiles_paths,time_since_start,i1,i2,len_vars] = q.get_nowait()
    logWrite(logfile,time_since_start,id,i1,css02_scratch_outfiles,len_vars)
    outfiles.extend()
    outfiles_paths.extend()
'''

# Write to logfile
p2.join()
[gdo2_scratch_outfiles,gdo2_scratch_outfiles_paths,time_since_start,i1,i2,len_vars] = queue2.get_nowait()
logWrite(logfile,time_since_start,'gdo2_scratch',i1,gdo2_scratch_outfiles,len_vars)
p1.join()
[gdo2_data_outfiles,gdo2_data_outfiles_paths,time_since_start,i1,i2,len_vars] = queue1.get_nowait()
logWrite(logfile,time_since_start,'gdo2_data',i1,gdo2_data_outfiles,len_vars)
p6.join()
[css01_scratch_outfiles,css01_scratch_outfiles_paths,time_since_start,i1,i2,len_vars] = queue6.get_nowait()
logWrite(logfile,time_since_start,'css01_scratch',i1,css01_scratch_outfiles,len_vars)
p5.join()
[css01_data_outfiles,css01_data_outfiles_paths,time_since_start,i1,i2,len_vars] = queue5.get_nowait()
logWrite(logfile,time_since_start,'css01_data',i1,css01_data_outfiles,len_vars)
p4.join()
[css02_scratch_outfiles,css02_scratch_outfiles_paths,time_since_start,i1,i2,len_vars] = queue4.get_nowait()
logWrite(logfile,time_since_start,'css02_scratch',i1,css02_scratch_outfiles,len_vars)
p3.join()
[css02_data_outfiles,css02_data_outfiles_paths,time_since_start,i1,i2,len_vars] = queue3.get_nowait()
logWrite(logfile,time_since_start,'css02_data',i1,css02_data_outfiles,len_vars)
p7.join()
[css02_cm5_outfiles,css02_cm5_outfiles_paths,time_since_start,i1,i2,len_vars] = queue7.get_nowait()
logWrite(logfile,time_since_start,'css02_cmip5',i1,css02_cm5_outfiles,len_vars)
p8.join()
[css02_gc_outfiles,css02_gc_outfiles_paths,time_since_start,i1,i2,len_vars] = queue8.get_nowait()
logWrite(logfile,time_since_start,'css02_gc',i1,css02_gc_outfiles,len_vars)
p9.join()
[css01_gc_outfiles,css01_gc_outfiles_paths,time_since_start,i1,i2,len_vars] = queue9.get_nowait()
logWrite(logfile,time_since_start,'css01_gc',i1,css01_gc_outfiles,len_vars)

# Generate master lists from sublists
outfiles_paths = list(gdo2_data_outfiles_paths)
outfiles_paths.extend(gdo2_scratch_outfiles_paths) ; # Add gdo2_scratch to master
outfiles_paths.extend(css01_data_outfiles_paths) ; # Add css01_data to master
outfiles_paths.extend(css01_scratch_outfiles_paths) ; # Add css01_scratch to master
outfiles_paths.extend(css02_data_outfiles_paths) ; # Add css02_data to master
outfiles_paths.extend(css02_scratch_outfiles_paths) ; # Add css02_scratch to master
outfiles_paths.extend(css02_cm5_outfiles_paths) ; # Add css02_cmip5 to master
outfiles_paths.extend(css02_gc_outfiles_paths) ; # Add css02_gc to master
outfiles_paths.extend(css01_gc_outfiles_paths) ; # Add css01_gc to master

outfiles = list(gdo2_data_outfiles)
outfiles.extend(gdo2_scratch_outfiles) ; # Add gdo2_scratch to master
outfiles.extend(css01_data_outfiles) ; # Add css01_data to master
outfiles.extend(css01_scratch_outfiles) ; # Add css01_scratch to master
outfiles.extend(css02_data_outfiles) ; # Add css02_data to master
outfiles.extend(css02_scratch_outfiles) ; # Add css02_scratch to master
outfiles.extend(css02_cm5_outfiles) ; # Add css02_cmip5 to master
outfiles.extend(css02_gc_outfiles) ; # Add css02_gc to master
outfiles.extend(css01_gc_outfiles) ; # Add css01_gc to master

# Sort lists by outfiles
outfilesAndPaths = zip(outfiles,outfiles_paths)
outfilesAndPaths.sort() ; # sort by str value forgetting case - key=str.lower; requires str object
del(outfiles,outfiles_paths)
gc.collect()
# Before extracting check for valid sizes
if len(outfilesAndPaths):
    outfiles,outfiles_paths = zip(*outfilesAndPaths)
else:
    print '** No valid files found, exiting.. **'
    writeToLog(logfile,"** report_cmip5_xml.py run in report mode **")
    sys.exit()

# Truncate duplicates from lists
outfiles_new = []; outfiles_paths_new = []; counter = 0
for count,testfile in enumerate(outfiles):
    if count < len(outfiles)-1:
        if counter == 0:
            # Deal with first file instance
            outfiles_new.append(outfiles[counter])
            outfiles_paths_new.append(outfiles_paths[counter])
        # Create first file to check
        file1 = outfiles_new[counter]
        # Create second file to check
        file2 = outfiles[count+1]
        if file1 == file2:
            continue
        else:
            outfiles_new.append(file2)
            outfiles_paths_new.append(outfiles_paths[count+1])
            counter = counter+1

# For debugging save to file
time_format = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
outFile = os.path.join(log_path,"".join([time_format,'_report_outfiles.cpklz']))
f = gzip.open(outFile,'wb')
cPickle.dump([outfiles,outfiles_new,outfiles_paths,outfiles_paths_new],f)
f.close()
del(outFile,f,time_format,i1,i2,len_vars,time_since_start) ; gc.collect()

# Reallocate variables
outfiles = outfiles_new
outfiles_paths = outfiles_paths_new
del(count,counter,testfile,outfiles_new,outfiles_paths_new)


'''
# Debug code for duplicate removal/checking
import os,pickle
picklefile = '/work/durack1/Shared/cmip5/tmp/130228_024214_list_outfiles.pickle'
f = open(picklefile,'r')
outfiles,outfiles_new,outfiles_paths,outfiles_paths_new = pickle.load(f)
f.close()

for count,path in enumerate(outfiles_paths_new):
    if any( (bad in path) for bad in badstuff):
        print count,path

130225 1344: Check for remaining duplicates
counter = 1
for count,testfile in enumerate(outfiles):
    if count < len(outfiles):
        file1 = testfile
        file2 = outfiles[count+1]
        if file1 == file2:
            print counter,count,file1
            print counter,count,outfiles_paths[count]
            print counter,count+1,file2
            print counter,count+1,outfiles_paths[count+1]
            print '----------'
            counter = counter+1
'''

print "** report_cmip5_xml.py run in report mode **"
writeToLog(logfile,"** report_cmip5_xml.py run in report mode **")
