# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 09:40:47 2012

Paul J. Durack 23rd January 2012

This script builds *.xml files for all "interesting" model variables

PJD 23 Jan 2012     - This file interrogates the current CMIP5 data holdings and creates xml files for each input
                      directory containing valid *.nc files
PJD 23 Jan 2012     - Edited to deal with syntax of CMIP5 DRS structure:
                      3776 'data' files reported
                      39118 'scratch' files reported, 39120 reported 1624
PJD 25 Jan 2012     - Continued to work to get xml files and output directory structure working
                      3776 'data' files reported - 74 match 7 vars
                      39140 'scratch' files reported 120125_1124 - 460 match 7 vars
PJD 26 Jan 2012     - 'data' files generating, extending to include 'scratch' files
                      3776 'data' files reported - 74 match 7 vars
                      39140 'scratch' files reported 120126 1024 - 460 match 7 vars
PJD  1 Feb 2012     - Quick test for current files
                      3776 'data' files reported - 74 match 7 vars
                      40218 'scratch' files reported 120201 1703 - 493 match 7 vars
PJD  2 Feb 2012     - Added make_xml check for reporting or file generation
                      3776 'data' paths reported - 74 outfile for 7 vars
                      40218 'scratch' paths reported 120202 1358 - 493 outfiles for 7 vars
PJD  2 Feb 2012     - Existing xml files 120202_1416=509; new 120202_1632=529;
                      Errors found on many files (567 were expected, are there 38 errors reported?)
PJD  6 Feb 2012     - 3776 'data' paths reported - 74 outfile for 7 vars
                      40218 'scratch' paths reported 120206 0946 - 493 outfiles for 7 vars
PJD  6 Feb 2012     - Added additional atm_vars on request of Peter (atm_vars2 does not include pr/tas)
                      3776 'data' paths reported - 538 outfiles for 51 vars
                      40218 'scratch' paths reported 120206 1456 - 3903 outfiles for 51 vars
PJD  7 Feb 2012     - Added 'complete' reporting to the logfile (was only reporting to console)
PJD 10 Feb 2012     - Reran to test data sources - 1981 list_outfiles total
                      3776 'data' paths reported - 1411 outfiles for 7 (+ 44 historical) vars
                      78903 'scratch' paths reported 120210 1156 - 570 outfiles for 7 (+ 44 historical) vars
PJD 14 Feb 2012     - Reran to test data sources - 2080 list_outfiles total
                      3776 'data' paths reported - 1480 outfiles for 7 (+ 44 historical) vars
                      80205 'scratch' paths reported 120214 1120 - 600 outfiles for 7 (+ 44 historical) vars
PJD 15 Feb 2012     - Removed ../output1/ from input pathnames
                      /cmip5/scratch/cmip5/output - add this dir checking code below
                      (CSIRO data - use different DRS structure to most /output vs /output1or2)
PJD 15 Feb 2012     - Reran to test data sources - 3199 list_outfiles total
                      3997 'data' paths reported - 2302 outfiles for 7 (+ 44 historical) vars
                      99454 'scratch' paths reported 120215 0912 - 1110 outfiles for 7 (+ 44 historical) vars
PJD 15 Feb 2012     - Appears xml generation runs robustly, and will continue on 0-file sizes and other pathologies
                      so running for mo (not mo_dyn) 120215 1201 mo=1593 xmls; mo_dyn=1753 xmls
PJD 18 Feb 2012     - Directory recovery complete (extundelete) and recreating directory structures
PJD 18 Feb 2012     - 120217_151605: 1849, 120218_170957: 2556 xml files generated
PJD 21 Feb 2012     - Reran 120221_165351: 202423 paths 'scratch', 3997 'data' paths
PJD 28 Feb 2012     - Data migration from scratch to data underway, reduced polling to 5000 increments for data
PJD 28 Feb 2012     - XML count 120228_1327: 2556  120228_1658: 3789
                      [durack1@crunchy cmip5]$ ls */*/mo/*/*.xml | wc -l
PJD  1 Mar 2012     - XML count 120301_1648: 3789 - prior to xml purge - [durack1@crunchy cmip5]$ rm -f */*/mo/*/*.xml
PJD  1 Mar 2012     - Updated cdat_path as ['/bin/sh: /usr/local/cdat/2012-01-12/bin/cdscan: No such file or directory\n']
PJD  2 Mar 2012     - XML count 120302_0848: 3067
PJD  8 Mar 2012     - XML count 120308_1204: 3067
PJD  8 Mar 2012     - XML count 120308_1916: 3568
PJD 18 Mar 2012     - Added 'zos' to ocean vars to process
PJD 19 Mar 2012     - Problem with /cmip5/scratch/cmip5/output1/NASA-GISS/GISS-E2-R/rcp26/mon/ocean/Omon/r1i1p1/v20111011/so/
                      relating to non-monotonic time axis
PJD 18 Mar 2012     - XML count 120318_19xx:
PJD 20 Mar 2012     - Added file counting to logfile, aids debugging
PJD 20 Mar 2012     - Added code to count number of file failures (add to an and an_trend file generation too)
PJD 20 Mar 2012     - Updated code to accurately report output *.xml files to be written (not paths)
PJD 20 Mar 2012     - Fixed reporting, i2 variables are not aligning with list lengths list_*_outfiles??
PJD 20 Mar 2012     - Trimmed out log reporting to include successful written file outfilename (not generic)
PJD 20 Mar 2012     - Fixed fairly serious bug where paths from scratch were being written into data variables:
                      list_data_outfiles and list_data_outfiles_paths were being indexed rather than list_scratch*
PJD 20 Mar 2012     - list_outfiles* now sorted, so should process alphabetically for model: cmip5.MODEL.EXPERIMENT..
PJD 21 Mar 2012     - XML count 120321_0949: 4488
PJD 21 Mar 2012     - Added 'amip' experiment to process list
PJD 21 Mar 2012     - Supplemented code to provide more diagnostic info for failures, check for file written if success and
                      if failure query for 0-file sizes which appear to be a particular issue with 'zos' variables - 
                      prompted by differing xml counts: 4488 in place (ls * | wc -l) vs 4928 reported/logged ok
PJD 21 Mar 2012     - PROBLEM 2 reported for files in /cmip5/scratch/cmip5/output1/NOAA-GFDL/GFDL-ESM2M/rcp26/mon/ocean/Omon/r1i1p1/v20110601/so/
                      tends to be incomplete files with incomplete time axis and cdscan notes a conflict
PJD 23 May 2012     - Updated to write files out to /mo_new, archive /mo and move /mo_new to /mo
PJD 23 May 2012     - Converted make_xml into script argument using argparse (default no files, arg makefiles generates files)
PJD 23 May 2012     - Added sic/sit variables to process list (for historical/amip exps), and realm seaIce
PJD 23 May 2012     - Added land_vars (mrro/mrros) and realm land
PJD 24 May 2012     - Fixed issue with file below e.readlines() and blocking, copied to _obsolete - cdscan is not reporting warnings to stderr:
                      120524_0923_mrros_Lmon_BNU-ESM_piControl_r1i1p1_145001-200812.nc
                      Traceback (most recent call last):
                      File "make_cmip5_xml.py", line 344, in <module>
                      ln = e.readlines()
PJD 25 May 2012	   - Updated seconds format for time_since_start_s from 08.2 to 09.2
PJD 25 May 2012	   - Converted fileerror from boolean (0/1) to logical (True/False) - and set as False prior to check (rather than else statement)
        		      Did conversion to boolean tests fix issue with reporting of zero-file sizes (last run reported 0)
