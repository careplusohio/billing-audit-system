import smtplib
import ssl
from email.message import EmailMessage

# Email settings
sender_email = "your-email@gmail.com"       # << your email
receiver_email = "recipient-email@example.com"  # << recipient email
password = "your-gmail-app-password"          # << app password (NOT your login password)

# Create the email
subject = "Rhino Claims Export"
body = "Attached is the latest Rhino Claims Export."

msg = EmailMessage()
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email
msg.set_content(body)

# Attach the Excel file
with open('rhino_claims_selected_export.xlsx', 'rb') as f:
    file_data = f.read()
    file_name = f.name

msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

# Send the email
context = ssl.create_default_context()
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(sender_email, password)
    smtp.send_message(msg)

print("✅ Email sent successfully!")
