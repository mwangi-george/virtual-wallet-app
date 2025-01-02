from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, BackgroundTasks
from datetime import datetime
from ..models import User, AccountRemovalRequest
from ..core import send_email_with_resend


class UserServices:

    @staticmethod
    async def process_account_removal_request(user: User, db: AsyncSession, bg_tasks: BackgroundTasks):
        try:
            account_removal_request = AccountRemovalRequest(
                user_id=user.id,
                request_timestamp=datetime.now(),
                status="Pending"
            )
            db.add(account_removal_request)
            await db.commit()
            await db.refresh(account_removal_request)

            bg_tasks.add_task(
                send_email_with_resend,
                user.email,
                "Account removal request received",
                f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eaeaea; padding: 20px; 
                        border-radius: 8px; background-color: #f9f9f9;">
                            <h2 style="color: #333;">Account Removal Request Received</h2>
                            <p>Hello {user.name},</p>
                            <p>We have received your request to remove your account from our platform. 
                            Please note the following:</p>
                            <ul>
                                <li>Your account removal request has been logged successfully.</li>
                                <li>The process will take <strong>up to 30 days</strong> to complete.</li>
                                <li>You will receive a confirmation email once the removal is finalized.</li>
                            </ul>
                            <p>If you have any questions or if this request was made in error, please contact our
                             support team immediately at <a href="mailto:support@acme.com">support@acme.com</a>.</p>
                            <p>Thank you for being a part of our community.</p>
                            <p>Best regards,</p>
                            <p><strong>The Acme Team</strong></p>
                        </div>
                    </body>
                </html>
                """
            )
            return f"Account removal request received. Request ID: {account_removal_request.id}"
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


user_services = UserServices()
