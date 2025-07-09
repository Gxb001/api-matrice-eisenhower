import requests

# Configuration de l'URL de base de l'API
BASE_URL = "http://localhost:5000/api"


# Fonction pour vérifier le succès d'une requête
def check_response(response, action):
    status = "SUCCÈS" if response.status_code in [200, 201] else f"ÉCHEC ({response.status_code})"
    print(f"{action}: {status}")
    if response.status_code not in [200, 201]:
        print(f"Erreur: {response.text}")
    try:
        print(f"Réponse: {response.json()}")
    except:
        print("Aucune réponse JSON")
    return response


# Fonction pour tenter une connexion ou créer un utilisateur
def login_or_create_user(session, name, password, role):
    print(f"\n=== Tentative de connexion pour {name} ===")
    login_data = {"name_util": name, "password": password}
    response = check_response(
        session.post(f"{BASE_URL}/login", json=login_data),
        f"Connexion {name}"
    )
    if response.status_code == 200:
        data = response.json()
        user_id = data.get('user_id')
        jwt_token = data.get('access_token')
        print(f"User ID: {user_id}")
        print(f"JWT Token: {jwt_token}")
        return user_id, jwt_token

    print(f"\n=== Création de l'utilisateur {name} ===")
    user_data = {"name_util": name, "password": password, "role": role}
    response = check_response(
        session.post(f"{BASE_URL}/register", json=user_data),
        f"Création {name}"
    )
    if response.status_code == 201:
        user_id = response.json().get('id')
        response = session.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            jwt_token = data.get('access_token')
            print(f"User ID: {user_id}")
            print(f"JWT Token: {jwt_token}")
            return user_id, jwt_token
    return None, None


