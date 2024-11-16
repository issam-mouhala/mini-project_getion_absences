
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='miniproject'
    )
    
    print("Connected to the database.")
except mysql.connector.Error as err:
    print(f"Database connection error: {err}")

import sys
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox, QFileDialog, QComboBox
from PyQt5.QtCore import Qt
import mysql.connector
import face_recognition



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
        self.filiere_input.addItems(["MGSI", "IL", "SDBDIA", "SIT"])
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
            insert_query = "INSERT INTO users (username, filiere, image,image_pure) VALUES (%s, %s,%s , %s)"
            cursor.execute(insert_query, (name, filiere, encoded_binary,photo_blob))
            conn.commit()
            print("Data inserted into the database.")  # Debug

            # Confirmation et nettoyage
            self.show_success("Student added successfully.")
            self.clear_form()

        except mysql.connector.Error as db_err:
            self.show_error(f"Database Error: {db_err}")
            print("Database Error:", db_err)  # Debug
        except Exception as e:
            self.show_error(f"Error: {e}")
            print("General Error:", e)  # Debug
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
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


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Absence Management System")
        self.setGeometry(100, 100, 600, 400)

        self.setCentralWidget(AddStudentInterface(self))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApplication()
    main_window.show()
    sys.exit(app.exec_())
