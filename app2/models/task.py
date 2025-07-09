from datetime import datetime

from app2 import db


class Task(db.Model):
    __tablename__ = 'Tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    urgency = db.Column(db.Enum('Urgent', 'Non Urgent'), nullable=False)
    importance = db.Column(db.Enum('Important', 'Non Important'), nullable=False)
    status = db.Column(db.Enum('En cours', 'Planifié', 'Bloqué', 'À faire'), nullable=False)
    plan_date = db.Column(db.Date)
    estimation = db.Column(db.Integer)
    estimation_unit = db.Column(db.Enum('heures', 'jours', 'semaines', 'mois'))
    id_user = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    id_project = db.Column(db.Integer, db.ForeignKey('Projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
