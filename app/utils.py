from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, hashed):
    return check_password_hash(hashed, password)


def is_admin():
    identity = get_jwt_identity()
    return identity.get('role') == 'ADMIN'


def is_self_or_admin(target_user_id):
    identity = get_jwt_identity()
    return identity.get('role') == 'ADMIN' or identity.get('id') == target_user_id