PJD 29 May 2012     - Fixed archiving and updating in preparation for cronjob, *.xml creation is archived, /mo dirs are removed and new /mo_new directories moved into /mo
                      for ref: build xmls in temp directory and as part of process purge old and move new directories into structure
                      [durack1@crunchy cmip5]$ 7za a -t7z xmls.7z */*/mo/*/*.xml 786Kb
                      [durack1@crunchy cmip5]$ tar -cjf xmls.tar.bz2 */*/mo/*/*.xml 12.1Mb
                      [durack1@crunchy cmip5]$ tar -czf xmls.tar.gz */*/mo/*/*.xml 36.9Mb
PJD  1 Jun 2012     - Reporting cdscan warnings on files found in the /data/ subdir - parse log and report to Bob Drach
PJD  1 Jun 2012     - Updated so that any files with cdscan warnings are purged if they are created
PJD  1 Jun 2012     - Checked ok: code shouldn't fail if migration /mo archive doesn't exist, add checker code - required to run in /work/cmip5
PJD  1 Jun 2012     - Added fx_vars to variables being scanned
PJD  1 Jun 2012     - Fixed reporting so that true len_vars is being generated (added fx_vars above)
PJD  3 Jun 2012     - Added fx to realm list, was dumping files in atm
PJD  4 Jun 2012     - Added fx to temporal list, was excluding all variables (areacello..) - works with ../data/..
PJD  5 Jun 2012     - Added fx to xml count and purge/migrate code, also fixed fx_vars in variable indenting
PJD  5 Jun 2012     - Issue with directories created with no files.. Is a non-issue as processing was early days, only got to CCSM4
PJD  5 Jun 2012     - Removed volo from fx_vars, it's a monthly field (Omon)
PJD  5 Jun 2012     - Added 'areacella','orog','sftlf' to fx_vars
PJD  7 Jun 2012     - Converted processing to cronjob - processing takes 1.5 days (36hrs)
PJD 10 Jun 2012     - Corrected issue with xml_count, now adding ints (rather than strs)
PJD 10 Jun 2012     - Use Bob Drach's esgquery_index function to obtain current version info and add label to xml files
PJD 12 Jun 2012     - Updated so mount links scan new data (/cmip5 -> /cmip5_gdo2, /cmip5_css02)
PJD 12 Jun 2012     - Variable purging causing grief, purging only happens after css02_scratch
PJD 12 Jun 2012     - Added '-h' argument to df call which will now report in TB units
PJD 12 Jun 2012     - Added conditional del() statements for css02 data scours
PJD 16 Jun 2012     - Fixed issue for *.7z archive path
PJD 18 Jun 2012     - Added 'uo','vo','rhopoto','agessc','soga','cfc11','mlotst','omlmax','evs','friver','ficeberg','wfonocorr','vsfpr','vsfevap','vsfriver','vsf','vsfcorr','sfriver' to ocn_vars
PJD  5 Jul 2012     - Updated archive path to remove duplicate '/' characters which prevented archive from being written
PJD  5 Jul 2012     - Updated atm_vars with prw and other vars
PJD  5 Jul 2012     - Updated path to 7za to explicit /export/durack/.. - /bin/sh wasn't finding this binary
PJD  6 Jul 2012     - Added 'realm' to xml filename - in response to 'pr' issue highlighted by Peter G - should these prs be dropped into seaIce subdir instead?
                      Edit above will require recoding of all subsequent analysis using xmls - annual mean calculation
PJD  6 Jul 2012     - Additional to mo_new purging, fx_new purging is now also taking place
PJD  6 Jul 2012     - Outpath for xml now obtains 'realm' directly from the output filename, so will solve the issue Peter G highlighted
PJD 11 Jul 2012     - Added 'historicalNat' experiment to list - Peter G request
PJD 14 Jul 2012     - Updated with WORK/BATCH MODE commented lines, to toggle depending on mode -
                    Write logs to {host_path}_logs - batch file
                    Commented print statements, only errors are being written to display/stdout (and emailed) - batch file
PJD 14 Jul 2012     - Edited commented realm statements, lack of indent caused the script to bomb
PJD 14 Jul 2012     - Fixed issue with 'variable' incorrectly being captured as 'realm' in xml outpaths
PJD 14 Jul 2012     - Fixed issue with fx_new being written under 'realm' rather than forced under fx (realm)
PJD 16 Jul 2012     - Added 'clisccp' variable from cfMon realm to atm_vars2 - any more cfMon data worth indexing? (Mark Z)
PJD 18 Jul 2012     - Further work attempting to get archiving working, this time try shlex and create a symlink locally (_archive) to 7za
                      http://www.gossamer-threads.com/lists/python/python/724330 - shell=False needs a list variable passed as arguments
PJD 25 Jul 2012     - Fixed issue with 7za - this issue was due to files being purged while they are attempting to be archived
                    So using subprocess.call() which waits for completion, rather than subprocess.Popen() which runs in the background should solve this
PJD  2 Aug 2012     - Following prompts from updated spyder, removing shutil import (redundant)
PJD  2 Aug 2012     - As 7z archiving appears to work, turning off logging
PJD  2 Aug 2012     - Implemented perm check code below - check permissions (file access issues) - cdscan called yet no outfile created (PROBLEM 4 cases)
PJD  3 Aug 2012     - Added '\n' to SOURCEFILES statement, ensuring a direct compare for css02 and gdo2 holdings
PJD 22 Aug 2012     - Added parent process PID to logfile name - easier to determine and killing if an overrun is imminent
PJD 16 Sep 2012     - Added batchmode option; batch edits are activated by a single switch
PJD 16 Sep 2012     - Confirmed existing xml counts are correct - 1604/1610 for last 2 runs?? "Argument list too long" error - converted to glob.glob()
PJD 17 Sep 2012     - Corrected issue with batch referencing (if statements need to have executing code)
PJD 17 Sep 2012     - "-will-delete" directories are now excluded from file listings - /cmip5_gdo2/scratch/cmip5/output1
PJD 17 Sep 2012     - Corrected variable passed for access check
PJD 18 Sep 2012     - Saved list_outfiles* variables so as not to have to reprocess and waste time - 120918_1015_list_outfiles.pickle
                    http://stackoverflow.com/questions/6568007/how-do-i-save-and-restore-multiple-variables-in-python
PJD 21 Sep 2012     - There appears to be another issue with the o.read() statement (line 604), this is highlighted in the log and hang detailed:
                    120917_131323_make_cmip5_xml-crunchy-PID30510-HANGUVCDATUPDATE.log
                    Added test print statements
PJD 24 Sep 2012     - Updated os.popen3 call to read stderr not stdout for warnings (cdscan outputs redirected)
PJD 25 Sep 2012     - Updated os.popen3 call with additional argument ",bufsize=0" which prevents waiting for all buffers to be written and also
                    purge outputs del(ii,o,e) ; gc.collect() to ensure buffer over run doesn't occur
PJD 26 Sep 2012     - Added zostoga to ocn_vars
PJD 26 Sep 2012     - It appears issue with o.read() is due to e containing exit code, so o is not readable until e is read first -
                    e.read() and o.read() then seems to work as expected ; e should never hang as buffer is written immediately? (Charles quote)
PJD 27 Sep 2012     - Updated os.popen3 to subprocess.Popen to solve blocking read issue (as noted above) ; Last fail:
                    31838 /cmip5_css02/scratch/cmip5/output1/MIROC/MIROC4h/piControl/mon/ocean/Omon/r1i1p1/v20110907/so
