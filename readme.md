# API Matrice d'Eisenhower

Ceci est une API REST basée sur Flask pour gérer les tâches et les projets selon la méthodologie de la matrice d'Eisenhower. Elle prend en charge l'authentification des utilisateurs, la gestion des projets et des tâches, ainsi que la priorisation des tâches avec des quadrants d'urgence et d'importance.

## Fonctionnalités
- **Gestion des utilisateurs** : Inscription et connexion des utilisateurs avec des rôles (`admin` ou `util`).
- **Gestion des projets** : Création, mise à jour, suppression (logique) et restauration de projets.
- **Gestion des tâches** : Création, mise à jour, suppression (logique) et filtrage des tâches par projet, statut, urgence ou importance.
- **Matrice d'Eisenhower** : Organisation des tâches en quadrants (urgent/important, etc.).
- **Statistiques** : Récupération des statistiques des tâches par utilisateur ou projet.

## Répertoire
[https://github.com/Gxb001/api-matrice-eisenhower](https://github.com/Gxb001/api-matrice-eisenhower)

## Prérequis
- Python 3.8+
- MySQL (avec une base de données nommée `eisenmatrix`)
- Git
- pip

## Instructions d'installation

### 1. Cloner le répertoire
```bash
git clone https://github.com/Gxb001/api-matrice-eisenhower.git
cd api-matrice-eisenhower
```

### 2. Installer les dépendances
Installez les packages Python requis :
```bash
pip install -r requirements.txt
```

**Dépendances** (depuis `requirements.txt`) :
- Flask==2.3.2
- Flask-SQLAlchemy==3.0.5
- Flask-JWT-Extended==4.5.0
- python-dotenv==1.0.0
- pymysql==1.1.0
- bcrypt==4.0.1

### 3. Configurer l'environnement
Créez un fichier `.env` à la racine du projet :
```plaintext
SECRET_KEY=your_secure_secret_key
JWT_SECRET_KEY=your_secure_jwt_secret_key
DATABASE_URI=mysql+pymysql://username:password@localhost/eisenmatrix
```
- Remplacez `your_secure_secret_key` et `your_secure_jwt_secret_key` par des chaînes sécurisées aléatoires.
- Remplacez `username` et `password` par vos identifiants MySQL.

### 4. Initialiser la base de données
Créez la base de données `eisenmatrix` et les tables nécessaires en exécutant le script SQL suivant dans MySQL :
```sql
CREATE DATABASE IF NOT EXISTS eisenmatrix;
USE eisenmatrix;

CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name_util VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('util', 'admin') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME
);

CREATE TABLE Projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME
);

CREATE TABLE UserProjects (
    id_user INT NOT NULL,
    id_project INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_user, id_project),
    FOREIGN KEY (id_user) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (id_project) REFERENCES Projects(id) ON DELETE CASCADE
);

CREATE TABLE Tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    urgency ENUM('Urgent', 'Non Urgent') NOT NULL,
    importance ENUM('Important', 'Non Important') NOT NULL,
    status ENUM('En cours', 'Planifié', 'Bloqué', 'À faire') NOT NULL,
    plan_date DATE,
    estimation INT,
    estimation_unit ENUM('heures', 'jours', 'semaines', 'mois'),
    id_user INT NOT NULL,
    id_project INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME,
    FOREIGN KEY (id_user) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (id_project) REFERENCES Projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON Tasks(id_user);
CREATE INDEX idx_tasks_urgency_importance ON Tasks(urgency, importance);
CREATE INDEX idx_tasks_project_id ON Tasks(id_project);
```

Ensuite, lancez l'application Flask pour vérifier la configuration :
```bash
python run.py
```
Arrêtez le serveur (Ctrl+C) après la création des tables.

### 5. Lancer l'application
Démarrez le serveur Flask :
```bash
python run.py
```
L'API sera accessible à `http://localhost:5000`.

### 6. Tester l'API
Utilisez le script `test_api.py` fourni pour tester tous les endpoints :
```bash
python test_api.py
```
Ce script :
- Crée ou connecte les utilisateurs (`testuser` et `adminuser`).
- Teste les endpoints pour la création, la mise à jour et la suppression de projets et de tâches.
- Affiche le succès ou l'échec de chaque requête avec les détails des erreurs.

Assurez-vous que le serveur Flask est en cours d'exécution avant d'exécuter le script.

## Endpoints de l'API

### Authentification
- **POST /api/register** : Créer un nouvel utilisateur.
  - Corps : `{"name_util": "username", "password": "password", "role": "admin|util"}`
  - Réponse : `201` avec `{"id": <user_id>, "message": "Utilisateur créé"}`
- **POST /api/login** : Connexion et récupération d'un token JWT.
  - Corps : `{"name_util": "username", "password": "password"}`
  - Réponse : `200` avec `{"access_token": "<jwt>", "user_id": <user_id>}`

### Projets
- **POST /api/projects** : Créer un projet (admin uniquement).
  - Corps : `{"name": "Nom du projet", "description": "Description"}`
  - Réponse : `201` avec `{"id": <project_id>, "name": "...", "description": "..."}`
- **GET /api/projects** : Lister les projets de l'utilisateur authentifié.
  - Réponse : `200` avec un tableau de projets.
- **GET /api/projects/<project_id>** : Obtenir les détails d'un projet.
  - Réponse : `200` avec `{"id": <project_id>, "name": "...", "description": "..."}`
- **PUT /api/projects/<project_id>** : Mettre à jour un projet (admin uniquement).
  - Corps : `{"name": "Nouveau nom", "description": "Nouvelle description"}`
  - Réponse : `200` avec `{"message": "Projet mis à jour"}`
- **DELETE /api/projects/<project_id>** : Supprimer logiquement un projet (admin uniquement).
  - Réponse : `200` avec `{"message": "Projet supprimé"}`
- **PATCH /api/projects/<project_id>/restore** : Restaurer un projet supprimé (admin uniquement).
  - Réponse : `200` avec `{"message": "Projet restauré"}`

### Tâches
- **POST /api/tasks** : Créer une tâche.
  - Corps : `{"name": "Nom de la tâche", "description": "Description", "urgency": "Urgent|Non Urgent", "importance": "Important|Non Important", "status": "À faire|En cours|Planifié|Bloqué", "plan_date": "YYYY-MM-DD", "estimation": <int>, "estimation_unit": "heures", "id_project": <project_id>}`
  - Réponse : `201` avec `{"id": <task_id>, "name": "..."}`
- **PUT /api/tasks/<task_id>** : Mettre à jour une tâche.
  - Corps : Identique au POST, avec des champs optionnels.
  - Réponse : `200` avec les détails de la tâche mise à jour.
- **DELETE /api/tasks/<task_id>** : Supprimer logiquement une tâche.
  - Réponse : `200` avec `{"message": "Tâche supprimée"}`
- **GET /api/tasks/project/<project_id>** : Lister les tâches d'un projet.
  - Réponse : `200` avec un tableau de tâches.
- **GET /api/tasks/matrix/<user_id>** : Obtenir les tâches organisées par matrice d'Eisenhower.
  - Réponse : `200` avec les tâches regroupées par quadrants.
- **GET /api/tasks/filter** : Filtrer les tâches par statut, urgence, importance ou projet.
  - Paramètres de requête : `?status=En%20cours&urgency=Urgent&importance=Important&project_id=<id>`
  - Réponse : `200` avec les tâches filtrées.

### Associations Utilisateur-Projet
- **POST /api/user-projects** : Associer un utilisateur à un projet (admin uniquement).
  - Corps : `{"id_user": <user_id>, "id_project": <project_id>}`
  - Réponse : `201` avec `{"message": "Utilisateur associé au projet"}`
- **DELETE /api/user-projects/<user_id>/<project_id>** : Supprimer l'association utilisateur-projet (admin uniquement).
  - Réponse : `200` avec `{"message": "Association supprimée"}`

### Utilisateurs
- **GET /api/users** : Lister tous les utilisateurs (admin uniquement).
  - Réponse : `200` avec un tableau d'utilisateurs.
- **GET /api/users/<user_id>/projects** : Lister les projets d'un utilisateur spécifique.
  - Réponse : `200` avec un tableau de projets.
- **PATCH /api/users/<user_id>/role** : Mettre à jour le rôle d'un utilisateur (admin uniquement).
  - Corps : `{"role": "admin|util"}`
  - Réponse : `200` avec `{"message": "Rôle mis à jour"}`

### Statistiques
- **GET /api/tasks/stats/<user_id>** : Obtenir les statistiques des tâches d'un utilisateur.
  - Réponse : `200` avec les statistiques par quadrant, statut et projet.
- **GET /api/projects/<project_id>/stats** : Obtenir les statistiques des tâches d'un projet.
  - Réponse : `200` avec les statistiques par quadrant et statut.

## Dépannage
- **Problèmes de base de données** : Assurez-vous que `DATABASE_URI` est correct et que la base de données `eisenmatrix` existe.
- **Erreurs JWT** : Si vous voyez `"Subject must be a string"`, vérifiez que `app/routes/auth.py` inclut `additional_claims={'sub': str(user.id)}` dans `create_access_token`.
- **Erreurs SQLAlchemy** : Pour les erreurs de jointure, vérifiez que `Task.query.join(UserProject, Task.id_project == UserProject.id_project)` est utilisé dans `app/routes/tasks.py`.
- **Erreurs 404** : Assurez-vous que les projets et les tâches sont créés et associés aux utilisateurs via `UserProjects`.

## Tests manuels avec `curl`
```bash
# Connexion
curl -X POST http://localhost:5000/api/login \
     -H "Content-Type: application/json" \
     -d '{"name_util": "adminuser", "password": "admin123"}'

# Créer un projet
curl -X POST http://localhost:5000/api/projects \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <JWT_TOKEN>" \
     -d '{"name": "Projet Alpha", "description": "Projet de test"}'

# Créer une tâche
curl -X POST http://localhost:5000/api/tasks \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <JWT_TOKEN>" \
     -d '{"name": "Tâche de test", "description": "Exemple", "urgency": "Urgent", "importance": "Important", "status": "À faire", "plan_date": "2025-07-10", "estimation": 5, "estimation_unit": "heures", "id_project": <project_id>}'

# Mettre à jour une tâche
curl -X PUT http://localhost:5000/api/tasks/<task_id> \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <JWT_TOKEN>" \
     -d '{"name": "Tâche mise à jour", "status": "En cours"}'

# Supprimer une tâche
curl -X DELETE http://localhost:5000/api/tasks/<task_id> \
     -H "Authorization: Bearer <JWT_TOKEN>"
```

## Contributeur
- **Gxb001** : Gabriel.F