# Fonction principale pour tester l'API
def test_api():
    session = requests.Session()

    # Utiliser des identifiants fixes
    user_name = "testuser"
    admin_name = "adminuser"

    # Étape 1 : Connexion ou création de l'utilisateur normal
    user_id, _ = login_or_create_user(session, user_name, "password123", "util")
    if user_id is None:
        print("Impossible de créer ou connecter l'utilisateur normal.")
        return

    # Étape 2 : Connexion ou création de l'utilisateur admin
    admin_id, jwt_token = login_or_create_user(session, admin_name, "admin123", "admin")
    if jwt_token is None:
        print("Impossible de créer ou connecter l'utilisateur admin.")
        return

    # Headers avec le token JWT
    headers = {"Authorization": f"Bearer {jwt_token}"}

    # Étape 3 : Retentative de connexion pour garantir un token valide
    print("\n=== Retentative de connexion pour adminuser ===")
    login_data = {"name_util": admin_name, "password": "admin123"}
    response = check_response(
        session.post(f"{BASE_URL}/login", json=login_data),
        "Connexion adminuser (retentative)"
    )
    if response.status_code == 200:
        jwt_token = response.json().get('access_token')
        headers = {"Authorization": f"Bearer {jwt_token}"}
        print(f"Nouveau JWT Token: {jwt_token}")

    # Étape 4 : Créer un projet
    print("\n=== Création d'un projet ===")
    project_data = {
        "name": "Project Alpha",
        "description": "A test project for Eisenhower Matrix"
    }
    response = check_response(
        session.post(f"{BASE_URL}/projects", json=project_data, headers=headers),
        "Création projet"
    )
    project_id = None
    if response.status_code == 201:
        project_id = response.json().get('id')

    # Étape 5 : Associer l'utilisateur normal au projet
    if project_id:
        print("\n=== Association utilisateur au projet ===")
        user_project_data = {
            "id_user": user_id,
            "id_project": project_id
        }
        check_response(
            session.post(f"{BASE_URL}/user-projects", json=user_project_data, headers=headers),
            "Association utilisateur-projet"
        )

    # Étape 6 : Créer une tâche
    if project_id:
        print("\n=== Création d'une tâche ===")
        task_data = {
            "name": "Test Task",
            "description": "A sample task",
            "urgency": "Urgent",
            "importance": "Important",
            "status": "À faire",
            "plan_date": "2025-07-10",
            "estimation": 5,
            "estimation_unit": "heures",
            "id_project": project_id
        }
        check_response(
            session.post(f"{BASE_URL}/tasks", json=task_data, headers=headers),
            "Création tâche"
        )

    # Étape : Del & update une tâche pour tester la suppression
    if project_id:
        print("\n=== Création d'une tâche pour tester la suppression ===")
        task_data = {
            "name": "Test Task for Deletion",
            "description": "A sample task to delete",
            "urgency": "Urgent",
            "importance": "Important",
            "status": "À faire",
            "plan_date": "2025-07-10",
            "estimation": 5,
            "estimation_unit": "heures",
            "id_project": project_id
        }
        response = check_response(
            session.post(f"{BASE_URL}/tasks", json=task_data, headers=headers),
            "Création tâche pour suppression"
        )
        task_id = None
        if response.status_code == 201:
            task_id = response.json().get('id')

        # Étape : Mettre à jour une tâche
        if project_id and task_id:
            print("\n=== Mise à jour d'une tâche ===")
            update_task_data = {
                "name": "Updated Test Task",
                "description": "Updated sample task",
                "urgency": "Non Urgent",
                "importance": "Non Important",
                "status": "En cours",
                "plan_date": "2025-07-11",
                "estimation": 10,
                "estimation_unit": "heures",
                "id_project": project_id
            }
            check_response(
                session.put(f"{BASE_URL}/tasks/{task_id}", json=update_task_data, headers=headers),
                "Mise à jour tâche"
            )

        if task_id:
            print("\n=== Suppression logique d'une tâche ===")
            check_response(
                session.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers),
                "Suppression tâche"
            )

    # Étape 7 : Lister tous les projets de l'utilisateur
    print("\n=== Liste des projets de l'utilisateur ===")
    check_response(
        session.get(f"{BASE_URL}/projects", headers=headers),
        "Liste projets utilisateur"
    )

    # Étape 8 : Récupérer les détails d'un projet
    if project_id:
        print("\n=== Détails d'un projet ===")
        check_response(
            session.get(f"{BASE_URL}/projects/{project_id}", headers=headers),
            "Détails projet"
        )

    # Étape 9 : Mettre à jour un projet
    if project_id:
        print("\n=== Mise à jour d'un projet ===")
        update_project_data = {
            "name": "Updated Project Alpha",
            "description": "Updated description"
        }
        check_response(
            session.put(f"{BASE_URL}/projects/{project_id}", json=update_project_data, headers=headers),
            "Mise à jour projet"
        )

    # Étape 10 : Supprimer un projet logiquement
    if project_id:
        print("\n=== Suppression logique d'un projet ===")
        check_response(
            session.delete(f"{BASE_URL}/projects/{project_id}", headers=headers),
            "Suppression projet"
        )

    # Étape 11 : Restaurer un projet
    if project_id:
        print("\n=== Restauration d'un projet ===")
        check_response(
            session.patch(f"{BASE_URL}/projects/{project_id}/restore", headers=headers),
            "Restauration projet"
        )

    # Étape 12 : Supprimer l'association utilisateur-projet
    if project_id:
        print("\n=== Suppression association utilisateur-projet ===")
        check_response(
            session.delete(f"{BASE_URL}/user-projects/{user_id}/{project_id}", headers=headers),
            "Suppression association utilisateur-projet"
        )

    # Étape 13 : Lister les projets d'un utilisateur spécifique
    print("\n=== Liste des projets d'un utilisateur ===")
    check_response(
        session.get(f"{BASE_URL}/users/{user_id}/projects", headers=headers),
        "Liste projets utilisateur spécifique"
    )

    # Étape 14 : Récupérer les tâches d'un projet
    if project_id:
        print("\n=== Liste des tâches d'un projet ===")
        check_response(
            session.get(f"{BASE_URL}/tasks/project/{project_id}", headers=headers),
            "Liste tâches projet"
        )

    # Étape 15 : Récupérer les tâches par matrice d'Eisenhower
    print("\n=== Tâches par matrice Eisenhower ===")
    check_response(
        session.get(f"{BASE_URL}/tasks/matrix/{user_id}", headers=headers),
        "Tâches matrice Eisenhower"
    )

    # Étape 16 : Filtrer les tâches
    print("\n=== Filtrage des tâches ===")
    check_response(
        session.get(f"{BASE_URL}/tasks/filter?status=En%20cours&urgency=Urgent", headers=headers),
        "Filtrage tâches"
    )

    # Étape 17 : Lister tous les utilisateurs
    print("\n=== Liste de tous les utilisateurs ===")
    check_response(
        session.get(f"{BASE_URL}/users", headers=headers),
        "Liste utilisateurs"
    )

    # Étape 18 : Mettre à jour le rôle d'un utilisateur
    print("\n=== Mise à jour rôle utilisateur ===")
    update_role_data = {
        "role": "admin"
    }
    check_response(
        session.patch(f"{BASE_URL}/users/{user_id}/role", json=update_role_data, headers=headers),
        "Mise à jour rôle"
    )

    # Étape 19 : Statistiques des tâches d'un utilisateur
    print("\n=== Statistiques des tâches utilisateur ===")
    check_response(
        session.get(f"{BASE_URL}/tasks/stats/{user_id}", headers=headers),
        "Statistiques tâches utilisateur"
    )

    # Étape 20 : Statistiques des tâches d'un projet
    if project_id:
        print("\n=== Statistiques des tâches projet ===")
        check_response(
            session.get(f"{BASE_URL}/projects/{project_id}/stats", headers=headers),
            "Statistiques tâches projet"
        )


if __name__ == "__main__":
    test_api()