PJD 27 Sep 2012     - Charles implemented changes in cdscan, so errors/warnings are pushed to stderr not stdout - edits above should solve issues
PJD 28 Sep 2012     - Updated references from st (e.read()) to err.*
PJD 28 Sep 2012     - Updated error reports with data source path rather than xml name
PJD 28 Sep 2012     - Generic commented code cleanup and purge
PJD  4 Oct 2012     - Moved ua and va from atm_vars2 to atm_vars
PJD  5 Oct 2012     - Corrected path for read access error reporting; 0-filesize wasn't working; cleaned up dual instances of filepath creation
                    /cmip5_css02/scratch/cmip5/output1/NCAR/CCSM4/abrupt4xCO2/mon/ocean/Omon/r1i1p1/v20120720/thetao
                    os.getuid(), os.geteuid(), os.getgid(), os.getegid(); if uid == euid and gid == egid: testing removed
PJD  5 Oct 2012     - Encased counter prints within batch (True/False) test to prevent writing to cron logs
PJD  8 Oct 2012     - Last run (excluding ua,va variables) took 98hrs/5 days 121001_080002 -> 120105_0959xx
PJD  9 Oct 2012     - Added else statement for i1 counters, as paths were all reporting 0
PJD 12 Nov 2012     - Corrected elif statement for batch - counter wasn't incrementing - logged "paths total" were reporting 0
PJD  4 Jan 2013     - Added 'ta' to atm_vars and purged from atm_vars2
PJD 10 Jan 2013     - Updated path scour to use function and multiprocess, parallelising network scouring
PJD 10 Jan 2013     - Added try/except for path_bits, as problem directories exist in /cmip5_css02/scratch/cmip5/
PJD 10 Jan 2013     - Reorganised fx files, removed experiment from directory structure - all are dropped in ..cmip5/fx (particularly for limited basin files)
PJD 10 Jan 2013     - Justified logs and screenprints to set characters
PJD 11 Jan 2013     - Changed all os.popen calls to subprocess
PJD 17 Jan 2013     - Added fx_vars declaration to xmlWrite - may need to remove duplicates (also in pathToFile)
PJD 17 Jan 2013     - Rearrange order of fileNoRead and fileNoWrite as the latter is a consequence to the former
PJD 17 Jan 2013     - Added 'evspsbl' to atm_vars and removed from atm_vars2
PJD 17 Jan 2013     - Parallelised xml file generation
                    subprocess.call (foreground); subprocess.Popen (background)
                    http://www.doughellmann.com/articles/pythonmagazine/completely-different/2007-10-multiprocessing/
                    http://www.parallelpython.com - looks promising, uncertain of process number control however
                    http://www.stackoverflow.com/questions/2993487/spawning-and-waiting-for-child-processes-in-python
PJD 17 Jan 2013     - Added a try/except clause in xmlWrite (if os.path.exists(os.path.join(host_path,out_path))) to catch situation
                    where directory doesn't exist but was created by a parallel process
