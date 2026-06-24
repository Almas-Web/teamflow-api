from utils.email_manager.base import EmailSender

class AWSESEmailSender(EmailSender):
    def __init__(self, access_key: str, secret_key: str, region: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region

    def send(self, to: str, subject: str, template: str, context: dict) -> bool:
        # TODO: integrate boto3 SES
        print("AWS SES sender not implemented yet")
        return False