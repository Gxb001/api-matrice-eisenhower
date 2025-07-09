from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app2 import db
from app2.models.project import Project
from app2.models.user_project import UserProject
from app2.utils.decorators import admin_required

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects', methods=['POST'])
@jwt_required()
@admin_required
def create_project():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    project = Project(name=data['name'], description=data.get('description'))
    db.session.add(project)
    db.session.commit()
    # Associer automatiquement l'utilisateur admin au projet
    user_id = get_jwt_identity()
    user_project = UserProject(id_user=user_id, id_project=project.id)
    db.session.add(user_project)
    db.session.commit()
    return jsonify({'id': project.id, 'name': project.name, 'description': project.description}), 201


@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def list_projects():
    user_id = get_jwt_identity()
    projects = Project.query.join(UserProject).filter(
        UserProject.id_user == user_id,
        Project.deleted_at.is_(None)
    ).all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description} for p in projects]), 200


@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    user_id = get_jwt_identity()
    project = Project.query.join(UserProject).filter(
        Project.id == project_id,
        UserProject.id_user == user_id,
        Project.deleted_at.is_(None)
    ).first()
    if not project:
        return jsonify({'error': 'Project not found or access denied'}), 404
    return jsonify({'id': project.id, 'name': project.name, 'description': project.description}), 200


@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_project(project_id):
    project = Project.query.filter_by(id=project_id, deleted_at=None).first_or_404()
    data = request.get_json()
    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)
    db.session.commit()
    return jsonify({'message': 'Project updated'}), 200


@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_project(project_id):
    project = Project.query.filter_by(id=project_id, deleted_at=None).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    project.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Project deleted'}), 200


@projects_bp.route('/projects/<int:project_id>/restore', methods=['PATCH'])
@jwt_required()
@admin_required
def restore_project(project_id):
    project = Project.query.filter_by(id=project_id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    project.deleted_at = None
    db.session.commit()
    return jsonify({'message': 'Project restored'}), 200
