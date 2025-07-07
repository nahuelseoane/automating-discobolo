import smtplib
from email.message import EmailMessage



def send_email(receiver, name, image_path):
    msg = EmailMessage()
    msg["Subject"] = f"¡Feliz cumple {name}!"
    msg["From"] = ""