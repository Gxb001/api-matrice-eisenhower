from datetime import datetime

from app2 import db


class UserProject(db.Model):
    __tablename__ = 'UserProjects'
    id_user = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    id_project = db.Column(db.Integer, db.ForeignKey('Projects.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
