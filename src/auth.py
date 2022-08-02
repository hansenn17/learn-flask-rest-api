from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from src.database import User, db
import validators
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password) < 6:
        return jsonify({'error': 'password less than 6 characters'}), 400

    if len(username) < 3:
        return jsonify({'error': 'username less than 3 characters'}), 400

    if not username.isalnum() or " " in username:
        return jsonify({'error': 'username should be alphanumeric and no spaces'}), 400

    if not validators.email(email):
        return jsonify({'error': 'email is not valid'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'username or email is taken'}), 409

    pwd = generate_password_hash(password)

    try:
        user = User(username=username, email=email, password=pwd)
        db.session.add(user)
        db.session.commit()
    except:
        db.session.rollback()

    return jsonify({
        'message': 'user created',
        'user': {
            'username': username,
            'email': email
        }
    }), 201


@auth.post('/login')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                "user": {
                    "refresh": refresh,
                    "access": access,
                    "username": user.username,
                    "email": user.email
                }
            })

    return jsonify({'error': 'wrong credentials'}), 401


@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }), 200


@auth.post('/token/refresh')
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), 200
