# tests/test_handlers/test_create_handlers.py


async def test_create_user(client, get_user_from_db):
    user_data = {"first_name": "test", "last_name": "test", "email": "test@test.com"}

    resp = await client.post("/user/", json=user_data)
    data = resp.json()

    assert resp.status_code == 200
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["email"] == user_data["email"]

    user_from_db = await get_user_from_db(data["id"])

    assert str(user_from_db["id"]) == data["id"]
    assert user_from_db["first_name"] == user_data["first_name"]
    assert user_from_db["last_name"] == user_data["last_name"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True


async def test_create_user_dublicate_email_error(client):
    user_data = {"first_name": "test", "last_name": "test", "email": "test@test.com"}

    resp = await client.post("/user/", json=user_data)

    assert resp.status_code == 200

    user_data_with_dublicate_email = {
        "first_name": "contest",
        "last_name": "contest",
        "email": "test@test.com",
    }

    resp = await client.post("/user/", json=user_data_with_dublicate_email)

    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "users_email_key"'
        in resp.json()["detail"]
    )


async def test_create_user_missing_fields(client):
    resp = await client.post("/user/", json={})
    data = resp.json()

    assert resp.status_code == 422
    assert data["detail"][0]["loc"] == ["body", "first_name"]
    assert data["detail"][0]["msg"] == "Field required"
    assert data["detail"][0]["type"] == "missing"

    assert data["detail"][1]["loc"] == ["body", "last_name"]
    assert data["detail"][1]["msg"] == "Field required"
    assert data["detail"][1]["type"] == "missing"

    assert data["detail"][2]["loc"] == ["body", "email"]
    assert data["detail"][2]["msg"] == "Field required"
    assert data["detail"][2]["type"] == "missing"


async def test_create_user_invalid_first_name(client):
    user_data = {"first_name": 123, "last_name": "Valid", "email": "test@test.com"}
    resp = await client.post("/user/", json=user_data)
    data = resp.json()

    assert resp.status_code == 422
    assert data["detail"][0]["loc"] == ["body", "first_name"]
    assert data["detail"][0]["msg"] == "Input should be a valid string"
    assert data["detail"][0]["type"] == "string_type"


async def test_create_user_invalid_last_name(client):
    user_data = {"first_name": "Nikolai", "last_name": 456, "email": "test@test.com"}
    resp = await client.post("/user/", json=user_data)
    data = resp.json()

    assert resp.status_code == 422
    assert data["detail"][0]["loc"] == ["body", "last_name"]
    assert data["detail"][0]["msg"] == "Input should be a valid string"
    assert data["detail"][0]["type"] == "string_type"


async def test_create_user_invalid_email(client):
    user_data = {"first_name": "Nikolai", "last_name": "Swicidex", "email": "Zol"}
    resp = await client.post("/user/", json=user_data)
    data = resp.json()

    assert resp.status_code == 422
    assert data["detail"][0]["loc"] == ["body", "email"]
    assert (
        data["detail"][0]["msg"]
        == "value is not a valid email address: An email address must have an @-sign."
    )
    assert data["detail"][0]["type"] == "value_error"