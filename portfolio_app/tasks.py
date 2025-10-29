"""
Celery tasks for portfolio_app.
"""

from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from smtplib import SMTPException
import logging

logger = logging.getLogger(__name__)


@shared_task
def test_celery():
    """
    Simple test task to verify Celery is working.
    """
    return "Celery is working!"


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_contact_email(self, name, email, subject, message):
    """
    Celery task to send contact form email asynchronously.
    
    Args:
        name (str): Sender's name
        email (str): Sender's email
        subject (str): Email subject
        message (str): Email message content
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Prepare email content
        full_message = f"""
        New Query-Contact Submission on your website- "www.iharpreet.com":

        Name: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message}
        """

        # Check if email password is configured
        if not settings.EMAIL_HOST_PASSWORD:
            logger.error('Email configuration error: EMAIL_HOST_PASSWORD not set.')
            return False

        # Send email notification to site owner
        email_message = EmailMessage(
            subject=f"{subject}-[Contact Form]",
            body=full_message,
            from_email='From Portfolio <talkwithharpreet@gmail.com>',
            to=['talkwithharpreet@gmail.com'],
            reply_to=[email],  # Allow direct reply to visitor
        )
        email_message.send(fail_silently=False)
        
        logger.info(f'Contact email sent successfully from {email}')
        return True

    except (SMTPException, Exception) as e:
        logger.error(f'Failed to send contact email: {str(e)}')
        
        # Retry the task if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(f'Retrying email send (attempt {self.request.retries + 1}/{self.max_retries})')
            raise self.retry(exc=e)
        else:
            logger.error(f'Max retries exceeded for email send from {email}')
            return False


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_admin_otp_email(self, user_email, otp_code):
    """
    Celery task to send admin OTP email asynchronously.
    
    Args:
        user_email (str): User's email address
        otp_code (str): OTP code to send
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'Your Admin Panel OTP'
        message = f'Your OTP for admin login is: {otp_code}'
        
        # Check if email password is configured
        if not settings.EMAIL_HOST_PASSWORD:
            logger.error('Email configuration error: EMAIL_HOST_PASSWORD not set.')
            return False

        # Send OTP email
        email_message = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        email_message.send(fail_silently=False)
        
        logger.info(f'Admin OTP email sent successfully to {user_email}')
        return True

    except (SMTPException, Exception) as e:
        logger.error(f'Failed to send admin OTP email: {str(e)}')
        
        # Retry the task if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(f'Retrying OTP email send (attempt {self.request.retries + 1}/{self.max_retries})')
            raise self.retry(exc=e)
        else:
            logger.error(f'Max retries exceeded for OTP email send to {user_email}')
            return False


