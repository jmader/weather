import os
import hashlib
import urllib.request
import json

def updateWxDb(sendUrl, log_writer=''):
	"""
	Sends command to update KOA data

	@param sendUrl: command and field to update
	@type sendUrl: string
	@param log_writer: logger
	@type log_writer: logging
	"""

	user = os.getlogin()

	# Database access URL

	url = 'https://www.keck.hawaii.edu/software/db_api/koa.php?'

	myHash = hashlib.md5(user.encode('utf-8')).hexdigest()
	myHash = hashlib.md5(b'koaadmin').hexdigest()
	sendUrl = ''.join((url, sendUrl, '&hash=', myHash))

	if log_writer:
		log_writer.info('weather.py {}'.format(sendUrl))

	data = urllib.request.urlopen(sendUrl)
	data = data.read().decode('utf8')       # Convert from byte to ascii
	data = json.loads(data)                 # Convert to Python list
	print(data)