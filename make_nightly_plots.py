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

        file = wxDir + '/nightly' + str(i) + '/envMet.arT'
        if log_writer:
            log_writer.info('make_nightly_plots.py creating plots for nightly{}'.format(i))
        if not os.path.exists(file):
            if log_writer:
                log_writer.error('make_nightly_plots.py file does not exist - {}'.format(file))

        # Read the file and skip if error

        try:
            keys = []
            keys.append(' "k0:met:tempRaw"')
            keys.append(' "k'+str(i)+':met:tempRaw"')
            keys.append(' "k'+str(i)+':dcs:sec:acsTemp"')
            keys.append(' "k'+str(i)+':dcs:sec:secondaryTemp"')
            keys.append(' "k0:met:humidityRaw"')
            keys.append(' "k'+str(i)+':met:humidityRaw"')
            keys.append(' "k0:met:pressureRaw"')
            keys.append(' "k0:met:dewpointRaw"')
            data = []
            data.append(get_archiver_data(utDate, i, 'k0:met:tempRaw'))
            data.append(get_archiver_data(utDate, i, f'k{i}:met:tempRaw'))
            data.append(get_archiver_data(utDate, i, f'k{i}:dcs:sec:acsTemp'))
            data.append(get_archiver_data(utDate, i, f'k{i}:dcs:sec:secondaryTemp'))
            data.append(get_archiver_data(utDate, i, 'k0:met:humidityRaw'))
            data.append(get_archiver_data(utDate, i, f'k{i}:met:humidityRaw'))
            data.append(get_archiver_data(utDate, i, 'k0:met:pressureRaw'))
            data.append(get_archiver_data(utDate, i, 'k0:met:dewpointRaw'))
#            num_lines = sum(1 for line in open(file))
#            data = pd.read_csv(file, skiprows=[0,2,num_lines-1], skip_blank_lines=True)
#            # Replace possible bad values
#            data.replace(' ***', '0.00', inplace=True)
#            data.replace(-100.0000, 0.00, inplace=True)
#            data.replace(999.0000, 0.00, inplace=True)
#        except IOError as e:
        except:
            if log_writer:
#                log_writer.error('make_nightly_plots.py unable to open file = {}'.format(file))
                log_writer.error('make_fwhm_plots.py unable read archiver data')
            continue

        # Set column headers or default to column numbers

        keys = []
        if 'UNIXDate' in data.keys():
            hst_keys = ['HSTdate', 'HSTtime']
            keys.append(' "k0:met:tempRaw"')
            keys.append(' "k'+str(i)+':met:tempRaw"')
            keys.append(' "k'+str(i)+':dcs:sec:acsTemp"')
            keys.append(' "k'+str(i)+':dcs:sec:secondaryTemp"')
            keys.append(' "k0:met:humidityRaw"')
            keys.append(' "k'+str(i)+':met:humidityRaw"')
            keys.append(' "k0:met:pressureRaw"')
            keys.append(' "k0:met:dewpointRaw"')
        else:
            hst_keys = [2, 3]
            keys.append(10)
            keys.append(18)
            keys.append(13)
            keys.append(14)
            keys.append(8)
            keys.append(20)
            keys.append(22)
            keys.append(5)

        names = []
        names.append('OutsideTemp')
        names.append('InsideTemp')
        names.append('PrimaryTemp')
        names.append('SecondaryTemp')
        names.append('OutsideHumidity')
        names.append('InsideHumidity')
        names.append('Pressure')
        names.append('Dewpoint')
        
        # Format time data

        keysRename = dict(zip(keys, names))
        data = data.rename(index=str, columns=keysRename)
        for n in names:
            data[n] = pd.to_numeric(data[n])
     
        data[hst_keys[1]] = pd.to_datetime(data[hst_keys[0]]+' '+data[hst_keys[1]], format=' %d-%b-%Y %H:%M:%S.%f')
        data[hst_keys[1]] += timedelta(hours=10)

        # Find entries between 03 and 17 hours UT

