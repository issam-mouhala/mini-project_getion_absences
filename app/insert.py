import face_recognition
import mysql.connector
import numpy as np
import pickle

# Connexion à la base de données
conn = mysql.connector.connect(
    host='localhost',  # Remplacez par votre hôte, par défaut c'est 'localhost'
    user='root',       # Remplacez par votre nom d'utilisateur MySQL
    password='',       # Remplacez par votre mot de passe MySQL
    database='miniproject'  # Remplacez par le nom de votre base de données
)

cursor = conn.cursor()
# Charger une image de référence et obtenir l'encodage
image_path = r"C:\\Users\\Any\\OneDrive\\Desktop\\mini-project_getion_absences\\download.jpeg"
with open(image_path, 'rb') as file:
            img_data = file.read()
            file.close()

reference_image = face_recognition.load_image_file(image_path)

reference_encoding = face_recognition.face_encodings(reference_image)[0]
encoded_binary = pickle.dumps(reference_encoding)

# Insérer l'encodage dans la base de données
name = "mostafa"
filiere="BDIASD"
insert_query = "INSERT INTO users (username, image,image_pure,filiere) VALUES (%s, %s,%s,%s)"
cursor.execute(insert_query, (name, encoded_binary,img_data,filiere))
conn.commit()

print("Encodage inséré dans la base de données.")