PJD 19 Jan 2013     - xmlWrite (and xmlLog) updated to hand back (and receive) path, so it can be used in cases of errors (an i-index outfile_paths doesn't work)
PJD 27 Jan 2013     - Added 'historicalGHG', 'historicalMisc' and 'past1000' experiments to list
PJD 29 Jan 2013     - Updated path to fx for purging, archiving and moving into place
PJD 12 Feb 2013     - Added purge code to delete $EXPERIMENT/fx subdirs, as new dedicated fx/fx/* directories are written (should only be effective once)
PJD 12 Feb 2013     - Added code to prevent archival and purging if <40k xmls are written
PJD 13 Feb 2013     - Quirky issues with 2013-02-11 build, rolling back to 2012-11-14
PJD 14 Feb 2013     - Following install of pyflakes and rope have done a general code tidyup and removed deprecated/obsolete code and imports
PJD 17 Feb 2013     - Renamed from make_cmip5_xml_new.py to make_cmip5_xml.py
                      - old vs parallel code checked out ok (more xmls in new than old, more recent scan however)
                      - Added oceanonly to known host list
                      - Purged threadcount diagnostics
                      - Corrected host_path to default
                      - Updated cdat_path to latest (was 2012-11-14)
PJD 17 Feb 2013     - oceanonly bombed on line 757, migrating old to new - created symlink to 7za in _archive subdir
PJD 19 Feb 2013     - Fixed issue with host_names not being resolved, due to nested if statements
PJD 21 Feb 2013     - Code working, so ${datenow}_list_outfiles.pickle now directed into _logs subdir
PJD 21 Feb 2013     - Added 'historicalExt' to experiment list
PJD 22 Feb 2013     - Added 'clwvi','clivi' to atm_vars2
PJD 25 Feb 2013     - Trimmed error prints to screen to only interactive runs (bounded all print statements within "if not batch")
PJD 25 Feb 2013     - Implemented code to deal with duplicates:
                      - Added tableId to xml filename
                      - Scanned and removed duplicate files from outfiles and outfiles_paths
                    There is an issue with duplicate entries for the same files, which is leading to cdscan "et>" values being created
                    /work/cmip5/amip/atm/mo/evspsbl/cmip5.CSIRO-Mk3-6-0.amip.r5i1p1.mo.atm.evspsbl.ver-v20120302.xml
                    /work/cmip5/historical/atm/mo/evspsbl/cmip5.CSIRO-Mk3-6-0.historical.r2i1p1.mo.atm.evspsbl.ver-v20111220.xml
PJD 25 Feb 2013     - Added time_format print statement to start of script - will assist trying to resolve when logs are emailed by the cron daemon
PJD 25 Feb 2013     - Converted back to test mode, is some pathology with HistoricalExt data causing grief?
PJD 26 Feb 2013     - Fixed issue with off-by-one indexing issue removing duplicates from outfiles,outfiles_paths - as indexes are 0-based, len(var)-1 is required
PJD 27 Feb 2013     - Corrected issue with tableId getting truncated to *mo (not *mon) - now filenames and paths are explicitly dealt with
PJD 27 Feb 2013     - An issue could exist where failure occurs due to a directory being purged (and doesn't exist) after outfiles_paths has been generated?
                      infilenames = glob.glob(*.nc) should fix this issue, as test for len(infilenames) != 0 should fail
                      Added preallocation of return arguments: fileWarning,fileNoWrite,fileNoRead,fileZero = False and errorCode = ''
PJD 27 Feb 2013     - Following issue above, added fileNone argument - edits to xmlWrite and xmlLog functions and addition of PROBLEM 5 case
PJD 27 Feb 2013     - Corrected quirky logical statements for fileNoWrite and if os.path.isfile(outfileName) in xmlWrite function
PJD 27 Feb 2013     - Corrected xmlWrite variable index (up one 6 -> 7 since tableId is now included in filename)
PJD 27 Feb 2013     - Corrected quirky logical statement in xmlWrite - if not os.path.exists(os.path.join(host_path,out_path)):
PJD 28 Feb 2013     - Added log_path variable and removed commented code blocks
PJD 28 Feb 2013     - Further removed commented code blocks by encasing argparse in if batch query, and further cleaned up commented code
PJD 28 Feb 2013     - Updated error print statements to report err_text,inpath rather than err_text,outfileName - same as logfile and easier to debug interactively
PJD  1 Mar 2013     - Added variables from atm_vars2 to atm_vars for Charles: hur,hurs,hus,huss,tasmin,tasmax
PJD  1 Mar 2013     - Added mkdirs function definition
PJD  7 Mar 2013     - Fixed issue with xmlWrite call - else component was setting fewer arguments than queue0 contained
PJD  8 Mar 2013     - Added clisccp,clt,rlut,rlutcs,rsdscs,rsuscs,rsut,rsutcs to atm_vars (from atm_vars2) for Mark Z
PJD 20 Mar 2013     - Added 'mfo' to ocn_vars
PJD 23 Apr 2013     - Converted "Warning:" to "Warning" when checking for cdscan issues: /cmip5_gdo2/data/cmip5/output1/MOHC/HadGEM2-ES/rcp85/mon/atmos/Amon/r1i1p1 - overlapping times
PJD 23 Apr 2013     - Added css01 to search paths
PJD 27 Apr 2013     - Reorganised logging of scratch and data paths
PJD 28 Apr 2013     - Updated index to report Warnings from cdscan
PJD 10 May 2013     - Added 'thetaoga' to ocn_vars
PJD 10 May 2013     - Added fix for issue with verbose stderr output being logged - small descriptive text now captured, not vectors describing issues
PJD 11 May 2013     - Added further tweaks to reduce verbosity of logs
PJD 19 May 2013     - Even more tweaks to reduce verbosity of logs, str.find failures return -1 which is the lowest index
PJD 27 May 2013     - Added further tweaks to reduce log verbosity - this time due to inconsistent error messages for cdscan type 2 error
PJD  5 Jun 2013     - Corrected parsing of data_outfiles following code tweak
PJD  6 Jun 2013     - Added test_latest def - validating this now - as nc file is opened 0-files will cause abort, so should reduce cdscan 0-file warnings
                      It appears 6-concurrent jobs are not testing this at all, increase 2x by increasing calls to pathToFile
                      Job bombed somewhere with nondescript error about urllib connection - internal error with esgquery_index? - see 130607_esgquery_index_crash.txt
                      for partial log info - attempt to rerun after xmls are recreated
PJD 13 Jun 2013     - Added permissions wash for */*/mo and */fx subdirs (issue only on oceanonly)
PJD 24 Jun 2013     - Added tsl to land variable list
PJD 24 Jul 2013     - Added sysCallTimeout function - possibly move to durolib
PJD 26 Aug 2013     - Added shebang
PJD 26 Aug 2013     - Removed atm_vars2 variable included in atm_vars and cleaned up code
PJD 27 Aug 2013     - Cleaned up issues with latest code checks
PJD 28 Aug 2013     - Turned off metadata scan (creation_date/tracking_id) from files to speed up processing - speed up ~4x
PJD 16 Sep 2013     - Import of cdms2 prompts user for yes/no logging query (since 1.4.0rc1) causing hangs - commented out cdms2 import in response
PJD 18 Nov 2013     - Added amipFuture experiment (Mark Z requested)
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
                    
                    - TODO:
                    Add check to ensure CSS/GDO systems are online, if not abort - use sysCallTimeout function
                    sysCallTimeout(['ls','/cmip5_gdo2/'],5.) ; http://stackoverflow.com/questions/13685239/check-in-python-script-if-nfs-server-is-mounted-and-online
                    Add model masternodes
                    Fix issue with no valid files being recorded
                    Add permissions wash over new xml files once copied in place (issue on oceanonly alone)
                    Placing read test in pathToFile will trim out issues with 0-sized files and read permissions, so reporting may need to be relocated
                    Add counters for lat1 vs lat0
                    Report new runtimeError in cdscan - problems with overlapping times, issue in combineKeys function - Report to Jeff/Charles
                    Added demo code from Charles to convert processes and queues into lists of objects thereby subverting hard-coding and parallel limits
                    update for gdo2_data (~8k; 2.2hrs) and css02_scratch (~25k; 7hrs) to scour using multiple threads each - what is the IO vs wait difference?
                     consider using multiprocess.pool to achieve this, so full loads until job(s) are completed
                    Consider using multiprocess.pool (which loads up processes concurrently) rather than multiprocess.Process
                    Consider adding a ./running file with 0/1 binary for new job to poll before it begins - overruns are a continuing issue
                     Ensure this file contains the PID of the parent process, so this can be checked for life before attempting to move mo_new to mo dirs
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

import argparse,datetime,errno,gc,glob,os,pickle,shlex,subprocess,sys,time
#import cdms2 as cdm
from durolib import writeToLog
from multiprocessing import Process,Manager
from socket import gethostname
from string import replace
from subprocess import Popen,PIPE

# Cleanup interactive/spyder sessions
if 'e' in locals():
    del(e,pi,sctypeNA,typeNA)
    gc.collect()

##### Set batch mode processing, console printing on/off and multiprocess loading #####
batch       = True ; # True = on, False = off
batch_print = False ; # Write log messages to console - suppress from cron daemon ; True = on, False = off
threadCount = 40 ; # ~36hrs xml creation solo ; 50hrs xml creation crunchy & oceanonly in parallel
##### Set batch mode processing, console printing on/off and multiprocess loading #####

# Set time counter and grab timestamp
start_time = time.time() ; # Set time counter
time_now = datetime.datetime.now()
time_format = time_now.strftime('%y%m%d_%H%M%S')

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
time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
pypid = str(os.getpid()) ; # Returns calling python instance, so master also see os.getppid() - Parent
logfile = os.path.join(log_path,"".join([time_format,'_make_cmip5_xml-',trim_host,'-threads',str(threadCount),'-PID',pypid,'.log']))
# Logging the explicit data path that is being searched
os.chdir('/cmip5_gdo2')
cmd = 'df -h | grep cmip5'
p = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)
out,err = p.communicate()
writeToLog(logfile,"".join(['TIME: ',time_format]))
writeToLog(logfile,"".join(['HOSTNAME: ',host_name]))
writeToLog(logfile,"".join(['SOURCEFILES:\n',out]))
del(trim_host,time_now,time_format,cmd,p,out,err)
gc.collect()


# Define functions
def mkdirs(newdir,mode=0777):
    #http://my.safaribooksonline.com/book/programming/python/0596001673/files/pythoncook-chp-4-sect18
    try: os.makedirs(newdir,mode)
    except OSError,err:
        #Re-raise the error unless it's about an already existing directory
        if err.errno != errno.EEXIST or not os.path.isdir(newdir):
            raise


def sysCallTimeout(cmd,timeout):
    start = time.time()
    p = Popen(cmd)
    while time.time() - start < timeout:
        if p.poll() is not None:
            return
        time.sleep(0.1)
    p.kill()
    raise OSError('System call timed out')


