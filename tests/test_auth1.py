from app import app, db

def test_register_and_login():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # desactivar CSRF en tests

    with app.app_context():
        db.create_all()

    client = app.test_client()

    # Registro
    resp = client.post(
        "/api/register",
        json={"username": "testuser", "password": "123456"},
    )
    assert resp.status_code == 201

    # Login
    resp = client.post(
        "/api/login",
        json={"username": "testuser", "password": "123456"},
    )
    assert resp.status_code == 200
