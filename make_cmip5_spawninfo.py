# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 13:57:02 2012

Paul J. Durack 23rd January 2012

This script interrogates *an*.nc files for all "interesting" model attributes

PJD 18 Sep 2012     - Fixed filename issue
PJD 19 Sep 2012     - Implemented fix for IPSL email address - cmip5.IPSL-CM5A-LR.piControl.r1i1p1.an.atm.hfls.ver-1.2370-2799.nc _at_ for contact
PJD 19 Sep 2012     - Removed realization info (duplicated)
PJD 19 Sep 2012     - Added first and last years
PJD 19 Sep 2012     - Updated calendar scrape from global attributes to time_axis attributes
PJD 21 Sep 2012     - Ordered entries by model (not model AND variable) - does adding another \t deal with long version strings?
PJD 26 Sep 2012     - Added 1pctCO2 and abrupt4xCO2 to experiment lists
PJD  2 Oct 2012     - Added a branch_time_validated table entry as a placeholder
PJD  2 Oct 2012     - Checking all variables within a realisation and only list dupes if they differ
PJD  8 Oct 2012     - Started removing tracking_id and creation_date to make comparisons easier - return when final
PJD  8 Oct 2012     - Corrected index lookups to '.an.' from 'an' which were tripping over on Can* models
PJD  9 Oct 2012     - Fixed issue with INMCM4 email address and trailing ",INM"
PJD  9 Oct 2012     - Added time:calendar attribute to correct for weird calendars
PJD  9 Oct 2012     - Corrected branch_time to reflect component time references to piControl time_units
                    Component-time conversions will highlight issues with cases like 20060101, 200501 as branch times not indexes
