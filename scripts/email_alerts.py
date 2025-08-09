import smtplib
from email.message import EmailMessage
from .config_loader import config
from scripts.logger import logger

SMTP_HOST = config("SMTP_HOST")
SMTP_PORT = int(config("SMTP_PORT", 587))
SMTP_USER = config("SMTP_USER")
SMTP_PASS = config("SMTP_PASS")
ALERT_EMAIL_TO = config("ALERT_EMAIL_TO")
ALERT_EMAIL_FROM = config("ALERT_EMAIL_FROM")

def send_email(subject: str, body: str):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = ALERT_EMAIL_FROM
        msg["To"] = ALERT_EMAIL_TO
        msg.set_content(body)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        logger.log_event(
            f"Email sent successfully to {ALERT_EMAIL_TO}",
            "INFO",
            {
                "operation": "send_email",
                "subject": subject,
                "recipient": ALERT_EMAIL_TO,
                "sender": ALERT_EMAIL_FROM,
                "body_length": len(body)
            }
        )
        
    except Exception as e:
        logger.log_event(
            f"Failed to send email: {str(e)}",
            "ERROR",
            {
                "operation": "send_email",
                "subject": subject,
                "recipient": ALERT_EMAIL_TO,
                "sender": ALERT_EMAIL_FROM,
                "smtp_host": SMTP_HOST,
                "smtp_port": SMTP_PORT,
                "error_type": type(e).__name__
            }
        )
        raise