from flask import Flask, jsonify, render_template, request, redirect, url_for, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.exceptions import HTTPException

# I will use this to verify that my load balancer Nginx conf is indeed working
import socket

import datetime
import bcrypt

app = Flask(__name__)
app.config.from_object("project.config.Config")

db = SQLAlchemy(app)

server_session = Session(app)


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
def index():
    # Start a new session by clearing credentials of old sessions if net already removed
    session["user_email"] = None
    session["admin_id"] = None
    return redirect(url_for("signin_user"))


@app.route("/user/<user_id>")
def display_user_data(user_id):
    #gethostname() will retrieve for us the container id of the replica web service that simulates load balancing of nginx
    #I will use that in the front end to check that load balancing is working
    container_id = socket.gethostname()
    try:
        user_data = User.query.filter_by(id=user_id).one_or_none()
        #If user does not exist in database
        if user_data is None:
            session["user_email"] = None
            session["admin_id"] = None
            abort(404)
        #if user current session creds does not match current requested user page, unauthorized access potentially by bad actor, lock them out, reset session and redirect to sign in page
        elif session["user_email"] != user_data.email:
            session["user_email"] = None
            session["admin_id"] = None
            return redirect(url_for("signin_user"))
        else:
            return render_template("usertable.html", userData=user_data, cid=container_id)
    except Exception as e:
        db.session.rollback()
        if isinstance(e, HTTPException):
            abort(e.code)
        else:
            abort(500)
    finally:
        db.session.close()


@app.route("/admin/<admin_id>")
def display_admin_panel(admin_id):
    container_id = socket.gethostname()
    try:
        admin = Admin.query.filter_by(id=admin_id).one_or_none()
        if admin is None:
            session["user_email"] = None
            session["admin_id"] = None
            print("none")
            abort(404)
            # Again for potential bad actors
        elif session["admin_id"] != admin.id:
            session["user_email"] = None
            session["admin_id"] = None
            print("bad actor")
            return redirect(url_for("signin_admin"))
        else:
            users = User.query.all()
            sum = 0
            for u in users:
                sum += u.current_balance
                users_number = User.query.count()
            print("about to render")
            print(session["admin_id"])
            return render_template("admintable.html", adminData=Admin.query.filter_by(id=admin_id).first(), sum=sum, users_number=users_number, cid=container_id)
    except Exception as e:
        db.session.rollback()
        if isinstance(e, HTTPException):
            abort(e.code)
        else:
            abort(500)
    finally:
        db.session.close()


@app.route("/user/register")
def register_user():
    container_id = socket.gethostname()
    #   Precautionary session reset at attempt of new account sign up
    session["user_email"] = None
    session["admin_id"] = None
    return render_template("usersignup.html", cid=container_id)


@app.route("/admin/register")
def register_admin():
    container_id = socket.gethostname()
    #   Same precaution as with user sign up
    session["user_email"] = None
    session["admin_id"] = None
    return render_template("adminsignup.html", cid=container_id)


@app.route("/user/registerForm", methods=["POST"])
def register_user_form():
    try:
        if request.method == "POST":
            request_body = request.get_json()
            #   Server side check for no empty fileds
            if request_body["name"] == "" or request_body["email"] == "" or request_body["password"] == "":
                abort(400)
            check_user = User.query.filter_by(email=request_body["email"]).one_or_none()
            #   check if user is already in database, can not overwrite
            if check_user:
                abort(409)
            name = request_body["name"]
            email = request_body["email"]
            password = request_body["password"]
            #   Encoding, salting and hashing password for database storage
            bpassword = password.encode("utf-8")
            hashed_password = bcrypt.hashpw(bpassword, bcrypt.gensalt(13))
            #   I have to decode hashed password because of db schema stores text, not byte "bText"
            hashed_password_decoded = hashed_password.decode("utf-8")
            new_user = User(name=name, email=email, hashed_password=hashed_password_decoded)
            db.session.add(new_user)
            db.session.commit()
        else:
            #   if method wasn't POST, abort
            abort(405)
    except Exception as e:
        #   Any abort above in try block will take me here and rollback any db commits or changes
        db.session.rollback()
        #   Check if one of the abort() calls in the try block is what triggered this except block
        if isinstance(e, HTTPException):
            abort(e.code)
        #   If not then throw internal server error
        else:
            abort(500)
    else:
        #   If all went well, get that newly registered user and set a session, and redirect to corresponding page
        new_user_id = User.query.filter_by(email=request_body["email"]).one_or_none()
        if new_user_id:
            session["user_email"] = new_user_id.email
            session["admin_id"] = None
            return redirect(url_for("display_user_data", user_id=new_user_id.id))
        else:
            #   If for some reason, we failed to finde the new user in db, for later debug
            abort(404)
    finally:
        #   Always close the db session after transaction success or fail
        db.session.close()

