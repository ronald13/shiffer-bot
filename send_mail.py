import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, message, sender_email, receiver_email, smtp_server, smtp_port, smtp_username, smtp_password):
    try:
        # Create a MIMEText object to represent the HTML email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Create HTML content for the email message with desired styling
        html_message = """
        <html>
            <head>
                <style>
                    /* Add your CSS styles here */
                    body {{
                        font-family: Arial, sans-serif;
                        color: #333;
                    }}
                    h1 {{
                        color: #007bff;
                    }}
                </style>
            </head>
            <body>
                <p>Код для авторизации:</p>
                <h1>{}</h1>
                <p>Код действителен в течении 10минут.</p>
            </body>
        </html>
        """.format(message)

        # Attach the HTML content to the email message
        html_part = MIMEText(html_message, 'html')
        msg.attach(html_part)

        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(smtp_username, smtp_password)  # Login to the SMTP server

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())

        # Close the connection to the SMTP server
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

# Example usage:
subject = "Stylized HTML Email"
message = "5848"
sender_email = "info@shiffer.info"
receiver_email = "luter195@gmail.com"
smtp_server = "smtp.elasticemail.com"
smtp_port = 2525  # Port for TLS/STARTTLS
smtp_username = "info@shiffer.info"
smtp_password = "58587C533340846104D673D74F13A472ABAE"


send_email(subject, message, sender_email, receiver_email, smtp_server, smtp_port, smtp_username, smtp_password)