# Debug code for duplicate removal/checking
#import os,pickle
#picklefile = '/work/cmip5/_logs/140808_155431_list_outfiles.pickle'
#f = open(picklefile,'r')
#outfiles,outfiles_new,outfiles_paths,outfiles_paths_new = pickle.load(f)
#f.close()
def pathToFile(inpath,start_time,queue1):
#def pathToFile(inpath,start_time): ; # Non-parallel version of code for testing
    data_paths = [] ; i1 = 0
    exclude_dir = '-will-delete' ; # Must be string in current syntax  
    for (path,dirs,files) in os.walk(inpath,'false'):
        if exclude_dir in path:
            continue
        elif files != [] and dirs == []:
            # Append to list variable
            data_paths += [path]
            i1 = i1 + 1 ; # Increment counter
    
    # Create variable and realm names
    experiments = ['1pctCO2','abrupt4xCO2','amip','amipFuture','historical','historicalExt','historicalGHG','historicalMisc',
                   'historicalNat','past1000','piControl','rcp26','rcp45','rcp60','rcp85'] ; experiments.sort()
    temporal    = ['fx','mon'] ; # For months and fixed fields only
    atm_vars    = ['cl','cli','clisccp','clivi','clt','clw','clwvi','evspsbl','hfls','hfss','hur','hurs',
                   'hus','huss','mc','pr','prc','prsn','prw','ps','psl','rlds','rldscs','rlus','rluscs','rlut',
                   'rlutcs','rsds','rsdscs','rsdt','rsus','rsuscs','rsut','rsutcs','sbl','sci','sfcWind',
                   'ta','tas','tasmax','tasmin','tauu','tauv','ts','ua','uas','va','vas','wap','zg'] ; atm_vars.sort()
    atmOrocn    = ['atm','ocn'] ; atmOrocn.sort()
    fx_vars     = ['areacella','areacello','basin','deptho','orog','sftlf','sftof','volcello'] ; fx_vars.sort()
    land_vars   = ['mrro','mrros','tsl'] ; land_vars.sort()
    ocn_vars    = ['agessc','cfc11','evs','ficeberg','friver','mfo','mlotst','omlmax','rhopoto','sfriver',
                   'so','soga','sos','tauuo','tauvo','thetao','thetaoga','tos','uo','vo','vsf','vsfcorr','vsfevap','vsfpr',
                   'vsfriver','wfo','wfonocorr','zos','zostoga'] ; ocn_vars.sort()
    seaIce_vars = ['sic','sit'] ; seaIce_vars.sort()
    len_vars    = len(atm_vars)+len(fx_vars)+len(land_vars)+len(ocn_vars)+len(seaIce_vars) ; # Create length counter for reporting
    
    # Check for valid outputs
    if not data_paths:
        #print "** No valid data found on path.. **"
        # Create timestamp as function completes
        time_since_start = time.time() - start_time
        #return('','',time_since_start,i1,0,len_vars) ; # Non-parallel version of code for testing
        queue1.put_nowait(['','',time_since_start,i1,0,len_vars]) ; # Queue
        return
    
    # Mine inputs for info and create outfiles and paths
    data_outfiles = [] ; data_outfiles_paths = [] ; i2 = 0
    for path in data_paths:
        path_bits   = path.split('/')
        # Set indexing
        if 'data' in path_bits:
            pathIndex = path_bits.index('data')
        elif 'scratch' in path_bits:
            pathIndex = path_bits.index('scratch')
        
        try:
            model       = path_bits[pathIndex+4] ; #6
            experiment  = path_bits[pathIndex+5] ; #7
            time_ax     = path_bits[pathIndex+6] ; #8
            realm       = path_bits[pathIndex+7] ; #9
            tableId     = path_bits[pathIndex+8] ; #10
            # Fix realms to standard acronyms
            if (realm == 'ocean'):
                realm = 'ocn'
            elif (realm == 'atmos'):
                realm = 'atm'
            realisation = path_bits[pathIndex+9] ; #11
            # Check for source path and order variable/version info
            if 'scratch' in path_bits:
                version     = path_bits[pathIndex+10] ; #12
                variable    = path_bits[pathIndex+11] ; #13
            elif 'data' in path_bits:
                version     = path_bits[pathIndex+11] ; #13
                variable    = path_bits[pathIndex+10] ; #12
            # Getting versioning/latest info
            testfile = os.listdir(path)[0]
            #print "".join(['file found: ',testfile])            
            # Test for zero-size file before trying to open
            #print os.path.join(path,testfile)
            fileinfo = os.stat(os.path.join(path,testfile))
            checksize = fileinfo.st_size
            if checksize == 0:
                #print "".join(['Zero-sized file: ',path])
                continue
            # Read access check
            if os.access(os.path.join(path,testfile),os.R_OK) != True:
                #print "".join(['No read permissions: ',path])
                continue
            #f_h = cdm.open(os.path.join(path,testfile))
            #tracking_id     = f_h.tracking_id
            tracking_id = ''
            #creation_date   = f_h.creation_date
            creation_date = ''
            #f_h.close()
            if test_latest(tracking_id,creation_date):
                lateststr = 'latestX' ; # Placeholder                
                #lateststr = 'latest1' ; # Latest
            else:
                lateststr = 'latest0' ; # Not latest
        except Exception,err:
            # Case HadGEM2-AO attempt to recover
            if 'HadGEM2-AO' in model:
                variable    = path_bits[pathIndex+8]
                if variable in atm_vars:
                    tableId = 'Amon'
                elif variable in ocn_vars:
                    tableId = 'Omon'
                elif variable in land_vars:
                    tableId = 'Lmon'
                elif variable in seaIce_vars:
                    tableId = 'OImon'
                version     = datetime.datetime.fromtimestamp(fileinfo.st_ctime).strftime('%Y%m%d')
            # Case BESM-OA2-3 skip
            if 'BESM-OA2-3' in model and 'decadal' in experiment:
                continue                
            else:
                print 'pathToFile - Exception:',err,path
                continue
        # Test for list entry and trim experiments and variables to manageable list
        if (experiment in experiments) and (time_ax in temporal) and ( (variable in ocn_vars) or (variable in atm_vars) or (variable in seaIce_vars) or (variable in land_vars) or (variable in fx_vars) ):
            data_outfiles.insert(i2,".".join(['cmip5',model,experiment,realisation,time_ax,realm,tableId,variable,"".join(['ver-',version]),lateststr,'xml']))
            data_outfiles_paths.insert(i2,path)
            i2 = i2 + 1
    
    # Create timestamp as function completes
    time_since_start = time.time() - start_time
    
    #return(data_outfiles,data_outfiles_paths,time_since_start,i1,i2,len_vars) ; # Non-parallel version of code for testing
    queue1.put_nowait([data_outfiles,data_outfiles_paths,time_since_start,i1,i2,len_vars]) ; # Queue
    return


def logWrite(logfile,time_since_start,path_name,i1,data_outfiles,len_vars):
    outfile_count = len(data_outfiles)
    time_since_start_s = '%09.2f' % time_since_start
    print "".join([path_name.ljust(13),' scan complete.. ',format(i1,"1d").ljust(6),' paths total; ',str(outfile_count).ljust(6),' output files to be written (',format(len_vars,"1d").ljust(3),' vars sampled)'])
    writeToLog(logfile,"".join([time_since_start_s,' : ',path_name.ljust(13),' scan complete.. ',format(i1,"1d").ljust(6),' paths total; ',format(outfile_count,"1d").ljust(6),' output files to be written (',format(len_vars,"1d").ljust(3),' vars sampled)']))
    return


