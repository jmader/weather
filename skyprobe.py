from datetime import datetime
import urllib.request
import os
import verification
import update_wx_db as wxdb

def skyprobe(utDate='', dir='.', log_writer=''):
    '''
    Retrieve skyprobe image from CFHT

    @type utDate: string
    @param utDate: UT date of data to retrieve (default is current UT date)
    @type dir: string
    @param dir: Directory to write data to (default is current directory)
    '''

    if log_writer:
        log_writer.info('skyprobe.py started for {}'.format(utDate))

    # If no utDate supplied, use the current value

    if utDate == '':
        utDate = datetime.datetime.utcnow().strftime('%Y%m%d')

    verification.verify_date(utDate)

    utDate = utDate.replace('/', '-')
    dbDate = utDate
    utDate = utDate.replace('-', '')

    if log_writer:
        log_writer.info('skyprobe.py gathering data from CFHT')

    # URL to copy

    url = 'http://nenue.cfht.hawaii.edu/Instruments/Elixir/skyprobe/archive/mcal_'
    joinSeq = (url, utDate, '.png')
    url = ''.join(joinSeq)

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
        if log_writer:
            log_writer.info('skyprobe.py url does not exist - {}'.format(url))
            sendUrl = ''.join(('cmd=updateWxDb&utdate=', dbDate, '&column=skyprobe&value=ERROR'))
            wxdb.updateWxDb(sendUrl, log_writer)
        return

    # Create HTML page

    if log_writer:
        log_writer.info('skyprobe.py creating skyprobe.html')

    joinSeq = (dir, '/skyprobe/skyprobe.html')
    writeFile = ''.join(joinSeq)
    with open(writeFile, 'w') as fp:
        fp.write('<html>\n')
        fp.write('<body>\n')
        fp.write('<title>CFHT SkyProbe</title>\n')
#        fp.write('<h1>CFHT SkyProbe for ' + utDate + '</h1>\n')
        fp.write('<a href="./skyprobe.png"><img src="./skyprobe.png" title="skyprobe.png"></a>\n')
        fp.write('</body>\n')
        fp.write('</html>')

    # Update koawx entry

    if log_writer:
        log_writer.info('skyprobe.py complete for {}'.format(utDate))
    sendUrl = ''.join(('cmd=updateWxDb&utdate=', dbDate, '&column=skyprobe&value=', datetime.utcnow().strftime('%Y%m%d+%H:%M:%S')))
    wxdb.updateWxDb(sendUrl, log_writer)
