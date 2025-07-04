# app.py
from datetime import datetime
from enum import Enum

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/eisenmatrix'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Modèles
class Role(Enum):
    UTIL = 'util'
    ADMIN = 'admin'


class Urgency(Enum):
    URGENT = 'Urgent'
    NON_URGENT = 'Non Urgent'


class Importance(Enum):
    IMPORTANT = 'Important'
    NON_IMPORTANT = 'Non Important'


class Status(Enum):
    EN_COURS = 'En cours'
    PLANIFIE = 'Planifié'
    BLOQUE = 'Bloqué'
    A_FAIRE = 'À faire'


class EstimationUnit(Enum):
    HEURES = 'heures'
    JOURS = 'jours'
    SEMAINES = 'semaines'
    MOIS = 'mois'


class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name_util = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    tasks = db.relationship('Task', backref='user', lazy=True)


class Task(db.Model):
    __tablename__ = 'Tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    urgency = db.Column(db.Enum(Urgency), nullable=False)
    importance = db.Column(db.Enum(Importance), nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    plan_date = db.Column(db.Date)
    estimation = db.Column(db.Integer)
    estimation_unit = db.Column(db.Enum(EstimationUnit))
    id_user = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)


# Routes pour Users
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.filter_by(deleted_at=None).all()
    return jsonify([{
        'id': user.id,
        'name_util': user.name_util,
        'role': user.role.value,
        'created_at': user.created_at.isoformat()
    } for user in users])


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        user = User(
            name_util=data['name_util'],
            password=data['password'],  # À hasher dans une version production
            role=Role[data['role'].upper()]
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'id': user.id}), 201
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': 'Invalid role value'}), 400


@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id, deleted_at=None).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'name_util': user.name_util,
        'role': user.role.value,
        'created_at': user.created_at.isoformat()
    })


# Routes pour Tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.filter_by(deleted_at=None).all()
    return jsonify([{
        'id': task.id,
        'name': task.name,
        'description': task.description,
        'urgency': task.urgency.value,
        'importance': task.importance.value,
        'status': task.status.value,
        'plan_date': task.plan_date.isoformat() if task.plan_date else None,
        'estimation': task.estimation,
        'estimation_unit': task.estimation_unit.value if task.estimation_unit else None,
        'id_user': task.id_user,
        'created_at': task.created_at.isoformat(),
        'updated_at': task.updated_at.isoformat()
    } for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    try:
        task = Task(
            name=data['name'],
            description=data.get('description'),
            urgency=Urgency[data['urgency'].replace(' ', '_').upper()],
            importance=Importance[data['importance'].replace(' ', '_').upper()],
            status=Status[data['status'].replace(' ', '_').upper()],
            plan_date=datetime.strptime(data['plan_date'], '%Y-%m-%d') if data.get('plan_date') else None,
            estimation=data.get('estimation'),
            estimation_unit=EstimationUnit[data['estimation_unit'].upper()] if data.get('estimation_unit') else None,
            id_user=data['id_user']
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully', 'id': task.id}), 201
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400


# Configuration pour lancement
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crée les tables si elles n'existent pas
    app.run(debug=True)

# lister les endpoints necessaires à l'application
