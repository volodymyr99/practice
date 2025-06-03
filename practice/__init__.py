from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # 🔐 Явно задаємо параметри конфігурації
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/practice_support"
    app.config['SECRET_KEY'] = "a718162567840bc3aea0c258b2318e401c70b2f1416dfcae4cc820d4633f5ee8"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 🔌 Ініціалізуємо SQLAlchemy
    db.init_app(app)

    # 🔁 Підключаємо Blueprint
    from .views import views
    app.register_blueprint(views)

    return app