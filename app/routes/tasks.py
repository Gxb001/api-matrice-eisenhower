from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.task import Task
from app.models.user_project import UserProject
from app.utils.decorators import user_or_admin_required

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not all(key in data for key in ['name', 'urgency', 'importance', 'status', 'id_project']):
        return jsonify({'error': 'Missing required fields'}), 400
    task = Task(
        name=data['name'],
        description=data.get('description'),
        urgency=data['urgency'],
        importance=data['importance'],
        status=data['status'],
        plan_date=data.get('plan_date'),
        estimation=data.get('estimation'),
        estimation_unit=data.get('estimation_unit'),
        id_user=user_id,
        id_project=data['id_project']
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'id': task.id, 'name': task.name}), 201


@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, deleted_at=None).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    # Vérifier si l'utilisateur a accès à la tâche
    if task.id_user != user_id:
        user_project = UserProject.query.filter_by(id_user=user_id, id_project=task.id_project).first()
        if not user_project:
            return jsonify({'error': 'Unauthorized access to task'}), 403
    data = request.get_json()
    task.name = data.get('name', task.name)
    task.description = data.get('description', task.description)
    task.urgency = data.get('urgency', task.urgency)
    task.importance = data.get('importance', task.importance)
    task.status = data.get('status', task.status)
    task.plan_date = data.get('plan_date', task.plan_date)
    task.estimation = data.get('estimation', task.estimation)
    task.estimation_unit = data.get('estimation_unit', task.estimation_unit)
    task.id_project = data.get('id_project', task.id_project)
    db.session.commit()
    return jsonify({
        'id': task.id,
        'name': task.name,
        'description': task.description,
        'urgency': task.urgency,
        'importance': task.importance,
        'status': task.status,
        'plan_date': task.plan_date,
        'estimation': task.estimation,
        'estimation_unit': task.estimation_unit,
        'id_project': task.id_project
    }), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, deleted_at=None).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    # Vérifier si l'utilisateur a accès à la tâche (soit via id_user, soit via UserProject)
    if task.id_user != user_id:
        user_project = UserProject.query.filter_by(id_user=user_id, id_project=task.id_project).first()
        if not user_project:
            return jsonify({'error': 'Unauthorized access to task'}), 403
    task.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200


@tasks_bp.route('/tasks/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_tasks(project_id):
    user_id = get_jwt_identity()
    tasks = Task.query.join(UserProject, Task.id_project == UserProject.id_project).filter(
        Task.id_project == project_id,
        UserProject.id_user == user_id,
        Task.deleted_at.is_(None)
    ).all()
    return jsonify([{
        'id': t.id, 'name': t.name, 'description': t.description,
        'urgency': t.urgency, 'importance': t.importance, 'status': t.status,
        'plan_date': t.plan_date.isoformat() if t.plan_date else None,
        'estimation': t.estimation, 'estimation_unit': t.estimation_unit
    } for t in tasks]), 200


@tasks_bp.route('/tasks/matrix/<int:user_id>', methods=['GET'])
@jwt_required()
@user_or_admin_required
def get_matrix_tasks(user_id):
    tasks = Task.query.filter_by(id_user=user_id, deleted_at=None).all()
    matrix = {
        'urgent_important': [],
        'urgent_non_important': [],
        'non_urgent_important': [],
        'non_urgent_non_important': []
    }
    for t in tasks:
        key = f"{t.urgency.lower().replace(' ', '_')}_{t.importance.lower().replace(' ', '_')}"
        matrix[key].append({
            'id': t.id, 'name': t.name, 'status': t.status,
            'plan_date': t.plan_date.isoformat() if t.plan_date else None
        })
    return jsonify(matrix), 200


@tasks_bp.route('/tasks/filter', methods=['GET'])
@jwt_required()
def filter_tasks():
    user_id = get_jwt_identity()
    query = Task.query.filter_by(id_user=user_id, deleted_at=None)

    if 'status' in request.args:
        query = query.filter_by(status=request.args['status'])
    if 'urgency' in request.args:
        query = query.filter_by(urgency=request.args['urgency'])
    if 'importance' in request.args:
        query = query.filter_by(importance=request.args['importance'])
    if 'project_id' in request.args:
        query = query.filter_by(id_project=request.args['project_id'])
    if 'plan_date' in request.args:
        query = query.filter_by(plan_date=request.args['plan_date'])

    tasks = query.all()
    return jsonify([{
        'id': t.id, 'name': t.name, 'description': t.description,
        'urgency': t.urgency, 'importance': t.importance, 'status': t.status
    } for t in tasks]), 200


@tasks_bp.route('/tasks/stats/<int:user_id>', methods=['GET'])
@jwt_required()
@user_or_admin_required
def get_user_tasks_stats(user_id):
    tasks = Task.query.filter_by(id_user=user_id, deleted_at=None).all()
    stats = {
        'by_quadrant': {
            'urgent_important': 0,
            'urgent_non_important': 0,
            'non_urgent_important': 0,
            'non_urgent_non_important': 0
        },
        'by_status': {
            'En cours': 0, 'Planifié': 0, 'Bloqué': 0, 'À faire': 0
        },
        'by_project': {}
    }
    for t in tasks:
        quadrant = f"{t.urgency.lower().replace(' ', '_')}_{t.importance.lower().replace(' ', '_')}"
        stats['by_quadrant'][quadrant] += 1
        stats['by_status'][t.status] += 1
        stats['by_project'][str(t.id_project)] = stats['by_project'].get(str(t.id_project), 0) + 1
    return jsonify(stats), 200


@tasks_bp.route('/projects/<int:project_id>/stats', methods=['GET'])
@jwt_required()
def get_project_stats(project_id):
    tasks = Task.query.filter_by(id_project=project_id, deleted_at=None).all()
    stats = {
        'by_quadrant': {
            'urgent_important': 0,
            'urgent_non_important': 0,
            'non_urgent_important': 0,
            'non_urgent_non_important': 0
        },
        'by_status': {
            'En cours': 0, 'Planifié': 0, 'Bloqué': 0, 'À faire': 0
        }
    }
    for t in tasks:
        quadrant = f"{t.urgency.lower().replace(' ', '_')}_{t.importance.lower().replace(' ', '_')}"
        stats['by_quadrant'][quadrant] += 1
        stats['by_status'][t.status] += 1
    return jsonify(stats), 200
