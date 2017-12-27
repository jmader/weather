#---------------------------------------------------------------
#
# Usage weather.csh YYYY/MM/DD
#
# Written by Jeff Mader
#
# This is the backbone for gathering all weather and
# ancillary information.  It has been stripped out of the
# instrument processing to avoid gathering duplicate data
# (i.e. NIRSPEC and NIRC2 processing have same ancillary data.
#
# 20101214 JM  Original version
#
#---------------------------------------------------------------

import verification
import logging
from datetime import datetime
from sys import argv
import subprocess as sp
import weather_nightly as wn
import os
import skyprobe as sky
import get_dimm_data as dimm

# Default UT date is today
# Runs at 2pm, so use now()

utDate = datetime.now().strftime('%Y-%m-%d')

# Usage can have 0 or 1 additional arguments

assert len(argv) <= 2, 'Usage: weather.py [YYYY-MM-DD]'

# Parse UT date from argument list

if len(argv) == 2:
	utDate = argv[1]
	utDate.replace('/', '-')
	split = utDate.split('-')

# Verify date, will exit if verification fails

verification.verify_date(utDate)

print('weather.py started for ' + utDate)
#logger -p local2.debug "weather: weather.csh $utdate"
#set dbdate = `echo $utdate | sed 's/\//-/g'`
#set utdate = `echo $utdate | sed 's/\///g'`

# Archive directory

wxDir = '/net/koaserver/koadata7'
wxDir = './test'

print('weather.py using ' + wxDir)
#logger -p local2.debug "weather: Using $wxDir"
##---------------------------------------------------------------
## koa.koawx entry
##---------------------------------------------------------------
#add_to_db.php koawx $dbdate utdate=\'$dbdate\' 
##---------------------------------------------------------------
## Create the directory
##---------------------------------------------------------------
if not os.path.exists(wxDir):
	os.makedirs(wxDir)
##---------------------------------------------------------------
## Write to log
##---------------------------------------------------------------
print('weather.py creating wx.LOC')
#logger -p local2.debug "weather: "$wxDir"/wx.LOC created"
##---------------------------------------------------------------
## Create the LOC file
##---------------------------------------------------------------
joinSeq = (wxDir, '/wx.LOC')
locFile = ''.join(joinSeq)
now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
joinSeq = ('Started ', now)
line = ''.join(joinSeq)
with open(locFile, 'w') as fp:
	fp.write(line)
##---------------------------------------------------------------
## Write to log
##---------------------------------------------------------------
print('weather.py calling weather_nightly.py')
#logger -p local2.debug "weather: weather_nightly.php "$utdate $wxDir
#set dir = `echo $wxDir | sed 's/\/net\/koaserver2//g'`
#set dir = `echo $dir | sed 's/\/net\/koaserver//g'`
#echo $dir > $wx_dir/README

# Call weather_nightly to create nightly# subdirectories

wn.weather_nightly(utDate, wxDir)

#weather_nightly.php $utdate $wx_dir

# Get CFHT Skyprobe plot

print('weather.py calling skyprobe.py')
sky.skyprobe(utDate, wxDir)

# Get CFHT MASS/DIMM data and plots

print('weather.py calling get_dimm_data.py')
dimm.get_dimm_data(utDate, wxDir)

# Create the main html page

print('weather.py creating index.html')

joinSeq = (wxDir, '/index.html')
file = ''.join(joinSeq)
with open(file, 'w') as fp:
	fp.write('<html>\n')
	fp.write('<body>\n')
	fp.write('<title>'+utDate+' Weather Data</title>\n')
	fp.write('<p><a href="keck_weather.html">WMKO Weather Data Plots</a>\n')
	fp.write('<p><a href="keck_fwhm.html">WMKO Guide Star FWHM Plots</a>\n')
	fp.write('<p><a href="skyprobe/skyprobe.html">SkyProbe @ CFHT:: Atmospheric Attenuation</a>\n')
	fp.write('<p><a href="massdimm/massdimm.html">CFHT Seeing and Mass Profile</a>\n')
	fp.write('</html>\n')
	fp.write('</body>\n')
##---------------------------------------------------------------
## Remove the LOC file
##---------------------------------------------------------------
os.remove(locFile)
##---------------------------------------------------------------
## md5sum file
##---------------------------------------------------------------
#cd $wx_dir
#touch weather$utdate.md5sum
#foreach file (`/usr/bin/find . -type f ! -name weather$utdate.md5sum`)
#	/usr/local/bin/md5sum $file >> weather$utdate.md5sum
#end
##---------------------------------------------------------------
## koa.koawx entry
##---------------------------------------------------------------
#set numfiles = `find $wx_dir -type f | wc | awk '{print $1}'`
#add_to_db.php koawx $dbdate files=\'$numfiles\' 
#set size = `du -ks $wx_dir | awk '{print $1/1000}'`
#add_to_db.php koawx $dbdate size=\'$size\' 
##---------------------------------------------------------------
## Transfer data to NExScI
##---------------------------------------------------------------
#/kroot/archive/koaxfr/default2/koaxfr.php weather $wx_dir rsync
##---------------------------------------------------------------
## Send email to NExScI
##---------------------------------------------------------------
#set subject = "weather $utdate"
#set body = "weather data successfully transferred to koaxfr"
#set email = "koaing-newops@ipac.caltech.edu"
#echo $body | mailx -s "$subject" $email
#set date = `date -u '+%Y%m%d %H:%M:%S'`
#add_to_db.php koawx $dbdate data_sent="$date"
