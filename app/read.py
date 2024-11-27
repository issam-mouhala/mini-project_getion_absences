import pickle
import mysql.connector
from PIL import Image
import io
import psycopg2

# Connexion à la base de données MySQL
conn = psycopg2.connect(
        host='localhost',
        user='docker',  # Nom d'utilisateur PostgreSQL
        password='docker',  # Mot de passe PostgreSQL
        database='miniproject'  # Nom de la base de données
    )

cursor = conn.cursor()


def read_image(image_id):
    """Lire et afficher une image depuis la base de données."""
    cursor.execute('SELECT username, image_pure FROM users WHERE id = %s', (image_id,))
    if record := cursor.fetchone():
        image_name, img_data = record
        print(f'Taille des données d\'image : {len(img_data)} octets')

        try:
            # Charger l'image à partir des données binaires
            image = Image.open(io.BytesIO(img_data))
            image.show()  # Afficher l'image
            print(f'Image {image_name} affichée avec succès.')
        except Exception as e:
            print(f'Erreur lors de l\'ouverture de l\'image : {e}')
    else:
        print('Image non trouvée.')


# Lire et afficher l'image avec l'ID 1
read_image(17)

# Fermer la connexion
cursor.close()
conn.close()