def xmlWrite(inpath,outfile,host_path,cdat_path,start_time,queue1):
    infilenames = glob.glob(os.path.join(inpath,'*.nc'))
    # Create list of fx vars
    fx_vars = ['areacello','basin','deptho','sftof','volcello','areacella','orog','sftlf'] ; fx_vars.sort()
    # Construct outfile path from outfilename
    outfile_string  = "".join(outfile)
    outfile_bits    = outfile_string.split('.')
    experiment      = outfile_bits[2]
    temporal        = outfile_bits[4]
    if (temporal == 'mon'):
        temporal = 'mo_new' ; # Updated path; existing xmls are in place until successful xml write completion
    elif (temporal == 'fx'):
        temporal = 'fx_new' ;
    
    realm           = outfile_bits[5]
    variable        = outfile_bits[7]
    if (variable in fx_vars):
        realm = 'fx'
        # Truncate experiment from fx files
        out_path = os.path.join(realm,temporal,variable)
    else:
        out_path = os.path.join(experiment,realm,temporal,variable)
    
    outfileName = os.path.join(host_path,out_path,"".join(outfile))
    # Fix mon -> mo
    outfileName = replace(outfileName,'.mon.','.mo.') ; # Replaces mon in filename
    if not os.path.exists(os.path.join(host_path,out_path)):
        # At first run create output directories
        try:
            os.makedirs(os.path.join(host_path,out_path))
            #mkdirs(os.path.join(host_path,out_path)) ; # Alternative call to not crash if directory exists
        except Exception,err:
            print 'xmlWrite - Exception:',err
            print "".join(['** Crash while trying to create a new directory: ',os.path.join(host_path,out_path)])                
    
    if os.path.isfile(outfileName):
        os.remove(outfileName)
    
    # Generate xml file - and preallocate error codes
    fileWarning = False
    errorCode   = ''
    fileNoWrite = False
    fileNoRead  = False
    fileZero    = False
    fileNone    = False
    if len(infilenames) != 0:
        # Create a fullpath list of bad files and exclude these, by trimming them out of a filename list
        cmd = "".join([cdat_path,'cdscan -x ',outfileName,' ',os.path.join(inpath,'*.nc')])
        # Catch errors with file generation            
        p = Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE)
        out,err = p.communicate()
        # Check cdscan output for warning flags
        fileWarning = False
        if err.find('Warning') > -1:
            errstart = err.find('Warning') ; # Indexing returns value for "W" of warning
            err1 = err.find(' to: [')
            if err1 == -1: err1 = len(err)-1 ; # Warning resetting axis time values
            err2 = err.find(': [')
            if err2 == -1: err2 = len(err)-1 ; # Problem 2 - cdscan error - Warning: axis values for axis time are not monotonic: [
            err3 = err.find(':  [')
            if err3 == -1: err3 = len(err)-1 ; # Problem 2 - cdscan error - Warning: resetting latitude values:  [    
            err4 = err.find(') ')
            if err4 == -1: err4 = len(err)-1 ; # Problem 1 - zero infile size ; Problem 4 - no outfile
            err5 = err.find(', value=')
            if err5 == -1: err5 = len(err)-1 ; # Problem 2 - cdscan error - 'Warning, file XXXX, dimension time overlaps file
            errorCode = err[errstart:min(err1,err2,err3,err4,err5)]
            fileWarning = True
        else:
            errorCode = ''
        #if err.find
        del(cmd,err,out,p) ; gc.collect()
        # Validate outfile was written
        fileNoWrite = not os.path.isfile(outfileName)
        # Validate infile is readable (permission error) and non-0-file size
        fileNoRead = False
        fileZero = False
        filestocheck = os.listdir(inpath)
        for checkfile in filestocheck:
            # 0-file size check
            fileinfo = os.stat(os.path.join(inpath,checkfile))
            checksize = fileinfo.st_size
            if checksize == 0:
                fileZero = True
            # Read access check
            if os.access(os.path.join(inpath,checkfile),os.R_OK) != True:
                fileNoRead = True
    else:
        fileNone = True
    
    # Create timestamp as function completes
    time_since_start = time.time() - start_time
            
    #return(inpath,outfileName,fileZero,fileWarning,fileNoRead,fileNoWrite,fileNone,errorCode,time_since_start) ; Non-parallel version of code
    queue1.put_nowait([inpath,outfileName,fileZero,fileWarning,fileNoRead,fileNoWrite,fileNone,errorCode,time_since_start]) ; # Queue
    return


def xmlLog(logFile,fileZero,fileWarning,fileNoWrite,fileNoRead,fileNone,errorCode,inpath,outfileName,time_since_start,i,xmlBad1,xmlBad2,xmlBad3,xmlBad4,xmlBad5,xmlGood):
    time_since_start_s = '%09.2f' % time_since_start
    logtime_now = datetime.datetime.now()
    logtime_format = logtime_now.strftime("%y%m%d_%H%M%S")
    if fileZero:
        # Case cdscan writes no file
        if '/data/cmip5/' in inpath:
            err_text = ' DATA PROBLEM 1 (cdscan error - zero infile size) indexing '
        else:
            err_text = ' PROBLEM 1 (cdscan error - zero infile size) indexing '
        writeToLog(logFile,"".join(['** ',format(xmlBad1,"07d"),' ',logtime_format,' ',time_since_start_s,'s',err_text,inpath,' **']))
        if batch_print:
            print "".join(['**',err_text,inpath,' **'])
        xmlBad1 = xmlBad1 + 1;
        # Purge problem files
        if os.path.isfile(outfileName):
            os.remove(outfileName)
    elif fileWarning:
        # Case cdscan reports an error
        if '/data/cmip5/' in inpath:
            err_text = "".join([' DATA PROBLEM 2 (cdscan error- \'',errorCode,'\') indexing '])
        else:
            err_text = "".join([' PROBLEM 2 (cdscan error - \'',errorCode,'\') indexing '])
        writeToLog(logFile,"".join(['** ',format(xmlBad2,"07d"),' ',logtime_format,' ',time_since_start_s,'s',err_text,inpath,' **']))
        if batch_print:
            print "".join(['**',err_text,inpath,' **'])
        xmlBad2 = xmlBad2 + 1;
        # Purge problem files
        if os.path.isfile(outfileName):
            os.remove(outfileName)
    elif fileNoRead:
        # Case cdscan reports no error, however file wasn't readable
        if '/data/cmip5/' in inpath:
            err_text = ' DATA PROBLEM 3 (read perms) indexing '
        else:
            err_text = ' PROBLEM 3 (read perms) indexing '
        writeToLog(logFile,"".join(['** ',format(xmlBad3,"07d"),' ',logtime_format,' ',time_since_start_s,'s',err_text,inpath,' **']))
        if batch_print:
            print "".join(['**',err_text,inpath,' **'])
        xmlBad3 = xmlBad3 + 1;
        # Purge problem files
        if os.path.isfile(outfileName):
            os.remove(outfileName)
    elif fileNoWrite:
        # Case cdscan reports no error, however file wasn't written
        if '/data/cmip5/' in inpath:
            err_text = ' DATA PROBLEM 4 (no outfile) indexing '
        else:
            err_text = ' PROBLEM 4 (no outfile) indexing '
        writeToLog(logFile,"".join(['** ',format(xmlBad4,"07d"),' ',logtime_format,' ',time_since_start_s,'s',err_text,inpath,' **']))
        if batch_print:
            print "".join(['**',err_text,inpath,' **'])
        xmlBad4 = xmlBad4 + 1;
        # Purge problem files
        if os.path.isfile(outfileName):
            os.remove(outfileName)
    elif fileNone:
        # Case cdscan reports no error, however file wasn't written
        if '/data/cmip5/' in inpath:
            err_text = ' DATA PROBLEM 5 (no infiles) indexing '
        else:
            err_text = ' PROBLEM 5 (no infiles) indexing '
        writeToLog(logFile,"".join(['** ',format(xmlBad5,"07d"),' ',logtime_format,' ',time_since_start_s,'s',err_text,inpath,' **']))
        if batch_print:
            print "".join(['**',err_text,inpath,' **'])
        xmlBad5 = xmlBad5 + 1;
        # Purge problem files
        if os.path.isfile(outfileName):
            os.remove(outfileName)
    else:
        writeToLog(logFile,"".join(['** ',format(xmlGood,"07d"),' ',logtime_format,' ',time_since_start_s,'s success creating: ',outfileName,' **']))
        xmlGood = xmlGood + 1;
    
    return[xmlBad1,xmlBad2,xmlBad3,xmlBad4,xmlBad5,xmlGood] # ; Non-parallel version of code
    #queue1.put_nowait([xmlBad1,xmlBad2,xmlBad3,xmlBad4,xmlBad5,xmlGood]) ; # Queue
    #return


