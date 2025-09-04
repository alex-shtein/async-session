# tests/test_handlers/test_delete_handlers.py
from uuid import uuid4


async def test_delete_user(client, create_user_in_db, get_user_from_db):
    user_data = {
        "id": uuid4(),
        "first_name": "test",
        "last_name": "test",
        "email": "test@test.com",
        "is_active": True,
    }

    await create_user_in_db(**user_data)
    resp = await client.delete(f"/user/?user_id={user_data['id']}")

    assert resp.status_code == 200
    assert resp.json() == {"id": str(user_data["id"])}

    user_from_db = await get_user_from_db(user_data["id"])

    assert user_from_db["first_name"] == user_data["first_name"]
    assert user_from_db["last_name"] == user_data["last_name"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is False
    assert user_from_db["id"] == user_data["id"]


async def test_delete_user_not_found(client):
    user_id = uuid4()
    resp = await client.delete(f"/user/?user_id={user_id}")

    assert resp.status_code == 404
    assert resp.json() == {"detail": f"User with id {user_id} not found."}


async def test_delete_user_user_id_validation_error(client):
    resp = await client.delete("/user/?user_id=123")

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
