def get_dimm_data(utDate='', dir='.'):
	'''
	Retrieve DIMM, MASS and MASSPRO data from Mauna Kea Weather Center

	@type utDate: string
	@param utDate: UT date of data to retrieve (default is current UT date)
	@type dir: string
	@param dir: Directory to write data to (default is current directory)
	'''

	import datetime
	import requests
	import re
	import os
	import verification
	import urllib.request

	# If no utDate supplied, use the current value

	if utDate == '':
		utDate = datetime.datetime.utcnow().strftime('%Y-%m-%d')

	verification.verify_date(utDate)

	utDate = utDate.replace('/', '-')
	split = utDate.split('-')
	year = split[0]
	month = split[1]
	day = split[2]
	utDate = utDate.replace('-', '')

	# Create directory

	joinSeq = (dir, '/massdimm')
	dir = ''.join(joinSeq)
	if not os.path.exists(dir):
		os.makedirs(dir)

	joinSeq = (dir, '/massdimm.html')
	writeFile = ''.join(joinSeq)
	with open(writeFile, 'w') as fp:
		fp.write('<html>\n')
		fp.write('<body>\n')
		fp.write('<title>Mass/Dimm Data</title>\n')

		# Type of data to retrieve

		files = {'dimm', 'mass', 'masspro'}

		# URL to retrieve data from

		url = 'http://mkwc.ifa.hawaii.edu/current/seeing'

		# Get data

		for file in files:

			# Construct URL

			joinSeq = (url, '/', file, '/', utDate, '.', file, '.dat')
			newUrl = ''.join(joinSeq)

			# Connect to URL

			response = requests.get(newUrl)

			# If page exists, then get data

			if response.status_code == 200:

				# Construct file to write to

				joinSeq = (dir, '/', utDate, '.mkwc.', file, '.dat')
				writeFile = ''.join(joinSeq)

				# Write data to file

				with open(writeFile, 'w') as fp2:
					fp2.write(response.text)
				fp.write('<a href="./'+os.path.basename(writeFile)+'">'+os.path.basename(writeFile)+'<p>\n')
			else:
				print('No', file, 'data from MKWC for', utDate)
#				Error to koawx

		# Get JPG plots

		plots = {
		'CFHT Weather Tower Seeing':'http://hokukea.soest.hawaii.edu/current/seeing/images/YYYYMMDD.wrf-vs-mkam.timeseries.jpg',
		'CFHT MASS Profile':' http://hokukea.soest.hawaii.edu/current/seeing/images/YYYYMMDD.massprofile.jpg',
		'CFHT DIMM Seeing Histogram':'http://hokukea.soest.hawaii.edu/current/seeing/analysis/images/dimmdailyhistogram.jpg',
		'CFHT MASS Seeing Histogram':'http://hokukea.soest.hawaii.edu/current/seeing/analysis/images/massdailyhistogram.jpg'
		}

		for key, url in plots.items():
			url = url.replace('YYYYMMDD', utDate)
			try:
				file = os.path.basename(url)
				if 'analysis' in url:
					joinSeq = (year, month, day, '.', file)
					file = ''.join(joinSeq)
				joinSeq = (dir, '/', file)
				writeFile = ''.join(joinSeq)
				urllib.request.urlretrieve(url, writeFile)
				fp.write('<a href="./'+file+'"><img src="'+file+'" width="750" title="'+file+'"><p>\n')
			except:
				print('url does not exist', url)
#				error to koawx

		fp.write('</body>\n')
		fp.write('</html>')
