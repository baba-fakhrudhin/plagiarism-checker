from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from app import db
from app.models import User
from app.utils.validators import validate_email, validate_password
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint("auth", __name__)


# ==========================================================
# SIGNUP
# ==========================================================

@auth_bp.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip().lower()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not email or not username or not password:
        return jsonify({
            "error": "Missing required fields: email, username, password"
        }), 400

    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if not validate_password(password):
        return jsonify({
            "error": "Password must be at least 8 characters with uppercase, lowercase, and numbers"
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    try:
        user = User(
            email=email,
            username=username,
            subscription_plan="free"
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "message": "User created successfully",
            "access_token": access_token,
            "user": user.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Signup failed"}), 500


# ==========================================================
# LOGIN
# ==========================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


# ==========================================================
# GET PROFILE
# ==========================================================

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():

    user_id = get_jwt_identity()

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


# ==========================================================
# UPDATE PROFILE
# ==========================================================

@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():

    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:

        if "username" in data:
            new_username = data["username"].strip()

            if new_username != user.username:
                if User.query.filter_by(username=new_username).first():
                    return jsonify({"error": "Username already taken"}), 409

                user.username = new_username

        if "password" in data:
            if not validate_password(data["password"]):
                return jsonify({
                    "error": "Password must be at least 8 characters with uppercase, lowercase, and numbers"
                }), 400

            user.set_password(data["password"])

        db.session.commit()

        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict()
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Profile update failed"}), 500


# ==========================================================
# LOGOUT
# ==========================================================

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Stateless logout.
    Client must delete token.
    """

    return jsonify({
        "message": "Logout successful. Please remove token from client."
    }), 200
