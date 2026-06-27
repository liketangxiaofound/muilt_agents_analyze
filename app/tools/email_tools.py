"""
邮件发送工具

提供 Agent 使用的 SMTP 邮件发送能力。
所需环境变量: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL
"""
import os
import ssl
import certifi
import logging
import smtplib
from email.message import EmailMessage
from email.utils import formatdate

from strands import tool
from dotenv import load_dotenv

load_dotenv()


@tool
def send_email(
    subject: str,
    body: str,
    recipient_emails: str,
    attachment_paths: str = "",
) -> str:
    """
    通过 SMTP 发送邮件，支持 HTML 正文和多附件。

    环境变量: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL

    参数:
        subject:          邮件主题
        body:             邮件正文（支持 HTML）
        recipient_emails: 收件人，逗号分隔
        attachment_paths: 附件路径，逗号分隔（可选）
    返回:
        发送结果描述
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    sender_email = os.getenv("SENDER_EMAIL", "")

    if not smtp_host:
        return "错误：SMTP_HOST 未配置"
    if not smtp_username or not smtp_password:
        return "错误：SMTP 凭据未配置"
    if not sender_email:
        return "错误：SENDER_EMAIL 未配置"
    if not recipient_emails.strip():
        return "错误：收件人为空"

    recipient_list = [a.strip() for a in recipient_emails.split(",") if a.strip()]
    if not recipient_list:
        return "错误：无法解析收件人地址"

    attachment_list = []
    if attachment_paths.strip():
        attachment_list = [p.strip() for p in attachment_paths.split(",") if p.strip()]
        for att in attachment_list:
            if not os.path.exists(att):
                return f"错误：附件不存在: {att}"

    try:
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipient_list)
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)

        is_html = body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html")
        if is_html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        for att in attachment_list:
            with open(att, "rb") as f:
                file_data = f.read()
            fname = os.path.basename(att)
            if fname.endswith(".html"):
                mt, st = "text", "html"
            elif fname.endswith(".zip"):
                mt, st = "application", "zip"
            elif fname.endswith(".pdf"):
                mt, st = "application", "pdf"
            else:
                mt, st = "application", "octet-stream"
            msg.add_attachment(file_data, maintype=mt, subtype=st, filename=fname)

        context = ssl.create_default_context(cafile=certifi.where())
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        return f"邮件已发送: 发件人={sender_email}, 收件人={recipient_list}, 附件={len(attachment_list)}个"
    except smtplib.SMTPAuthenticationError:
        return "错误：SMTP 认证失败，请检查用户名密码"
    except smtplib.SMTPConnectError:
        return f"错误：无法连接 SMTP 服务器 {smtp_host}:{smtp_port}"
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")
        return f"邮件发送错误: {str(e)}"
