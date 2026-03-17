## 1. Arquitectura e infraestructura

### Tecnologías principales

- Backend: Flask 3.x
- Autenticación: Flask-JWT-Extended
- ORM / Base de datos: Flask-SQLAlchemy + SQLite (`forum.db`)
- CORS: Flask-CORS
- Contenedores: Docker + `docker-compose`
- CI/CD: GitHub Actions (workflows en `.github/workflows/`)
- Pruebas: tests en la carpeta `tests/`
- Cliente API: Postman (colección en `postman/`)

### Estructura de carpetas (simplificada)

```text
foro-docker/
  app.py                 # Punto de entrada Flask, rutas y seguridad
  models.py              # Modelos User y Thread con SQLAlchemy
  index.html             # Frontend mínimo del foro
  requirements.txt       # Dependencias de Python
  docker-compose.yml     # Orquestación con Docker
  Dockerfile             # Imagen de la app Flask
  tests/                 # Pruebas automatizadas
  postman/
    PRUEBAS POSTMAN.postman_collection.json
  instance/
    forum.db             # Base de datos SQLite (se genera al arrancar)
2. Puesta en marcha del proyecto
2.1. Ejecución local (sin Docker)
Requisitos: Python 3.14 y pip.

bash
# 1. Clonar el repositorio
git clone https://github.com/Javier-Trapero/Foro-basico-docker-threads.git
cd Foro-basico-docker-threads

# 2. (Opcional) Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\activate  # Windows

# 3. Instalar dependencias
python -m pip install -r requirements.txt

# 4. Lanzar la aplicación
python app.py
La aplicación quedará expuesta en:

http://127.0.0.1:5000

2.2. Ejecución con Docker Compose
bash
# Desde la raíz del proyecto
docker-compose up --build
Esto levanta el contenedor de la aplicación Flask en el puerto 5000 del host:

http://localhost:5000

Para parar y borrar contenedores:

bash
docker-compose down
3. API del foro
3.1. Autenticación
POST /api/register
Crea un nuevo usuario.

Body (JSON):

json
{
  "username": "usuario123",
  "password": "123456"
}
Respuestas:

201 Created: usuario creado.

400 Bad Request: campos faltantes o inválidos.

POST /api/login
Genera un token JWT para un usuario válido.

Body (JSON):

json
{
  "username": "usuario123",
  "password": "123456"
}
Respuestas:

200 OK: devuelve {"token": "...", "user": {...}}.

400 Bad Request: formato de credenciales inválido.

401 Unauthorized: usuario no existe o contraseña incorrecta.

3.2. Hilos
GET /api/threads
Devuelve la lista de hilos ordenados por fecha de creación (más reciente primero).

Respuestas:

200 OK: {"threads": [ ... ]}

POST /api/threads
Crea un nuevo hilo. Protegido por token CSRF.

Headers:

Content-Type: application/json

X-CSRF-Token: <token> (mismo valor que la cookie CSRF generada)

Body (JSON):

json
{
  "title": "Título del hilo",
  "content": "Contenido del hilo"
}
Respuestas:

201 Created: hilo creado.

400 Bad Request: título o contenido inválidos.

403 Forbidden: token CSRF inválido o ausente.

3.3. Salud
GET /health
Devuelve el estado básico del servicio.

Respuesta:

200 OK: {"status": "ok"}

4. Colección de Postman
Se incluye una colección para probar todos los endpoints:

Ruta: postman/PRUEBAS POSTMAN.postman_collection.json

Importar en Postman
Abrir Postman.

Botón Import → pestaña File.

Seleccionar el archivo PRUEBAS POSTMAN.postman_collection.json.

La colección aparecerá con peticiones para:

Obtener token CSRF.

Registrar usuario.

Login.

Listar y crear hilos. [web:555]

5. Medidas de seguridad (OWASP Top 10)
El proyecto incorpora medidas para mitigar varios riesgos OWASP Top 10:2021. [web:562][web:552]

A01 – Broken Access Control
Uso de JWT para controlar acceso a recursos:

python
token = create_access_token(identity=user.id)
Las rutas que requieran autenticación se pueden proteger con:

python
@jwt_required()
def recurso_privado():
    ...
A02 – Cryptographic Failures
Contraseñas almacenadas mediante hash (nunca en texto plano):

python
# models.py
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, password):
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
Clave JWT configurable por entorno:

python
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")
A03 – Injection
Uso de SQLAlchemy en lugar de concatenar SQL manualmente:

python
user = User.query.filter_by(username=username).first()
Validación estricta de entrada antes de usarla:

python
if not validate_username(username) or not validate_password(password):
    return jsonify({"error": "Credenciales inválidas"}), 400
Validaciones similares para título y contenido de hilos (validate_thread_title, validate_thread_content).

A05 – Security Misconfiguration
Cabeceras de seguridad añadidas en un after_request:

python
@app.after_request
def add_security_headers_and_csrf_cookie(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data:",
    )
    ...
    return response
CORS controlado explícitamente:

python
from flask_cors import CORS
CORS(app)
A07 – Identification and Authentication Failures
Proceso de login controlado:

python
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not validate_username(username) or not validate_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 200
Diferenciación clara entre:

400 → formato de entrada incorrecto.

401 → credenciales erróneas.

A08 – Software and Data Integrity Failures
Dependencias controladas en requirements.txt.

Recomendado revisar periódicamente versiones y vulnerabilidades en dependencias. [web:557][web:560]

A09 – Security Logging and Monitoring Failures
Endpoints de salud (/health) y logs de Flask facilitan la monitorización. [web:535]

Se recomienda desactivar debug=True en producción y añadir logging estructurado.

6. Protección CSRF
Para proteger operaciones que modifican datos (POST /api/threads) se utiliza un token CSRF propio.

Generación del token (cookie)
En cada respuesta se asegura la existencia de la cookie CSRF:

python
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

@app.after_request
def add_security_headers_and_csrf_cookie(response):
    ...
    request_csrf = request.cookies.get(CSRF_COOKIE_NAME)
    if not request_csrf:
        token = secrets.token_hex(16)
        response.set_cookie(
            CSRF_COOKIE_NAME,
            token,
            httponly=False,
            secure=False,   # poner True en HTTPS
            samesite="Lax",
        )
    return response
Verificación del token (decorador)
python
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
Aplicado en:

python
@app.route("/api/threads", methods=["GET", "POST"])
@csrf_protect
def threads():
    ...
7. Incidencias resueltas durante el desarrollo
404 / 405 en /api/login
Causa: el servidor Flask no se estaba ejecutando desde el archivo correcto
y Postman apuntaba a otra URL/puerto.

Solución: ejecutar python app.py desde la raíz del proyecto y usar
exactamente http://127.0.0.1:5000/api/login en Postman. [web:401]
8. Trabajo futuro
Proteger más rutas con @jwt_required.

Añadir roles (admin / usuario normal).

Incorporar logging estructurado y alertas.

Preparar configuración específica para despliegue en producción
con JWT_SECRET_KEY, HTTPS y base de datos externa endurecida.