from app import app, db, User


def test_register_and_login():
    # Config especial para tests
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        # Creamos todas las tablas necesarias si no existen
        db.create_all()

    client = app.test_client()

    # Registro
    resp = client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "1234"
        },
    )
    assert resp.status_code == 201

    # Login
    resp = client.post(
        "/api/login",
        json={
            "username": "testuser",
            "password": "1234"
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "token" in data
    assert data["user"]["username"] == "testuser"
