# tests/test_handlers/test_update_handlers.py
from uuid import uuid4

import pytest
import json


async def test_update_user(client, create_user_in_db, get_user_from_db):
    user_data = {
        "id": uuid4(),
        "first_name": "test",
        "last_name": "test",
        "email": "test@test.com",
        "is_active": True,
    }

    update_data = {
        "first_name": "updated",
        "last_name": "user",
        "email": "updated@test.com",
    }

    await create_user_in_db(**user_data)
    resp = await client.patch(f"/user/?user_id={user_data['id']}", json=update_data)

    assert resp.status_code == 200
    assert resp.json() == {"id": str(user_data["id"])}

    user_from_db = await get_user_from_db(user_data["id"])

    assert user_from_db["id"] == user_data["id"]
    assert user_from_db["first_name"] == update_data["first_name"]
    assert user_from_db["last_name"] == update_data["last_name"]
    assert user_from_db["email"] == update_data["email"]
    assert user_from_db["is_active"] == user_data["is_active"]


@pytest.mark.parametrize(
    "user_data_updated, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {"detail": "At least one parameter for user update should be provided"},
        ),
        (
            {"email": ""},
            422,
            {
                "detail": [
                    {
                        "ctx": {"reason": "An email address must have an @-sign."},
                        "input": "",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: An email address must have an @-sign.",
                        "type": "value_error",
                    }
                ]
            },
        ),
        (
            {"first_name": ""},
            422,
            {
                "detail": "First name should contain only letters",
            },
        ),
        (
            {"last_name": ""},
            422,
            {
                "detail": "Last name should contain only letters",
            },
        ),
        (
            {"first_name": "123"},
            422,
            {
                "detail": "First name should contain only letters",
            },
        ),
        (
            {"last_name": "123"},
            422,
            {
                "detail": "Last name should contain only letters",
            },
        ),
        (
            {"email": "123"},
            422,
            {
                "detail": [
                    {
                        "ctx": {"reason": "An email address must have an @-sign."},
                        "input": "123",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: An email address must have an @-sign.",
                        "type": "value_error",
                    }
                ]
            },
        ),
    ],
)
async def test_update_user_validation_error(
    client,
    create_user_in_db,
    user_data_updated,
    expected_status_code,
    expected_detail,
):
    user_data = {
        "id": uuid4(),
        "first_name": "test1",
        "last_name": "test1",
        "email": "test1@test.com",
        "is_active": True,
    }

    await create_user_in_db(**user_data)
    resp = await client.patch(
        f"/user/?user_id={user_data["id"]}", data=json.dumps(user_data_updated)
    )

    assert resp.status_code == expected_status_code

    resp_data = resp.json()

    assert resp_data == expected_detail


async def test_update_user_id_validation_error(client):
    user_data_updated = {
        "first_name": "test",
        "last_name": "test",
        "email": "test@test.com",
    }
    resp = await client.patch(f"/user/?user_id=123", data=json.dumps(user_data_updated))

    assert resp.status_code == 422

    data_from_response = resp.json()

    assert data_from_response == {
        "detail": [
            {
                "ctx": {
                    "error": "invalid length: expected length 32 for simple format, found 3",
                },
                "input": "123",
                "loc": ["query", "user_id"],
                "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 3",
                "type": "uuid_parsing",
            }
        ]
    }


async def test_update_user_not_found_error(client):
    user_data_updated = {
        "first_name": "test",
        "last_name": "test",
        "email": "test@test.com",
    }
    user_id = uuid4()
    resp = await client.patch(
        f"/user/?user_id={user_id}", data=json.dumps(user_data_updated)
    )
    assert resp.status_code == 404

    resp_data = resp.json()

    assert resp_data == {"detail": f"User with id {user_id} not found."}
