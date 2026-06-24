from utils.email_manager.base import EmailSender

class BrevoEmailSender(EmailSender):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, to: str, subject: str, template: str, context: dict) -> bool:
        # TODO: integrate Brevo SMTP / API
        print("Brevo sender not implemented yet")
        return False