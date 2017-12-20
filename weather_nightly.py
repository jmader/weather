from datetime
import os
import shutil
import re

def weather_nightly(utDate='', wxDir='.'):
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

	utDate = utDate.replace('/', '-')
	assert re.search('\d\d\d\d[-/]\d\d[-/]\d\d', utDate), 'unknown date format'

	utDate_split = utDate.split('-')
	year = int(utDate_split[0]) - 2000
	month = utDate_split[1]
	day = utDate_split[2]

	for i in range(1,3):
		dir = wxDir + '/nightly' + str(i)

#		system("logger -p local2.debug 'weather_nightly.php: weather_nightly.php $utdate $wx_dir'");

		# Determine nightly location - /h or /s

		nightlyDir = '/h/nightly' + str(i) + '/' + str(year) + '/' + month + '/' + day
		nightlyDir = './nightly' + str(i)
		if not os.path.isdir(nightlyDir):
			nightlyDir.replace('/h/', '/s/')
			if not os.path.isdir(nightlyDir):
#				logger
				exit
		wxNewDir = wxDir + '/nightly' + str(i)
#		system("logger -p local2.debug 'weather_nightly.php: Keck nightly$nightly directory is $nightlyDir'");

		# Copy the data.  Will also create the new directories.

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

#	system("add_to_db.php koawx $dbdate nightly$nightly='$date'");
