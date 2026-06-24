import os
from utils.email_manager.base import EmailSender
from core.config import settings
from utils.email_manager.gmail_sender import GmailSMTPEmailSender
from utils.email_manager.brevo_sender import BrevoEmailSender
from utils.email_manager.aws_ses_sender import AWSESEmailSender

class EmailSenderFactory:
   @staticmethod
   def create(provider: str) -> EmailSender:
       if not provider:
           raise ValueError("EMAIL_PROVIDER is not set in the configuration or .env file.")
           
       provider = provider.lower()
       
       if provider == "gmail":
           return GmailSMTPEmailSender(
               email=settings.SENDER_EMAIL,
               app_password=settings.EMAIL_PASSWORD
           )
           
       if provider == "brevo":
           return BrevoEmailSender(api_key=settings.BREVO_API_KEY)
           
       if provider == "aws_ses":
           return AWSESEmailSender(
               access_key=settings.AWS_ACCESS_KEY,
               secret_key=settings.AWS_SECRET_KEY,
               region=settings.AWS_REGION
           )
           
       raise ValueError(f"Unknown email provider: {provider}")

def provide_email_sender() -> EmailSender:
   return EmailSenderFactory.create(settings.EMAIL_PROVIDER)