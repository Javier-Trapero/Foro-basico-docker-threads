🚀 Foro básico con Flask, JWT y Docker
Foro minimalista con API REST segura 🎯
Flask + JWT + CSRF + Docker + CI/CD con GitHub Actions.

🏗️ Arquitectura e infraestructura
🔥 Tecnologías principales
| Componente    | Tecnología                |
| ------------- | ------------------------- |
| Backend       | Flask 3.x                 |
| Autenticación | Flask-JWT-Extended        |
| Base de datos | Flask-SQLAlchemy + SQLite |
| CORS          | Flask-CORS                |
| Contenedores  | Docker + docker-compose   |
| CI/CD         | GitHub Actions            |
| Pruebas       | pytest (carpeta tests/)   |
| API Client    | Postman Collection        |

📁 Estructura del proyecto
foro-docker/
├── app.py                 # 🎯 Punto de entrada Flask
├── models.py              # 🗄️ Modelos User/Thread
├── index.html             # 🖥️ Frontend básico
├── requirements.txt       # 📦 Dependencias
├── docker-compose.yml     # 🐳 Orquestación
├── Dockerfile             # 🐳 Imagen app
├── tests/                 # 🧪 Pruebas automatizadas
├── postman/               # 📋 Colección Postman
└── instance/
    └── forum.db           # 💾 SQLite DB

⚡ Puesta en marcha (5 minutos ⏱️)
🖥️ Opción 1: Local (sin Docker)
Requisitos: Python 3.14+

# 🚀 Clonar e instalar
git clone https://github.com/Javier-Trapero/Foro-basico-docker-threads.git
cd Foro-basico-docker-threads

# 🐍 Entorno virtual (opcional)
python -m venv .venv && source .venv/bin/activate  # Linux/Mac
# .\.venv\Scripts\activate  # Windows

pip install -r requirements.txt
python app.py

✅ Listo en: http://127.0.0.1:5000

🐳 Opción 2: Docker Compose (Recomendado)
docker-compose up --build
✅ Listo en: http://localhost:5000
🛑 Parar:
docker-compose down

🔌 API REST (Documentada)
🔐 Autenticación

| Método | Endpoint      | Descripción            |
| ------ | ------------- | ---------------------- |
| POST   | /api/register | 📝 Crear usuario       |
| POST   | /api/login    | 🔑 Obtener JWT         |
| GET    | /health       | ❤️ Estado del servicio |

Ejemplo Login:
{
  "username": "usuario123",
  "password": "123456789"
}
✅ Respuesta: {"token": "eyJ...", "user": {...}}

🧵 Hilos del foro
Método	Endpoint	Autenticación	Descripción
GET	/api/threads	No	📋 Listar hilos
POST	/api/threads	CSRF	➕ Crear hilo
Crear hilo (requiere X-CSRF-Token header):

{
  "title": "¡Mi primer hilo!",
  "content": "Contenido del debate..."
}

📱 Postman Collection (¡Importa y prueba!)
📥 Archivo: postman/PRUEBAS POSTMAN.postman_collection.json

🔥 Incluye:
✅ Token CSRF automático
✅ Registro/Login
✅ Listar/Crear hilos
✅ Todas las validaciones

🛡️ Seguridad OWASP Top 10
| OWASP                         | Protección implementada  | Ejemplo                 |
| ----------------------------- | ------------------------ | ----------------------- |
| A01 Broken Access Control     | @jwt_required()          | JWT por usuario ID      |
| A02 Cryptographic Failures    | generate_password_hash() | Contraseñas hasheadas   |
| A03 Injection                 | SQLAlchemy ORM           | User.query.filter_by()  |
| A05 Security Misconfiguration | CSP, X-Frame-Options     | Headers de seguridad    |
| A07 Auth Failures             | Validación 400/401       | Formato vs credenciales |
| CSRF                          | Token doble envío        | Cookie + Header         |

🔐 Headers de seguridad automáticos

X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
CSP: default-src 'self'; script-src 'self'...

🛡️ Protección CSRF (Doble envío)
Patrón: Cookie csrf_token + Header X-CSRF-Token
# Automático en cada respuesta
response.set_cookie("csrf_token", secrets.token_hex(16), 
                   httponly=False, samesite="Lax")
# Verificación en POST/PUT/DELETE
if cookie_token != header_token:
    return 403 "CSRF inválido"
Aplicado: @csrf_protect en /api/threads

🐛 Problemas resueltos
| Error              | Causa                 | ✅ Solución                                            |
| ------------------ | --------------------- | -------------------------------------------------------|
| 404/405 /api/login | Puerto/URL incorrecta | python app.py + http://127.0.0.1:5000/api/login github​ |

🚀 Próximos pasos
🔒 Más rutas con @jwt_required()
📊 Logging estructurado + alertas