def test_latest(tracking_id,creation_date):
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
## CSS02 data sources - Mine for paths and files
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

# Generate master lists from sublists
outfiles_paths = list(gdo2_data_outfiles_paths)
outfiles_paths.extend(gdo2_scratch_outfiles_paths) ; # Add gdo2_scratch to master
outfiles_paths.extend(css01_data_outfiles_paths) ; # Add css01_data to master
outfiles_paths.extend(css01_scratch_outfiles_paths) ; # Add css01_scratch to master
outfiles_paths.extend(css02_data_outfiles_paths) ; # Add css02_data to master
outfiles_paths.extend(css02_scratch_outfiles_paths) ; # Add css02_scratch to master
outfiles_paths.extend(css02_cm5_outfiles_paths) ; # Add css02_cmip5 to master

outfiles = list(gdo2_data_outfiles)
outfiles.extend(gdo2_scratch_outfiles) ; # Add gdo2_scratch to master
outfiles.extend(css01_data_outfiles) ; # Add css01_data to master
outfiles.extend(css01_scratch_outfiles) ; # Add css01_scratch to master
outfiles.extend(css02_data_outfiles) ; # Add css02_data to master
outfiles.extend(css02_scratch_outfiles) ; # Add css02_scratch to master
outfiles.extend(css02_cm5_outfiles) ; # Add css02_cmip5 to master

# Sort lists by outfiles
outfilesAndPaths = zip(outfiles,outfiles_paths)
outfilesAndPaths.sort() ; # sort by str value forgetting case - key=str.lower; requires str object
del(outfiles,outfiles_paths)
gc.collect()
outfiles,outfiles_paths = zip(*outfilesAndPaths)

# Truncate duplicates from lists
#130225 1342: Pathologies to consider check for bad data
#badpaths = ['/bad','-old/','/output/','/ICHEC-old1/']
#bad = GISS-E2-R, EC-EARTH ; -old = CSIRO-QCCCE-old ; /output/ = CSIRO-Mk3-6-0 ; /ICHEC-old1/ = EC-EARTH
#paths rather than files = CNRM-CM5, FGOALS-g2, bcc-csm1-1
#duplicates exist between /cmip5_gdo2/scratch and /cmip5_css02/scratch = CCSM4, CSIRO-Mk3-6-0
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
time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
f = open(os.path.join(log_path,"".join([time_format,'_list_outfiles.pickle'])),'w')
pickle.dump([outfiles,outfiles_new,outfiles_paths,outfiles_paths_new],f)
f.close()
del(time_now,time_format,i1,i2,len_vars,time_since_start)

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

130225 1342: Check for bad data
badpaths = ['/bad','-old/','/output/','/ICHEC-old1/']
bad = GISS-E2-R, EC-EARTH ; -old = CSIRO-QCCCE-old ; /output/ = CSIRO-Mk3-6-0 ; /ICHEC-old1/ = EC-EARTH
paths rather than files = CNRM-CM5, FGOALS-g2, bcc-csm1-1
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


