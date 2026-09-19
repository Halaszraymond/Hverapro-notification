import smtplib
from email.mime.text import MIMEText

import config


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_FROM
    msg["To"] = config.EMAIL_TO

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.sendmail(config.EMAIL_FROM, [config.EMAIL_TO], msg.as_string())


def notify_listing(listing):
    if listing["price"] is not None:
        price_text = f"{listing['price']:,} Ft".replace(",", " ")
    else:
        price_text = "price unknown"

    subject = f"New HardverApro listing: {listing['title']}"
    body = (
        f"{listing['title']}\n"
        f"Price: {price_text}\n"
        f"Link: {listing['link']}\n"
    )
    send_email(subject, body)
