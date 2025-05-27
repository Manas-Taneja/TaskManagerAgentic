# ai_task_manager/email_service.py
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import markdown

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, host=None, port=None, username=None, password=None, recipient=None):
        # Get settings from environment variables if not provided
        self.host = host or os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.port = port or int(os.getenv("EMAIL_PORT", 587))
        self.username = username or os.getenv("EMAIL_USERNAME")
        self.password = password or os.getenv("EMAIL_PASSWORD")
        self.recipient = recipient or os.getenv("EMAIL_RECIPIENT")
        
        # Validate required settings
        if not all([self.host, self.port, self.username, self.password, self.recipient]):
            raise ValueError("Email settings are incomplete. Check your environment variables.")
    
    def send_daily_digest(self, digest_content: str, subject: str = None) -> bool:
        """
        Send the daily digest email.
        
        Args:
            digest_content: Markdown-formatted content for the email
            subject: Email subject (default: auto-generated with date)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not subject:
            today = datetime.now().strftime("%A, %B %d")
            subject = f"Task Manager Digest - {today}"
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.username
            msg["To"] = self.recipient
            
            # Convert markdown to HTML for better email rendering
            html_content = markdown.markdown(digest_content)
            
            # Attach both plain text and HTML versions
            plain_part = MIMEText(digest_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            msg.attach(plain_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Daily digest email sent to {self.recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False