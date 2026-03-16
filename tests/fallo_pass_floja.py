from app import app, db

def test_register_short_password_rejected():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.drop_all()
        db.create_all()

    client = app.test_client()

    # Password demasiado corta (menos de 6)
    resp = client.post(
        "/api/register",
        json={"username": "shortpassuser", "password": "123"},
    )

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
