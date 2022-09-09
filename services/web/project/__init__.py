from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import datetime
import bcrypt

app = Flask(__name__)
app.config.from_object("project.config.Config")

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    hashed_password = db.Column(db.String(256), nullable=False, unique=True)
    current_balance = db.Column(db.Integer, nullable=False, default=0) # checkconstraint
    current_reading = db.Column(db.Integer, nullable=False, default=0)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f'<User id: {self.id}, name: {self.name}, email: {self.email}, balance: {self.current_balance}, reading: {self.current_reading}, login: {self.last_login}>'

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    hashed_password = db.Column(db.String(256), nullable=False, unique=True)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Admin id: {self.id}, username: {self.username}, login: {self.last_login}>'


@app.route("/")
def hello_world():
    return jsonify(hello="world")
