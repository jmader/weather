import os
import hashlib
import urllib.request
import json
import configparser

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

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config.read(dir_path+'/config.live.ini')
    url = config['API']['KOAAPI']

    myHash = hashlib.md5(user.encode('utf-8')).hexdigest()
    sendUrl = ''.join((url, sendUrl, '&hash=', myHash))

    if log_writer:
        log_writer.info('weather.py {}'.format(sendUrl))

    data = urllib.request.urlopen(sendUrl)
    if data == False:
        log_writer.warning('weather.py could not update koawx database table')
