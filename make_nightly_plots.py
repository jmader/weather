import matplotlib as mpl
mpl.use('Agg')
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md

def make_nightly_plots(utDate, wxDir, log_writer=''):
	'''
	Create plots of nightly weather and FWHM data

	@type wxDir: string
	@param wxDir: directory to nightly data
	'''

	if not wxDir or not os.path.exists(wxDir):
		if log_writer:
			log_writer.error('make_nightly_plots.py wxDir does not exist - {}'.format(wxDir))
		return

	if log_writer:
		log_writer.info('make_nightly_plots.py calling make_weather_plots')
	make_weather_plots(utDate, wxDir, log_writer)
	if log_writer:
		log_writer.info('make_nightly_plots.py calling make_fwhm_plots')
	make_fwhm_plots(utDate, wxDir, log_writer)

def make_weather_plots(utDate, wxDir, log_writer=''):
	'''
	Create plots of nightly weather from envMet.arT

	@type wxDir: string
	@param wxDir: directory to nightly data
	'''

	split = utDate.split('-')
	year = split[0]
	month = split[1]
	day = split[2]

	# For each nightly directory

	for i in range(1,3):

		# Nightly met file path

		file = wxDir + '/nightly' + str(i) + '/envMet.arT'
		if log_writer:
			log_writer.info('make_nightly_plots.py creating plots for nightly{}'.format(i))
		if not os.path.exists(file):
			if log_writer:
				log_writer.error('make_nightly_plots.py file does not exist - {}'.format(file))
		# Read the file and skip if error

		try:
			data = pd.read_csv(file, skiprows=[0,2])
		except IOError as e:
			if log_writer:
				log_writer.error('make_nightly_plots.py unable to open file = {}'.format(file))
			continue

		# Set column headers or default to column numbers

		keys = []
		if 'UNIXDate' in data.keys():
			hst_keys = ['HSTdate', 'HSTtime']
			keys.append([
				' "k0:met:tempRaw"', 
				' "k'+str(i)+':met:tempRaw"', 
				' "k'+str(i)+':dcs:sec:acsTemp"', 
				' "k'+str(i)+':dcs:sec:secondaryTemp"'
				])
			keys.append([' "k0:met:humidityRaw"', ' "k'+str(i)+':met:humidityRaw"'])
			keys.append([' "k0:met:dewpointRaw"'])
			keys.append([' "k0:met:pressureRaw"'])
		else:
			hst_keys = [2, 3]
			keys.append([10, 18, 13, 14])
			keys.append([8, 20])
			keys.append([5])
			keys.append([22])

		legend = []
		legend.append([
			'Outside Temperature', 
			'K'+str(i)+' Dome Temperature', 
			'K'+str(i)+' Primary Temperature', 
			'K'+str(i)+' Secondary Temperature'
			])
		legend.append([
			'Outside Humidity', 
			'K'+str(i)+' Humidity'
			])
		legend.append([''])
		legend.append([''])

		files = ['temperature.png', 'humidity.png', 'dewpoint.png', 'pressure.png']
		yLabel = ['Temperature (C)', 'Humidity (%)', 'Dewpoint (C)', 'Pressure (mb)']

		# Format time data

		data[hst_keys[1]] = pd.to_datetime(data[hst_keys[0]]+' '+data[hst_keys[1]], format=' %d-%b-%Y %H:%M:%S.%f')
		data[hst_keys[1]] += timedelta(hours=10)

		# Find entries between 03 and 17 hours UT

		limits = pd.DataFrame({'year':[year, year], 'month':[month, month], 'day':[day, day], 'hour':[3, 17]})
		limits = pd.to_datetime(limits)
		test = pd.to_datetime(data[hst_keys[1]], format=' %d-%b-%Y %H:%M:%S.%f').between(limits[0], limits[1])

		# Create the plots

		for num, columns in enumerate(keys):
			plt.clf()
			for key, value in enumerate(columns):
				xData = data[hst_keys[1]].index[test]
				yData = data[value].index[test]
				newData = np.array([data[hst_keys[1]][xData], data[value][yData]])
				plt.plot(newData[0], newData[1], label=legend[num][key])

			ax = plt.gca()
			xfmt = md.DateFormatter('%H:%M')
			ax.xaxis.set_major_formatter(xfmt)
			plt.xlabel('Time')
			plt.ylabel(yLabel[num])
			plt.title(utDate)
			if len(columns) > 1:
				plt.legend(fontsize=6)
			joinSeq = (wxDir, '/k', str(i), '_', files[num])
			file = ''.join(joinSeq)
			plt.savefig(file)
			if log_writer:
				log_writer.info('make_nightly_plots.py {} created'.format(file))

	# Create the HTML page

	joinSeq = (wxDir, '/keck_weather.html')
	file = ''.join(joinSeq)
	if log_writer:
		log_writer.info('make_nightly_plots.py creating {}'.format(file))
	images = ['kN_temperature.png', 'kN_humidity.png', 'kN_dewpoint.png', 'kN_pressure.png']
	with open(file, 'w') as fp:
		fp.write('<html>\n')
		fp.write('<body>\n')
		fp.write('<title>'+utDate+' Keck Weather Data</title>\n')
		fp.write('<h1>Keck 1</h1>\n')
		fp.write('<table><tr>')
		joinSeq = (wxDir, '/k1_temperature.png')
		image = ''.join(joinSeq)
		if os.path.exists(image):
			fp.write('<td><a href="k1_temperature.png"><img src="k1_temperature.png"></a></td>')
		joinSeq = (wxDir, '/k1_humidity.png')
		image = ''.join(joinSeq)
		if os.path.exists(image):
			fp.write('<td><a href="k1_humidity.png"><img src="k1_humidity.png"></a></td>')
		fp.write('</tr></table>\n')
		fp.write('<h1>Keck 2</h1>\n')
		fp.write('<table><tr>')
		joinSeq = (wxDir, '/k2_temperature.png')
		image = ''.join(joinSeq)
		if os.path.exists(image):
			fp.write('<td><a href="k2_temperature.png"><img src="k2_temperature.png"></a></td>')
		joinSeq = (wxDir, '/k2_humidity.png')
		image = ''.join(joinSeq)
		if os.path.exists(image):
			fp.write('<td><a href="k2_humidity.png"><img src="k2_humidity.png"></a></td>')
		fp.write('</tr></table>\n')
		fp.write('<table><tr>')
		joinSeq = (wxDir, '/k1_dewpoint.png')
		image = ''.join(joinSeq)
		if os.path.exists(image):
			fp.write('<td><a href="k1_dewpoint.png"><img src="k1_dewpoint.png"></a></td>')
		else:
			joinSeq = (wxDir, '/k2_dewpoint.png')
			image = ''.join(joinSeq)
			if os.path.exists(image):
				fp.write('<td><a href="k2_dewpoint.png"><img src="k2_dewpoint.png"></a></td>')
		joinSeq = (wxDir, '/k1_pressure.png')
		image = ''.join(joinSeq)
		if os.path.exists(image):
			fp.write('<td><a href="k1_pressure.png"><img src="k1_pressure.png"></a></td>')
		else:
			joinSeq = (wxDir, '/k2_pressure.png')
			image = ''.join(joinSeq)
			if os.path.exists(image):
				fp.write('<td><a href="k2_pressure.png"><img src="k2_pressure.png"></a></td>')
		fp.write('</tr></table>\n')

		fp.write('</html>\n')
		fp.write('</body>\n')

