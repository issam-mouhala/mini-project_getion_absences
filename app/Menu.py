
import datetime
from matplotlib import dates, pyplot as plt
from matplotlib.ticker import MaxNLocator
import mysql.connector
import numpy as np  
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QSpacerItem, QSizePolicy, QMainWindow, QComboBox,QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QGridLayout, QListWidget, QListWidgetItem, QCalendarWidget, QLineEdit, QStackedWidget
from PyQt5.QtCore import Qt , QDate
from PyQt5.QtWidgets import QApplication , QSizePolicy, QSpacerItem,QMessageBox, QScrollArea,QMainWindow, QLabel, QVBoxLayout ,QHBoxLayout, QWidget, QPushButton, QGridLayout, QListWidget, QListWidgetItem, QCalendarWidget, QLineEdit, QStackedWidget,QProgressBar, QDialog, QFileDialog
from PyQt5.QtGui import QPixmap ,QCursor

from PyQt5.QtGui import QIcon, QFont,QCursor
import subprocess
import sys

conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='miniproject'
                )
               






        # Fetch absence data from the database

class AbsenceManagerHome(QWidget):
    def __init__(self, stacked_widget, app_reference):
        super().__init__()
        self.stacked_widget = stacked_widget  # Référence au QStackedWidget
        self.app_reference = app_reference  # Référence à l'application principale
        # Disposition principale pour l'interface d'accueil
        main_layout = QVBoxLayout(self)

        # Boutons de navigation en haut
        nav_layout = QHBoxLayout()
        home_btn = QPushButton("Home")
        record_absence_btn = QPushButton("Record Absence")
        manage_users_btn = QPushButton("Manage Users")  # Passer à l'interface de gestion des utilisateurs
        absence_analysis_btn = QPushButton("Absence Analysis")

        home_btn.setStyleSheet("background-color: #a6e3a1; padding: 10px; font-size: 14px; border-radius: 12px; cursor: pointer;")
        record_absence_btn.setStyleSheet("background-color: #a6e3a1; padding: 10px; font-size: 14px; border-radius: 12px; cursor: pointer;")
        manage_users_btn.setStyleSheet("background-color: #a6e3a1; padding: 10px; font-size: 14px; border-radius: 12px; cursor: pointer;")
        absence_analysis_btn.setStyleSheet("background-color: #a6e3a1; padding: 10px; font-size: 14px; border-radius: 12px; cursor: pointer;")

        nav_layout.addWidget(home_btn)
        nav_layout.addWidget(record_absence_btn)
        nav_layout.addWidget(manage_users_btn)
        nav_layout.addWidget(absence_analysis_btn)
        main_layout.addLayout(nav_layout)

        # Contenu principal pour l'interface d'accueil
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setStyleSheet("background-color: #f0f0f0; border-radius: 10px;")
        self.grid_layout.addWidget(self.calendar_widget, 0, 0, 2, 1)
        self.calendar_widget.clicked[QDate].connect(self.get_selected_date)
        

        # Autres sections comme Absences à venir, Notifications, etc.
        self.upcoming_absences_label = QLabel("Listes des  Absences")
        self.upcoming_absences_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        self.upcoming_absences_list = QListWidget()
        


        notifications_label = QLabel("Notifications")
        notifications_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        notifications_list = QListWidget()
        for i in range(3):
            item = QListWidgetItem(f"Notification {i+1}")
            notifications_list.addItem(item)
        self.grid_layout.addWidget(notifications_label, 0, 2)
        self.grid_layout.addWidget(notifications_list, 1, 2)

        statistics_label = QLabel("Your Statistics")
        statistics_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        statistics_list = QListWidget()
        for stat in ["Absences Inbox: 5", "Total Absences: 12", "Users: 9", "Time Spent Absent: 11:34:12"]:
            item = QListWidgetItem(stat)
            statistics_list.addItem(item)
        self.grid_layout.addWidget(statistics_label, 2, 0)
        self.grid_layout.addWidget(statistics_list, 3, 0)

        new_absences_label = QLabel("New Absence Records")
        new_absences_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        new_absences_list = QListWidget()
        for i in range(5):
            item = QListWidgetItem(f"Record {i+1}: Approved")
            new_absences_list.addItem(item)
        self.grid_layout.addWidget(new_absences_label, 2, 1)
        self.grid_layout.addWidget(new_absences_list, 3, 1)

        your_stats_label = QLabel("Your Stats")
        your_stats_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        your_stats_list = QListWidget()
        for stat in ["Absences: 12", "Users: 9", "Success Rate: 99%"]:
            item = QListWidgetItem(stat)
            your_stats_list.addItem(item)
        self.grid_layout.addWidget(your_stats_label, 2, 2)
        self.grid_layout.addWidget(your_stats_list, 3, 2)

        achievements_label = QLabel("Your Achievements")
        achievements_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        achievements_layout = QHBoxLayout()
        for achievement in ["Attendance", "Fast Absence", "Growth Hero", "Explorer", "Newbie"]:
            label = QLabel(achievement)
            label.setStyleSheet("background-color: #a6e3a1; padding: 10px; border-radius: 10px;")
            achievements_layout.addWidget(label)
        main_layout.addWidget(achievements_label)
        main_layout.addLayout(achievements_layout)

        # Connecter le bouton "Record Absence" à la fonction du script
        record_absence_btn.clicked.connect(self.app_reference.run_record_absence_script)

        # Signal pour passer à l'interface de gestion des utilisateurs
        manage_users_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        absence_analysis_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
    def get_selected_date(self, date):
        formatted_date = date.toString("yyyy/MM/dd")
        self.upcoming_absences_list.clear()

        cursor = conn.cursor()
        print(formatted_date)
        # Exécuter la requête pour récupérer les données d'absence par heure
        cursor.execute("""
           SELECT u.username
           FROM absence a
           JOIN users u ON a.id = u.id
           WHERE a.date = DATE(%s)
           """,(formatted_date,))
        liste=cursor.fetchall()
        if liste==[]:

            item = QListWidgetItem("No Absences ...")
            self.upcoming_absences_list.addItem(item)
        else:
            for j, in liste:
                item = QListWidgetItem(j)
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
        home_btn.setStyleSheet("padding: 10px; font-size: 16px; border-radius: 8px; background-color: #90c695;cursor: pointer;")
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

        # Search and action section
        search_section = QHBoxLayout()
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Enter category...")
        search_bar.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 5px;")
        search_section.addWidget(search_bar)

        search_button = QPushButton("Search")
        search_button.setStyleSheet("padding: 8px 15px; background-color: #90c695; color: white; border-radius: 5px;")
        search_section.addWidget(search_button)

        main_layout.addLayout(search_section)

        actions_layout = QHBoxLayout()
        button_style = "padding: 10px; background-color: #6dc9f2; border-radius: 12px; font-size: 14px;cursor: pointer;"

        add_student_btn = QPushButton("Add Student")
        add_student_btn.setStyleSheet(button_style)
        add_student_btn.clicked.connect(self.add_student)
        actions_layout.addWidget(add_student_btn)

        view_student_info_btn = QPushButton("View Student Info")
        view_student_info_btn.setStyleSheet(button_style)
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
        if not conn.is_connected():
            conn.ping(reconnect=True)

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
        cursor = conn.cursor(dictionary=True)

        # Récupérer les informations des étudiants
        query = """
        SELECT users.username AS name, users.filiere, users.image_pure AS photo, COUNT(absence.id) AS absences
        ,users.id id FROM users
       LEFT JOIN absence ON users.id = absence.id
        GROUP BY users.id;
        """
        cursor.execute(query)
        students_data = cursor.fetchall()
        print(students_data)
        # Créer une ligne pour chaque étudiant
        for student_data in students_data:
            student_line_layout = QHBoxLayout()  

            photo_label = QLabel()
            # Photo de l'étudiant
            if student_data['photo']:
                try:
                    # Vérifier si les données de l'image sont valides
                    if isinstance(student_data['photo'], bytes) and len(student_data['photo']) > 0:
                        image_data = student_data['photo']
                        pixmap = QPixmap()
                
                        if not pixmap.loadFromData(image_data):
                            print("Erreur : impossible de charger l'image à partir du BLOB.")
                        
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
            # Nom, Filière et Pourcentage d'absences
            name_label = QLabel(f"NOM: {student_data['name']}")
            
            filiere_label = QLabel(f"FILIERE: {student_data['filiere']}")
            absences_label = QLabel(f"ABSENCES: {student_data['absences']}")
            # Définir une taille fixe pour les labels d'information
            name_label.setStyleSheet("border: none;font-size:18px")  
            filiere_label.setStyleSheet("border: none;font-size:18px")
            absences_label.setStyleSheet("border: none;font-size:18px")
            
            # Ajouter les informations dans la ligne (layout horizontal)
            student_line_layout.addWidget(photo_label)
            student_line_layout.addWidget(name_label)
            student_line_layout.addWidget(filiere_label)
            student_line_layout.addWidget(absences_label)

            # Ajouter un bouton de suppression
            delete_button = QPushButton("Supprimer")
            delete_button.setIcon(QIcon("norvrh-module-gta.png"))
            delete_button.setCursor(Qt.PointingHandCursor)
            delete_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px; border-radius:1px;font-size:20px")
            
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
        conn.close()
    def add_student(self):
        # Method to run the insert.py script when "Add Student" is clicked
        try:
            subprocess.run(['python', r'insert.py'])
            print("insert.py script executed successfully.")
        except Exception as e:
            print(f"Error executing script: {e}")

    def delete_student(self, student_id):
        # Confirmation de la suppression
        reply = QMessageBox.question(self, 'Confirmation', 'Êtes-vous sûr de vouloir supprimer cet étudiant ?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Vérifier si la connexion est ouverte
                if not conn.is_connected():
                    conn.ping(reconnect=True)

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
                conn.close()
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
        home_btn.setStyleSheet("padding: 10px; font-size: 16px; border-radius: 8px; background-color: #90c695; cursor: pointer;")
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
        button_style = "padding: 10px; background-color: #6dc9f2; border-radius: 12px; font-size: 14px; cursor: pointer;"

        par_filiere_btn = QPushButton("Statistiques par filière")
        par_filiere_btn.setStyleSheet(button_style)
        actions_layout.addWidget(par_filiere_btn)

        par_somaine_btn = QPushButton("Statistiques par Somaine")
        par_somaine_btn.setStyleSheet(button_style)
        actions_layout.addWidget(par_somaine_btn)

        par_temps_btn = QPushButton("Statistiques par temps")
        par_temps_btn.setStyleSheet(button_style)
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
    def closeEvent(self, event):
        """Fermer la connexion à la base de données en quittant."""
        conn.close()
        event.accept()
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
            WHERE date BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE()
            GROUP BY date
            ORDER BY date 
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

        self.analytics = AbsenceAnalyticsInterface(self.stacked_widget,self)
        self.stacked_widget.addWidget(self.analytics)

        self.manage_users_interface = ManageUsersInterface(self.stacked_widget)
        self.stacked_widget.addWidget(self.manage_users_interface)

    def run_record_absence_script(self):
        # Code pour enregistrer une absence ici
       script_path = r"app\\app.py"
       try:
            subprocess.run(["python", script_path], check=True)
       except subprocess.CalledProcessError as e:
            print(f"Failed to run the script: {e}")


app = QApplication(sys.argv)
window = AbsenceManagerApp()
window.show()

sys.exit(app.exec_())
