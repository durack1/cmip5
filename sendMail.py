# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 03:14:45 2013

@author: durack1

"""

import os,datetime

def sendMail():
    sendmail_location = '/usr/sbin/sendmail'
    time_now = datetime.datetime.now()
    time_format = time_now.strftime("%y%m%d_%H%M%S")
    p = os.popen('%s -t' % sendmail_location, 'w')
    p.write('From: %s\n' % 'from@crunchy.com')
    p.write('To: %s\n' % 'me@pauldurack.com')
    p.write("".join(['Subject: crunchy email ',time_format,'\n']))
    p.write('\n') ; # Blank line separating headers from body
    p.write("".join(['crunchy email 1 ',time_format]))
    status = p.close()
    if status != 0:
        print 'Sendmail exit status',status


# Another variant
import datetime
from email.mime.text import MIMEText
from subprocess import Popen,PIPE

time_now = datetime.datetime.now()
time_format = time_now.strftime("%y%m%d_%H%M%S")
msg = MIMEText('The body of the email message')
msg['From'] = 'from@crunchy.com'
msg['To'] = 'me@pauldurack.com'
msg['Subject'] = "".join(['crunchy email 2 ',time_format,'\n'])
p = Popen(['/usr/sbin/sendmail','-t'],stdin=PIPE)
p.communicate(msg.as_string())