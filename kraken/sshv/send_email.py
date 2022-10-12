import smtplib
from email.mime.text import MIMEText
from email.header import Header

class STMPEmail(object):

    def __init__(self,receivers,
                 message1 = '“Congratulations, the test passes”',
                 message2 = '“Sorry, There was a error with the test and the test exited”'):
        self.mail_host = 'smtp.exmail.qq.com'
        self.mail_user = 'github.host@feixitek.com'
        self.mail_pass = 'Githubhost1234'
        self.sender = 'github.host@feixitek.com'
        self.receivers = receivers.strip(',').split(',')
        self.receivers = receivers
        self.message1 = message1
        self.message2 = message2



    def send_succeed(self):

        message = MIMEText(self.message1, 'plain', 'utf-8')
        message['From'] = Header("发送方", 'utf-8')
        message['To'] = Header("接收方", 'utf-8')

        subject = 'The results of test'
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(self.mail_host, 25)
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(self.sender, self.receivers, message.as_string())
            smtpObj.quit()

            mess = "The message was sent successfully"
        except smtplib.SMTPException:


            mess = "Error,Message failed to send"

        return mess

    def send_fail(self):

        message = MIMEText(self.message2, 'plain', 'utf-8')
        message['From'] = Header("发送方", 'utf-8')
        message['To'] = Header("接收方", 'utf-8')

        subject = 'The results of test'
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(self.mail_host, 465)
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(self.sender, self.receivers, message.as_string())
            smtpObj.quit()

            mess = "The message was sent successfully"
        except smtplib.SMTPException:


            mess = "Error,Message failed to send"

        return mess
if __name__ == '__main__':
    t1 = STMPEmail('shiki.fu@feixitek.com').send_fail()
