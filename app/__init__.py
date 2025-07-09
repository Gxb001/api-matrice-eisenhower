from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    jwt = JWTManager(app)

    # Vérifier les erreurs de chargement du token
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"msg": f"Invalid token: {error}"}, 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return {"msg": f"Missing Authorization Header: {error}"}, 401

    from .routes import auth, projects, user_projects, tasks, users
    app.register_blueprint(auth.auth_bp, url_prefix='/api')
    app.register_blueprint(projects.projects_bp, url_prefix='/api')
    app.register_blueprint(user_projects.user_projects_bp, url_prefix='/api')
    app.register_blueprint(tasks.tasks_bp, url_prefix='/api')
    app.register_blueprint(users.users_bp, url_prefix='/api')

    return app
