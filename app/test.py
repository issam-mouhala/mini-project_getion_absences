import cv2
import face_recognition

# Chemin vers la photo de référence d'Issam
reference_image_path = r"C:\Users\Any\OneDrive\Desktop\mini-project_getion_absences\app\norvrh-module-gta.png"

# Charger et encoder l'image de référence d'Issam
reference_image = face_recognition.load_image_file(reference_image_path)
reference_encoding = face_recognition.face_encodings(reference_image)[0]

# Initialiser la capture vidéo
cap = cv2.VideoCapture(0)

while True:
    # Lire une image de la caméra
    ret, frame = cap.read()
    if not ret:
        print("Erreur de capture vidéo.")
        break

    # Convertir l'image de la caméra du format BGR au format RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Trouver toutes les localisations et encodages de visages dans l'image actuelle
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Comparer chaque visage détecté avec la référence d'Issam
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces([reference_encoding], face_encoding)
        name = "Inconnu"

        # Si le visage correspond à celui d'Issam
        if True in matches:
            name = "Issam"

        # Dessiner un rectangle autour du visage et afficher le nom
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Afficher le flux vidéo
    cv2.imshow('Face Recognition', frame)

    # Quitter avec la touche 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()
