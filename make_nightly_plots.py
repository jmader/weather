import configparser
from urllib.request import urlopen
import json
import time
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
from fix_html import fix_html
import holoviews as hv
hv.extension('bokeh')

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

#        file = wxDir + '/nightly' + str(i) + '/envMet.arT'
        if log_writer:
            log_writer.info('make_nightly_plots.py creating plots for nightly{}'.format(i))
#        if not os.path.exists(file):
#            if log_writer:
#                log_writer.error('make_nightly_plots.py file does not exist - {}'.format(file))

        # Query archive

        keys = []
        keys.append('k0:met:tempRaw')
        keys.append(f'k{i}:met:tempRaw')
        keys.append(f'k{i}:dcs:sec:acsTemp')
        keys.append(f'k{i}:dcs:sec:secondaryTemp')
        keys.append('k0:met:humidityRaw')
        keys.append(f'k{i}:met:humidityRaw')
        keys.append('k0:met:pressureRaw')
        keys.append('k0:met:dewpointRaw')

        # Set column header - used to swap from channel strings

        names = []
        names.append('OutsideTemp')
        names.append('InsideTemp')
        names.append('PrimaryTemp')
        names.append('SecondaryTemp')
        names.append('OutsideHumidity')
        names.append('InsideHumidity')
        names.append('Pressure')
        names.append('Dewpoint')
        
        data = []
        for key, channel in enumerate(keys):
            try:
                archData = get_archiver_data(utDate, i, channel)
                data.append(archData)
                joinSeq = (wxDir, '/nightly', str(i), '/k', str(i), '_', names[key], '.txt')
                file = ''.join(joinSeq)
                archData.to_csv(file, sep='\t')
            except:
                if log_writer:
                    log_writer.error('make_fwhm_plots.py unable read archiver data')
                continue

        # Format time data

        keysRename = dict(zip(keys, names))
     
        for key, d in enumerate(data):
            data[key]['UT'] = pd.to_datetime(d['timestamp'], format='%Y-%m-%d %H:%M:%S')
            data[key] = d.rename(index=str, columns=keysRename)

        # Create the plots

        files = ['temperature', 'humidity', 'pressure', 'dewpoint']
        columns = [names[0:4], names[4:6], names[6:7], names[7:]]
        grp = []
        grp.append(''.join(('Keck', str(i), '_Temperature')))
        grp.append(''.join(('Keck', str(i), '_Humidity')))
        grp.append(''.join(('Keck', str(i), '_Pressure')))
        grp.append(''.join(('Keck', str(i), '_DewPoint')))

        colors = ['steelblue', 'orange', 'green', 'red']
        
        curve_opts = dict(tools=['hover'])
        plot_opts = dict(height=400, width=450)

        # Offsets for the 4 plots created
        #  plot 1 = data[0:3]
        #  plot 2 = data[4:5]
        #  plot 3 = data[6:6]
        #  plot 4 = data[7:7]

        skip = [0, 4, 6, 7]

        renderer = hv.renderer('bokeh')
        for key, plot in enumerate(files):
            plt = None
            for key2, c in enumerate(columns[key]):
                index = key2 + skip[key]
                p = hv.Curve(data[index], 'UT', c, label=c)#, group=grp[key])
                c_opts = dict(color=colors[key2])
                c_opts.update(curve_opts)
                p = p.options(**c_opts)
                if not plt:
                    p = p.redim.label(OutsideTemp='Temperature (C)')
                    p = p.redim.label(OutsideHumidity='Humidity (%)')
                    p = p.redim.label(Dewpoint='Dewpoint (C)')
                    p = p.redim.label(Pressure='Pressure (mbar)')
                    p = p.redim.label(UT='Universal Time')
                    plt = p
                else: plt = plt * p
                p = None
            joinSeq = (wxDir, '/k', str(i), '_', plot)
            file = ''.join(joinSeq)
            plt.options(width=450, height=400)
            renderer.save(plt.options(**plot_opts), file)
            if log_writer:
                log_writer.info('make_nightly_plots.py file saved {}'.format(file))
            fix_html(file + '.html', log_writer)

                    
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

        if log_writer:
            log_writer.info('make_fwhm_plots.py creating fwhm plot for nightly{}'.format(i))

        # Read the file and skip if error

        try:
            channel = f'k{i}:dcs:pnt:cam0:fwhm'
            data = get_archiver_data(utDate, i, channel)
            joinSeq = (wxDir, '/nightly', str(i), '/k', str(i), '_fwhm.txt')
            file = ''.join(joinSeq)
            data.to_csv(file, sep='\t')
        except IOError as e:
            if log_writer:
                log_writer.error('make_fwhm_plots.py unable read archiver data')
            continue

        # Set column headers or default to column numbers

        keys = []
        keys.append(channel)

        files = ['fwhm']
        yLabel = ['FWHM (arcseconds)']

        # This is needed to rename labels below

        names = []
        names.append('KECK')
        columns = [names[0:]]
        keysRename = dict(zip(keys, names))
        data = data.rename(index=str, columns=keysRename)
        for n in names:
            data[n] = pd.to_numeric(data[n])

        # Format time data

        data['UT'] = pd.to_datetime(data['timestamp'], format='%Y-%m-%d %H:%M:%S')

        # Create the plots

        curve_opts = dict(tools=['hover'])
        plot_opts = dict(height=300, width=450)
        grp = []
        grp.append(''.join((str(i))))

        renderer = hv.renderer('bokeh')
        for key, plot in enumerate(files):
            p = hv.Curve(data, 'UT', 'KECK', label='KECK', group=grp[key])
            c_opts = dict(color='steelblue')
            c_opts.update(curve_opts)
            p = p.options(**c_opts)
            p = p.redim.label(KECK='FWHM (arcseconds)')
            p = p.redim.label(UT='Universal Time')
            plt = p
            joinSeq = (wxDir, '/k', str(i), '_', plot)
            file = ''.join(joinSeq)
            plt.options(width=450, height=300)
            renderer.save(plt.options(**plot_opts), file)
            if log_writer:
                log_writer.info('make_nightly_plots.py file saved {}'.format(file))
            fix_html(file + '.html', log_writer)


def get_archiver_data(utDate, telNum, channel):
    '''
    Uses the archiver API to retrieve JSON data for the
    supplied channel. Returns a pandas data frame.
    '''

    # K1ARCHIVER or K2ARCHIVER
    api = f'K{telNum}ARCHIVER'

    # times for the query
    start = f'{utDate}T00:00:00Z'
    end   = f'{utDate}T23:59:59Z'

    config = configparser.ConfigParser()
    config.read('config.live.ini')
    archiveUrl = config['API'][api]
    archiveUrl = f'{archiveUrl}pv={channel}&from={start}&to={end}'

    # Retrieve data
    data = urlopen(archiveUrl)
    data = data.read().decode('utf8')
    data = json.loads(data)

    newdata = {}
    newdata['timestamp'] = []
    newdata['timeinsecs'] = []
    newdata[channel] = []

    for entry in data:
        for d in entry['data']:
            if 'acsTemp' in channel and d['val']>100: continue
            timeString = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(d['secs']))
            mydate, mytime = timeString.split(' ')
            if mydate != utDate: continue
            hr, mn, sc = mytime.split(':')
            if int(hr) >= 18: continue
            newdata['timestamp'].append(timeString)
            newdata['timeinsecs'].append(d['secs'])
            newdata[channel].append(d['val'])

    newdata = pd.DataFrame(data=newdata)
    return newdata
