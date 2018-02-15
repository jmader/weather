#---------------------------------------------------------------
#
# Gathers nightly weather, seeing and other information from
# various sources.  This information is archived in KOA for
# users to view at any time.
#
# Usage: weather.py wxDir [YYYY-MM-DD]
#
# @param wxDir: output directory location
# @type wxDir: string
# @param YYYY-MM-DD: UT date
# @type YYYY-MM-DD: string
#
# Log is wxDir/weather_utDate.log
#
# Calls:
# - weather_nightly(utDate, wxDir, log_writer)
# - make_nightly_plots(utDate, wxDir, log_writer)
# - skyprobe(utDate, wxDir, log_writer)
# - get_dimm_data(utDate, wxDir, log_writer)
#
# Written by Jeff Mader
#
#---------------------------------------------------------------

import verification
import logging as lg
from datetime import datetime
from sys import argv
import subprocess as sp
import weather_nightly as wn
import make_nightly_plots as mn
import os
import skyprobe as sky
import get_dimm_data as dimm
import hashlib
import urllib.request
import json
import update_wx_db as wxdb
import koaxfr

# Default UT date is today
# Runs at 2pm, so use now()

utDate = datetime.now().strftime('%Y-%m-%d')

# Usage can have 0 or 1 additional arguments

assert len(argv) >= 2, 'Usage: weather.py wxDir [YYYY-MM-DD]'

# Parse UT date from argument list

if len(argv) <= 3:
	wxDir = argv[1]
	if len(argv) == 3:
		utDate = argv[2]
		utDate.replace('/', '-')

# Verify date, will exit if verification fails

verification.verify_date(utDate)

# Archive directory

if not os.path.exists(wxDir):
	os.makedirs(wxDir)

user = os.getlogin()

# Setup logging

joinSeq = ('weather <', user, '>')
writerName = ''.join(joinSeq)
log_writer = lg.getLogger(writerName)
log_writer.setLevel(lg.INFO)

# Crete a file handler

joinSeq = (wxDir, '/weather_', utDate.replace('-', ''), '.log')
logFile = ''.join(joinSeq)
log_handler = lg.FileHandler(logFile)
log_handler.setLevel(lg.INFO)

# Create a logging format

formatter = lg.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
log_handler.setFormatter(formatter)

# Add handlers to the logger

log_writer.addHandler(log_handler)

log_writer.info('weather.py started for {}'.format(utDate))

# koa.koawx entry

sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=utdate&value=', utDate))
wxdb.updateWxDb(sendUrl, log_writer)

# Add utdate to wxDir

joinSeq = (wxDir, '/', utDate.replace('-', ''))
wxDir = ''.join(joinSeq)
if not os.path.exists(wxDir):
	os.makedirs(wxDir)

log_writer.info('weather.py using directory {}'.format(wxDir))
log_writer.info('weather.py creating wx.LOC')

# Create the LOC file

joinSeq = (wxDir, '/wx.LOC')
locFile = ''.join(joinSeq)
joinSeq = ('Started, see ', logFile)
line = ''.join(joinSeq)
with open(locFile, 'w') as fp:
	fp.write(line)

# Call weather_nightly to create nightly# subdirectories

log_writer.info('weather.py calling weather_nightly.py')
wn.weather_nightly(utDate, wxDir, log_writer)

# Call make_nightly_plots to create weather and fwhm plots

log_writer.info('weather.py calling make_nightly_plots.py')
mn.make_nightly_plots(utDate, wxDir, log_writer)
sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=graphs&value=', datetime.utcnow().strftime('%Y%m%d+%H:%M:%S')))
wxdb.updateWxDb(sendUrl, log_writer)

# Get CFHT Skyprobe plot

log_writer.info('weather.py calling skyprobe.py')
sky.skyprobe(utDate, wxDir, log_writer)

# Get CFHT MASS/DIMM data and plots

log_writer.info('weather.py calling get_dimm_data.py')
dimm.get_dimm_data(utDate, wxDir, log_writer)

# Create the main html page

log_writer.info('weather.py creating index.html')

joinSeq = (wxDir, '/index.html')
file = ''.join(joinSeq)
with open(file, 'w') as fp:
	fp.write('<html>\n')
	fp.write('<body>\n')
	fp.write('<title>'+utDate+' Weather Data</title>\n')
	fp.write('<p><a href="keck_weather.html">WMKO Weather Data Plots</a>\n')
	fp.write('<p><a href="keck_fwhm.html">WMKO Guide Star FWHM Plots</a>\n')
	fp.write('<p><a href="skyprobe/skyprobe.html">SkyProbe @ CFHT: Atmospheric Attenuation</a>\n')
	fp.write('<p><a href="massdimm/massdimm.html">CFHT Seeing and Mass Profile</a>\n')
	fp.write('</html>\n')
	fp.write('</body>\n')

# All done, remove LOC file

log_writer.info('weather.py removing wx.LOC')
os.remove(locFile)

# Walk through and create md5sum

totalFiles = 0
totalSize = 0
joinSeq = (wxDir, '/weather', utDate.replace('-', ''), '.md5sum')
md5sumFile = ''.join(joinSeq)
with open(md5sumFile, 'w') as fp:
	for root, dirs, files in os.walk(wxDir):
		totalFiles += len(files)
		for file in files:
			if file in md5sumFile:
				continue
			joinSeq = (root, '/', file)
			fullPath = ''.join(joinSeq)
			md = hashlib.md5(open(fullPath, 'rb').read()).hexdigest()
			joinSeq = (md, '  ', fullPath.replace(wxDir, '.'), '\n')
			md = ''.join(joinSeq)
			fp.write(md)
			totalSize += os.path.getsize(fullPath) / 1000000.0

# koa.koawx entry

sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=files&value=', str(totalFiles)))
wxdb.updateWxDb(sendUrl, log_writer)

totalSize = "{0:.3f}".format(totalSize)
sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=size&value=', str(totalSize)))
wxdb.updateWxDb(sendUrl, log_writer)

# Transfer data to NExScI

log_writer.info('weather.py transferring data to NExScI')
koaxfr.koaxfr(utDate, wxDir)

sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=data_sent&value=', datetime.utcnow().strftime('%Y%m%d+%H:%M:%S')))
wxdb.updateWxDb(sendUrl, log_writer)

sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=wx_complete&value=', datetime.utcnow().strftime('%Y%m%d+%H:%M:%S')))
wxdb.updateWxDb(sendUrl, log_writer)
log_writer.info('weather.py complete for {}'.format(utDate))
