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
            num_lines = sum(1 for line in open(file))
            data = pd.read_csv(file, skiprows=[0,2,num_lines-1], skip_blank_lines=True)
            # Replace possible bad values
            data.replace(' ***', '0.00', inplace=True)
            data.replace(-100.0000, 0.00, inplace=True)
            data.replace(999.0000, 0.00, inplace=True)
        except IOError as e:
            if log_writer:
                log_writer.error('make_nightly_plots.py unable to open file = {}'.format(file))
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

        file = wxDir + '/nightly' + str(i) + '/envFocus.arT'
        if log_writer:
            log_writer.info('make_fwhm_plots.py creating fwhm plot for nightly{}'.format(i))
        if not os.path.exists(file):
            if log_writer:
                log_writer.error('make_fwhm_plots.py file does not exist - {}'.format(file))
            continue

        # Read the file and skip if error

        try:
            num_lines = sum(1 for line in open(file))
            data = pd.read_csv(file, skiprows=[0,2,num_lines-1], skip_blank_lines=True)
            # Replace possible bad values
            data.replace(' ***', '0.00', inplace=True)
        except IOError as e:
            if log_writer:
                log_writer.error('make_fwhm_plots.py unable to open file - {}'.format(file))
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

        data.replace(['***'], [0.0], inplace=True)

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
