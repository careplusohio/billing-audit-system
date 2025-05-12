import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Your email details
gmail_user = 'careplusohio3@gmail.com'
gmail_password = 'kssd wdjl xaeq nrpu'  # <-- Replace this with your 16-character App Password

# Email content
to_email = 'careplusohio3@gmail.com'
subject = 'CarePlus Ohio - Rhino Claims Export 📋'
body = """
Hello,

Attached is the latest CarePlus Ohio Rhino Claims export.

Best regards,
CarePlus Ohio System
"""

# File to attach
attachment_path = 'rhino_claims_selected_export.xlsx'

# Create email
msg = MIMEMultipart()
msg['From'] = gmail_user
msg['To'] = to_email
msg['Subject'] = subject

msg.attach(MIMEText(body, 'plain'))

# Attach the file
if os.path.exists(attachment_path):
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
    msg.attach(part)
else:
    print(f"❌ Attachment file not found: {attachment_path}")
    exit()

# Send the email
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(gmail_user, gmail_password)
    server.sendmail(gmail_user, to_email, msg.as_string())
    server.quit()
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