# Check whether running for file reporting or xml generation:
if make_xml:
    # Create counters for xml_good and xml_bad
    xmlGood = 1; xmlBad1 = 1; xmlBad2 = 1; xmlBad3 = 1; xmlBad4 = 1; xmlBad5 = 1;
    # Deal with existing *.xml files
    o = glob.glob("".join([host_path,'*/*/mo/*/*.xml']))
    xml_count1 = len(o)
    o = glob.glob("".join([host_path,'*/fx/*/*.xml']))
    xml_count2 = len(o)
    xml_count = int(xml_count1)+int(xml_count2);
    print "".join(['** Updating ',format(xml_count,"1d"),' existing *.xml files **'])
    writeToLog(logfile,"".join(['** Updating ',format(xml_count,"1d"),' existing *.xml files **']))
    # Catch errors with system commands
    cmd = "".join(['rm -rf ',host_path,'*/*/mo_new'])
    fnull = open(os.devnull,'w')
    p = subprocess.call(cmd,stdout=fnull,shell=True)
    fnull.close()    
    cmd = "".join(['rm -rf ',host_path,'*/fx_new'])
    fnull = open(os.devnull,'w')
    p = subprocess.call(cmd,stdout=fnull,shell=True)
    fnull.close() 
    print "** Generating new *.xml files **"
    writeToLog(logfile,"** Generating new *.xml files **")
    i = 0

    # Loop through all inpaths and outfiles
    while i <= (len(outfiles)-threadCount):
        # Case where full threads are used
        threads = threadCount
        # Create queue and pool variables
        queue0 = manager0.Queue() ; pool = []
        for n in range(threads):
            p =  Process(target=xmlWrite,args=(outfiles_paths[i+n],outfiles[i+n],host_path,cdat_path,start_time,queue0))
            p.start() ; pool.append(p)
        
        # Wait for processes to terminate
        for p in pool:
            p.join()
        
        # Get data back from queue object
        inpaths = [] ; outfileNames = [] ; fileZeros = [] ; fileWarnings = [] ; fileNoReads = [] ; fileNoWrites = [] ; fileNones = [] ; errorCodes = [] ; time_since_starts = []
        while not queue0.empty():
            [inpath,outfileName,fileZero,fileWarning,fileNoRead,fileNoWrite,fileNone,errorCode,time_since_start] = queue0.get_nowait()
            inpaths.append(inpath)  
            outfileNames.append(outfileName)
            fileZeros.append(fileZero)
            fileWarnings.append(fileWarning)
            fileNoReads.append(fileNoRead)
            fileNoWrites.append(fileNoWrite)
            fileNones.append(fileNone)
            errorCodes.append(errorCode)
            time_since_starts.append(time_since_start)
        
        # Purge queue and pool object
        del(queue0,pool) ; gc.collect()
        # Sort lists by time_since_start
        tmp = zip(time_since_starts,inpaths,outfileNames,fileZeros,fileWarnings,fileNoReads,fileNoWrites,fileNones,errorCodes)
        tmp.sort() ; # sort by str value forgetting case - key=str.lower; requires str object        
        time_since_starts,inpaths,outfileNames,fileZeros,fileWarnings,fileNoReads,fileNoWrites,fileNones,errorCodes = zip(*tmp)
        # Loop through inputs and log
        for n in range(threads):
            [xmlBad1,xmlBad2,xmlBad3,xmlBad4,xmlBad5,xmlGood] = xmlLog(logfile,fileZeros[n],fileWarnings[n],fileNoWrites[n],fileNoReads[n],fileNones[n],errorCodes[n],inpaths[n],outfileNames[n],time_since_starts[n],(i+n),xmlBad1,xmlBad2,xmlBad3,xmlBad4,xmlBad5,xmlGood)
        
        # Increment counter and check for completion
        i = i + threads
        if i == len(outfiles):
            break
        
    else:
        # Case where partial threads are used
        threads = len(outfiles)-i
        # Create queue and pool variables
        queue0 = manager0.Queue() ; pool = []
        for n in range(threads):
            p =  Process(target=xmlWrite,args=(outfiles_paths[i+n],outfiles[i+n],host_path,cdat_path,start_time,queue0))
            p.start() ; pool.append(p)
        
        # Wait for processes to terminate
        for p in pool:
            p.join()
        
        # Get data back from queue object
        inpaths = [] ; outfileNames = [] ; fileZeros = [] ; fileWarnings = [] ; fileNoReads = [] ; fileNoWrites = [] ; fileNones = [] ; errorCodes = [] ; time_since_starts = []
        while not queue0.empty():
            [inpath,outfileName,fileZero,fileWarning,fileNoRead,fileNoWrite,fileNone,errorCode,time_since_start] = queue0.get_nowait()
            inpaths.append(inpath)            
            outfileNames.append(outfileName)
            fileZeros.append(fileZero)
            fileWarnings.append(fileWarning)
            fileNoReads.append(fileNoRead)
            fileNoWrites.append(fileNoWrite)
            fileNones.append(fileNone)
            errorCodes.append(errorCode)
            time_since_starts.append(time_since_start)
        
        # Purge queue and pool object
        del(queue0,pool) ; gc.collect()
        # Sort lists by time_since_start
        tmp = zip(time_since_starts,inpaths,outfileNames,fileZeros,fileWarnings,fileNoReads,fileNoWrites,fileNones,errorCodes)
        tmp.sort() ; # sort by str value forgetting case - key=str.lower; requires str object        
        time_since_starts,inpaths,outfileNames,fileZeros,fileWarnings,fileNoReads,fileNoWrites,fileNones,errorCodes = zip(*tmp)
        # Loop through inputs and log
        for n in range(threads):
            [xmlBad1,xmlBad2,xmlBad3,xmlBad4,xmlBad5,xmlGood] = xmlLog(logfile,fileZeros[n],fileWarnings[n],fileNoWrites[n],fileNoReads[n],fileNones[n],errorCodes[n],inpaths[n],outfileNames[n],time_since_starts[n],(i+n),xmlBad1,xmlBad2,xmlBad3,xmlBad4,xmlBad5,xmlGood)
        
        # Increment counter
        i = i + threads
    
    # Create master list of xmlBad and log final to file and console
    xmlBad = xmlBad1+xmlBad2+xmlBad3+xmlBad4+xmlBad5
    print "".join(['** Complete for \'data\' & \'scratch\' sources; Total outfiles: ',format(len(outfiles),"01d"),' **'])
    print "".join(['** XML file count - Good: ',format(xmlGood-1,"1d"),' **'])
    print "".join(['** XML file count - Bad/skipped: ',format(xmlBad-5,"1d"),'; bad1 (cdscan - zero files): ',format(xmlBad1-1,"1d"),'; bad2 (cdscan - warning specified): ',format(xmlBad2-1,"1d"),'; bad3 (read perms): ',format(xmlBad3-1,"1d"),'; bad4 (no outfile): ',format(xmlBad4-1,"1d"),'; bad5 (no infiles): ',format(xmlBad5-1,"1d")])
    writeToLog(logfile,"".join(['** make_cmip5_xml.py complete for \'data\' & \'scratch\' sources; Total outfiles: ',format(len(outfiles),"01d"),' **']))
    writeToLog(logfile,"".join(['** XML file count - Good: ',format(xmlGood-1,"1d"),' **']))
    writeToLog(logfile,"".join(['** XML file count - Bad/skipped: ',format(xmlBad-5,"1d"),'; bad1 (cdscan - zero files): ',format(xmlBad1-1,"1d"),'; bad2 (cdscan - warning specified): ',format(xmlBad2-1,"1d"),'; bad3 (read perms): ',format(xmlBad3-1,"1d"),'; bad4 (no outfile): ',format(xmlBad4-1,"1d"),'; bad5 (no infiles): ',format(xmlBad5-1,"1d"),' **']))

    # Once run is complete, and xmlGood > 1e5, archive old files and move new files into place
    if xmlGood > 1e5:
        time_now = datetime.datetime.now()
        time_format = time_now.strftime("%y%m%d_%H%M%S")
        # Ensure /cmip5 directory is cwd
        os.chdir(host_path)
        # Archive old files
        cmd = "".join(['_archive/7za a ',host_path,'_archive/',time_format,'_cmip5_xml.7z */*/*/*/*.xml -t7z'])
        #cmd = "".join(['_archive/7za a ',host_path,'_archive/',time_format,'_cmip5_xml.7z */*/mo/*/*.xml -t7z']) ; # Only backup old *.xml files
        args = shlex.split(cmd) ; # Create input argument of type list - shell=False requires this, shell=True tokenises (lists) and runs this
        fnull = open(os.devnull,'w')
        #fnull = open("".join([time_format,'_7za.log']),'w') ; # Debug binary being called from script
        p = subprocess.call(args,stdout=fnull,shell=False) ; # call runs in the foreground, so script will wait for termination
        fnull.close()
        # Purge old files [durack1@crunchy cmip5]$ rm -rf */*/mo
        cmd = 'rm -rf */*/mo'
        fnull = open(os.devnull,'w')
        p = subprocess.call(cmd,stdout=fnull,shell=True)
        fnull.close()
        fnull = open(os.devnull,'w')
        cmd = 'rm -rf fx/fx'
        p = subprocess.call(cmd,stdout=fnull,shell=True)
        cmd = 'rm -rf */fx' ; # Purge existing subdirs beneath $EXPERIMENT/fx
        p = subprocess.call(cmd,stdout=fnull,shell=True)
        fnull.close()    
        # Move new files into place
        cmd = 'find */*/mo_new -maxdepth 0 -exec sh -c \'mv -f `echo {}` `echo {} | sed s/mo_new/mo/`\' \;'
        fnull = open(os.devnull,'w')
        p = subprocess.call(cmd,stdout=fnull,shell=True)
        fnull.close()
        cmd = 'find fx/fx_new -maxdepth 0 -exec sh -c \'mv -f `echo {}` `echo {} | sed s/fx_new/fx/`\' \;'
        fnull = open(os.devnull,'w')
        p = subprocess.call(cmd,stdout=fnull,shell=True)
        fnull.close()
        # Wash new directories with fresh permissions
        cmd = 'chmod 755 -R */*/mo' ; # Pete G needs x to list directories
        fnull = open(os.devnull,'w')
        p = subprocess.call(cmd,stdout=fnull,shell=True)
        fnull.close()        
        cmd = 'chmod 755 -R */fx'
        fnull = open(os.devnull,'w')
        p = subprocess.call(cmd,stdout=fnull,shell=True)
        fnull.close() 
        del(time_now,cmd,fnull,p)
        gc.collect()
        #[durack1@crunchy cmip5]$ find */*/mo_new -maxdepth 0 -exec sh -c 'mv -f `echo {}` `echo {} | sed s/mo_new/mo/`' \;
        #[durack1@crunchy cmip5]$ ls -d1 */*/mo_new | sed -e 'p;s/mo_new/mo/' | xargs -n 2 mv
        # Report migration success to prompt and log
        print "".join(['** Archive and migration complete from */*/*_new to */*/*, archive file: ',host_path,'_archive/',time_format,'_cmip5_xml.7z **'])
        writeToLog(logfile,"".join(['** Archive and migration complete from */*/*_new to */*/*,\n archive file: ',host_path,'_archive/',time_format,'_cmip5_xml.7z **']))
    else:
        print "".join(['** XML count too low: ',format(xmlGood-1,"1d") ,', archival, purging and migration halted **'])
        writeToLog(logfile,"".join(['** XML count too low: ',format(xmlGood-1,"1d") ,', archival, purging and migration halted **']))
        
else:
    print "** make_cmip5_xml.py run in report mode **"
    writeToLog(logfile,"** make_cmip5_xml.py run in report mode **")
