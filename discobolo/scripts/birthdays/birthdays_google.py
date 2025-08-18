from __future__ import print_function

import datetime
import mimetypes
import os.path
import pickle
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from discobolo.config.config import (
    EMAIL_PASSWORD,
    EMAIL_USER,
    GMAIL_FALLBACK_ID,
    GMAIL_GROUP_ID,
    SMTP_PORT,
    SMTP_SERVER,
)

SCOPES = ["https://www.googleapis.com/auth/contacts.readonly"]


def listar_grupos_disponibles(service):
    results = service.contactGroups().list(pageSize=100).execute()
    grupos = results.get("contactGroups", [])

    print("📂 Grupos encontrados:")
    for grupo in grupos:
        print(f"- {grupo['name']} (ID: {grupo['resourceName']})")


def obtain_resource_group_name(service, group_name, fallback_resource_name=None):
    results = service.contactGroups().list(pageSize=100).execute()
    groups = results.get("contactGroups", [])

    for group in groups:
        group_name_actual = group.get("name", "")
        if group_name_actual.strip().lower() == group_name.strip().lower():
            print(f"✅ Grupo encontrado: {group_name_actual}")
            return group["resourceName"]

        print(f"❌ Group name couldn't be found: {group_name}")

        if fallback_resource_name:
            print(f"➡️ Usando fallback resourceName: {fallback_resource_name}")
            return fallback_resource_name
        return None


## 1
def authenticate():
    creds = None
    if os.path.exists("token.json"):
        # Ya nos autenticamos antes
        with open("token.json", "rb") as token:
            creds = pickle.load(token)
    # Si no hay token o expiró, pedimos login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)

        # Guardamos el token
        with open("token.json", "wb") as token:
            pickle.dump(creds, token)
    return creds


## 2
def obtain_birthday(creds):
    service = build("people", "v1", credentials=creds)
    listar_grupos_disponibles(service)
    contact_group_id = obtain_resource_group_name(
        service, GMAIL_GROUP_ID, fallback_resource_name=GMAIL_FALLBACK_ID
    )

    results = (
        service.people()
        .connections()
        .list(
            resourceName="people/me",
            pageSize=2000,
            personFields="names,birthdays,emailAddresses,memberships",
        )
        .execute()
    )

    cumpleañeros = []

    for person in results.get("connections", []):
        groups = person.get("memberships", [])

        belong = any(
            g.get("contactGroupMembership", {}).get("contactGroupResourceName")
            == contact_group_id
            for g in groups
        )

        if not belong:
            continue

        name = person.get("names", [{}])[0].get("displayName")
        email = person.get("emailAddresses", [{}])[0].get("value")
        cumple = person.get("birthdays", [{}])[0].get("date")

        if name and email and cumple:
            mes_dia = f"{cumple.get('month'):02d}-{cumple.get('day'):02d}"
            hoy = datetime.datetime.today().strftime("%m-%d")
            if mes_dia == hoy:
                cumpleañeros.append((name, email))

    return cumpleañeros


def send_email(destinatario, name, image_path):
    msg = EmailMessage()
    msg["Subject"] = f"🎉 ¡Feliz Cumple {name}!"
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario

    image_cid = make_msgid(
        domain="discobolo.club"
    )  # podés poner cualquier dominio válido
    image_cid_stripped = image_cid[1:-1]

    msg.set_content(f"""
        Hola {name} 👋
        
        
        🎂 ¡El Club Discóbolo te desea un muy feliz cumpleaños!

        Que tengas un gran día lleno de alegría y buenos momentos 🎾🎈

        ¡Te esperamos para celebrarlo en el club!

        Saludos,
        Club Discóbolo
        """)

    msg.add_alternative(
        f"""
        <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <p>Hola {name} 👋🎉</p>
                    <br>
                    <p>¡El <strong>Club Discobolo</strong> te desea un muy feliz cumpleaños!🎂</p>
                    <div style="text-align: center; margin: 25px 0;">
                        <img src="cid:{image_cid_stripped}" alt="Feliz cumple" style="width:65%; max-width:360px; border-radius:16px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"/>
                    </div>
                    <p>¡Te esperamos para celebrarlo en el club! 🎾🥳</p>
                    <br>
                    <p>Saludos,</p>
                    <p style="font-size: 0.9em; color #888;">Club de Deportes Discobolo</p>
                </body>
        </html>
        """,
        subtype="html",
    )

    # Detectar el tipo MIME de la imagen
    mime_type, _ = mimetypes.guess_type(image_path)
    maintype, subtype = mime_type.split("/")

    with open(image_path, "rb") as img:
        msg.get_payload()[1].add_related(
            img.read(), maintype=maintype, subtype=subtype, cid=image_cid
        )

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print(f"📧 Email enviado a {name} ({destinatario})")


## 3
if __name__ == "__main__":
    creds = authenticate()
    cumpleañeros = obtain_birthday(creds)

    if cumpleañeros:
        for name, email in cumpleañeros:
            print(f"🎉 Hoy cumple {name} ({email})")
            image_path = "./card_last.png"
            send_email(email, name, image_path)

    else:
        print("📭 Hoy no cumple nadie (según tus contactos).")
