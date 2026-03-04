from app import app, db, User

def setup_function(function):
    # Cada test empieza con BD limpia en memoria
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.drop_all()
        db.create_all()

def test_register_and_login():
    client = app.test_client()

    # Registro
    resp = client.post("/api/register", json={
        "username": "testuser",
        "password": "1234"
    })
    assert resp.status_code == 201

    # Login
    resp = client.post("/api/login", json={
        "username": "testuser",
        "password": "1234"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "token" in data
