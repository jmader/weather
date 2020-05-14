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
from shutil import copyfile
import skyprobe as sky
import get_dimm_data as dimm
import hashlib
import urllib.request
import json
import update_wx_db as wxdb
import koaxfr
import configparser

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(dir_path+'/config.live.ini')
emailFrom = config['KOAXFR']['EMAILFROM']
emailError = config['KOAXFR']['EMAILERROR']

# Default UT date is today
# Runs at 2pm, so use now()

utDate = datetime.now().strftime('%Y-%m-%d')
dbUpdate = 1

# Usage can have 0 or 1 additional arguments

assert len(argv) >= 3, 'Usage: weather.py wxDir [YYYY-MM-DD] [-nodb]'

# Parse UT date from argument list

if len(argv) >= 2:
    wxDir = argv[1]
    if len(argv) == 3:
        utDate = argv[2].replace('/', '-')
    if len(argv) == 4:
        dbUpdate = 0

# Verify date, will exit if verification fails

verification.verify_date(utDate)

# Setup logging

user = os.getlogin()
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

# Archive directory

if not os.path.exists(wxDir):
    try:
        os.makedirs(wxDir)
    except:
        log_writer.error('weather.py could not create {}'.format(wxDir))
        exit()

# koa.koawx entry

sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=utdate&value=', utDate))
if dbUpdate: wxdb.updateWxDb(sendUrl, log_writer)

# No longer use all sky
sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=allsky&value=n/a'))
if dbUpdate: wxdb.updateWxDb(sendUrl, log_writer)

# Add utdate to wxDir

joinSeq = (wxDir, '/', utDate.replace('-', ''))
wxDir = ''.join(joinSeq)
if not os.path.exists(wxDir):
    try:
        os.makedirs(wxDir)
    except:
        log_writer.error('weather.py could not create {}'.format(wxDir))
        exit()

log_writer.info('weather.py using directory {}'.format(wxDir))
log_writer.info('weather.py creating wx.LOC')

# Create README

with open(wxDir+'/README', 'w') as fp:
    fp.write(wxDir)

# Create the LOC file

joinSeq = (wxDir, '/wx.LOC')
locFile = ''.join(joinSeq)
joinSeq = ('Started, see ', logFile)
line = ''.join(joinSeq)
with open(locFile, 'w') as fp:
    fp.write(line)

# Call weather_nightly to create nightly# subdirectories

log_writer.info('weather.py calling weather_nightly.py')
wn.weather_nightly(utDate, wxDir, dbUpdate, log_writer)

# Call make_nightly_plots to create weather and fwhm plots

log_writer.info('weather.py calling make_nightly_plots.py')
mn.make_nightly_plots(utDate, wxDir, log_writer)
sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=graphs&value=', datetime.utcnow().strftime('%Y%m%d+%H:%M:%S')))
if dbUpdate: wxdb.updateWxDb(sendUrl, log_writer)

# Get CFHT Skyprobe plot

log_writer.info('weather.py calling skyprobe.py')
sky.skyprobe(utDate, wxDir, log_writer)

# Get CFHT MASS/DIMM data and plots

log_writer.info('weather.py calling get_dimm_data.py')
dimm.get_dimm_data(utDate, wxDir, log_writer)


# Read template html page

lines = []
utDate2 = utDate.replace('-', '')
with open(dir_path+'/template.html', 'r') as fp:
    l = fp.read().replace('YYYY-MM-DD', utDate)
    l = l.replace('YYYYMMDD', utDate2)
    lines.append(l)

# Create the main html page

log_writer.info('weather.py creating index.html')

joinSeq = (wxDir, '/index.html')
file = ''.join(joinSeq)
with open(file, 'w') as fp:
    for l in lines:
        fp.write(l)

# Copy header files to release directory
# There are copies of these files at NExScI already
#copyfile(dir_path+'/header.css', wxDir+'/header.css')
#copyfile(dir_path+'/header.js', wxDir+'/header.js')

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
if dbUpdate: wxdb.updateWxDb(sendUrl, log_writer)

totalSize = "{0:.3f}".format(totalSize)
sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=size&value=', str(totalSize)))
if dbUpdate: wxdb.updateWxDb(sendUrl, log_writer)

# Transfer data to NExScI

log_writer.info('weather.py transferring data to NExScI')
if dbUpdate: koaxfr.koaxfr(utDate, wxDir)

sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=data_sent&value=', datetime.utcnow().strftime('%Y%m%d+%H:%M:%S')))
if dbUpdate: wxdb.updateWxDb(sendUrl, log_writer)

sendUrl = ''.join(('cmd=updateWxDb&utdate=', utDate, '&column=wx_complete&value=', datetime.utcnow().strftime('%Y%m%d+%H:%M:%S')))
if dbUpdate: wxdb.updateWxDb(sendUrl, log_writer)
log_writer.info('weather.py complete for {}'.format(utDate))

# Send log contents

subject = ' '.join(('WEATHER',utDate))
message = ''
error = 0
with open(logFile, 'r') as fp:
    for line in fp:
        if 'ERROR' in line:
            error += 1
        message = ''.join((message, line))

message = ''.join((str(error), ' errors\n\n', message))
if message:
    koaxfr.send_email(emailError, emailFrom, subject, message, log_writer)

