"""Email utilities for sending processed data."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional


class EmailSender:
    """Handles sending emails with attachments."""

    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, to_email: str, subject: str, body: str,
                   attachment_data: Optional[bytes] = None,
                   attachment_filename: Optional[str] = None,
                   from_email: Optional[str] = None,
                   password: Optional[str] = None) -> bool:
        """
        Send email with optional attachment.

        Note: For Gmail, you need to enable "Less secure app access" or use App Passwords.
        For production, use proper email service providers.
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email or os.getenv('EMAIL_FROM', 'noreply@example.com')
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Add attachment if provided
            if attachment_data and attachment_filename:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
                msg.attach(part)

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()

            # Use environment variables or provided credentials
            email_user = from_email or os.getenv('EMAIL_USER')
            email_pass = password or os.getenv('EMAIL_PASS')

            if email_user and email_pass:
                server.login(email_user, email_pass)

            server.sendmail(msg['From'], to_email, msg.as_string())
            server.quit()

            return True

        except Exception as e:
            print(f"Email sending failed: {e}")
            return False