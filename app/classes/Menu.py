
# Imports standards
import sys
import datetime
import subprocess
import psycopg2
from psycopg2.extras import DictCursor

# Bibliothèques tierces
import numpy as np
from matplotlib import dates,pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from imapclient import IMAPClient
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime ,parseaddr
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap, QCursor, QIcon, QFont,QColor
import pandas as pd  
from fpdf import FPDF
import pickle
import face_recognition
from PyQt5.QtWidgets import (
    QHeaderView,
    QTextEdit,
    QTreeWidgetItem,
    QTreeWidget,
    QApplication,
    QSpacerItem,
    QSizePolicy,
    QMainWindow,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QCalendarWidget,
    QLineEdit,
    QStackedWidget,
    QMessageBox,
    QScrollArea,
    QProgressBar,
    QDialog,
    QFileDialog,
    QGraphicsDropShadowEffect
)
from imapclient import IMAPClient
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime




try:
    # Connexion par défaut pour créer la base de données si elle n'existe pas
    default_conn = psycopg2.connect(
        host='localhost',
        user='docker',  # Nom d'utilisateur PostgreSQL
        password='docker',  # Mot de passe PostgreSQL
        database='postgres'  # Base par défaut pour les connexions
    )
    default_conn.autocommit = True
    default_cursor = default_conn.cursor()

    # Vérifier si la base de données "miniproject" existe, sinon la créer
    default_cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'miniproject';")
    if not default_cursor.fetchone():
        default_cursor.execute("CREATE DATABASE miniproject;")
        print("Base de données 'miniproject' créée avec succès.")
    default_cursor.close()
    default_conn.close()

    # Connexion à la base de données "miniproject"
    conn = psycopg2.connect(
        host='localhost',
        user='docker',  # Nom d'utilisateur PostgreSQL
        password='docker',  # Mot de passe PostgreSQL
        database='miniproject'  # Nom de la base de données
    )

    # Création de tables si elles n'existent pas encore
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    filiere VARCHAR(255),
    image BYTEA,
    image_pure BYTEA,
    accepte INT
);
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS absence (
            id_ab SERIAL PRIMARY KEY,
            id INT NOT NULL,
            time TIME NOT NULL,
            date DATE NOT NULL
        );
    """)
    conn.commit()
except psycopg2.Error as e:
    print(f"Erreur lors de la connexion ou de l'exécution SQL : {e}")
               


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
def fetch_last_10_emails(host, email_user, email_pass):
    try:
        with IMAPClient(host) as client:
            client.login(email_user, email_pass)
            client.select_folder("INBOX", readonly=True)  # Accès à la boîte de réception
            
            # Récupérer les ID des messages
            messages = client.search("ALL")
            if not messages:
                return "Aucun e-mail trouvé."

            # Récupérer les 10 derniers messages (ou moins si moins de 10 messages)
            last_10_message_ids = messages[-10:]
            last_10_message_ids.reverse()
            emails = []

            for message_id in last_10_message_ids:
                message_data = client.fetch(message_id, "RFC822")
                msg = email.message_from_bytes(message_data[message_id][b"RFC822"])
                
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
                
                content = content.replace("\r\n", "")
                emails.append((subject, sender, content, date_sent_parsed))
            
            return emails
    except Exception as e:
        return [("Erreur", str(e), "", "")]


# Fonction pour afficher les e-mails sous forme de tuple dans Tkinter

# Paramètres de connexion
host = "imap.gmail.com"  # Remplacez par le serveur IMAP de votre fournisseur
email_user = "issam.mouhala@gmail.com"  # Votre e-mail
email_pass = "rgiz lcpm isfb iydi"  # Votre mot de passe ou mot de passe d'application

# Récupération et affichage du dernier e-mail sous forme de tuple
emails = fetch_last_10_emails(host, email_user, email_pass)






class AbsenceManagerHome(QWidget):
    def __init__(self, stacked_widget, app_reference):
        super().__init__()
        self.stacked_widget = stacked_widget  
        self.app_reference = app_reference  
        self.conn = psycopg2.connect(
        host='localhost',
        user='docker',  # Nom d'utilisateur PostgreSQL
        password='docker',  # Mot de passe PostgreSQL
        database='miniproject'  # Nom de la base de données
    )


        common_stylesheet = """
        QListWidget {
            background-color: #f9f9f9; 
            border-radius: 12px; 
            padding: 5px; 
        }
        QListWidget::item {
            padding: 10px; 
            color: black;
            font-size: 14px;
            font-family: Arial;
            border: 1px solid transparent; 
            border-radius: 8px; 
        }
        QListWidget::item:hover {
            background-color: #a6e3a1; 
            border: 1px solid #6cc24a; 
        }
        """

        # Stylesheet pour le calendrier
        calendar_stylesheet = """
        QCalendarWidget {
            background-color: #f9f9f9; 
            border-radius: 10px;
            padding: 5px;
            font-size: 14px;
            font-family: Arial;
        }
        """
      
        main_layout = QVBoxLayout(self)

        
        nav_layout = QHBoxLayout()
        notif_btn = QPushButton("Notification")
        record_absence_btn = QPushButton("Record Absence")
        manage_users_btn = QPushButton("Manage Users")  
        absence_analysis_btn = QPushButton("Absence Analysis")


        button_stylesheet = """
        QPushButton {
            background-color: #a6e3a1; 
            padding: 10px; 
            font-size: 14px; 
            border-radius: 12px;
        }
        QPushButton:hover {
            background-color: #8bc68b;
        }
        """
        def apply_shadow(widget):
            shadow_effect = QGraphicsDropShadowEffect()
            shadow_effect.setBlurRadius(15)  # Flou de l'ombre
            shadow_effect.setColor(QColor(0, 0, 0, 100))  # Couleur noire avec transparence
            shadow_effect.setOffset(3, 3)  # Décalage de l'ombre
            widget.setGraphicsEffect(shadow_effect)

       
        





        notif_btn.setStyleSheet(button_stylesheet)
        notif_btn.setCursor(Qt.PointingHandCursor)
        record_absence_btn.setStyleSheet(button_stylesheet)
        record_absence_btn.setCursor(Qt.PointingHandCursor)
        manage_users_btn.setStyleSheet(button_stylesheet)
        manage_users_btn.setCursor(Qt.PointingHandCursor)
        absence_analysis_btn.setStyleSheet(button_stylesheet)
        absence_analysis_btn.setCursor(Qt.PointingHandCursor)

        nav_layout.addWidget(record_absence_btn)
        nav_layout.addWidget(manage_users_btn)
        nav_layout.addWidget(absence_analysis_btn)
        nav_layout.addWidget(notif_btn)
        main_layout.addLayout(nav_layout)


        export_button = QPushButton("Exporter les données")
        export_button.setStyleSheet("""
        background-color: #90caf9; 
        padding: 10px; 
        font-size: 14px; 
        border-radius: 10px;
        """)
        export_button.setCursor(Qt.PointingHandCursor)
        export_button.clicked.connect(self.show_export_dialog)

        
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch() 
      
        bottom_layout.addWidget(export_button, alignment=Qt.AlignRight) 
        
        main_layout.addLayout(bottom_layout)

       
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setStyleSheet(calendar_stylesheet)
        self.grid_layout.addWidget(self.calendar_widget, 0, 0, 2, 1)
        self.calendar_widget.clicked[QDate].connect(self.get_selected_date)
        

        # Autres sections comme Absences à venir, Notifications, etc.
        self.upcoming_absences_label = QLabel("Listes des  Absences")
        self.upcoming_absences_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        self.upcoming_absences_list = QListWidget()
        self.upcoming_absences_list.setStyleSheet(common_stylesheet)
        self.grid_layout.addWidget(self.upcoming_absences_label, 0, 1)
        self.grid_layout.addWidget(self.upcoming_absences_list, 1, 1)
        

       


        statistics_label = QLabel("Your Statistics")
        statistics_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        statistics_list = QListWidget()
        query = """
        SELECT users.filiere, COUNT(absence.id) AS total_absences
        FROM absence
        JOIN users ON absence.id = users.id
        GROUP BY users.filiere;
        """
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(query)
        statistics_data = cursor.fetchall()

        print("Data fetched from the database:", statistics_data)
        # Ajout des statistiques à la liste
        if statistics_data:
            for record in statistics_data:
                filiere = record['filiere']
                total_absences = record['total_absences']
                print(f"Filière: {filiere}, Total des absences: {total_absences}")
                formatted_item = f"Filière: {filiere} | Total des absences: {total_absences}"
                statistics_list.addItem(formatted_item)

        else:
            statistics_list.addItem(QListWidgetItem("No statistics available."))

        # Ajout au layout principal
 
        
        self.grid_layout.addWidget(statistics_label, 0, 2)
        self.grid_layout.addWidget(statistics_list, 1, 2)

        # Appliquer le style et l'ombre à la liste des absences
        self.upcoming_absences_list.setStyleSheet(common_stylesheet)
        apply_shadow(self.upcoming_absences_list)

        # Appliquer le style et l'ombre à la liste des statistiques
        statistics_list.setStyleSheet(common_stylesheet)
        apply_shadow(statistics_list)





        # Connecter le bouton "Record Absence" à la fonction du script
        record_absence_btn.clicked.connect(self.app_reference.run_record_absence_script)

        # Signal pour passer à l'interface de gestion des utilisateurs
        notif_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        manage_users_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        absence_analysis_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
    def get_selected_date(self, date):
        formatted_date = date.toString("yyyy/MM/dd")
        self.upcoming_absences_list.clear()

        cursor = conn.cursor()
        print(formatted_date)
        # Exécuter la requête pour récupérer les données d'absence par heure
        cursor.execute("""
           SELECT u.username,u.filiere,a.time
           FROM absence a
           JOIN users u ON a.id = u.id
           WHERE a.date = DATE(%s) order by u.filiere
           """,(formatted_date,))
        liste=cursor.fetchall()
        if liste==[]:

            item = QListWidgetItem("No Absences ...")
            self.upcoming_absences_list.addItem(item)
        else:
            for j,i,k in liste:
                item = QListWidgetItem(f"{j}--{i}--{k}")
                self.upcoming_absences_list.addItem(item)
            for i in range(len(self.upcoming_absences_list)):
               font = QFont()
               font.setBold(True)
               font.setPointSize(14)
               font.setCapitalization(QFont.Capitalize)
               self.upcoming_absences_list.item(i).setFont(font)
               self.upcoming_absences_list.item(i).setTextAlignment(Qt.AlignCenter)



        self.grid_layout.addWidget(self.upcoming_absences_label, 0, 1)
        self.grid_layout.addWidget(self.upcoming_absences_list, 1, 1) 
    # Fonction pour récupérer le dernier e-mail et retourner un tuple (expéditeur, sujet, date sans heure)
  

    def show_export_dialog(self):
        # Étape 1 : Récupérer les filières disponibles depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT filiere FROM users")
        filieres = [row[0] for row in cursor.fetchall()]

        if not filieres:
            QMessageBox.warning(self, "Erreur", "Aucune filière trouvée dans la base de données.")
            return

        # Étape 2 : Afficher une boîte de dialogue pour sélectionner une filière
        dialog = QDialog(self)
        dialog.setWindowTitle("Choisir une filière")
        dialog_layout = QVBoxLayout(dialog)

        filiere_label = QLabel("Sélectionnez une filière à exporter :")
        dialog_layout.addWidget(filiere_label)

        filiere_dropdown = QComboBox()
        filiere_dropdown.addItems(filieres)
        dialog_layout.addWidget(filiere_dropdown)

        confirm_button = QPushButton("Confirmer")
        confirm_button.clicked.connect(lambda: self.show_export_format(dialog, filiere_dropdown.currentText()))
        dialog_layout.addWidget(confirm_button)

        dialog.exec()

    def show_export_format(self, parent_dialog, filiere):
        # Étape 3 : Afficher les options de format d'exportation
        parent_dialog.accept()

        format_dialog = QDialog(self)
        format_dialog.setWindowTitle("Choisir le format d'exportation")
        dialog_layout = QVBoxLayout(format_dialog)

        format_label = QLabel("Choisissez un format :")
        dialog_layout.addWidget(format_label)

        format_dropdown = QComboBox()
        format_dropdown.addItems(["Excel", "PDF", "Texte"])
        dialog_layout.addWidget(format_dropdown)

        confirm_button = QPushButton("Exporter")
        confirm_button.clicked.connect(lambda: self.perform_export(filiere, format_dropdown.currentText()))
        dialog_layout.addWidget(confirm_button)

        format_dialog.exec()

    def perform_export(self, filiere, file_format):
        # Étape 4 : Récupérer les données de la base de données
        query = """
        SELECT u.username, u.filiere, a.date,a.time
        FROM users u
        JOIN absence a ON u.id = a.id
        WHERE u.filiere = %s
        """
        cursor = self.conn.cursor(cursor_factory=DictCursor)
        cursor.execute(query, (filiere,))
        data = cursor.fetchall()

        if not data:
            QMessageBox.warning(self, "Erreur", f"Aucune donnée trouvée pour la filière {filiere}.")
            return

        # Étape 5 : Exporter selon le format sélectionné
        if file_format == "Excel":
            self.export_to_excel(data, filiere)
        elif file_format == "PDF":
            self.export_to_pdf(data, filiere)
        elif file_format == "Texte":
            self.export_to_text(data, filiere)

    def export_to_excel(self, data, filiere):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter en Excel", "", "Fichiers Excel (*.xlsx)")
        if file_path:
            df = pd.DataFrame(data)
            df = df.sort_values(by='date')
            df = df.sort_values(by='date')
            df.to_excel(file_path, index=False , sheet_name=filiere)
            QMessageBox.information(self, "Succès", f"Les données de la filière {filiere} ont été exportées en Excel.")

    def export_to_pdf(self, data, filiere):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter en PDF", "", "Fichiers PDF (*.pdf)")
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Données de la filière {filiere}", ln=True, align="C")
            pdf.ln(10)

            for record in data:
                pdf.cell(200, 10, txt=str(record), ln=True)

            pdf.output(file_path)
            QMessageBox.information(self, "Succès", f"Les données de la filière {filiere} ont été exportées en PDF.")

    def export_to_text(self, data, filiere):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter en Texte", "", "Fichiers texte (*.txt)")
        if file_path:
            with open(file_path, "w") as f:
                f.write(f"Données de la filière {filiere}\n\n")
                for record in data:
                    f.write(str(record) + "\n")
            QMessageBox.information(self, "Succès", f"Les données de la filière {filiere} ont été exportées en texte.")


    # Fonction pour afficher les e-mails sous forme de tuple dans Tkinter
    



class AddStudentInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Student")
        self.setGeometry(100, 100, 300, 400)

        main_layout = QVBoxLayout(self)

        # Titre
        title_label = QLabel("Add New Student")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        main_layout.addWidget(title_label)

        # Formulaire
        form_layout = QVBoxLayout()

        # Champ de saisie pour le nom d'utilisateur
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        form_layout.addWidget(self.username_input)

        # Choix de la filière avec un QComboBox
        self.filiere_input = QComboBox(self)
        self.filiere_input.addItems(["MGSI", "GL", "SDBDIA", "SCITCN"])
        self.filiere_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        form_layout.addWidget(self.filiere_input)

        # Champ pour afficher le nom de l'image
        self.image_path_display = QLineEdit(self)
        self.image_path_display.setPlaceholderText("No image selected")
        self.image_path_display.setReadOnly(True)
        form_layout.addWidget(self.image_path_display)

        # Bouton pour sélectionner une image
        select_image_button = QPushButton("Select Image")
        select_image_button.clicked.connect(self.select_image)
        form_layout.addWidget(select_image_button)

        main_layout.addLayout(form_layout)

        # Boutons pour sauvegarder et nettoyer
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.setStyleSheet("background-color: #90c695; padding: 10px; border-radius: 5px;")
        save_button.clicked.connect(self.save_student)
        button_layout.addWidget(save_button)

        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_button)

        main_layout.addLayout(button_layout)

    def select_image(self):
        # Ouvrir une boîte de dialogue pour sélectionner une image
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.jpg *.jpeg *.png)")
        if image_path:
            self.image_path_display.setText(image_path)

    def save_student(self):
        try:
            # Vérifier si le chemin de l'image est renseigné
            image_path = self.image_path_display.text()
            if not image_path:
                self.show_error("Please select an image.")
                return

            print("Image path:", image_path)  # Debug

            # Charger l'image et obtenir l'encodage
            reference_image = face_recognition.load_image_file(image_path)
            reference_encoding = face_recognition.face_encodings(reference_image)

            # Vérifier si un encodage a été trouvé
            if len(reference_encoding) == 0:
                self.show_error("No face detected in the selected image.")
                return
            reference_encoding = reference_encoding[0]
            print("Face encoding obtained.")  # Debug

            # Convertir l'encodage en binaire
            encoded_binary = pickle.dumps(reference_encoding)

            # Récupérer le nom d'utilisateur et la filière
            name = self.username_input.text().strip()
            filiere = self.filiere_input.currentText()
            if not name:
                self.show_error("Please enter a username.")
                return

            print("Username:", name)  # Debug
            print("Filiere:", filiere)  # Debug

            # Appel de la fonction de connexion à la base de données
            
            if conn is None:
                self.show_error("Failed to connect to the database.")
                return
            
            with open(image_path, 'rb') as file:
                photo_blob = file.read()

            cursor = conn.cursor()

            # Insertion dans la base de données
            insert_query = "INSERT INTO users (username, filiere, image,image_pure,accept) VALUES (%s, %s,%s , %s,0)"
            cursor.execute(insert_query, (name, filiere, encoded_binary,photo_blob))
            conn.commit()
            print("Data inserted into the database.")  # Debug

            # Confirmation et nettoyage
            self.show_success("Student added successfully.")
            self.clear_form()

        except psycopg2.Error as db_err:
            self.show_error(f"Database Error: {db_err}")
            print("Database Error:", db_err)  # Debug
        except Exception as e:
            self.show_error(f"Error: {e}")
            print("General Error:", e)  # Debug
        finally:
            if conn.closed != 0:
             cursor = conn.cursor()
             cursor.execute("SELECT 1;")
             print("Database connection closed.")

    def clear_form(self):
        # Vider tous les champs
        self.username_input.clear()
        self.filiere_input.setCurrentIndex(0)
        self.image_path_display.clear()

    def show_success(self, message):
        # Afficher un message de succès
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Success")
        msg.exec_()

    def show_error(self, message):
        # Afficher un message d'erreur
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()


class ManageUsersInterface(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        main_layout = QVBoxLayout(self)

        # Title section with Home button on the left and centered title
        title_section = QHBoxLayout()
        
        # Home button with icon
        home_btn = QPushButton("Home")
        home_btn.setIcon(QIcon("path_to_home_icon.png"))  # Replace with your home icon path
        home_btn.setStyleSheet("padding: 10px; font-size: 16px; border-radius: 8px; background-color: #90c695;")
        home_btn.setCursor(Qt.PointingHandCursor)
        title_section.addWidget(home_btn, alignment=Qt.AlignLeft)

        # Spacer to center the title
        title_section.addStretch(1)

        # Title label
        title_label = QLabel("Manage Absences Efficiently")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_section.addWidget(title_label, alignment=Qt.AlignCenter)

        # Spacer for centering
        title_section.addStretch(1)

        main_layout.addLayout(title_section)



        actions_layout = QHBoxLayout()
        button_style = "padding: 10px; background-color: #6dc9f2; border-radius: 12px; font-size: 14px;c"
        

        add_student_btn = QPushButton("Add Student")
        add_student_btn.setStyleSheet(button_style)
        add_student_btn.setCursor(Qt.PointingHandCursor)
        add_student_btn.clicked.connect(self.show_add_student_interface)
        actions_layout.addWidget(add_student_btn)

        view_student_info_btn = QPushButton("View Student Info")
        view_student_info_btn.setStyleSheet(button_style)
        view_student_info_btn.setCursor(Qt.PointingHandCursor)
        view_student_info_btn.clicked.connect(self.view_student_info)
        actions_layout.addWidget(view_student_info_btn)



        main_layout.addLayout(actions_layout)

        # Placeholder area for displaying student info or search results
        self.info_display_area = QStackedWidget(self)
        self.info_display_area.setStyleSheet("background-color: #f7f7f7; border: 1px solid #ccc; padding: 15px;")
        main_layout.addWidget(self.info_display_area)



        # Connect home button to navigate back to the main screen
        home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))



    def view_student_info(self):
        # Vérifier si la connexion est ouverte
        if conn.closed != 0:
             cursor = conn.cursor()
             cursor.execute("SELECT 1;")

        # Supprimer tous les widgets précédemment ajoutés
        for i in range(self.info_display_area.count()):
            widget = self.info_display_area.widget(i)
            if widget is not None:
                self.info_display_area.removeWidget(widget)
                widget.deleteLater()  

        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) 
        container_widget = QWidget()
        student_layout = QVBoxLayout(container_widget) 
        cursor = conn.cursor(cursor_factory=DictCursor)

        # Récupérer les informations des étudiants
        query = """
        SELECT users.username AS name, users.filiere, users.image_pure AS photo, COUNT(absence.id) AS absences ,users.id
        FROM users
        LEFT JOIN absence ON users.id = absence.id_ab
        GROUP BY users.id;
        """
        cursor.execute(query)
        students_data = cursor.fetchall()

        # Créer une ligne pour chaque étudiant
        for student_data in students_data:
            student_line_layout = QHBoxLayout()  
            photo_label = QLabel()
            # Photo de l'étudiant
            if student_data['photo']:
                try:
                    # Vérifier si les données de l'image sont valides
                    if isinstance(student_data['photo'], bytes) and len(student_data['image_pure']) > 0:
                        image_data = student_data['photo']
                        pixmap = QPixmap()
                        
                        # Tenter de charger l'image à partir des données
                        if not pixmap.loadFromData(image_data):
                            print("Erreur : impossible de charger l'image à partir du BLOB.")
                            raise ValueError("Impossible de charger l'image à partir du BLOB.")
                        
                        # Vérifier si le pixmap est valide (ne pas redimensionner un pixmap vide)
                        if pixmap.isNull():
                            print("Erreur : l'image est invalide après le chargement.")
                            raise ValueError("L'image est invalide après le chargement.")
                        
                        # Si l'image est valide, redimensionner
                        photo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                    else:
                        # Image par défaut si les données ne sont pas valides
                        default_pixmap = QPixmap("default_image_path.jpg")  # Remplacez par le chemin de l'image par défaut
                        photo_label.setPixmap(default_pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                except Exception as e:
                    print(f"Erreur lors du chargement de l'image: {e}")
                    # Image par défaut en cas d'erreur
                    default_pixmap = QPixmap("default_image_path.jpg")  # Remplacez par le chemin de l'image par défaut
                    photo_label.setPixmap(default_pixmap.scaled(100, 100, Qt.KeepAspectRatio))
            else:
                # Image par défaut si aucune photo n'est disponible
                default_pixmap = QPixmap("default_image_path.jpg")  # Remplacez par le chemin de l'image par défaut
                photo_label.setPixmap(default_pixmap.scaled(100, 100, Qt.KeepAspectRatio))



            # Nom, Filière et Pourcentage d'absences
            name_label = QLabel(f"Nom: {student_data['name']}")
            filiere_label = QLabel(f"Filière: {student_data['filiere']}")
            absences_label = QLabel(f"Absences: {student_data['absences']}")

            # Définir une taille fixe pour les labels d'information]\[\
            
            
            name_label.setStyleSheet("border: 1px red; font-size:16px")  
            filiere_label.setStyleSheet("border: 1px red;font-size:16px")
            absences_label.setStyleSheet("border: 1px red;font-size:16px")
            
            # Ajouter les informations dans la ligne (layout horizontal)
            student_line_layout.addWidget(photo_label)
            student_line_layout.addWidget(name_label)
            student_line_layout.addWidget(filiere_label)
            student_line_layout.addWidget(absences_label)

            # Ajouter un bouton de suppression
            delete_button = QPushButton("Supprimer")
            delete_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px; border-radius: 5px;font-size:20px")
            
            # Utiliser une fonction intermédiaire pour capturer student_id
            def connect_delete_button(button, student_id):
                button.clicked.connect(lambda checked, student_id=student_id: self.delete_student(student_id))

            connect_delete_button(delete_button, student_data['id'])
            
            student_line_layout.addWidget(delete_button)

            # Ajouter cette ligne au layout principal
            student_layout.addLayout(student_line_layout)

        # Appliquer le layout au `info_display_area`
        container_widget.setLayout(student_layout)
        scroll_area.setWidget(container_widget)  # Mettre le widget conteneur dans le QScrollArea
        self.info_display_area.addWidget(scroll_area)  # Ajouter le QScrollArea au QStackedWidget
        self.info_display_area.setCurrentWidget(scroll_area)  # Afficher cette page

        # Fermer la connexion et le curseur
        cursor.close()
    def show_add_student_interface(self):
        # Supprimer tous les widgets précédemment affichés
        for i in range(self.info_display_area.count()):
            widget = self.info_display_area.widget(i)
            if widget:
                self.info_display_area.removeWidget(widget)
                widget.deleteLater()
        
        # Ajouter une instance de AddStudentInterface
        add_student_widget = AddStudentInterface(self)
        self.info_display_area.addWidget(add_student_widget)
        self.info_display_area.setCurrentWidget(add_student_widget)

    def delete_student(self, student_id):
        # Confirmation de la suppression
        reply = QMessageBox.question(self, 'Confirmation', 'Êtes-vous sûr de vouloir supprimer cet étudiant ?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Vérifier si la connexion est ouverte
                if conn.closed != 0:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1;")

                cursor = conn.cursor()
                # Exécuter la requête pour supprimer l'étudiant
                delete_query = "DELETE FROM users WHERE id = %s"
                cursor.execute(delete_query, (student_id,))
                conn.commit()  # Valider les changements dans la base de données

                # Informer l'utilisateur que la suppression a été effectuée
                QMessageBox.information(self, 'Succès', 'L\'étudiant a été supprimé avec succès.')

                # Rafraîchir la liste des étudiants après la suppression
                self.view_student_info()

            except Exception as e:
                QMessageBox.critical(self, 'Erreur', f'Erreur lors de la suppression de l\'étudiant: {e}')
            finally:
                cursor.close()





class NotifiInterface(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget  # Référence au QStackedWidget pour la navigation

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Section titre avec bouton Home et titre centré
        title_section = QHBoxLayout()

        # Bouton Home avec icône
        home_btn = QPushButton("Home")
        home_btn.setIcon(QIcon("path_to_home_icon.png"))  # Remplace par le chemin vers ton icône
        home_btn.setStyleSheet(
            """
            QPushButton {
                padding: 10px; 
                font-size: 16px; 
                border-radius: 8px; 
                background-color: #90c695; 
                color: white;
            }
            QPushButton:hover {
                background-color: #77ab85;
            }
            """
        )
        home_btn.setCursor(Qt.PointingHandCursor)
        title_section.addWidget(home_btn, alignment=Qt.AlignLeft)

        # Spacer pour centrer le titre
        title_section.addStretch(1)

        # Label du titre
        title_label = QLabel("Votre Boîte Email")
        title_label.setFont(QFont("Helvetica", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_section.addWidget(title_label)

        # Spacer pour équilibrer le layout
        title_section.addStretch(1)

        # Ajouter le layout de titre au layout principal
        main_layout.addLayout(title_section)

        # Connecter le bouton Home pour naviguer
        home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Section Liste des Emails
        email_section_layout = QVBoxLayout()
        email_label = QLabel("📬 Liste des Emails")
        email_label.setFont(QFont("Arial", 23 ,QFont.Bold))
        email_section_layout.addWidget(email_label)

        # Ajout du tableau pour les emails
        self.email_table = QTreeWidget(self)
        self.email_table.setColumnCount(3)
        self.email_table.setHeaderLabels(["📌 Sujet", "✉️ Expéditeur", "🗓️ Date d'envoi"])
        # Appliquer la feuille de style comme précédemment
        self.email_table.setStyleSheet(
    """
    QTreeWidget {
        background-color: #f7f7f7; 
        border: 1px solid #ccc; 
        font-size: 16px; 
        alternate-background-color: #f0f0f0; /* Couleur des lignes paires */
    }
    QTreeWidget::item {
        height: 40px;
        padding: 5px;
    }
    QTreeWidget::item:hover {
        background-color: #e8f5e9; /* Vert clair pour le survol */
    }
    QTreeWidget::item:selected {
        background-color: #c8e6c9; /* Vert pastel pour la sélection */
        color: black;
    }
    QHeaderView::section {
        background-color: #007bff; /* Bleu moderne */
        color: white; /* Texte blanc pour une meilleure visibilité */
        font-size: 18px;  /* Taille de la police ajustée */
        font-weight: bold; 
        padding: 10px 5px;  /* Espacement augmenté pour plus de lisibilité */
        border: none; /* Enlève la bordure */
        text-align: center;
    }
    """
)

# Rendre les colonnes de largeur égale
        header = self.email_table.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Colonne 0
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Colonne 1
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Colonne 2
# Ajoutez d'autres colonnes si nécessaire en ajustant les indices.



        email_section_layout.addWidget(self.email_table)



        # Remplir le tableau avec les emails
        for subject, sender, content, date in emails:
            item = QTreeWidgetItem(self.email_table, [subject, sender, date])
            item.setData(0, Qt.UserRole, (subject, sender, content, date))

        main_layout.addLayout(email_section_layout)

        # Zone Détails Email
        details_section_layout = QVBoxLayout()
        details_label = QLabel("Détails de l'Email")
        details_label.setFont(QFont("Arial", 21, QFont.Bold))
        details_section_layout.addWidget(details_label)

        self.details_text = QTextEdit(self)
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("background-color: #f9f9f1; font-size: 18px; padding: 10px;")
        details_section_layout.addWidget(self.details_text)

        main_layout.addLayout(details_section_layout)

        # Connecter l'affichage des détails
        self.email_table.itemClicked.connect(self.show_email_details)

    def show_email_details(self, item):
        """Affiche les détails de l'email sélectionné dans le QTextEdit"""
        subject, sender, content, date = item.data(0, Qt.UserRole)
        details = (
            f"Sujet : {subject}\n"
            f"Expéditeur : {sender}\n"
            f"Date d'envoi : {date}\n\n"
            f"Contenu :\n{content}"
        )
        self.details_text.setText(details)



