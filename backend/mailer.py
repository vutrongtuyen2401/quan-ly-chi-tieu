"""Gửi mã reset mật khẩu qua SMTP."""

import smtplib
import ssl
from email.message import EmailMessage

from backend.config import (IS_PRODUCTION, RESET_TOKEN_EXPIRE_MINUTES, SMTP_FROM, SMTP_HOST, SMTP_PASSWORD,
                            SMTP_PORT, SMTP_SECURITY, SMTP_USER)

# Các giá trị cấu hình được đọc qua module này (mailer.IS_PRODUCTION, mailer.SMTP_HOST...) để test có thể mock
__all__ = ["IS_PRODUCTION", "smtp_configured", "send_reset_email"]


def smtp_configured() -> bool:
    return bool(SMTP_HOST and SMTP_FROM)


def send_reset_email(to_email: str, reset_token: str) -> None:
    """Gửi mã reset qua SMTP. Ném exception nếu gửi thất bại."""
    msg = EmailMessage()
    msg["Subject"] = "Mã khôi phục mật khẩu - Càn Khôn Linh Thạch Các"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        f"Xin chào Đạo Hữu,\n\n"
        f"Mã xác thực để đặt lại mật khẩu của bạn là: {reset_token}\n"
        f"Mã có hiệu lực trong {RESET_TOKEN_EXPIRE_MINUTES} phút và chỉ dùng được một lần.\n\n"
        f"Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này.\n"
    )

    if SMTP_SECURITY == "ssl":
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15, context=ssl.create_default_context())
    else:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
    with server:
        if SMTP_SECURITY == "starttls":
            server.starttls(context=ssl.create_default_context())
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