PJD 10 Oct 2012     - Added contact field in log file
PJD 10 Oct 2012     - Added pickle load (Pete G's dictionary stuff)
PJD 10 Oct 2012     - Reordered logic considerably in preparation for using validated values
PJD 24 Oct 2012     - Converted yearlast/first to ints so max/min work
PJD 24 Oct 2012     - Alot of fiddling to get min/max years to correctly report, comment cleanup
PJD 24 Oct 2012     - Added test to ensure that start-end years of piControl are complete, as below:
                    piControl/atm/an/hfls/cmip5.IPSL-CM5A-LR.piControl.r1i1p1.an.atm.hfls.ver-1.2370-2799.nc
                    piControl/atm/an/hfss/cmip5.IPSL-CM5A-LR.piControl.r1i1p1.an.atm.hfss.ver-1.1800-2799.nc
                    Issue is that once new model is found, log is written, need to wait for change, then write previous
PJD 24 Oct 2012     - Dealt with issue of header being written before data finalised (historical inmcm4 falls into rcp26)
PJD 29 Oct 2012     - Removed contact from logs
PJD 29 Oct 2012     - branch_time_comp1,comp2 and valid info written to logfile
PJD 30 Oct 2012     - Following latest spawn info from Pete, updated fixes array
PJD 17 Dec 2012     - Added Jonathan Gregory's table info into analysis
PJD 18 Dec 2012     - Fixed issue with string branch_time for GFDL-CM3
PJD 19 Dec 2012     - [durack1@crunchy historical]$ ls */an/*/cmip5.CCSM4*r6i1p1*.nc | xargs -n 1 ncdump -h | grep branch_time
PJD 19 Dec 2012     - Replaced fixes list with valid list and updated all up-to-date entries
PJD  3 Jan 2013     - Updated to latest file from Jonathan Gregory 130102
PJD  3 Jan 2013     - Updated Pete's branch dictionary path
PJD  3 Jan 2013     - Updated to use OrderedDict rather than standard dictionary variable
PJD  3 Jan 2013     - Corrected GFDL-CM3 entries, tabulated values were incorrect
PJD  3 Jan 2013     - Added mod importing from numpy
PJD 11 Jan 2013     - Updated ancestry file to latest from Jonathan
PJD 11 Jan 2013     - OrderedDict (from collections) now used for storing pickled model info
PJD 16 Jan 2013     - Updated branch_time_paul to branch_time_valid
PJD 22 Jan 2013     - Updated ancestry file to latest from Jonathan
PJD 22 Jan 2013     - Updated all valid times from latest Gleckler/Gregory entries
PJD 29 Jan 2013     - List multiple entries for problematic branch_times across multiple variables:
                    [durack1@crunchy historical]$ ls */an/*/cmip5.CCSM4*r2i1p1*.nc | xargs -n 1 ncdump -h | grep -i -e netcdf -e branch_time -e creation_date -e tracking_id
PJD 31 Jan 2013     - Updated NCAR branch_times as prompted by email correspondence with Gary Strand (cesm_data@) and website: www.cesm.ucar.edu/CMIP5/errata/branch_times.html
PJD 31 Jan 2013     - It appears inconsistent branch_times in FGOALS-s2 and GISS-E2-R are due to float vs string types,
                      the numbers are identical so branch_time conversion updated
PJD 11 Feb 2013     - Filled in more unvalidated branch_times - these have no valid_method entry - linked to blue entries in 130131_162038_make_cmip5_spawninfo-crunchy.ods
PJD  3 May 2013     - Added GISS-E2-* branch times for 1pctCO2 runs (Mark Zelinka)
PJD  3 May 2013     - Added bcc-csm1-1* branch times for 1pctCO2 runs (Mark Zelinka)
PJD  9 May 2013     - Added oceanonly to known host list
PJD  9 May 2013     - Added FGOALS-s2 branch times for 1pctCO2 and abrupt4xCO2 runs (Mark Zelinka)
PJD 10 Jun 2013     - Added ACCESS1-3.historical.r2/r3
PJD 12 Jun 2013     - Added NorESM1-ME.historical.r1
PJD 12 Jun 2013     - Added MPI-ESM-MR.historical.r2/3
PJD 12 Jun 2013     - TODO: Hunt down issue with incorrect branch_time reported for bcc-csm1-1-m.r1i1p1.1pctCO2 - reported 160-1-1 should be 240-1-1
PJD 12 Jun 2013     - TODO: piControl_info isn't saving correct start years IPSL-CM5A-LR.historical.r1i1p1 reports 2370 not 1850
PJD 12 Jun 2013     - TODO: lost branch_time difference reporting (121009_* file) smaller when compared to 121024_* although
                    All problem files from 121009_* are noted, but only one entry (rather than all differing) are logged
PJD 12 Jun 2013     - TODO: Add thetao/so variables (on which drift calcs are based) to interrogation, so as to ascertain
                    if the thetao/so variables locally available have the complete (or subset) temporal coverage
PJD 12 Jun 2013     - TODO: include tracking_id and creation_date in logfile/dictionary
PJD 12 Jun 2013     - TODO: Write out all diagnostics to a dictionary and pickle dump file

@author: durack1
"""

if 'e' in locals():
    del(e,pi,sctypeNA,typeNA) ; # Purge spyder variables

import datetime,gc,os,re,pickle,sys
import cdms2 as cdms
from collections import OrderedDict
from numpy import mod
from numpy import float32
from socket import gethostname
from string import replace

# Set directories
host_name = gethostname()
if host_name in {'crunchy.llnl.gov','oceanonly.llnl.gov'}:
    trim_host = replace(host_name,'.llnl.gov','')
    host_path = '/work/durack1/Shared/cmip5/' ; # an mean files
    cdat_path = '/usr/local/uvcdat/latest/bin/'
else:
    print '** HOST UNKNOWN, aborting.. **'
    sys.exit()

# Change directory to host
os.chdir(host_path)

# Create directory list - piControl first then order by model
data_paths = []
for experiment in ['piControl','historical','rcp26','rcp45','rcp60','rcp85','1pctCO2','abrupt4xCO2']:
    data_files1 = [] ; data_paths1 = []
    for (path, dirs, files) in os.walk(os.path.join(host_path,experiment),'false'):
        if ('/ncs/' in path) or ('/an_clims/' in path) or ('/an_trends/' in path):
            continue
        elif files != [] and dirs == []:
            # Append to list variable
            for file in files:
                data_files1 += [file]
                data_paths1 += [os.path.join(path,file)]
    del(path,dirs,files,file)
    # Sort paths and files by files variable
    filesAndPaths = zip(data_files1,data_paths1)
    filesAndPaths.sort()
    del(data_files1,data_paths1)
    data_files1,data_paths1 = zip(*filesAndPaths)
    # Write paths to persistent master variable
    data_paths.extend(data_paths1)
    del(data_files1,data_paths1,filesAndPaths,experiment)


# Get data from Jonathan Gregory
with open('/work/cmip5/130122_JonathanGregory_cmip5_ancestry.txt','r') as f:
    data = f.readlines()

# Split line info and copy year for '=' entries
data2 = [] ; header = True
for line in data:
    if header:
        data2 += [['model.exp.rip','branch_time_yr','parent_exp.rip']]
        header = False
    line = line.strip().split()
    if '=' in line[6]:
        line[6] = line[3]
    modelexprip = ".".join([line[0],line[1],line[2]])
    parentexprip = ".".join([line[4],line[5]])
    branch_time_yr = line[6]
    # Only add data that's had a visual inspection
    if len(line) == 8 and 'OK' in line[7]:
        data2 += [[modelexprip,branch_time_yr,parentexprip]]

gregory = data2
del(data,data2,header,line,modelexprip,parentexprip,branch_time_yr)


# Create exclusion list ; Provides model.experiment.rip and branch_time_comp, parent_experiment_id, parent_experiment_rip
# Consider creating a dictionary with keys: model,experiment,realisation: values etc
valid = [
        ['model.experiment.rip',                'branch_time_comp','branch_time_relative','branch_time_gregory','parent_exp.rip','valid_method'],
        ['ACCESS1-0.historical.r1i1p1',         '0300-1-1 0:0:0.0',109207,300,'piControl.r1i1p1','Gregory'],
        ['ACCESS1-3.historical.r1i1p1',         '0250-1-1 0:0:0.0',90945,250,'piControl.r1i1p1','Gleckler'],
        ['ACCESS1-3.historical.r2i1p1',         '0340-1-1 0:0:0.0',123816,340,'piControl.r1i1p1',''],
        ['ACCESS1-3.historical.r3i1p1',         '0550-1-1 0:0:0.0',200518,550,'piControl.r1i1p1',''],
        ['BNU-ESM.historical.r1i1p1',           '1850-1-1 0:0:0.0','',1850,'piControl.r1i1p1','Gleckler'],
        ['CCSM4.historical.r1i1p1',             '0937-1-1 0:0:0.0',342005,937,'piControl.r1i1p1','Gregory; www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CCSM4.historical.r2i1p1',             '1031-1-1 0:0:0.0',376315,'','piControl.r1i1p1','Gleckler; www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CCSM4.historical.r3i1p1',             '0863-1-1 0:0:0.0',314995,'','piControl.r1i1p1','Gleckler; www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CCSM4.historical.r4i1p1',             '0893-1-1 0:0:0.0',325945,'','piControl.r1i1p1','Gleckler; www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CCSM4.historical.r5i1p1',             '0983-1-1 0:0:0.0',358795,'','piControl.r1i1p1','Gleckler; www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CCSM4.historical.r6i1p1',             '0953-1-1 0:0:0.0',347845,'','piControl.r1i1p1','Gleckler; www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-BGC.historical.r1i1p1',         '0151-1-1 0:0:0.0',55115,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-CAM5.historical.r1i1p1',        '0225-1-1 0:0:0.0',82125,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-CAM5.historical.r2i1p1',        '0232-1-1 0:0:0.0',84680,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-CAM5.historical.r3i1p1',        '0320-1-1 0:0:0.0',116800,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-CAM5-1-FV2.historical.r1i1p1',  '0102-1-1 0:0:0.0','','','piControl.r1i1p1','Gary Strand (cesm_data@); PNNL data so limited info available'],
        ['CESM1-CAM5-1-FV2.historical.r2i1p1',  '0070-1-1 0:0:0.0','','','piControl.r1i1p1','Gary Strand (cesm_data@); PNNL data so limited info available'],
        ['CESM1-CAM5-1-FV2.historical.r3i1p1',  '0051-1-1 0:0:0.0','','','piControl.r1i1p1','Gary Strand (cesm_data@); PNNL data so limited info available'],
        ['CESM1-CAM5-1-FV2.historical.r4i1p1',  '0052-1-1 0:0:0.0','','','piControl.r1i1p1','Gary Strand (cesm_data@); PNNL data so limited info available'],
        ['CESM1-FASTCHEM.historical.r1i1p1',    '0086-1-1 0:0:0.0',31390,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-FASTCHEM.historical.r2i1p1',    '0150-1-1 0:0:0.0',54750,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-FASTCHEM.historical.r3i1p1',    '0250-1-1 0:0:0.0',91250,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-WACCM.historical.r1i1p1',       '0156-1-1 0:0:0.0',56940,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-WACCM.historical.r2i1p1',       '1955-1-1 0:0:0.0',713575,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-WACCM.historical.r3i1p1',       '1955-1-1 0:0:0.0',713575,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CESM1-WACCM.historical.r4i1p1',       '1955-1-1 0:0:0.0',713575,'','piControl.r1i1p1','Gary Strand (cesm_data@); www.cesm.ucar.edu/CMIP5/errata/branch_times.html'],
        ['CMCC-CESM.historical.r1i1p1',         '4324-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler - pathology in 2nd half of simulation'],
        ['CMCC-CM.historical.r1i1p1',           '1849-12-21 0:0:0.0',109562,1849,'piControl.r1i1p1','Gleckler'],
        ['CMCC-CMS.historical.r1i1p1',          '3684-1-1 0:0:0.0','',3684,'piControl.r1i1p1','Gregory'],
        ['CNRM-CM5.historical.r1i1p1',          '2250-1-1 0:0:0.0',146097,2250,'piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r2i1p1',          '1950-1-1 0:0:0.0',36524,'','piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r3i1p1',          '2000-1-2 0:0:0.0',54787,'','piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r4i1p1',          '2050-1-1 0:0:0.0',73049,'','piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r5i1p1',          '2100-1-1 0:0:0.0',91311,'','piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r6i1p1',          '2150-1-1 0:0:0.0',109573,'','piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r7i1p1',          '2200-1-1 0:0:0.0',127835,'','piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r8i1p1',          '1850-1-1 0:0:0.0',0,'','piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r9i1p1',          '2300-1-2 0:0:0.0',164359,'','piControl.r1i1p1','Gleckler'],
        ['CNRM-CM5.historical.r10i1p1',         '2350-1-1 0:0:0.0',182621,'','piControl.r1i1p1','Gleckler'],
        ['CSIRO-Mk3-6-0.historical.r1i1p1',     '0081-1-1 0:0:0.0',29200,81,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r2i1p1',     '0092-1-1 0:0:0.0',33215,92,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r3i1p1',     '0104-1-1 0:0:0.0',37595,104,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r4i1p1',     '0117-1-1 0:0:0.0',42340,117,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r5i1p1',     '0127-1-1 0:0:0.0',45990,127,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r6i1p1',     '0138-1-1 0:0:0.0',50005,138,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r7i1p1',     '0153-1-1 0:0:0.0',55480,153,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r8i1p1',     '0169-1-1 0:0:0.0',61320,169,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r9i1p1',     '0186-1-1 0:0:0.0',67525,186,'piControl.r1i1p1','Gregory'],
        ['CSIRO-Mk3-6-0.historical.r10i1p1',    '0200-1-1 0:0:0.0',72635,200,'piControl.r1i1p1','Gregory'],
        ['CanESM2.historical.r1i1p1',           '2321-1-1 0:0:0.0',171915,2321,'piControl.r1i1p1','Gleckler'],
        ['CanESM2.historical.r2i1p1',           '2271-1-1 0:0:0.0',153665,2271,'piControl.r1i1p1','Gleckler'],
        ['CanESM2.historical.r3i1p1',           '2221-1-1 0:0:0.0',135415,2221,'piControl.r1i1p1','Gleckler'],
        ['CanESM2.historical.r4i1p1',           '2171-1-1 0:0:0.0',117165,2171,'piControl.r1i1p1','Gleckler'],
        ['CanESM2.historical.r5i1p1',           '2121-1-1 0:0:0.0',98915,2121,'piControl.r1i1p1','Gleckler'],
        ['EC-EARTH.historical.r1i1p1',          '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r2i1p1',          '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r3i1p1',          '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r5i1p1',          '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r6i1p1',          '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r7i1p1',          '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r8i1p1',          '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r9i1p1',          '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r10i1p1',         '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r11i1p1',         '2250-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r12i1p1',         '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r13i1p1',         '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['EC-EARTH.historical.r14i1p1',         '2125-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['FGOALS-g2.historical.r2i1p1',         '0500-1-1 0:0:0.0',182135,500,'piControl.r1i1p1','Gregory'],
        ['FGOALS-g2.historical.r3i1p1',         '0520-1-1 0:0:0.0',189435,520,'piControl.r1i1p1','Gregory'],
        ['FGOALS-g2.historical.r4i1p1',         '0550-1-1 0:0:0.0',200385,500,'piControl.r1i1p1','Gregory'],
        ['FGOALS-g2.historical.r5i1p1',         '0500-1-1 0:0:0.0',182135,500,'piControl.r1i1p1','Gregory'],
        ['FGOALS-s2.historical.r1i1p1',         '1853-7-25 0:0:0.0',1300,1853,'piControl.r1i1p1','Gleckler'],
        ['FGOALS-s2.historical.r2i1p1',         '1853-8-4 0:0:0.0',1310,'','piControl.r1i1p1','Gleckler'],
        ['FGOALS-s2.historical.r3i1p1',         '1853-8-14 0:0:0.0',1320,'','piControl.r1i1p1','Gleckler'],
        ['FIO-ESM.historical.r1i1p1',           '0701-1-1 0:0:0.0','','','piControl.r1i1p1',''],        
        ['FIO-ESM.historical.r2i1p1',           '0651-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['FIO-ESM.historical.r3i1p1',           '0401-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GFDL-CM3.historical.r1i1p1',          '0001-1-1 0:0:0.0',0,'','piControl.r1i1p1','Gleckler'],
        ['GFDL-CM3.historical.r2i1p1',          '0051-1-1 0:0:0.0',18250,'','piControl.r1i1p1','Gleckler'],
        ['GFDL-CM3.historical.r3i1p1',          '0101-1-1 0:0:0.0',36500,'','piControl.r1i1p1','Gleckler'],
        ['GFDL-CM3.historical.r4i1p1',          '0151-1-1 0:0:0.0',54750,'','piControl.r1i1p1','Gleckler'],
        ['GFDL-CM3.historical.r5i1p1',          '0201-1-1 0:0:0.0',73000,'','piControl.r1i1p1','Gleckler'],
        ['GFDL-ESM2M.historical.r1i1p1',        '0162-1-1 0:0:0.0','','','historicalMisc.r1i1p1','Gregory'],
        ['GISS-E2-H-CC.historical.r1i1p1',      '2081-1-1 0:0:0.0','',2081,'piControl.r1i1p1','Gleckler'],
        ['GISS-E2-H.historical.r1i1p1',         '2410-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-H.historical.r1i1p2',         '2490-1-1 0:0:0.0','','','piControl.r1i1p2',''],
        ['GISS-E2-H.historical.r1i1p3',         '2490-1-1 0:0:0.0','','','piControl.r1i1p3',''],
        ['GISS-E2-H.historical.r2i1p1',         '2430-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-H.historical.r2i1p2',         '2510-1-1 0:0:0.0','','','piControl.r1i1p2',''],
        ['GISS-E2-H.historical.r2i1p3',         '2510-1-1 0:0:0.0','','','piControl.r1i1p3',''],
        ['GISS-E2-H.historical.r3i1p1',         '2450-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-H.historical.r3i1p2',         '2530-1-1 0:0:0.0','','','piControl.r1i1p2',''],
        ['GISS-E2-H.historical.r3i1p3',         '2530-1-1 0:0:0.0','','','piControl.r1i1p3',''],
        ['GISS-E2-H.historical.r4i1p1',         '2470-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-H.historical.r4i1p2',         '2550-1-1 0:0:0.0','','','piControl.r1i1p2',''],
        ['GISS-E2-H.historical.r4i1p3',         '2550-1-1 0:0:0.0','','','piControl.r1i1p3',''],
        ['GISS-E2-H.historical.r5i1p1',         '2490-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-H.historical.r5i1p2',         '2570-1-1 0:0:0.0','','','piControl.r1i1p2',''],
        ['GISS-E2-H.historical.r5i1p3',         '2570-1-1 0:0:0.0','','','piControl.r1i1p3',''],
        ['GISS-E2-R-CC.historical.r1i1p1',      '2050-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r1i1p1',         '3981-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-R.historical.r1i1p2',         '3590-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r1i1p3',         '3560-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r2i1p1',         '4001-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-R.historical.r2i1p2',         '3610-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r2i1p3',         '3580-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r3i1p1',         '4021-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-R.historical.r3i1p2',         '3630-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r3i1p3',         '3600-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r4i1p1',         '4041-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-R.historical.r4i1p2',         '3650-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r4i1p3',         '3620-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r5i1p1',         '4061-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['GISS-E2-R.historical.r5i1p2',         '3670-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r5i1p3',         '3640-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r6i1p1',         '4081-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r6i1p2',         '3690-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['GISS-E2-R.historical.r6i1p3',         '3660-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['HadGEM2-AO.historical.r1i1p1',        'BLANK','','','piControl.r1i1p1',''],
        ['HadGEM2-CC.historical.r1i1p1',        '1859-12-1 0:0:0.0',0,1859,'piControl.r1i1p1','Gleckler'],
        ['HadGEM2-CC.historical.r2i1p1',        '1959-12-21 0:0:0.0',36020,'','piControl.r1i1p1','Gleckler'],
        ['HadGEM2-CC.historical.r3i1p1',        '1959-12-11 0:0:0.0',36010,'','piControl.r1i1p1','Gleckler'],
        ['HadGEM2-ES.historical.r1i1p1',        '1859-12-1 0:0:0.0',0,1859,'piControl.r1i1p1','Gleckler'],
        ['HadGEM2-ES.historical.r2i1p1',        '1909-12-1 0:0:0.0',18000,1909,'piControl.r1i1p1','Gregory'],
        ['HadGEM2-ES.historical.r3i1p1',        '1959-12-1 0:0:0.0',36000,1859,'piControl.r1i1p1','Gleckler'],
        ['HadGEM2-ES.historical.r4i1p1',        '2009-12-1 0:0:0.0',54000,2009,'piControl.r1i1p1','Gregory'],
        ['IPSL-CM5A-LR.historical.r1i1p1',      '1850-1-1 0:0:0.0','',1850,'piControl.r1i1p1','Gregory'],
        ['IPSL-CM5A-LR.historical.r2i1p1',      '1860-1-1 0:0:0.0','',1860,'piControl.r1i1p1','Gregory'],
        ['IPSL-CM5A-LR.historical.r3i1p1',      '1870-1-1 0:0:0.0','',1870,'piControl.r1i1p1','Gregory'],
        ['IPSL-CM5A-LR.historical.r4i1p1',      '1985-1-1 0:0:0.0','',1985,'piControl.r1i1p1','Gregory'],
        ['IPSL-CM5A-LR.historical.r5i1p1',      '2000-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['IPSL-CM5A-LR.historical.r6i1p1',      '2010-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['IPSL-CM5A-MR.historical.r1i1p1',      '1850-1-1 0:0:0.0','',1850,'piControl.r1i1p1','Gregory'],
        ['IPSL-CM5A-MR.historical.r2i1p1',      '1860-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['IPSL-CM5A-MR.historical.r3i1p1',      '1870-1-1 0:0:0.0','','','piControl.r1i1p1','Gleckler'],
        ['IPSL-CM5B-LR.historical.r1i1p1',      '1850-1-1 0:0:0.0','',1850,'piControl.r1i1p1','Gleckler'],
        ['MIROC-ESM-CHEM.historical.r1i1p1',    '1850-1-1 0:0:0.0',1461,1850,'piControl.r1i1p1','Gregory'],
        ['MIROC-ESM.historical.r1i1p1',         '1880-1-1 0:0:0.0',29219,1880,'piControl.r1i1p1','Gleckler'],
        ['MIROC-ESM.historical.r2i1p1',         '1820-1-1 0:0:0.0',7304,'','piControl.r1i1p1','Gleckler'],
        ['MIROC-ESM.historical.r3i1p1',         '1850-1-1 0:0:0.0',18262,'','piControl.r1i1p1','Gleckler'],
        ['MIROC4h.historical.r1i1p1',           '0091-1-1 0:0:0.0',14600,91,'piControl.r1i1p1','Gleckler'],
        ['MIROC4h.historical.r2i1p1',           '0071-1-1 0:0:0.0',7300,71,'piControl.r1i1p1','Gleckler'],
        ['MIROC4h.historical.r3i1p1',           '0111-1-1 0:0:0.0',21900,111,'piControl.r1i1p1','Gleckler'],
        ['MIROC5.historical.r1i1p1',            '2411-1-1 0:0:0.0',150015,2411,'piControl.r1i1p1','Gregory'],
        ['MIROC5.historical.r2i1p1',            '2081-1-1 0:0:0.0',29565,2081,'piControl.r1i1p1','Gleckler'],
        ['MIROC5.historical.r3i1p1',            '2181-1-1 0:0:0.0',66065,2181,'piControl.r1i1p1','Gleckler'],
        ['MIROC5.historical.r4i1p1',            '2281-1-1 0:0:0.0',102565,'','piControl.r1i1p1','Gleckler'],
        ['MIROC5.historical.r5i1p1',            '2021-1-1 0:0:0.0',7665,'','piControl.r1i1p1','Gleckler'],
        ['MPI-ESM-LR.historical.r1i1p1',        '1880-1-1 0:0:0.0',10957,1880,'piControl.r1i1p1','Gregory'],
        ['MPI-ESM-LR.historical.r2i1p1',        '1980-1-1 0:0:0.0',47481,1980,'piControl.r1i1p1','Gregory'],
        ['MPI-ESM-LR.historical.r3i1p1',        '1921-1-1 0:0:0.0',25932,1921,'piControl.r1i1p1','Gregory'],
        ['MPI-ESM-MR.historical.r1i1p1',        '1850-1-1 0:0:0.0',0,1850,'piControl.r1i1p1','Gregory'],
        ['MPI-ESM-MR.historical.r2i1p1',        '1901-1-1 0:0:0.0',18627,1901,'piControl.r1i1p1','Gregory'],
        ['MPI-ESM-MR.historical.r3i1p1',        '1966-1-1 0:0:0.0',42368,1966,'piControl.r1i1p1','Gregory'],
        ['MPI-ESM-P.historical.r2i1p1',         '1850-1-1 0:0:0.0',0,1850,'piControl.r1i1p1','Gregory'],
        ['MRI-CGCM3.historical.r1i1p1',         '1950-1-1 0:0:0.0',36159,1950,'piControl.r1i1p1','Gregory'],
        ['MRI-CGCM3.historical.r2i1p1',         '1980-1-1 0:0:0.0',47116,1980,'piControl.r1i1p1','Gregory'],
        ['MRI-CGCM3.historical.r3i1p1',         '2010-1-1 0:0:0.0',58074,2010,'piControl.r1i1p1','Gregory'],
        ['MRI-CGCM3.historical.r4i1p2',         '1890-1-1 0:0:0.0',14245,1890,'piControl.r1i1p1','Gregory'],
        ['MRI-CGCM3.historical.r5i1p2',         '1920-1-1 0:0:0.0',25201,1920,'piControl.r1i1p1','Gregory'],
        ['NorESM1-M.historical.r1i1p1',         '0700-1-1 0:0:0.0',255135,700,'piControl.r1i1p1','Gregory'],
        ['NorESM1-M.historical.r2i1p1',         '0730-1-1 0:0:0.0',266085,730,'piControl.r1i1p1','Gregory'],
        ['NorESM1-M.historical.r3i1p1',         '0760-1-1 0:0:0.0',277035,760,'piControl.r1i1p1','Gregory'],
        ['NorESM1-ME.historical.r1i1p1',        '0901-1-1 0:0:0.0',0,'','piControl.r1i1p1',''],
        ['bcc-csm1-1-m.historical.r1i1p1',      '0344-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['bcc-csm1-1-m.historical.r2i1p1',      '0270-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['bcc-csm1-1-m.historical.r3i1p1',      '0300-1-1 0:0:0.0','','','piControl.r1i1p1',''],
        ['bcc-csm1-1.historical.r1i1p1',        '0470-1-1 0:0:0.0','',470,'piControl.r1i1p1','Gleckler'],
        ['bcc-csm1-1.historical.r2i1p1',        '0160-1-1 0:0:0.0','',160,'piControl.r1i1p1','Gregory'],
        ['bcc-csm1-1.historical.r3i1p1',        '0460-1-1 0:0:0.0','',460,'piControl.r1i1p1','Gleckler'],
        ['inmcm4.historical.r1i1p1',            '1850-1-1 0:0:0.0','',1850,'piControl.r1i1p1','Gregory'],
        ['bcc-csm1-1-m.1pctCO2.r1i1p1',         '0240-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130503'],
        ['bcc-csm1-1.1pctCO2.r1i1p1',           '0160-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130503'],
        ['FGOALS-s2.1pctCO2.r1i1p1',            '1850-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130509; baoqing@mail.iap.ac.cn'],
        ['GISS-E2-H.1pctCO2.r1i1p1',            '2410-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130506; kwok-wai.lo@nasa.gov'],
        ['GISS-E2-H.1pctCO2.r1i1p2',            '2810-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130506; kwok-wai.lo@nasa.gov'],
        ['GISS-E2-H.1pctCO2.r1i1p3',            '2810-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130506; kwok-wai.lo@nasa.gov'],
        ['GISS-E2-R.1pctCO2.r1i1p1',            '3981-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130506; kwok-wai.lo@nasa.gov'],
        ['IPSL-CM5A-LR.1pctCO2.r1i1p1',         '1850-1-1 0:0:0.0','',1850,'piControl.r1i1p1','Mark Zelinka 130507; sebastian.denvil@ipsl.jussieu.fr'],
        ['IPSL-CM5A-MR.1pctCO2.r1i1p1',         '1850-1-1 0:0:0.0','',1850,'piControl.r1i1p1','Mark Zelinka 130507; sebastian.denvil@ipsl.jussieu.fr'],
        ['IPSL-CM5B-LR.1pctCO2.r1i1p1',         '1850-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130507; sebastian.denvil@ipsl.jussieu.fr'],
        ['FGOALS-s2.abrupt4xCO2.r1i1p1',        '1850-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130509; baoqing@mail.iap.ac.cn'],
        ['GISS-E2-H.abrupt4xCO2.r1i1p2',        '2810-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130506; kwok-wai.lo@nasa.gov'],
        ['GISS-E2-H.abrupt4xCO2.r1i1p3',        '2810-1-1 0:0:0.0','','','piControl.r1i1p1','Mark Zelinka 130506; kwok-wai.lo@nasa.gov'],
]

# Update branch_historical_dict file
cmip5_branch_time_dict = OrderedDict() ; count = 0

for count,run in enumerate(valid):
    if count == 0:
        pass ; # Skip header line
    model                   = run[0].split('.')[0]
    experiment              = run[0].split('.')[1]
    realisation             = run[0].split('.')[2]
    branch_time_comp        = run[1]
    branch_time_relative    = run[2]
    branch_time_gregory     = run[3]
    parent_exp_rip          = run[4]
    valid_info              = run[5]
    # Create dictionary entries
    if model not in cmip5_branch_time_dict.keys():
        cmip5_branch_time_dict[model] = {}
    if experiment not in cmip5_branch_time_dict[model].keys():
        cmip5_branch_time_dict[model][experiment] = {}
    cmip5_branch_time_dict[model][experiment][realisation] = {'branch_time_comp':branch_time_comp,'branch_time_relative':branch_time_relative,
                                                              'branch_time_gregory':branch_time_gregory,'parent_exp_rip':parent_exp_rip,
                                                              'valid':valid_info,'tracking_id':'','creation_date':''}
    del(run,model,experiment,realisation,branch_time_comp,branch_time_relative,branch_time_gregory,parent_exp_rip,valid_info)

del(count)

# Write to pickle dictionary
f = 'cmip5_branch_time_dict.pickle'
f_h = open(f,'w')
pickle.dump(cmip5_branch_time_dict,f_h)
f_h.close()
del(f)



# Load Pete G's spawning dictionary - contains time_indx,time_rel,time_comp and keys model and realisation
spawn_dict = pickle.load(open('130509_all_mod_branch_estimates.p','rb'))


# Specify default delimiters
delim = ',\t' ; ldelim = '\',\''
# Specify default headers
header = "".join(['filename',delim,'calendar',delim,'time_units',delim,'startyr',delim,
          'endyr',delim,'branch_time',delim,'branch_time_comp',delim,'branch_time_valid',delim,
          'branch_time_gleckler',delim,'branch_time_gregory',delim,'piC_startyr',delim,'piC_endyr',delim,'parent_exp_id',delim,
          'parent_exp_rip','\n'])
''' Add tracking_id & creation_date
header = "".join(['filename',delim,'tracking_id',delim,'creation_date',delim,'calendar',delim,'time_units',delim,'startyear',delim,
          'endyear',delim,'branch_time',delim,'branch_time_comp',delim,'branch_time_validated',delim,'parent_experiment_id',delim,'parent_experiment_rip',
          delim,'contact','\n'])
'''

# Create log file
time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
logfile = os.path.join(host_path,"".join([time_format,'_make_cmip5_spawninfo-',trim_host,'.log'])) ; # BATCH MODE
logfile_handle = open(logfile,'w')
logfile_handle.write("".join(['TIME: ',time_format,'\n']))
logfile_handle.write("".join(['CONTACT: Paul J. Durack, PCMDI, LLNL\n']))
logfile_handle.write("".join(['#cmip*: denotes issue with inconsistent branch time between single realisation variables\n']))
logfile_handle.close()
del(time_now,time_format)
gc.collect()




# Set check variables
filename_trim_1 = '' ; branch_time_1 = [] ; piControl_info = []; count = 0; yearfirst_1 = ''; yearlast_1 = ''
# Interrogate files for info and write to log file
for file1 in data_paths: #[0:5200]: # 130103 9877 first rcp26 file ; 130114 9748 first rcp26 file; 130318 9749 first rcp26 file; 130318 5200 include inmcm4
    if mod(count,1) == 0:
        print "".join(['count: ',str(count)])
        #print file1
    count = count + 1
    if '.directory' in file1:
        continue
    
    # Open file
    f = cdms.open(file1)
    filename = file1.split('/')[-1]
    filename_trim = filename[6:(filename.index('.an.'))]
    #filename_trim = filename[6:(filename.index('.mo.'))] ; # SHORTTERM FIX DUE TO AN FILE INVALID NAMES
    
    # Test for model change
    if (filename_trim_1 == ''):
        writelog = False
    elif (filename_trim != filename_trim_1): # First not last
        writelog = True
    elif (count == len(data_paths)):
        writelog = True

    # Write out to logfile (before harvesting new info from files)
    if writelog:
        logfile_handle = open(logfile,'a')
        # Add tracking_id, creation_date and contact to output
        logfile_handle.write("".join([filename_pad,delim,calendar,delim,time_units,delim,str(firstyear),delim,
                                    str(lastyear),delim,branch_time,delim,branch_time_comp1,delim,branch_time_comp2,delim,
                                    branch_time_valid,delim,greg_year,delim,str(piC_startyr),delim,str(piC_endyr),delim,
                                    parent_experiment_id,delim,parent_experiment_rip,'\n']))
        writelog = False ; # Reset
        logfile_handle.close()
    
    # Write header info
    header2 = "".join(['## ',file1.split('/')[5],' ##\n'])
    if 'header1' not in locals():
        header1 = "".join(['## ',file1.split('/')[5],' ##\n'])
        logfile_handle = open(logfile,'a')
        logfile_handle.write(header1)
        logfile_handle.write(header)
        logfile_handle.close()
    elif header2 != header1:
        header1 = "".join(['## ',file1.split('/')[5],' ##\n'])
        logfile_handle = open(logfile,'a')
        logfile_handle.write(header1)
        logfile_handle.write(header)
        logfile_handle.close()
    
    # Read attributes and create variables
    #branch_time = str(f.branch_time[0])
    try:
        #branch_time = str(f.branch_time.squeeze())
        branch_time = str(int(float(f.branch_time.squeeze())))
    except:
        #branch_time = f.branch_time
        branch_time = str(int(float(f.branch_time)))
    creation_date = f.creation_date
    experiment_id = f.experiment_id ; # Also experiment variable
    #print experiment_id
    parent_experiment_id = f.parent_experiment_id ; # Also parent_experiment variable 
    realization = str(f.realization[0])
    time_units = f.getdimensionunits('time')
    tracking_id = f.tracking_id
    
    # If branch_time is same for multiple variables only list first instance
    yearfirst = int(filename.split('.')[-2].split('-')[0])
    yearlast = int(filename.split('.')[-2].split('-')[-1])
    # Test years
    # First year
    if yearfirst_1 == '':
        firstyear = yearfirst
    elif (filename_trim == filename_trim_1) and (yearfirst != yearfirst_1):
        firstyear = min(yearfirst,yearfirst_1)
    # Last year
    if yearlast_1 == '':
        lastyear = yearlast  
    elif (filename_trim == filename_trim_1) and (yearlast != yearlast_1):
        lastyear = max(yearlast,yearlast_1)
    if (filename_trim != filename_trim_1):
        firstyear = yearfirst
        lastyear = yearlast
        branch_time_comp2 = 'BLANK'
    # After checking reset test variables
    yearfirst_1 = firstyear
    yearlast_1 = lastyear        
 
    # Test branch_times
    if (filename_trim == filename_trim_1) and (branch_time == branch_time_1):
        f.close()
        continue ; # Skip to next file
    elif (filename_trim == filename_trim_1) and (branch_time != branch_time_1):
        filename_pad = "".join(['#',filename]) ; # Flag problem file
    else:
        filename_pad = filename

    # After checking, reset test variables
    filename_trim_1 = filename[6:(filename.index('.an.'))]
    #filename_trim_1 = filename[6:(filename.index('.mo.'))] ; # SHORTTERM FIX DUE TO AN FILE INVALID NAMES
    branch_time_1 = branch_time
    branch_time_valid = 'BLANK'
    
    # Attempt conditional reads
    # Calendar
    try:
        calendar = f.getAxis('time').calendar
    except:
        calendar = 'BLANK'
    try:
        parent_experiment_rip = f.parent_experiment_rip
    except:
        parent_experiment_rip = 'BLANK'
    
    # Process other global attributes        
    for tmp in f.contact.split():
        if '@' in tmp:
            contact = tmp ; # Return last email address
            # Cleanup resulting email addresses            
            contact = re.sub(':','',re.sub('\(','',re.sub('\)','',re.sub(',','',contact))))
            contact = re.sub('McKinstry<','',re.sub('>','',contact)) ; # Case EC-EARTH
            contact = re.sub('INM','',contact) ; # Case INMCM4
            contact = re.sub('&Leon','',contact) ; # Case CSIRO-Mk3-6-0.piControl
            contact = contact.rstrip('.') ; # Case NorESM1-M piControl
            break ; # Upon success
        elif '_at_' in tmp: # Deal with IPSL
            contact = f.contact.split()
            # Cleanup resulting email addresses
            ind = contact.index('_at_')
            contact = contact[(ind-1):(ind+2)] ; # Return partial email address
            contact = re.sub(' ','',re.sub('_at_','@',"".join(contact)))
            break ; # Upon success
        else:
            contact = 'BLANK'

    # Create component time from piControl time:units - need parent_experiment_id, parent_experiment_rip and resulting time:units
    # http://www2-pcmdi.llnl.gov/cdat/tutorials/cdatbasics/cdms-basics/createaxes
    if 'piControl' in header2:
        branch_time_comp1   = 'BLANK'
        piC_startyr         = 'BLANK'
        piC_endyr           = 'BLANK'
        greg_year           = 'BLANK'
        #piControl_info += [[filename_pad,tracking_id,creation_date,calendar,time_units,yearfirst,yearlast,branch_time,branch_time_comp,
        #                    branch_time_validated,parent_experiment_id,parent_experiment_rip,contact]]
        piControl_info += [[filename_pad,tracking_id,creation_date,calendar,time_units,firstyear,lastyear,branch_time,branch_time_comp1,
                            branch_time_valid,parent_experiment_id,parent_experiment_rip,contact]]
    else:
        tmp = cdms.createAxis(float32([f.branch_time]))
        tmp.id = 'time'
        # Determine dob attributes to apply to look up
        model = filename_trim[0:filename_trim.index('.')]
        # Create piControl string to search
        if 'BLANK' in parent_experiment_rip:
            parent_experiment_rip_s = 'r1i1p1'
        else:
            parent_experiment_rip_s = parent_experiment_rip
        piControl_search = "".join([model,'.',parent_experiment_id,'.',parent_experiment_rip_s])
        print "".join(['1: ',piControl_search])
        # Overwrite piControl info with valid info
        for piFix in valid:
            if (filename_trim == piFix[0]):
                branch_time_comp2 = piFix[1]
                parent_experiment_id = piFix[4].split('.')[0]
                parent_experiment_rip_s = piFix[4].split('.')[-1]
                parent_experiment_rip = piFix[4].split('.')[-1]
        piControl_search = "".join([model,'.',parent_experiment_id,'.',parent_experiment_rip_s])
        print "".join(['2: ',piControl_search])
        # Get Gregory branch_year
        greg_year = 'BLANK'
        for greg_info in gregory:
            if (filename_trim == greg_info[0]):
                greg_year = greg_info[1]
                break
        # Pair with piControl - get time:units from piControl
        for piFile in piControl_info:
            piFilename = piFile[0]
            piFileTUnits = piFile[4]
            pInd = [] ; i = -1 ; ind1 = ''
            try:
                while i < len(piFilename):
                    i = i+1
                    ind = piFilename.index('.',i)
                    if ind != ind1:
                        pInd += [ind]
                    ind1 = ind
            except ValueError:
                pass
            # Match with piControl info
            if piControl_search in piFilename[pInd[0]+1:pInd[3]]:
                #print "".join([piFilename[pInd[0]+1:pInd[3]],' ',"".join(map(str,piFileTUnits))])
                tmp.units = piFileTUnits
                tmp.calendar = piFile[3]
                branch_time_comp1 = "".join(map(str,tmp.asComponentTime()))
                #print "".join([piControl_search,' ',branch_time_comp]) ; print '-----'
                piC_startyr = piFile[5]
                piC_endyr = piFile[6]
                break
            else:
                branch_time_comp1 = 'BLANK'
                piC_startyr = 'BLANK'
                piC_endyr = 'BLANK'
        # Overwrite piControl branch_time_comp info with valid info
        for piFix in valid:
            if (filename_trim == piFix[0]):
                branch_time_comp2 = piFix[1]
                parent_experiment_id = piFix[4].split('.')[-1]

    # Create to save log error
    if 'branch_time_comp2' not in locals():
        branch_time_comp2 = 'BLANK'
        
    # Create branch_time_validated variable
    if experiment_id == 'historical':
        print "enter branch_time_valid.."
        try:
            branch_time_valid = spawn_dict[filename_trim.split('.')[0]][filename_trim.split('.')[-1]]['time_comp']
            print "branch_time_valid success!"
        except:
            branch_time_valid = "BLANK"
            print "branch_time_valid failure!"
    else:
        branch_time_valid = "BLANK"
    print "".join(["branch_time_valid test: ",branch_time_valid])
        
    f.close()

    # Clean up
'''
    del(branch_time,branch_time_comp,branch_time_validated,calendar,contact,creation_date,experiment_id,file1,filename,
        filename_pad,parent_experiment_id,parent_experiment_rip,realization,time_units,tmp,tracking_id,yearfirst,yearlast)
    gc.collect()
if 'branch_time_comp' in locals():
    del(branch_time,branch_time_comp,branch_time_validated,calendar,contact,creation_date,experiment_id,file1,filename,
        filename_pad,parent_experiment_id,parent_experiment_rip,realization,time_units,tmp,tracking_id,yearfirst,yearlast)
if 'ind' in locals():
    del(branch_time_1,count,delim,ind,header,header1,header2)
'''    
    
"""
branch_time,branch_time_YMDH (YYYYMMDDHHMMSS)
calendar
contact
creation_date
experiment, experiment_id
parent_experiment,parent_experiment_id
parent_experiment_rip
realization
time_units
tracking_id
"""