def make_fwhm_plots(utDate, wxDir, log_writer=''):
	'''
	Create plots of nightly weather from envFocus.arT

	@type wxDir: string
	@param wxDir: directory to nightly data
	'''

	split = utDate.split('-')
	year = split[0]
	month = split[1]
	day = split[2]

	# For each nightly directory

	for i in range(1,3):

		# Nightly focus file path

		file = wxDir + '/nightly' + str(i) + '/envFocus.arT'
		if log_writer:
			log_writer.info('make_fwhm_plots.py creating fwhm plot for nightly{}'.format(i))
		if not os.path.exists(file):
			if log_writer:
				log_writer.error('make_fwhm_plots.py file does not exist - {}'.format(file))
			continue

		# Read the file and skip if error

		try:
			data = pd.read_csv(file, skiprows=[0,2])
		except IOError as e:
			if log_writer:
				log_writer.error('make_fwhm_plots.py unable to open file - {}'.format(file))
			continue

		# Set column headers or default to column numbers

		keys = []
		if 'UNIXDate' in data.keys():
			hst_keys = ['HSTdate', 'HSTtime']
			keys.append([' "k'+str(i)+':dcs:pnt:cam0:fwhm"'])
		else:
			hst_keys = [2, 3]
			keys.append([26])

		files = ['fwhm.png']
		yLabel = ['FWHM (arcseconds)']

		# Remove *** values

		data.replace(['***'], [0.0], inplace=True)

		# Format time data

		data[hst_keys[1]] = pd.to_datetime(data[hst_keys[0]]+' '+data[hst_keys[1]], format=' %d-%b-%Y %H:%M:%S.%f')
		data[hst_keys[1]] += timedelta(hours=10)

		# Find entries between 03 and 17 hours UT

		limits = pd.DataFrame({'year':[year, year], 'month':[month, month], 'day':[day, day], 'hour':[3, 17]})
		limits = pd.to_datetime(limits)
		test = pd.to_datetime(data[hst_keys[1]], format=' %d-%b-%Y %H:%M:%S.%f').between(limits[0], limits[1])

		# Create the plots

		for num, columns in enumerate(keys):
			plt.clf()
			for key, value in enumerate(columns):
				xData = data[hst_keys[1]].index[test]
				yData = data[value].index[test]
				newData = np.array([data[hst_keys[1]][xData], data[value][yData]])
				# Since there were *** values, need to use list to reset to float
				plt.plot(newData[0], list(newData[1]))

			ax = plt.gca()
			xfmt = md.DateFormatter('%H:%M')
			ax.xaxis.set_major_formatter(xfmt)
			plt.xlabel('Time')
			plt.ylabel(yLabel[num])
			plt.title(utDate)
			joinSeq = (wxDir, '/k', str(i), '_', files[num])
			file = ''.join(joinSeq)
			plt.savefig(file)
			if log_writer:
				log_writer.info('make_fwhm_plots.py {} created'.format(file))

	# Create the HTML page

	joinSeq = (wxDir, '/keck_fwhm.html')
	file = ''.join(joinSeq)
	if log_writer:
		log_writer.info('make_fwhm_plots.py creating {}'.format(file))
	images = ['kN_fwhm.png']
	with open(file, 'w') as fp:
		fp.write('<html>\n')
		fp.write('<body>\n')
		fp.write('<title>'+utDate+' Keck Weather Data</title>\n')
		fp.write('<h1>Keck 1</h1>\n')
		joinSeq = (wxDir, '/k1_fwhm.png')
		image = ''.join(joinSeq)
		if os.path.exists(image):
			fp.write('<a href="k1_fwhm.png"><img src="k1_fwhm.png"></a>')
		fp.write('<h1>Keck 2</h1>\n')
		joinSeq = (wxDir, '/k2_fwhm.png')
		image = ''.join(joinSeq)
		if os.path.exists(image):
			fp.write('<a href="k2_fwhm.png"><img src="k2_fwhm.png"></a>')
		fp.write('</html>\n')
		fp.write('</body>\n')
