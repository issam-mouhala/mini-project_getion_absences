import pickle
import mysql.connector
from PIL import Image
import io

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    host='localhost',  # Remplacez par votre hôte, par défaut c'est 'localhost'
    user='root',       # Remplacez par votre nom d'utilisateur MySQL
    password='',       # Remplacez par votre mot de passe MySQL
    database='miniproject'  # Remplacez par le nom de votre base de données
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
read_image(3)

# Fermer la connexion
cursor.close()
conn.close()