#       Like in the register user handler above, like-for-like code runs for admins
@app.route("/admin/registerForm", methods=["POST"])
def register_admin_form():
    try:
        if request.method == "POST":
            request_body = request.get_json()
            if request_body["username"] == "" or request_body["password"] == "":
                abort(400)
            check_admin = Admin.query.filter_by(username=request_body["username"]).one_or_none()
            if check_admin:
                abort(409)
            username = request_body["username"]
            password = request_body["password"]
            bpassword = password.encode("utf-8")
            hashed_password = bcrypt.hashpw(bpassword, bcrypt.gensalt(13))
            hashed_password_decoded = hashed_password.decode("utf-8")
            new_admin = Admin(username=username, hashed_password=hashed_password_decoded)
            db.session.add(new_admin)
            db.session.commit()
        else:
            abort(405)
    except Exception as e:
        db.session.rollback()
        if isinstance(e, HTTPException):
            abort(e.code)
        else:
            abort(500)
    else:
        new_admin_id = Admin.query.filter_by(username=request_body["username"]).one_or_none()
        if new_admin_id:
            session["user_email"] = None
            session["admin_id"] = new_admin_id.id
            return redirect(url_for("display_admin_panel", admin_id=new_admin_id.id))
        else:
            abort(404)
    finally:
        db.session.close()


@app.route("/user/login")
def signin_user():
    container_id = socket.gethostname()
    #   Ensure new session on load up of sign-in page
    session["user_email"] = None
    session["admin_id"] = None
    return render_template("userlogin.html", cid=container_id)


@app.route("/admin/login")
def signin_admin():
    container_id = socket.gethostname()
    session["user_email"] = None
    session["admin_id"] = None
    return render_template("adminlogin.html", cid=container_id)


@app.route("/user/loginForm", methods=["POST"])
def signin_user_form():
    try:
        if request.method == "POST":
            request_body = request.get_json()
            if request_body["email"] =="" or request_body["password"] == "":
                abort(400)
            check_user = User.query.filter_by(email=request_body["email"]).one_or_none()
            #   check if user exists in db
            if check_user is None:
                abort(404)
            else:
                bpassword = request_body["password"].encode("utf-8")
                bhash_pass = check_user.hashed_password.encode("utf-8")
                pass_match = bcrypt.checkpw(bpassword, bhash_pass)
                #   If password match, set session and update last_login time
                if pass_match:
                    session["user_email"] = check_user.email
                    session["admin_id"] = None
                    check_user.last_login = datetime.datetime.now()
                    db.session.commit()
                    return redirect(url_for("display_user_data", user_id=check_user.id))
                #   If incorrect password submitted, unauthorized access abort.
                else:
                    abort(401)
        else:
            abort(405)
    except Exception as e:
        db.session.rollback()
        if isinstance(e, HTTPException):
            abort(e.code)
        else:
            abort(500)
    finally:
        db.session.close()


@app.route("/admin/loginForm", methods=["POST"])
def signin_admin_form():
    try:
        if request.method == "POST":
            request_body = request.get_json()
            print(request_body)
            if request_body["username"] == "" or request_body["password"] == "":
                abort(400)
            check_admin = Admin.query.filter_by(username=request_body["username"]).one_or_none()
            if check_admin is None:
                abort(404)
            else:
                bpassword = request_body["password"].encode("utf-8")
                bhash_pass = check_admin.hashed_password.encode("utf-8")
                pass_match = bcrypt.checkpw(bpassword, bhash_pass)
                if pass_match:
                    session["user_email"] = None
                    session["admin_id"] = check_admin.id
                    check_admin.last_login = datetime.datetime.now()
                    print("before commit")
                    db.session.commit()
                    print("commit success")
                    return redirect(url_for("display_admin_panel", admin_id=check_admin.id))
                else:
                    abort(401)
        else:
            abort(405)
    except Exception as e:
        db.session.rollback()
        print("rollback done")
        if isinstance(e, HTTPException):
            abort(e.code)
        else:
            abort(500)
    finally:
        db.session.close()


@app.route("/user/logout", methods=["POST"])
def logout_user():
    try:
        if request.method == "POST":
            check_user = User.query.filter_by(id=request.get_json()["userId"]).one_or_none()
            if check_user is None:
                abort(404)
            session["user_email"] = None
            session["admin_id"] = None
            return redirect(url_for("index"))
        else:
            abort(405)
    except:
        abort(422)
    finally:
        db.session.close()


@app.route("/admin/logout", methods=["POST"])
def logout_admin():
    try:
        if request.method == "POST":
            check_admin = Admin.query.filter_by(id=request.get_json()["adminId"]).one_or_none()
            if check_admin is None:
                abort(404)
            session["user_email"] = None
            session["admin_id"] = None
            return redirect(url_for("signin_admin"))
        else:
            abort(405)
    except:
        abort(422)
    finally:
        db.session.close()


# Error Handlers
@app.errorhandler(400)
def bad_format(error):
    return (
        jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
        }), 400
    )

@app.errorhandler(401)
def unauthorized(error):
    return (
        jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
        }), 401
    )

@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
        }), 404
    )

@app.errorhandler(405)
def not_allowed(error):
    return (
        jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
        }), 405
    )

@app.errorhandler(409)
def conflict(error):
    return (
        jsonify({
        "success": False,
        "error": 409,
        "message": "User already exists"
        }), 409
    )

@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
        }), 422
    )

@app.errorhandler(500)
def internal_server_error(error):
    return (
        jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500
    )
