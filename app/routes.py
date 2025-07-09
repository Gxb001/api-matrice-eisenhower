from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db, User, Task, Role, Urgency, Importance, Status, EstimationUnit
from utils import is_admin

routes_bp = Blueprint('routes', __name__)


# Helper : sérialisation user
def serialize_user(user):
    return {
        'id': user.id,
        'name_util': user.name_util,
        'role': user.role.value,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'deleted_at': user.deleted_at.isoformat() if user.deleted_at else None
    }


# Helper : sérialisation task
def serialize_task(task):
    return {
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
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'updated_at': task.updated_at.isoformat() if task.updated_at else None,
        'deleted_at': task.deleted_at.isoformat() if task.deleted_at else None,
    }


# --- USERS ---

@routes_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user = get_jwt_identity()
    if not (is_admin() or current_user['id'] == user_id):
        return jsonify({'error': 'Forbidden'}), 403

    user = User.query.get_or_404(user_id)
    return jsonify(serialize_user(user))


@routes_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'name_util' in data:
        user.name_util = data['name_util']
    if 'role' in data:
        try:
            user.role = Role[data['role'].upper()]
        except KeyError:
            return jsonify({'error': 'Invalid role value'}), 400

    db.session.commit()
    return jsonify({'message': 'User updated', 'user': serialize_user(user)})


@routes_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403

    user = User.query.get_or_404(user_id)
    if user.deleted_at:
        return jsonify({'error': 'User already deleted'}), 400

    user.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'User deleted logically'})


@routes_bp.route('/users/<int:user_id>/restore', methods=['PATCH'])
@jwt_required()
def restore_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403

    user = User.query.get_or_404(user_id)
    if not user.deleted_at:
        return jsonify({'error': 'User not deleted'}), 400

    user.deleted_at = None
    db.session.commit()
    return jsonify({'message': 'User restored', 'user': serialize_user(user)})


# --- TASKS ---

@routes_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    current_user = get_jwt_identity()
    data = request.get_json()

    # Si l'utilisateur n'est pas admin, id_user doit être le sien
    if not is_admin():
        if data.get('id_user') != current_user['id']:
            return jsonify({'error': 'Cannot create task for other user'}), 403

    # Validation règles métiers
    try:
        urgency = Urgency(data['urgency'])
        importance = Importance(data['importance'])
        status = Status(data['status'])
    except KeyError as e:
        return jsonify({'error': f'Invalid enum value: {str(e)}'}), 400

    if urgency == Urgency.NON_URGENT and importance == Importance.IMPORTANT and not data.get('plan_date'):
        return jsonify({'error': 'plan_date required for Non Urgent & Important'}), 400

    estimation = data.get('estimation')
    if estimation is not None and estimation < 0:
        return jsonify({'error': 'Estimation must be positive'}), 400

    estimation_unit = None
    if data.get('estimation_unit'):
        try:
            estimation_unit = EstimationUnit[data['estimation_unit'].upper()]
        except KeyError:
            return jsonify({'error': 'Invalid estimation_unit value'}), 400

    task = Task(
        name=data['name'],
        description=data.get('description'),
        urgency=urgency,
        importance=importance,
        status=status,
        plan_date=datetime.strptime(data['plan_date'], '%Y-%m-%d') if data.get('plan_date') else None,
        estimation=estimation,
        estimation_unit=estimation_unit,
        id_user=data['id_user']
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task created', 'id': task.id}), 201


@routes_bp.route('/tasks/<int:user_id>', methods=['GET'])
@jwt_required()
def get_tasks_by_user(user_id):
    current_user = get_jwt_identity()
    if not (is_admin() or current_user['id'] == user_id):
        return jsonify({'error': 'Forbidden'}), 403

    tasks = Task.query.filter_by(id_user=user_id, deleted_at=None).all()
    return jsonify([serialize_task(t) for t in tasks])


@routes_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    current_user = get_jwt_identity()
    task = Task.query.get_or_404(task_id)

    # Vérifier droits : admin ou proprio de la tâche
    if not (is_admin() or task.id_user == current_user['id']):
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()

    try:
        urgency = Urgency(data['urgency'])
        importance = Importance(data['importance'])
        status = Status(data['status'])
    except KeyError as e:
        return jsonify({'error': f'Invalid enum value: {str(e)}'}), 400

    if urgency == Urgency.NON_URGENT and importance == Importance.IMPORTANT and not data.get('plan_date'):
        return jsonify({'error': 'plan_date required for Non Urgent & Important'}), 400

    estimation = data.get('estimation')
    if estimation is not None and estimation < 0:
        return jsonify({'error': 'Estimation must be positive'}), 400

    task.name = data['name']
    task.description = data.get('description')
    task.urgency = urgency
    task.importance = importance
    task.status = status
    task.plan_date = datetime.strptime(data['plan_date'], '%Y-%m-%d') if data.get('plan_date') else None
    task.estimation = estimation

    db.session.commit()
    return jsonify({'message': 'Task updated', 'task': serialize_task(task)})


@routes_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user = get_jwt_identity()
    task = Task.query.get_or_404(task_id)

    # Vérifier droits : admin ou proprio
    if not (is_admin() or task.id_user == current_user['id']):
        return jsonify({'error': 'Forbidden'}), 403

    if task.deleted_at:
        return jsonify({'error': 'Task already deleted'}), 400

    task.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Task deleted logically'})


@routes_bp.route('/tasks/<int:task_id>/restore', methods=['PATCH'])
@jwt_required()
def restore_task(task_id):
    if not is_admin():
        return jsonify({'error': 'Forbidden'}), 403

    task = Task.query.get_or_404(task_id)
    if not task.deleted_at:
        return jsonify({'error': 'Task not deleted'}), 400

    task.deleted_at = None
    db.session.commit()
    return jsonify({'message': 'Task restored', 'task': serialize_task(task)})
