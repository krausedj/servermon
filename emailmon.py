import smtplib
from typing import List

class sendemail(object):
    def __init__(self, user: str, password: str, email_to: list, subject: str, body: str):
        sent_from = user 
        to = [email_to]  

        email_text = 'From: {emailfrom}\nTo: {emailto}\nSubject: {subject}\n\n{body}'.format(emailfrom=sent_from, emailto=", ".join(to), subject=subject, body=body)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(user, password)
        server.sendmail(sent_from, to, email_text)
        server.close()
