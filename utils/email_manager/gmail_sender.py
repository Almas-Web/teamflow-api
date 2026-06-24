import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from utils.email_manager.base import EmailSender

env = Environment(loader=FileSystemLoader("templates"))

class GmailSMTPEmailSender(EmailSender):
   def __init__(self, email: str, app_password: str):
       self.email = email
       self.password = app_password

   def send(self, to: str, subject: str, template: str, context: dict) -> bool:
       try:
           html = env.get_template(template).render(context)
           msg = MIMEMultipart("alternative")
           msg["Subject"] = subject
           msg["From"] = self.email
           msg["To"] = to
           msg.attach(MIMEText(html, "html"))
           
           server = smtplib.SMTP("smtp.gmail.com", 587)
           server.starttls()
           server.login(self.email, self.password)
           server.sendmail(self.email, to, msg.as_string())
           server.quit()
           return True
       except Exception as e:
           print(f"Gmail SMTP error: {e}")
           return False