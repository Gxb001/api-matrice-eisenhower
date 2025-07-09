import json

import requests

# Configuration de l'URL de base de l'API
BASE_URL = "http://localhost:5000/api"


# Fonction pour vérifier le succès d'une requête
def check_response(response, action):
    status = "SUCCÈS" if response.status_code == 200 else f"ÉCHEC ({response.status_code})"
    print(f"{action}: {status}")
    if response.status_code != 200:
        print(f"Erreur: {response.text}")
    return response


# Fonction pour se connecter
def login():
    session = requests.Session()

    # Données de connexion
    login_data = {
        "name_util": "adminuser",  # Remplacez par votre nom d'utilisateur
        "password": "admin123"  # Remplacez par votre mot de passe
    }

    print("\n=== Tentative de connexion ===")
    response = check_response(
        session.post(f"{BASE_URL}/login", json=login_data),
        "Connexion"
    )

    if response.status_code == 200:
        try:
            data = response.json()
            jwt_token = data.get('access_token')
            user_id = data.get('user_id')
            print(f"JWT Token: {jwt_token}")
            print(f"User ID: {user_id}")
            return jwt_token, user_id
        except json.JSONDecodeError:
            print("Erreur: La réponse n'est pas au format JSON")
            return None, None
    return None, None


if __name__ == "__main__":
    jwt_token, user_id = login()
    if jwt_token:
        print("\nConnexion réussie ! Vous pouvez utiliser le JWT token pour d'autres requêtes.")
    else:
        print("\nÉchec de la connexion.")
