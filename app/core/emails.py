import logging
import json
import requests
from fastapi import HTTPException, status
from .config import settings
from ..models import User
from .logs import create_logger

logger = create_logger(__name__, logging.ERROR)


class EmailServices:
    """ Handles mail services including functions to send emails and generating html templates for each email."""

    @staticmethod
    def send_email_with_brevo(recipient: str, subject: str, body: str) -> None:
        """
        Sends an email via the BREVO API.

        Args:
            recipient (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The HTML content of the email body.

        Raises:
            HTTPException: If the email fails to send or if there is an error with the request, an HTTP 400 exception is raised.
        """

        # BREVO email sending url
        url = "https://api.brevo.com/v3/smtp/email"

        # Define the payload
        payload = json.dumps(
            {
                "sender": {"name": "VMS Team", "email": settings.BREVO_EMAIL},
                "to": [{"email": recipient}],
                "subject": subject,
                "htmlContent": body  # Use htmlContent for HTML emails
            }
        )

        # Define headers
        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        }

        # Make the POST request
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code != status.HTTP_201_CREATED:
            logger.error(response.text)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error sending email to {recipient}"
            )

    @staticmethod
    def generate_account_removal_request_email_body(user: User):
        """
        Generates an HTML string to notify the user that a request has been received to delete their account.

        Args:
            user (User): The name of the user to personalize the notification.

        Returns:
            str: A formatted HTML string.
        """
        user_name = user.name if user.name else user.email
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eaeaea; padding: 20px; 
                border-radius: 8px; background-color: #f9f9f9;">
                    <h2 style="color: #333;">Account Removal Request Received</h2>
                    <p>Hello {user_name},</p>
                    <p>We have received your request to remove your account from our platform. Please note the following:</p>
                    <ol>
                        <li>
                            <strong>Step 1: Account Deactivation</strong><br>
                            Your account will first be deactivated. This means you will no longer have access to the platform, 
                            but your data will remain intact in case you decide to reactivate your account within the next 
                            <strong>90 days</strong>. During this period, your personal data will be anonymized in line with our 
                            privacy policy.
                        </li>
                        <li>
                            <strong>Step 2: Permanent Removal</strong><br>
                            After 90 days, all your data will be permanently removed from our systems and will no longer be recoverable.
                        </li>
                    </ol>
                    <p>If you have any questions or if this request was made in error, please contact our support team immediately 
                    at <a href="mailto:{settings.SYSTEM_SUPPORT_EMAIL}">{settings.SYSTEM_SUPPORT_EMAIL}</a>.</p>
                    <p>Thank you for being a valued part of our community.</p>
                    <p>Best regards,</p>
                    <p><strong>The VWS Team</strong></p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def generate_account_verification_email(user: User, verification_link: str):
        """
        Generates an HTML string to notify the user that their account has been created
        successfully and that they need to verify their email.

        Args:
            user (User): The name of the user to personalize the notification.
            verification_link (str): The link to process verification.

        Returns:
            str: A formatted HTML string.
        """
        user_name = user.name if user.name else user.email
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eaeaea; padding: 20px; 
                border-radius: 8px; background-color: #f9f9f9;">
                    <h2 style="color: #333;">Verify Your Account</h2>
                    <p>Hello {user_name},</p>
                    <p>Thank you for signing up with us! To complete your registration and activate your account, 
                    please verify your email address by clicking the button below:</p>
                    <p style="text-align: center; margin: 20px 0;">
                        <a href="{verification_link}" style="
                            display: inline-block;
                            background-color: #007BFF;
                            color: white;
                            text-decoration: none;
                            padding: 10px 20px;
                            border-radius: 5px;
                            font-size: 16px;
                        ">Verify My Account</a>
                    </p>
                    <p>If the button above doesn’t work, copy and paste the following link into your browser:</p>
                    <p><a href="{verification_link}" style="word-break: break-all;">{verification_link}</a></p>
                    <p>If you did not sign up for an account, please ignore this email or contact our support team at 
                    <a href="mailto:{settings.SYSTEM_SUPPORT_EMAIL}">{settings.SYSTEM_SUPPORT_EMAIL}</a>.</p>
                    <p>Thank you for joining us!</p>
                    <p>Best regards,</p>
                    <p><strong>The VWS Team</strong></p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def generate_account_deletion_success_email_body(user_email: str) -> str:
        """
        Generates an HTML string to notify the user that their account has been deleted successfully.

        Args:
            user_email (str): The name of the user to personalize the notification.

        Returns:
            str: A formatted HTML string.
        """
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #fff; border-radius: 8px; 
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 20px;">
                    <h2 style="color: #333;">Account Deletion Confirmation</h2>
                    <p>Hello {user_email},</p>
                    <p>We are writing to confirm that your account has been successfully deleted from our platform.</p>
                    <p>As part of this process, all your data has been removed in accordance 
                    with our privacy policy.</p>
                    <p>If you did not request this action or have any concerns, 
                    please contact our support team immediately at 
                    <a href="mailto:{settings.SYSTEM_SUPPORT_EMAIL}">{settings.SYSTEM_SUPPORT_EMAIL}</a>.</p>
                    <p>Thank you for being a part of our community, and we wish you all the best.</p>
                    <p>Best regards,</p>
                    <p><strong>The VWS Team</strong></p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def generate_account_activation_email_body(user_email: str) -> str:
        """
        Generates an HTML string to notify the user that their account has been activated successfully.

        Args:
            user_email (str): The email of the user to personalize the notification.

        Returns:
            str: A formatted HTML string.
        """
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #fff; border-radius: 8px; 
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 20px;">
                    <h2 style="color: #333;">Account Activation Successful</h2>
                    <p>Hello {user_email},</p>
                    <p>We’re excited to inform you that your account has been successfully activated. 
                    You can now access all the features and benefits of our platform.</p>
                    <p>If you have any questions or need assistance, feel free to reach out to our support team at 
                    <a href="mailto:{settings.SYSTEM_SUPPORT_EMAIL}">{settings.SYSTEM_SUPPORT_EMAIL}</a>.</p>
                    <p>Welcome aboard!</p>
                    <p>Best regards,</p>
                    <p><strong>The VWS Team</strong></p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def generate_account_deactivation_email_body(user_email: str) -> str:
        """
        Generates an HTML string to notify the user that their account has been deactivated.

        Args:
            user_email (str): The email of the user to personalize the notification.

        Returns:
            str: A formatted HTML string.
        """
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #fff; border-radius: 8px; 
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 20px;">
                    <h2 style="color: #333;">Account Deactivation Notice</h2>
                    <p>Hello {user_email},</p>
                    <p>We would like to inform you that your account has been deactivated. 
                    This means that you will no longer be able to access your account or its associated services.</p>
                    <p>As part of this process, all your personal data has been anonymized in accordance 
                    with our privacy policy.</p>
                    <p>If you believe this action was taken in error or would like to reactivate your account, 
                    please contact our support team at <a href="mailto:{settings.SYSTEM_SUPPORT_EMAIL}">{settings.SYSTEM_SUPPORT_EMAIL}</a>.</p>
                    <p>Thank you for your understanding.</p>
                    <p>Best regards,</p>
                    <p><strong>The VWS Team</strong></p>
                </div>
            </body>
        </html>
        """

    @staticmethod
    def generate_password_reset_email_body(user_name: str, reset_link: str) -> str:
        """
        Generates an HTML string to notify the user that their password reset request has been received.

        Args:
            user_name (str): The name of the user to personalize the notification.
            reset_link (str): The link to reset the user's password. The link should redirect to a frontend page where the user enters their new password.

        Return:
            str: A formatted HTML string.
        """
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eaeaea; padding: 20px; 
                border-radius: 8px; background-color: #f9f9f9;">
                    <h2 style="color: #333;">Password Reset Request</h2>
                    <p>Hello {user_name},</p>
                    <p>We received a request to reset your password. You can reset your password by clicking the button below:</p>
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{reset_link}" style="
                            display: inline-block;
                            padding: 10px 20px;
                            color: white;
                            background-color: #007BFF;
                            text-decoration: none;
                            border-radius: 5px;
                            font-size: 16px;
                            font-weight: bold;
                        ">Reset Password</a>
                    </div>
                    <p>If the button above doesn't work, copy and paste the following link into your browser:</p>
                    <p><a href="{reset_link}" style="word-wrap: break-word;">{reset_link}</a></p>
                    <p>If you did not request a password reset, please ignore this email or contact our support team for assistance.</p>
                    <p>Thank you,</p>
                    <p><strong>The VWS Team</strong></p>
                </div>
            </body>
        </html>
        """


email_services = EmailServices()
