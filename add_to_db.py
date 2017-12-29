import subprocess as sp
import re

def add_to_db(dbTable, utDate, field):
	'''
	Inserts or updates a database record for the supplied table

	@type dbTable: str
	@param dbTable: databaes table name
	@type utDate: str
	@param utDate: YYYY-MM-DD
	@type field: str
	@param field: field to add/update (e.g. utdate="2017-12-26")
	'''

	if not dbTable or not utDate or not field:
		print('usage: add_to_db(dbTablee, utDate, field)')
		return

	# Verify correct format (yyyy-mm-dd or yyyy/mm/dd)

	utDate = utDate.replace('/', '-')
	if not re.search('\d\d\d\d[-/]\d\d[-/]\d\d', utDate):
		print('add_to_db.py unknown date format - {}'.format(utDate))
		return

	# Construct call to add_to_db.php

	joinSeq = ('/kroot/archive/db/default/add_to_db.php ', dbTable, ' ', utDate, ' ', field)
	cmd = ''.join(joinSeq)
	proc = sp.Popen(cmd, shell=True, stdout=sp.PIPE)

