from datetime import datetime
from enum import Enum

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
