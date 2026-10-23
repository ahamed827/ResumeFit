import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.logging import logger


class EmailService:
    def __init__(self):
        self.provider = settings.EMAIL_PROVIDER.lower()
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME

    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Sends a password reset email with the reset link/token."""
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        subject = f"Password Reset Request - {settings.PROJECT_NAME}"

        plain_content = (
            f"Hello,\n\n"
            f"You requested a password reset for your {settings.PROJECT_NAME} account.\n"
            f"Click the link below or copy it to your browser to set a new password:\n\n"
            f"{reset_link}\n\n"
            f"This link will expire in 1 hour. If you did not request this, please ignore this email.\n\n"
            f"Regards,\n{settings.PROJECT_NAME} Team"
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                <h2 style="color: #4f46e5;">{settings.PROJECT_NAME}</h2>
                <p>Hello,</p>
                <p>We received a request to reset the password for your account.</p>
                <p style="margin: 25px 0;">
                    <a href="{reset_link}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        Reset Password
                    </a>
                </p>
                <p style="font-size: 13px; color: #64748b;">Or paste this link into your browser: <br>{reset_link}</p>
                <p style="font-size: 13px; color: #94a3b8;">This link expires in 1 hour.</p>
            </div>
        </body>
        </html>
        """

        if self.provider == "console":
            # Development console preview
            border = "=" * 70
            print(f"\n{border}")
            print(f"📧 [DEV EMAIL CONSOLE PREVIEW] To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Reset Link: {reset_link}")
            print(f"Token: {reset_token}")
            print(f"{border}\n")
            logger.info(f"Password reset email simulated for {to_email}. Reset link: {reset_link}")
            return True

        elif self.provider == "smtp":
            if not settings.SMTP_HOST or not settings.SMTP_USER:
                logger.warning(
                    "SMTP configured but host/user missing; falling back to console logging."
                )
                logger.info(f"Reset link for {to_email}: {reset_link}")
                return True

            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{self.from_name} <{self.from_email}>"
                msg["To"] = to_email

                msg.attach(MIMEText(plain_content, "plain"))
                msg.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    if settings.SMTP_TLS:
                        server.starttls()
                    if settings.SMTP_USER and settings.SMTP_PASSWORD:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)

                logger.info(f"Password reset email sent via SMTP to {to_email}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via SMTP: {e}")
                return False

        return True


email_service = EmailService()
