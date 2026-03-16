from app import app, db, User

def test_register_and_login():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # por si acaso
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.drop_all()
        db.create_all()

    client = app.test_client()

    # Registro con contraseña válida (mínimo 6)
    resp = client.post(
        "/api/register",
        json={"username": "testuser", "password": "123456"},
    )
    assert resp.status_code == 201

    # Login con las mismas credenciales
    resp = client.post(
        "/api/login",
        json={"username": "testuser", "password": "123456"},
    )
    assert resp.status_code == 200

    data = resp.get_json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"
