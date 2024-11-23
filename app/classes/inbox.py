from imapclient import IMAPClient
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime

# Fonction pour récupérer le dernier e-mail et retourner un tuple (expéditeur, sujet, date sans heure)
def decode_header_value(value):
    if value:
        decoded_parts = decode_header(value)
        decoded_string = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                part = part.decode(encoding if encoding else "utf-8", errors="ignore")
            decoded_string += part
        return decoded_string
    return "Non disponible"

# Fonction pour récupérer le dernier e-mail (sujet, expéditeur, date, contenu)
def fetch_last_email(host, email_user, email_pass):
    try:
        with IMAPClient(host) as client:
            client.login(email_user, email_pass)
            client.select_folder("INBOX", readonly=True)  # Accès à la boîte de réception
            
            # Récupérer les ID des messages
            messages = client.search("ALL")
            if not messages:
                return "Aucun e-mail trouvé.", "", "", ""

            last_message_id = messages[-1]  # Dernier e-mail
            message_data = client.fetch(last_message_id, "RFC822")
            msg = email.message_from_bytes(message_data[last_message_id][b"RFC822"])
            
            # Décoder le sujet, l'expéditeur et la date
            subject = decode_header_value(msg.get("Subject"))
            sender = decode_header_value(msg.get("From"))
            date_sent = msg.get("Date")
            date_sent_parsed = (
                parsedate_to_datetime(date_sent).strftime("%Y-%m-%d")
                if date_sent
                else "Date non disponible"
            )
            
            # Extraire le contenu de l'e-mail
            content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        content = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                content = msg.get_payload(decode=True).decode(errors="ignore")
            content=content.replace("\r\n","")
            return subject, sender, date_sent_parsed, content
    except Exception as e:
        return "Erreur", str(e), "", ""

# Fonction pour afficher les e-mails sous forme de tuple dans Tkinter

# Paramètres de connexion
host = "imap.gmail.com"  # Remplacez par le serveur IMAP de votre fournisseur
email_user = "issam.mouhala@gmail.com"  # Votre e-mail
email_pass = "rgiz lcpm isfb iydi"  # Votre mot de passe ou mot de passe d'application

# Récupération et affichage du dernier e-mail sous forme de tuple
emails = fetch_last_email(host, email_user, email_pass)