class AbsenceAnalyticsInterface(QWidget):
    def __init__(self, stacked_widget, app_reference):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.app_reference = app_reference

        # Création du layout principal avec marges pour entourer le contenu
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Section de titre et bouton Home
        title_section = QHBoxLayout()

        # Ajouter le bouton Home à gauche
        home_btn = QPushButton("Home")
        home_btn.setIcon(QIcon("C:\\Users\\Any\\OneDrive\\Desktop\\mini-project_getion_absences\\app\\norvrh-module-gta.png"))
        home_btn.setStyleSheet("padding: 10px; font-size: 16px; border-radius: 8px; background-color: #90c695; ")
        home_btn.setCursor(Qt.PointingHandCursor)
        home_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Ajouter le bouton Home dans un layout séparé pour faciliter l'alignement
        home_layout = QHBoxLayout()
        home_layout.addWidget(home_btn)
        home_layout.addStretch(1)  # Ajouter un espace flexible après le bouton Home

        # Ajouter un espace flexible pour centrer le titre
        title_section.addLayout(home_layout)
        title_section.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Création du titre centré
        title_label = QLabel("Manage Statistiques des Absences")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_section.addWidget(title_label)

        # Ajouter un autre espace flexible après le titre
        title_section.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        main_layout.addLayout(title_section)

        # Espace entre le titre et les boutons d'action
        main_layout.addSpacing(20)

        # Création des boutons d'actions alignés sur une même ligne
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        button_style = "padding: 10px; background-color: #6dc9f2; border-radius: 12px; font-size: 14px;"
        

        par_filiere_btn = QPushButton("Statistiques par filière")
        par_filiere_btn.setStyleSheet(button_style)
        par_filiere_btn.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(par_filiere_btn)

        par_somaine_btn = QPushButton("Statistiques par Somaine")
        par_somaine_btn.setStyleSheet(button_style)
        par_somaine_btn.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(par_somaine_btn)

        par_temps_btn = QPushButton("Statistiques par temps")
        par_temps_btn.setStyleSheet(button_style)
        par_temps_btn.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(par_temps_btn)

        main_layout.addLayout(actions_layout)

        # Espace entre les boutons d'action et le graphique
        main_layout.addSpacing(30)

        # Initialisation de la figure (graphique) et ajout au layout
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedHeight(int(self.height() * 1.5))  # Limite la taille du graphique à 80% de la fenêtre
        main_layout.addWidget(self.canvas)

        # Connecter les boutons aux méthodes
        par_filiere_btn.clicked.connect(self.show_absence)
        par_temps_btn.clicked.connect(self.show_absence_temp)
        par_somaine_btn.clicked.connect(self.show_par_somaine)
        home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
    
    def show_absence_temp(self):
        cursor = conn.cursor()

        # Exécuter la requête pour récupérer les données d'absence par heure
        cursor.execute("""
            SELECT time, COUNT(time)
            FROM absence  
            GROUP BY time 
        """)

        list_time = []
        list_nb = []

        # Ajouter les données dans les listes
        for t, nb in cursor.fetchall():
            list_time.append(t)
            list_nb.append(nb)

        # Fermer le curseur
        cursor.close()

        # Effacer le contenu précédent de la figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Tracer le graphique en camembert
        wedges, texts, autotexts = ax.pie(
            list_nb, labels=list_time, autopct='%1.1f%%', startangle=90,
            textprops={'color': 'white', 'bbox': dict(facecolor='black', alpha=0.8, edgecolor='none')}
        )

        # Personnaliser les labels de pourcentage
        for autotext in autotexts:
            autotext.set_bbox(dict(facecolor='black', edgecolor='none', alpha=0.8))
            autotext.set_color('white')

        # Titre et légende
        ax.set_title("Temps d'absences", color='black')
        ax.legend(wedges, list_time, title="Temps", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        # Rafraîchir le canvas pour afficher le graphique
        self.canvas.draw()
    def show_absence(self):
        # Exécution d'une requête pour obtenir les données
        cursor = conn.cursor()
        cursor.execute("""
            SELECT filiere, COUNT(filiere)
            FROM users u JOIN absence a ON a.id = u.id
            GROUP BY filiere
        """)

        list_filiere = []
        list_nombre_absences = []
        for f, ab in cursor.fetchall():
            list_filiere.append(f)
            list_nombre_absences.append(ab)


        # Création et mise à jour du graphique
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        colors = plt.cm.viridis(np.linspace(0, 1, len(list_filiere)))
        bars = ax.bar(list_filiere, list_nombre_absences, color=colors)

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), ha='center', va='bottom', fontsize=12)

        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title("Absences par filière", color='black')
        ax.set_xlabel("Filière", fontsize=14, color='red')
        ax.set_ylabel("Total des Absences", fontsize=12, color='green')

        # Mise à jour de la figure sur le canvas
        self.canvas.draw()

    def show_par_somaine(self):
    
        cursor=conn.cursor()
        # Exécuter la requête pour récupérer les données d'absence
        cursor.execute("""
            SELECT date, COUNT(id) 
FROM absence  
WHERE date BETWEEN CURRENT_DATE - INTERVAL '7 days' AND CURRENT_DATE
GROUP BY date
ORDER BY date;

        """)

        today = datetime.datetime.now()
        seven_days_ago = (today - datetime.timedelta(days=7)).date()
        current_day = today.date()

        # Initialiser les listes pour les données d'absence et les dates
        list_absence = []
        list_date = []

        # Ajouter les données dans les listes
        for date, ab in cursor.fetchall():
            list_absence.append(ab)
            list_date.append(date)

        # Fermer la connexion à la base de données

        # Effacer le contenu précédent de la figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Tracer les données
        ax.plot(list_date, list_absence, marker='o', linestyle='-', color='black', label='Total d\'absences')

        # Ajouter des annotations pour chaque point avec la date et le total d'absences
        for date, ab in zip(list_date, list_absence):
            ax.annotate(f"{date.strftime('%Y-%m-%d')}: {ab}", (date, ab), 
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center', fontsize=11, color='white',
                        bbox=dict(facecolor='black', alpha=0.9))  # Fond noir avec transparence

        # Formater l'axe des x pour afficher les dates de manière lisible
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
        self.figure.autofmt_xdate()  # Rotation des dates

        # Ajustement dynamique de l'axe y
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # Permet des valeurs entières sur l'axe y

        # Ajouter un titre et des labels avec couleurs spécifiques
        ax.set_title(
            f"Absences au fil du temps Semaine : {seven_days_ago} => {current_day}",
            fontsize=17, color='black', bbox=dict(facecolor='red', alpha=0.1)
        )
        ax.set_xlabel("Date", fontsize=15, color='red', bbox=dict(facecolor='red', alpha=0.1))
        ax.set_ylabel("Total des Absences", fontsize=15, color='green', bbox=dict(facecolor='green', alpha=0.1))

        # Afficher la légende
        ax.legend()

        # Rafraîchir le canvas pour afficher le graphique
        self.canvas.draw()

class AbsenceManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Absence Manager")
        self.setGeometry(100, 100, 1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.home_interface = AbsenceManagerHome(self.stacked_widget, self)
        self.stacked_widget.addWidget(self.home_interface)
        self.notif = NotifiInterface(self.stacked_widget)
        self.stacked_widget.addWidget(self.notif)
        self.analytics = AbsenceAnalyticsInterface(self.stacked_widget,self)
        self.stacked_widget.addWidget(self.analytics)

        self.manage_users_interface = ManageUsersInterface(self.stacked_widget)
        self.stacked_widget.addWidget(self.manage_users_interface)

    def run_record_absence_script(self):
        try:
            subprocess.run(['python', r'app\\classes\\recorder.py'])
            print("insert.py script executed successfully.")
        except Exception as e:
            print(f"Error executing script: {e}")
    def closeEvent(self, event):
        """Fermer la connexion à la base de données en quittant."""
        conn.close()
        event.accept()

app = QApplication(sys.argv)
window = AbsenceManagerApp()
window.show()

sys.exit(app.exec_())
