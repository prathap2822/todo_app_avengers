from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from secretkey import PASSWORD, SENDER


class Mailer():
    def __init__(self) -> None:
        self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login(SENDER, PASSWORD)

    def message(self, subject="Todo App Notification", text=""):

        self.msg = MIMEMultipart()
        self.msg['Subject'] = subject
        self.msg.attach(MIMEText(text))

        return self.msg
    def send(self, to):
        self.smtp.sendmail(from_addr="avengerstodo@gmail.com", to_addrs=to, msg=self.msg.as_string())

    def close(self):
        self.smtp.close()