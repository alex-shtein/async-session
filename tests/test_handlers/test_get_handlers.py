# tests/test_handlers/test_get_handlers.py
from uuid import uuid4


async def test_get_user(client, create_user_in_db):
    user_data = {
        "id": uuid4(),
        "first_name": "test",
        "last_name": "test",
        "email": "test@test.com",
        "is_active": True,
    }

    await create_user_in_db(**user_data)
    resp = await client.get(f"/user/?user_id={user_data['id']}")

    assert resp.status_code == 200

    user_from_resp = resp.json()

    assert user_from_resp["id"] == str(user_data["id"])
    assert user_from_resp["first_name"] == user_data["first_name"]
    assert user_from_resp["last_name"] == user_data["last_name"]
    assert user_from_resp["email"] == user_data["email"]
    assert user_from_resp["is_active"] == user_data["is_active"]


async def test_get_user_id_validation_error(client, create_user_in_db):
    user_data = {
        "id": uuid4(),
        "first_name": "test",
        "last_name": "test",
        "email": "test@test.com",
        "is_active": True,
    }

    await create_user_in_db(**user_data)
    resp = await client.get("/user/?user_id=123")

    assert resp.status_code == 422

    assert resp.json() == {
        "detail": [
            {
                "ctx": {
                    "error": "invalid length: expected length 32 for simple format, found 3",
                },
                "input": "123",
                "loc": [
                    "query",
                    "user_id",
                ],
                "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 3",
                "type": "uuid_parsing",
            }
        ]
    }


async def test_get_user_not_found(client, create_user_in_db):
    user_data = {
        "id": uuid4(),
        "first_name": "test",
        "last_name": "test",
        "email": "test@test.com",
        "is_active": True,
    }

    await create_user_in_db(**user_data)

    temp_user_id = uuid4()
    resp = await client.get(f"/user/?user_id={temp_user_id}")

    assert resp.status_code == 404
    assert resp.json() == {"detail": f"User with id {temp_user_id} not found."}
