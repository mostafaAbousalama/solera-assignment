from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

import datetime

app = Flask(__name__)
app.config.from_object("project.config.Config")

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    hashed_password = db.Column(db.String(256), nullable=False, unique=True)
    current_balance = db.Column(db.Integer, nullable=False)
    current_reading = db.Column(db.Integer, nullable=False)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f'<User {self.id}, {self.name}, {self.email}, {self.current_balance}, {self.current_reading}, {self.last_login}>'

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    hashed_password = db.Column(db.String(256), nullable=False, unique=True)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Admin {self.id}, {self.username}, {self.last_login}>'


@app.route("/")
def hello_world():
    return jsonify(hello="world")
