from flask import Flask, request, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_cors import CORS
from models import db, User, Thread

import os
import re
import secrets
from functools import wraps

app = Flask(__name__)
CORS(app)

# Configuración
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///forum.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")

# Configuración CSRF sencilla
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


@app.route("/")
def index():
    return send_file("index.html")


# === VALIDACIÓN DE ENTRADAS ===

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{3,20}$")


def validate_username(username: str) -> bool:
    if not username:
        return False
    return USERNAME_REGEX.match(username) is not None


def validate_password(password: str) -> bool:
    if not password:
        return False
    return 6 <= len(password) <= 50


def validate_thread_title(title: str) -> bool:
    if not title:
        return False
    return 3 <= len(title) <= 100


def validate_thread_content(content: str) -> bool:
    if not content:
        return False
    return 3 <= len(content) <= 1000


# === CABECERAS DE SEGURIDAD Y CSRF COOKIE ===

@app.after_request
def add_security_headers_and_csrf_cookie(response):
    # Cabeceras de seguridad básicas
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:",
    )

    # Si ya hay cookie CSRF no hacemos nada
    request_csrf = request.cookies.get(CSRF_COOKIE_NAME)
    if not request_csrf:
        token = secrets.token_hex(16)
        response.set_cookie(
            CSRF_COOKIE_NAME,
            token,
            httponly=False,  # frontend debe leerla
            secure=False,    # ponlo True si usas HTTPS
            samesite="Lax",
        )
    return response


# === PROTECCIÓN CSRF PARA PETICIONES MODIFICADORAS ===

def csrf_protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
            header_token = request.headers.get(CSRF_HEADER_NAME)

            if not cookie_token or not header_token or cookie_token != header_token:
                return jsonify({"error": "CSRF token inválido"}), 403

        return f(*args, **kwargs)

    return wrapper


# === REGISTRO ===
@app.route("/api/register", methods=["POST"])
@csrf_protect
def register():
    data = request.get_json()

    username = (data or {}).get("username", "").strip()
    password = (data or {}).get("password", "")

    if not validate_username(username) or not validate_password(password):
        return jsonify({"error": "Datos inválidos"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Usuario ya existe"}), 409

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    is_admin = username == "admin"

    user = User(
        username=username,
        password_hash=hashed,
        is_admin=is_admin,
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuario registrado", "user": user.to_dict()}), 201


# === LOGIN ===
@app.route("/api/login", methods=["POST"])
@csrf_protect
def login():
    data = request.get_json()

    username = (data or {}).get("username", "").strip()
    password = (data or {}).get("password", "")

    if not validate_username(username) or not validate_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 200


# === HILOS: LISTAR Y CREAR ===
@app.route("/api/threads", methods=["GET", "POST"])
@csrf_protect
def threads():
    if request.method == "GET":
        threads = Thread.query.order_by(Thread.created_at.desc()).all()
        return jsonify({"threads": [t.to_dict() for t in threads]}), 200

    if request.method == "POST":
        data = request.get_json()
        title = (data or {}).get("title", "").strip()
        content = (data or {}).get("content", "").strip()

        # Validación básica de entrada
        if not validate_thread_title(title) or not validate_thread_content(content):
            return jsonify({"error": "Datos de hilo inválidos"}), 400

        # Por ahora autor anónimo (podrías usar el JWT para obtener el usuario)
        author = "Anónimo"

        thread = Thread(
            title=title,
            content=content,
            author=author,
        )
        db.session.add(thread)
        db.session.commit()

        return jsonify(
            {
                "message": "Hilo creado",
                "thread": thread.to_dict(),
            }
        ), 201


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
