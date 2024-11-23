import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Fonction pour afficher les détails d'un email
def show_email_details(event):
    selected_item = emails_list.selection()
    if selected_item:
        email_index = emails_list.index(selected_item)
        subject, sender, content, date = emails[email_index]
        details_text.delete(1.0, "end")
        details_text.insert("end", f"Sujet : {subject}\n")
        details_text.insert("end", f"Expéditeur : {sender}\n")
        details_text.insert("end", f"Date d'envoi : {date}\n\n")
        details_text.insert("end", f"Contenu :\n{content}")

# Liste fictive d'emails avec des dates
emails = [
    ("📬 Bienvenue sur la plateforme", "admin@exemple.com", "Bonjour ! Merci de rejoindre notre plateforme.", "2024-11-20"),
    ("🔔 Rappel : Réunion demain", "manager@workplace.com", "N'oubliez pas la réunion prévue à 10h demain.", "2024-11-19"),
    ("🎉 Promotion spéciale !", "promo@shop.com", "Découvrez nos offres incroyables ce weekend.", "2024-11-18"),
    ("✅ Compte mis à jour", "noreply@service.com", "Votre compte a été mis à jour avec succès.", "2024-11-17"),
    ("📅 Invitation à un événement", "event@exemple.org", "Rejoignez-nous pour une soirée networking jeudi prochain.", "2024-11-16"),
]

# Création de la fenêtre principale avec ttkbootstrap
root = ttk.Window(themename="cosmo")  # Thème moderne
root.title("Boîte Email Moderne et Stylée")
root.geometry("1100x600")

# Section titre
title_label = ttk.Label(
    root, text="Votre Boîte Email", font=("Helvetica", 26, "bold"), bootstyle="primary", anchor="center"
)
title_label.pack(fill=X, pady=10)

# Cadre principal
main_frame = ttk.Frame(root)
main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

# Liste des emails
emails_frame = ttk.Frame(main_frame)
emails_frame.pack(side=LEFT, fill=Y, padx=10)

# Colonnes stylées
emails_list = ttk.Treeview(
    emails_frame,
    columns=("Sujet", "Expéditeur", "Date d'envoi"),
    show="headings",
    height=20,
    bootstyle="info",
)
emails_list.heading("Sujet", text="📌 Sujet", anchor="w")
emails_list.heading("Expéditeur", text="✉️ Expéditeur", anchor="w")
emails_list.heading("Date d'envoi", text="🗓️ Date d'envoi", anchor="w")
emails_list.column("Sujet", anchor="w", width=350)
emails_list.column("Expéditeur", anchor="w", width=250)
emails_list.column("Date d'envoi", anchor="w", width=150)

# Remplir la liste avec des emails fictifs
for email_data in emails:
    subject, sender, content, date = email_data
    emails_list.insert("", "end", values=(subject, sender, date))

emails_list.pack(fill=BOTH, expand=True)

# Cadre pour les détails de l'email
details_frame = ttk.Frame(main_frame, padding=10)
details_frame.pack(side=RIGHT, fill=BOTH, expand=True)

details_label = ttk.Label(details_frame, text="Détails de l'Email", font=("Helvetica", 18, "bold"), bootstyle="info")
details_label.pack(anchor="w", pady=5)

details_text = ttk.Text(details_frame, wrap="word", font=("Arial", 14), height=20, bg="#f9f9f9", fg="#333")
details_text.pack(fill=BOTH, expand=True)

# Ajouter un bouton pour rafraîchir (fictif pour cette démo)
refresh_button = ttk.Button(root, text="🔄 Rafraîchir", bootstyle="success-outline", command=lambda: None)
refresh_button.pack(pady=10)

# Événement pour afficher les détails
emails_list.bind("<<TreeviewSelect>>", show_email_details)

# Lancer l'application
root.mainloop()
