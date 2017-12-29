from datetime import datetime
import os
import shutil
import subprocess as sp
import verification
import add_to_db as adb

def weather_nightly(utDate='', wxDir='.', log_writer=''):
	'''
	Copies /h (or /s) nightly data to archive location

	@type utDate: string
	@param utDate: UT date of data to copy (defaults to current UT date)
	@type wxDir: string
	@param wxDir: Directory to copy nightly data to (defaults to current directory)
	'''

	if utDate == '':
		utDate = datetime.datetime.utcnow().strftime('%Y-%m-%d')

	if not wxDir:
		exit

	if log_writer:
		log_writer.info('weather_nightly.py started for {}'.format(utDate))

	verification.verify_date(utDate)

	utDate = utDate.replace('/', '-')
	utDate_split = utDate.split('-')
	year = int(utDate_split[0]) - 2000
	month = utDate_split[1]
	day = utDate_split[2]

	error = 0

	for i in range(1,3):

		# Determine nightly location - /h or /s

		joinSeq = ('/h/nightly', str(i), '/', str(year), '/', month, '/', day)
		nightlyDir = ''.join(joinSeq)
#####
		nightlyDir = './nightly' + str(i)
		if not os.path.isdir(nightlyDir):
			nightlyDir.replace('/h/', '/s/')
			if not os.path.isdir(nightlyDir):
				error = 1
				if log_writer:
					log_writer.error('weather_nightly.py nightly directory not found for K{}'.format(i))
					joinSeq = ('nightly', str(i), '="ERROR"')
					field = ''.join(joinSeq)
					adb.add_to_db('koawx', utDate, field)
				continue

		joinSeq = (wxDir, '/nightly', str(i))
		wxNewDir = ''.join(joinSeq)

		# Copy the data.  Will also create the new directories.

		if log_writer:
			log_writer.info('weather_nightly.py copying nightly data from {}'.format(nightlyDir))
		shutil.copytree(nightlyDir, wxNewDir)

		# Go through and uncompress any .Z or .gz files

		for (dirpath, dirnames, filenames) in os.walk(wxNewDir):
			for file in filenames:
				cmd = ''
				if file.endswith('.gz'):
					cmd = 'gunzip'
				if file.endswith('.Z'):
					cmd = 'uncompress'
				if cmd:
					sp.run([cmd, dirpath+'/'+file])

		# Update koa.koawx entry

		joinSeq = ('nightly', str(i), '="', datetime.utcnow().strftime('%Y%m%d %H:%M:%S'), '"')
		field = ''.join(joinSeq)
		adb.add_to_db('koawx', utDate, field)

	if log_writer:
		log_writer.info('weather_nightly.py complete for {}'.format(utDate))
