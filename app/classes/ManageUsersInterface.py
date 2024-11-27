import sys
import datetime
import subprocess
import psycopg2
from psycopg2.extras import DictCursor
import AbsenceAnalyticsInterface
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

class AddStudentInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conn = psycopg2.connect(
        host='localhost',
        user='docker',  # Nom d'utilisateur PostgreSQL
        password='docker',  # Mot de passe PostgreSQL
        database='miniproject'  # Nom de la base de données
    )
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
        self.username_input.setStyleSheet("padding: 10px; border: 1px solid bleu; border-radius: 5px;")
        form_layout.addWidget(self.username_input)

        # Choix de la filière avec un QComboBox
        self.filiere_input = QComboBox(self)
        self.filiere_input.addItems(["MGSI", "GL", "SDBDIA", "SCITCN"])
        self.filiere_input.setStyleSheet("padding: 10px; border: 1px solid bleu; border-radius: 5px;")
        form_layout.addWidget(self.filiere_input)

        # Champ pour afficher le nom de l'image
        self.image_path_display = QLineEdit(self)
        self.image_path_display.setPlaceholderText("No image selected")
        self.image_path_display.setStyleSheet("padding: 10px; border: 1px solid bleu; border-radius: 5px;")
        self.image_path_display.setReadOnly(True)
        form_layout.addWidget(self.image_path_display)

        # Bouton pour sélectionner une image
        select_image_button = QPushButton("Select Image")
        select_image_button.clicked.connect(self.select_image)
        select_image_button.setStyleSheet("padding: 10px;font-size:15px; border: 1px solid bleu; border-radius: 5px;")

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
            
            if self.conn is None:
                self.show_error("Failed to connect to the database.")
                return
            
            with open(image_path, 'rb') as file:
                photo_blob = file.read()

            cursor = self.conn.cursor()

            # Insertion dans la base de données
            insert_query = "INSERT INTO users (username, filiere, image,image_pure,accept) VALUES (%s, %s,%s , %s,0)"
            cursor.execute(insert_query, (name, filiere, encoded_binary,photo_blob))
            self.conn.commit()
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
            if self.conn.closed != 0:
             cursor = self.conn.cursor()
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
        self.conn = psycopg2.connect(
        host='localhost',
        user='docker',  # Nom d'utilisateur PostgreSQL
        password='docker',  # Mot de passe PostgreSQL
        database='miniproject'  # Nom de la base de données
    )
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
        if self.conn.closed != 0:
             cursor = self.conn.cursor()
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
        cursor = self.conn.cursor(cursor_factory=DictCursor)

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
                button.clicked.connect(lambda  student_id=student_id: self.delete_student(student_id))

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
            if widget := self.info_display_area.widget(i):
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
                if self.conn.closed != 0:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT 1;")

                cursor = self.conn.cursor()
                # Exécuter la requête pour supprimer l'étudiant
                delete_query = "DELETE FROM users WHERE id = %s"
                cursor.execute(delete_query, (student_id,))
                self.conn.commit()  # Valider les changements dans la base de données

                # Informer l'utilisateur que la suppression a été effectuée
                QMessageBox.information(self, 'Succès', 'L\'étudiant a été supprimé avec succès.')

                # Rafraîchir la liste des étudiants après la suppression
                self.view_student_info()

            except Exception as e:
                QMessageBox.critical(self, 'Erreur', f'Erreur lors de la suppression de l\'étudiant: {e}')
            finally:
                cursor.close()

