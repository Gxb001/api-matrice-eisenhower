from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app2 import db
from app2.models.project import Project
from app2.models.user_project import UserProject
from app2.utils.decorators import admin_required, user_or_admin_required

user_projects_bp = Blueprint('user_projects', __name__)


@user_projects_bp.route('/user-projects', methods=['POST'])
@jwt_required()
@admin_required
def add_user_to_project():
    data = request.get_json()
    user_project = UserProject(id_user=data['id_user'], id_project=data['id_project'])
    db.session.add(user_project)
    db.session.commit()
    return jsonify({'message': 'Utilisateur ajouté au projet'}), 201


@user_projects_bp.route('/user-projects/<int:user_id>/<int:project_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def remove_user_from_project(user_id, project_id):
    user_project = UserProject.query.filter_by(id_user=user_id, id_project=project_id).first_or_404()
    db.session.delete(user_project)
    db.session.commit()
    return jsonify({'message': 'Utilisateur retiré du projet'}), 200


@user_projects_bp.route('/users/<int:user_id>/projects', methods=['GET'])
@jwt_required()
@user_or_admin_required
def list_user_projects(user_id):
    projects = Project.query.join(UserProject).filter(
        UserProject.id_user == user_id,
        Project.deleted_at.is_(None)
    ).all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description} for p in projects]), 200
