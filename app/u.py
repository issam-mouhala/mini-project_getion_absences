import mysql.connector
conn = mysql.connector.connect(
            host='localhost',  
            user='root',       
            password='',       
            database='mini-project'  
        )
cursor = conn.cursor()

        # Exécuter la requête SQL pour récupérer les données d'absence
cursor.execute("""
            SELECT filiere, COUNT(filiere) 
            FROM users u JOIN absence a ON a.id=u.id 
            GROUP BY filiere
        """)
global list_filiere,list_nombre_absences
list_filiere = []
list_nombre_absences = []
# Ajouter les données dans les listes
for f, ab in cursor.fetchall():
            list_nombre_absences.append(ab)
            list_filiere.append(f)