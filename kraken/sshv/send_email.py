import smtplib
from email.mime.text import MIMEText
from email.header import Header

class STMPEmail(object):

    def __init__(self,receivers,
                 message1 = '“Congratulations, the test passes”',
                 message2 = '“Sorry, there was a error with the test and the test exited”'):
        self.mail_host = 'smtp.exmail.qq.com'
        self.mail_user = 'github.host@feixitek.com'
        self.mail_pass = 'Githubhost1234'
        self.sender = 'github.host@feixitek.com'
        self.receivers = receivers
        self.message1 = message1
        self.message2 = message2


    def connect_stmp(self):
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(self.mail_host, 25)
        except:
            print("Failed to connect smtp server!")
            return False

        try:
            smtpObj.login(self.mail_user, self.mail_pass)
        except:
            print("User or password is wrong")
            return False

        return smtpObj





    def send_succeed(self):
        smtpObj = self.connect_stmp()
        message = MIMEText(self.message1, 'plain', 'utf-8')
        message['From'] = Header("VersaTST", 'utf-8')
        message['To'] = Header("接收方", 'utf-8')

        subject = 'The test of VersaTST'
        message['Subject'] = Header(subject, 'utf-8')
        try:
          smtpObj.sendmail(self.sender, self.receivers, message.as_string())
        except smtplib.SMTPSenderRefused:
            print('mail from address must be same as authorization user')
        smtpObj.quit()


    def send_fail(self):
        smtpObj = self.connect_stmp()
        message = MIMEText(self.message2, 'plain', 'utf-8')
        message['From'] = Header("VersaTST", 'utf-8')

        message['To'] = ','.join(self.receivers)

        subject = 'The test of VersaTST'
        message['Subject'] = Header(subject, 'utf-8')
        try:
          smtpObj.sendmail(self.sender, self.receivers, message.as_string())
        except smtplib.SMTPSenderRefused:
            print('mail from address must be same as authorization user')
        smtpObj.quit()
