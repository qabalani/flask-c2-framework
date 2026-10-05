from c2 import create_app


def test_register_and_beacon():
    app = create_app()
    client = app.test_client()

    r = client.post("/api/register", json={
        "uid": "test123", "hostname": "box", "username": "u", "os": "Linux"
    })
    assert r.status_code == 200
    assert "key" in r.get_json()

    r = client.post("/api/beacon/test123")
    assert r.status_code == 200
