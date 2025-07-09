import secrets

def generate_jwt_secret_key(length=64):
    """Génère une clé secrète sécurisée pour JWT."""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    secret_key = generate_jwt_secret_key()
    print("Clé secrète JWT générée :")
    print(secret_key)