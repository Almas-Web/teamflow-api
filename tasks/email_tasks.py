from worker import celery_app
from utils.email_manager.manager import provide_email_sender

@celery_app.task
def send_email_task(to: str, subject: str, template: str, context: dict):
    
    try:
    
        sender = provide_email_sender()
      
        success = sender.send(to=to, subject=subject, template=template, context=context)
        
        if success:
            return f"Email successfully sent to {to}"
        else:
            return f"Failed to send email to {to}"
            
    except Exception as e:
        
        return f"Error occurred: {str(e)}"