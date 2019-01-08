from datetime import datetime, timedelta
import requests
import re
import os
import verification
import urllib.request
import update_wx_db as wxdb
import pandas as pd
from fix_html import fix_html
import holoviews as hv
hv.extension('bokeh')

def get_dimm_data(utDate='', mdir='.', log_writer=''):
    '''
    Retrieve DIMM, MASS and MASSPRO data from Mauna Kea Weather Center

    @type utDate: string
    @param utDate: UT date of data to retrieve (default is current UT date)
    @type mdir: string
    @param mdir: Directory to write data to (default is current directory)
    '''

    if log_writer:
        log_writer.info('get_dimm_data.py started for {}'.format(utDate))

    # If no utDate supplied, use the current value

    if utDate == '':
        utDate = datetime.datetime.utcnow().strftime('%Y-%m-%d')

    verification.verify_date(utDate)

    utDate = utDate.replace('/', '-')
    split = utDate.split('-')
    year = split[0]
    month = split[1]
    day = split[2]
    dbDate = utDate
    utDate = utDate.replace('-', '')

    # Create directory

#    joinSeq = (dir, '/massdimm')
#    dir = ''.join(joinSeq)
    if not os.path.exists(mdir):
        os.makedirs(mdir)

    if log_writer:
        log_writer.info('get_dimm_data.py creating massdimm.html')

    joinSeq = (mdir, '/massdimm.html')
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

        for f in files:

            # Construct URL

            joinSeq = (url, '/', f, '/', utDate, '.', f, '.dat')
            newUrl = ''.join(joinSeq)

            if log_writer:
                log_writer.info('get_dimm_data.py retrieving data from {}'.format(newUrl))

            # Connect to URL

            response = requests.get(newUrl)

            # If page exists, then get data

            if response.status_code == 200:

                # Construct file to write to

                joinSeq = (mdir, '/', utDate, '.mkwc.', f, '.dat')
                writeFile = ''.join(joinSeq)

                # Write data to file

                with open(writeFile, 'w') as fp2:
                    fp2.write(response.text)
                fp.write('<a href="./'+os.path.basename(writeFile)+'">'+os.path.basename(writeFile)+'<p>\n')
            else:
                if log_writer:
                    log_writer.error('get_dimm_data.py no {} data for {}'.format(f, utDate))

        # Get JPG plots

        plots = {
        'CFHT Weather Tower Seeing':'http://hokukea.soest.hawaii.edu/current/seeing/images/YYYYMMDD.wrf-vs-mkam.timeseries.jpg',
        'CFHT MASS Profile':' http://hokukea.soest.hawaii.edu/current/seeing/images/YYYYMMDD.massprofile.jpg',
        'CFHT DIMM Seeing Histogram':'http://hokukea.soest.hawaii.edu/current/seeing/analysis/images/dimmdailyhistogram.jpg',
        'CFHT MASS Seeing Histogram':'http://hokukea.soest.hawaii.edu/current/seeing/analysis/images/massdailyhistogram.jpg'
        }

        for key, url in plots.items():
            url = url.replace('YYYYMMDD', utDate)
            if log_writer:
                log_writer.info('get_dimm_data.py retrieving {}'.format(url))
            try:
                f = os.path.basename(url)
                if 'analysis' in url:
                    joinSeq = (year, month, day, '.', f)
                    f = ''.join(joinSeq)
                joinSeq = (mdir, '/', f)
                writeFile = ''.join(joinSeq)
                urllib.request.urlretrieve(url, writeFile)
                fp.write('<a href="./'+f+'"><img src="'+f+'" width="750" title="'+f+'"><p>\n')
            except:
                if log_writer:
                    log_writer.error('get_dimm_data.py url does not exist - {}'.format(url))
                sendUrl = ''.join(('cmd=updateWxDb&utdate=', dbDate, '&column=cfht_seeing&value=ERROR'))
                wxdb.updateWxDb(sendUrl, log_writer)

        fp.write('</body>\n')
        fp.write('</html>')

    # Create bokeh plot 

    create_bokeh_plot(utDate, mdir)

    if log_writer:
        log_writer.info('get_dimm_data.py complete for {}'.format(utDate))
    sendUrl = ''.join(('cmd=updateWxDb&utdate=', dbDate, '&column=cfht_seeing&value=', datetime.utcnow().strftime('%Y%m%d+%H:%M:%S')))
    wxdb.updateWxDb(sendUrl, log_writer)

    for n in ['mass', 'dimm', 'masspro']:
        joinSeq = (mdir, '/', utDate, '.mkwc.', n, '.dat')
        writeFile = ''.join(joinSeq)
        if not os.path.exists(writeFile):
            with open(writeFile, 'w') as fp2:
                fp2.write('No Data')

def create_bokeh_plot(utDate, mdir):
    """ Creates Bokeh plot of mass/dimm data """

#    files = {'dimm', 'mass', 'masspro'}
    files = {'dimm', 'mass'}

    renderer = hv.renderer('bokeh')

    # Column name for first 7 columns of each file
    keyNames = [0, 1, 2, 3, 4, 5, 6]
    colNames = ['year', 'month', 'day', 'hour', 'minute', 'second']

    # Set hover and point size
    curve_opts = dict(tools=['hover'], size=6)

    # Create a combined plot of all data
    plot = None
    for f in files:
        joinSeq = (mdir, '/', utDate, '.mkwc.', f, '.dat')
        fileName = ''.join((joinSeq))

        if not os.path.exists(fileName): continue

        # Update keys to add seeing column and others for masspro data
        keys = keyNames.copy()
        names = colNames.copy()
        if 'masspro' in f:
            keys += [7, 8, 9, 10, 11, 12]
            names += ['a', 'b', 'c', 'd', 'e', 'f']
        names.append('seeing')

        # Read the data and assign column names
        data = pd.read_csv(fileName, header=None, delimiter=' ', dtype=str)
        keysRename = dict(zip(keys, names))
        data = data.rename(index=str, columns=keysRename)

        # Set date column
        dateCol = pd.to_datetime(data['year']+data['month']+data['day']+' '+data['hour']+data['minute']+data['second'], format='%Y%m%d %H:%M:%S')
        dateCol += timedelta(hours=10)
        data = data.assign(date=dateCol)
        data['seeing'] = pd.to_numeric(data['seeing'])

        # Create this scatter plot
        p = hv.Scatter(data, 'date', 'seeing', label=f.upper())
        p = p.options(**curve_opts)

        # Create or update master plot
        if plot:
            plot = plot * p
        else:
            p = p.redim.label(date='Universal Time')
            p = p.redim.label(seeing='Seeing')
            plot = p

    # Save HTML if plot exits
    if plot:
        plot_opts = dict(height=400, width=800)
        joinSeq = (mdir, '/massdimm_plot')
        outFile = ''.join((joinSeq))
        renderer.save(plot.options(**plot_opts), outFile)
        fix_html(outFile + '.html')
    else: print('No plot created')
