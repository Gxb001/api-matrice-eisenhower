import os

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from auth import auth_bp
from database import db
from routes import routes_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
jwt = JWTManager(app)

# Init Swagger
swagger = Swagger(app)

app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
