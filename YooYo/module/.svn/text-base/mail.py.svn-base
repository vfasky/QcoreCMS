#coding=utf-8
from sae.mail import EmailMessage

class sae:

    smtp = False

    @staticmethod
    def setSMTP(smtp):
        sae.smtp = smtp

    @staticmethod
    def send(kwargs):
        m = EmailMessage()
        m.to = kwargs['to']
        m.subject = kwargs['title']
        m.html = kwargs['content']
        m.smtp = sae.smtp
        m.send()
