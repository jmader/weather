def skyprobe(utDate='', dir='.'):
	'''
	Retrieve skyprobe image from CFHT

	@type utDate: string
	@param utDate: UT date of data to retrieve (default is current UT date)
	@type dir: string
	@param dir: Directory to write data to (default is current directory)
	'''

	import datetime
	import urllib.request
	import re
	import os

	# If no utDate supplied, use the current value

	if utDate == '':
		utDate = datetime.datetime.utcnow().strftime('%Y%m%d')

	utDate = utDate.replace('-', '')
	utDate = utDate.replace('/', '')
	assert re.search('\d\d\d\d\d\d\d\d', utDate), 'unknown utDate format'

#	system("logger -p local2.debug 'skyprobe.php: gathering CFHT Skyprobe data'")

	# URL to copy

	url = 'http://nenue.cfht.hawaii.edu/Instruments/Elixir/skyprobe/archive/mcal_'
	joinSeq = (url, utDate, '.png')
	url = ''.join(joinSeq)

	# Connect to URL

	# Create directory

	joinSeq = (dir, '/skyprobe')
	writeDir = ''.join(joinSeq)
	if not os.path.exists(writeDir):
		os.makedirs(writeDir)

	# Construct file to write to

	joinSeq = (dir, '/skyprobe/skyprobe.png')
	writeFile = ''.join(joinSeq)

	try:
		urllib.request.urlretrieve(url, writeFile)

	except:
		print('url does not exist', url)
		return

	# Create HTML page

#	system("logger -p local2.debug 'skyprobe.php: creating skyprobe.html'");
	joinSeq = (dir, '/skyprobe/skyprobe.html')
	writeFile = ''.join(joinSeq)
	with open(writeFile, 'w') as fp:
		fp.write('<html>\n')
		fp.write('<body>\n')
		fp.write('<title>CFHT SkyProbe</title>\n')
		fp.write('<h1>CFHT SkyProbe for ' + utDate + '</h1>\n')
		fp.write('<a href="./skyprobe.png"><img src="./skyprobe.png" title="skyprobe.png"></a>\n')
		fp.write('</body>\n')
		fp.write('</html>')

	# Update koawx entry

#	system("add_to_db.php koawx $dbdate skyprobe='$date'");

