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

	# If no utDate supplied, use the current value

	if utDate == '':
		utDate = datetime.datetime.utcnow().strftime('%Y%m%d')

	utDate = utDate.replace('-', '')
	utDate = utDate.replace('/', '')

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

			with open(writeFile, 'w') as fp:
				fp.write(response.text)
		else:
			print('No', file, 'data from MKWC for', utDate)
