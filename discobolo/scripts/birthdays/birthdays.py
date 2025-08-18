from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file("token.json")
service = build("people", "v1", credentials=creds)

results = (
    service.people()
    .connections()
    .list(resourceName="people/me", personFields="names,birthdays,emailAddresses")
    .execute()
)

connections = results.get("connections", [])

for person in connections:
    nombres = person.get("names", [])
    cumpleaños = person.get("birthdays", [])
    emails = person.get("emailAddresses", [])

    if nombres and cumpleaños and emails:
        nombre = nombres[0].get("displayName")
        cumpleaños_str = cumpleaños[0].get("date")
        email = emails[0].get("value")
        # 🎉 acá podés comparar la fecha y generar la tarjeta
