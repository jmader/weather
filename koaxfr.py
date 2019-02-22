import os
import smtplib
from email.mime.text import MIMEText
import configparser

def koaxfr(utDate, wxDir, log_writer=''):
    """
    Transfers the contents of wxDir to NExSci and sends email notification

    @param wxDir: Directory to transfer
    @type wxDir: string
    """

    utDate = utDate.replace('-', '')

    if not os.path.isdir(wxDir):
        if log_writer:
            log_writer.error('koaxfr.py directory ({}) does not exist'.format(wxDir))
            return

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config.read(dir_path+'/config.live.ini')
    emailError = config['KOAXFR']['EMAILERROR']
    emailFrom = config['KOAXFR']['EMAILFROM']
    emailTo = config['KOAXFR']['EMAILTO']
    transferTo = config['KOAXFR']['SERVER']
    transferAcct = config['KOAXFR']['ACCOUNT']
    transferDir = config['KOAXFR']['DIR']

    xfr_to = ''.join((transferAcct, '@', transferTo, ':', transferDir))

    try:
        cmd = ''.join(('/usr/bin/rsync -avz ', wxDir, ' ', xfr_to))
        print(cmd)

        if log_writer:
            log_writer.info('koaxfr.py transferring directory ({}) to NExScI'.format(wxDir))
            log_writer.info('koaxfr.py {}'.format(cmd))

#       os.system(cmd)
        subject = ''.join(('weather ', utDate))
        message = 'weather data successfully transferred to koaxfr'
        send_email(emailTo, emailFrom, subject, message, log_writer)
    except:
        if log_writer:
            log_writer.error('koaxfr.py error transferring directory ({}) to NExScI'.format(wxDir))
        message = ''.join(('Error transferring directory to NExScI\n\n', wxDir))
        send_email(emailError, emailFrom, 'Weather transfer error', message, log_writer)


def send_email(toEmail, fromEmail, subject, message, log_writer=''):
    '''
    Sends email using input parameters

    @type toEmail: str
    @param toEmail: email recipient
    @type subject: str
    @param subject: subject of message
    @type message: str
    @param message: body of email
    '''

    # Construct email msg

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['To'] = toEmail
    msg['From'] = fromEmail

    # Send the email

    try:
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()
    except:
        if log_writer:
            log_writer.info('send_email.py failed to send email with subject "{}" to {}'.format(subject, toEmail))
        else:
            print('send_email.py failed to send email with subject "{}" to {}'.format(subject, toEmail))
