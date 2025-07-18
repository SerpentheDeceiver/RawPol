import os
import smtplib
from dotenv import load_dotenv

class EmailAutomation():

    def __init__(self):
        #LOADING
        load_dotenv('.env')
        #ENV VARIABLE'S
        self.EMAIL_ID = os.getenv('EMAIL_ID')
        self.PASSWORD = os.getenv('PASSWORD')
        self.SENDER_MAIL_ID = os.getenv('SENDER_MAIL_ID')

    def emailsender(self,MESSAGE):
        #CONNECTION TO SMTPLIB SERVER
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(f"{self.EMAIL_ID}",f"{self.PASSWORD}")

            #SENDER
            connection.sendmail(from_addr=self.EMAIL_ID,
                                to_addrs=self.SENDER_MAIL_ID,
                                msg=MESSAGE.as_string())