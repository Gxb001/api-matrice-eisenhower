from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app import db
from app.models.user import User
from app.utils.auth import hash_password, check_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name_util')
    password = data.get('password')
    role = data.get('role', 'util')

    if not name or not password:
        return jsonify({'error': 'Name and password are required'}), 400

    if User.query.filter_by(name_util=name).first():
        return jsonify({'error': 'User already exists'}), 400

    user = User(name_util=name, password=hash_password(password), role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'message': 'User created'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(name_util=data.get('name_util')).first()
    if user and check_password(data.get('password'), user.password):
        access_token = create_access_token(identity=user.id, additional_claims={'sub': str(user.id), 'role': user.role})
        return jsonify({'access_token': access_token, 'user_id': user.id}), 200
    return jsonify({'error': 'Invalid credentials'}), 401
