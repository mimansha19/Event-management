# User registration and login
from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.utils.auth import hash_password, verify_password
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["POST"])
def register(): # Register a new user
    data = request.json
    user = User(
        username=data["username"],
        email=data["email"],
        password=hash_password(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201

@bp.route("/login", methods=["POST"])
def login(): # Authenticate and return JWT
    data = request.json
    user = User.query.filter((User.username == data["username"]) | (User.email == data["username"])).first()
    if user and verify_password(data["password"], user.password):
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token}), 200
    return jsonify({"msg": "Invalid credentials"}), 401