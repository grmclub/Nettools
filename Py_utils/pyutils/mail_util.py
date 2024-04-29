# -*- coding: utf-8 -*-
import os
import sys
import string

# Import the email modules
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email import Encoders

def send_email(subject, body_text, from_email, to_emails, cc_emails=[], bcc_emails=[]):

    msg = MIMEMultipart()
    msg["From"]    = from_email
    msg["To"]      = ', '.join(to_emails)
    msg["cc"]      = ', '.join(cc_emails)
    dst_emails     = to_emails + cc_emails + bcc_emails
    msg["Subject"] = subject

    if body_text:
        msg.attach( MIMEText(body_text) )

    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(from_email, dst_emails, msg.as_string())
    except smtplib.SMTPException as err:
        raise IOError("Error: send email failed : %s " % err)
    finally:
        server.quit()

def send_email_with_attachment(subject, body_text, from_email,
                               to_emails, file_to_attach, cc_emails=[], bcc_emails=[]):
    msg = MIMEMultipart()
    msg["From"]    = from_email
    msg["To"]      = ', '.join(to_emails)
    msg["cc"]      = ', '.join(cc_emails)
    dst_emails     = to_emails + cc_emails + bcc_emails
    msg["Subject"] = subject

    if body_text:
        msg.attach( MIMEText(body_text) )

    attachment = MIMEBase('application', "octet-stream")
    try:
        with open(file_to_attach, "rb") as fh:
            data = fh.read()
        attachment.set_payload( data )
        Encoders.encode_base64(attachment)

        header = ('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file_to_attach))
        attachment.add_header(*header)
        msg.attach(attachment)

    except IOError as err:
        raise IOError("%s: Error opening attachment file %s\n %s" % \
                     (sys._getframe().f_code.co_name,file_to_attach, err))
    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(from_email, dst_emails, msg.as_string())
    except smtplib.SMTPException as err:
        raise IOError("Error: send email failed : %s " % err)
    finally:
        server.quit()

class unit_test:
    def check_simple_mail(self):
        sub = "test"
        from_mail = "xx@t.co.jp"
        to        = [from_mail]
        cc        = [from_mail]
        bcc       = ["xx@ts.com"]
        body      = " ある" + \
                    " testing"
        send_email(sub, body, from_mail,to,cc,bcc)

    def check_mail_with_attachment(self):
        sub  = "test"
        from_mail = "xx@t.co.jp,"
        to_mail   = [from_mail]
        cc   = [from_mail]
        bcc  = ["xx@ts.com"]
        body = " testing" + \
               " testing"
        attach_file = "/etc/redhat-release"
        send_email_with_attachment(sub, body, from_mail, to_mail, attach_file, cc, bcc)
        send_email_with_attachment(sub, body, from_mail, to_mail, attach_file, cc)
        send_email_with_attachment(sub, body, from_mail, to_mail, attach_file)

def main():
    try:
        test = unit_test()
        test.check_simple_mail()
        test.check_mail_with_attachment()

    except Exception, err:
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

if __name__ == "__main__":
    main()