#        limits = pd.DataFrame({'year':[year, year], 'month':[month, month], 'day':[day, day], 'hour':[3, 17]})
#        limits = pd.to_datetime(limits)
#        test = pd.to_datetime(data[hst_keys[1]], format=' %d-%b-%Y %H:%M:%S.%f').between(limits[0], limits[1])

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

        renderer = hv.renderer('bokeh')
        for key, plot in enumerate(files):
            plt = None
            for key2, c in enumerate(columns[key]):
                p = hv.Curve(data, hst_keys[1], c, label=c)#, group=grp[key])
                c_opts = dict(color=colors[key2])
                c_opts.update(curve_opts)
                p = p.options(**c_opts)
                if not plt:
                    p  = p.redim.label(OutsideTemp='Temperature (C)')
                    p  = p.redim.label(OutsideHumidity='Humidity (%)')
                    p  = p.redim.label(Dewpoint='Dewpoint (C)')
                    p  = p.redim.label(Pressure='Pressure (mbar)')
                    p  = p.redim.label(HSTtime='Universal Time')
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

#        file = wxDir + '/nightly' + str(i) + '/envFocus.arT'
        if log_writer:
            log_writer.info('make_fwhm_plots.py creating fwhm plot for nightly{}'.format(i))
#        if not os.path.exists(file):
#            if log_writer:
#                log_writer.error('make_fwhm_plots.py file does not exist - {}'.format(file))
#            continue

        # Read the file and skip if error

        try:
            data = get_archiver_data(utDate, i, f'k{i}:dcs:pnt:cam0:fwhm')
#            num_lines = sum(1 for line in open(file))
#            data = pd.read_csv(file, skiprows=[0,2,num_lines-1], skip_blank_lines=True)
#            # Replace possible bad values
#            data.replace(' ***', '0.00', inplace=True)
        except IOError as e:
            if log_writer:
#                log_writer.error('make_fwhm_plots.py unable to open file - {}'.format(file))
                log_writer.error('make_fwhm_plots.py unable read archiver data')
            continue

        # Set column headers or default to column numbers

        keys = []
        if 'UNIXDate' in data.keys():
            hst_keys = ['HSTdate', 'HSTtime']
            keys.append(' "k'+str(i)+':dcs:pnt:cam0:fwhm"')
        else:
            hst_keys = [2, 3]
            keys.append(26)

        files = ['fwhm']
        yLabel = ['FWHM (arcseconds)']

        # Remove *** values

    #    data.replace(['***'], [0.0], inplace=True)

        names = []
        names.append('KECK')
        columns = [names[0:]]
        
        # Format time data

        keysRename = dict(zip(keys, names))
        data = data.rename(index=str, columns=keysRename)
        for n in names:
            data[n] = pd.to_numeric(data[n])
        # Format time data

        data[hst_keys[1]] = pd.to_datetime(data[hst_keys[0]]+' '+data[hst_keys[1]], format=' %d-%b-%Y %H:%M:%S.%f')
        data[hst_keys[1]] += timedelta(hours=10)

        # Create the plots

        curve_opts = dict(tools=['hover'])
        plot_opts = dict(height=300, width=450)
        grp = []
        grp.append(''.join((str(i))))

        renderer = hv.renderer('bokeh')
        for key, plot in enumerate(files):
            print(key, plot)
            for key2, c in enumerate(columns[key]):
                p = hv.Curve(data, hst_keys[1], c, label=c, group=grp[key])
                c_opts = dict(color='steelblue')
                c_opts.update(curve_opts)
                p = p.options(**c_opts)
                if key2 == 0:
                    p  = p.redim.label(KECK='FWHM (arcseconds)')
                    p  = p.redim.label(HSTtime='Universal Time')
                    plt = p
                else: plt = plt * p
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
    supplied channel.

    [{'meta': {'name': 'k1:met:tempRaw', 'PREC': '2'},
      'data': [{'secs': 1587686399, 'val': 4.4, 'nanos': 568229777, 'severity': 0, 'status': 0},
               {'secs': 1587686402, 'val': 4.5, 'nanos': 601184824, 'severity': 0, 'status': 0},
               {'secs': 1587686405, 'val': 4.4, 'nanos': 620859534, 'severity': 0, 'status': 0},
               {'secs': 1587686408, 'val': 4.5, 'nanos': 642535755, 'severity': 0, 'status': 0},
               {'secs': 1587686411, 'val': 4.4, 'nanos': 563372592, 'severity': 0, 'status': 0},
               {'secs': 1587686414, 'val': 4.5, 'nanos': 594924652, 'severity': 0, 'status': 0}
              ]
    ]
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

    newdata = []

    for entry in data:
        for d in entry['data']:
            timeString = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(d['secs']))
            mydate, mytime = timeString.split(' ')
            if mydate != utDate: continue
            datadict = {}
            datadict['timestamp'] = timeString
            datadict['secs'] = d['secs']
            datadict['value'] = d['val']
            newdata.append(datadict)

    return newdata
