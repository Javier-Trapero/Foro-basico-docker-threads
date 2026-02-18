from flask import Flask, request, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from models import db, User, Thread

app = Flask(__name__)
CORS(app)

# Configuración
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'change-me-in-production'

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


@app.route('/')
def index():
    return send_file('index.html')


# === REGISTRO ===
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Faltan campos'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Usuario ya existe'}), 409

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password_hash=hashed)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado', 'user': user.to_dict()}), 201


# === LOGIN ===
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Faltan credenciales'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    token = create_access_token(identity=user.id)

    return jsonify({'token': token, 'user': user.to_dict()}), 200


# === VER HILOS ===
@app.route('/api/threads', methods=['GET'])
def get_threads():
    threads = Thread.query.order_by(Thread.created_at.desc()).all()
    return jsonify({'threads': [t.to_dict() for t in threads]}), 200


# === CREAR HILO (SIN JWT POR AHORA) ===
@app.route('/api/threads', methods=['POST'])
def create_thread():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se envió JSON'}), 400

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'error': 'Faltan campos title o content'}), 400

    # De momento usamos siempre el primer usuario existente
    user = User.query.first()
    if not user:
        return jsonify({'error': 'No hay usuarios, regístrate primero'}), 400

    thread = Thread(
        title=title,
        content=content,
        user_id=user.id
    )

    db.session.add(thread)
    db.session.commit()

    return jsonify({'message': 'Hilo creado', 'thread': thread.to_dict()}), 201


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
