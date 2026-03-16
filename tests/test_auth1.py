from app import app, db, User

def test_register_and_login():
    # Config especial para entorno de tests
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    client = app.test_client()

    # Limpiamos la base de datos de usuarios de prueba (opcional)
    with app.app_context():
        User.query.filter_by(username="testuser").delete()
        db.session.commit()

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