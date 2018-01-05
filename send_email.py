import smtplib
from email.mime.text import MIMEText

def send_email(toEmail, subject, message, log_writer=''):
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
	msg['From'] = 'koaadmin@keck.hawaiii.edu'

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
