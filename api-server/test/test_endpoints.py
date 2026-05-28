from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.endpoints import *
from src.auth import validate_jwt

from main import app, JWT_NAME
client = TestClient(app)

def clear_cookies():
    client.cookies.clear()

def set_valid_cookie():
    client.cookies.set(JWT_NAME, generate_jwt("abcdefg-hijklmnop"))

def test_post_me_201():
    clear_cookies()
    mock_query_result = {"account_id": "abcdefg-hijklmnop"}
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        res = client.post("/me", data={
            "username": "john",
            "password": "12345"
        })
    cookie_str = res.headers.get("set-cookie")
    token = res.cookies.get(JWT_NAME)

    assert res.status_code == 201
    assert "HttpOnly" in cookie_str
    validate_jwt(token)

def test_post_me_409():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=Exception("username exists"))):
        res = client.post("/me", data={
            "username": "john",
            "password": "12345"
        })
    cookie_str = res.headers.get("set-cookie")

    assert res.status_code == 409
    assert cookie_str is None

def test_delete_me_204():
    set_valid_cookie()
    with patch("src.endpoints.db_execute"):
        res = client.delete("/me")
    token = res.cookies.get(JWT_NAME)

    assert res.status_code == 204
    assert token is None

def test_delete_me_401():
    clear_cookies()
    with patch("src.endpoints.db_execute"):
        res = client.delete("/me")

    assert res.status_code == 401

def test_post_me_token_200():
    clear_cookies()
    mock_query_result = {"account_id": "abcdefg-hijklmnop"}
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        res = client.post("/me/token", data={
            "username": "john",
            "password": "12345"
        })
    cookie_str = res.headers.get("set-cookie")
    token = res.cookies.get(JWT_NAME)

    assert res.status_code == 200
    assert "HttpOnly" in cookie_str
    validate_jwt(token)

def test_post_me_token_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        res = client.post("/me/token", data={
            "username": "john",
            "password": "12345"
        })
    cookie_str = res.headers.get("set-cookie")

    assert res.status_code == 401
    assert cookie_str is None

def test_delete_me_token_204():
    set_valid_cookie()
    res = client.delete("/me/token")
    token = res.cookies.get(JWT_NAME)

    assert res.status_code == 204
    assert token is None

def test_get_me_friends_200():
    set_valid_cookie()
    mock_query_result = [
        {"username": "jane", "status": "accepted"},
        {"username": "mary", "status": "pending"}
    ]
    with patch("src.endpoints.db_query", new=AsyncMock(return_value=mock_query_result)):
        res = client.get("/me/friends")

    assert res.status_code == 200
    assert res.json() == mock_query_result

def test_get_me_friends_401():
    clear_cookies()
    with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
        res = client.get("/me/friends")

    assert res.status_code == 401

def test_post_me_friends_201():
    set_valid_cookie()
    mock_query_result = {"account_id": "bcdefgh-ijklmnop"}
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.post("/me/friends/bcdefgh-ijklmnop")

    assert res.status_code == 201

def test_post_me_friends_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.post("/me/friends/bcdefgh-ijklmnop")

    assert res.status_code == 401

def test_post_me_friends_404():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.post("/me/friends/bcdefgh-ijklmnop")

    assert res.status_code == 404

def test_post_me_friends_self_404():
    set_valid_cookie()
    mock_query_result = {"account_id": "abcdefg-hijklmnop"}
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.post("/me/friends/abcdefg-hijklmnop")

    assert res.status_code == 404

def test_patch_me_friends_accept_200():
    set_valid_cookie()
    mock_query_result = {"status": "pending"}
    mock_execute = AsyncMock()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        with patch("src.endpoints.db_execute", new=mock_execute):
            res = client.patch("/me/friends/bcdefgh-ijklmnop", data={
                "action": "accept"
            })

    assert res.status_code == 200
    mock_execute.assert_awaited_once()

def test_patch_me_friends_reject_200():
    set_valid_cookie()
    mock_query_result = {"status": "pending"}
    mock_execute = AsyncMock()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        with patch("src.endpoints.db_execute", new=mock_execute):
            res = client.patch("/me/friends/bcdefgh-ijklmnop", data={
                "action": "reject"
            })

    assert res.status_code == 200
    mock_execute.assert_awaited_once()

def test_patch_me_friends_400():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value={"status": "pending"})):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.patch("/me/friends/bcdefgh-ijklmnop", data={
                "action": "maybe"
            })

    assert res.status_code == 400

def test_patch_me_friends_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value={"status": "pending"})):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.patch("/me/friends/bcdefgh-ijklmnop", data={
                "action": "accept"
            })

    assert res.status_code == 401

def test_patch_me_friends_404():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.patch("/me/friends/bcdefgh-ijklmnop", data={
                "action": "accept"
            })

    assert res.status_code == 404

def test_delete_me_friends_204():
    set_valid_cookie()
    mock_query_result = {"status": "accepted"}
    mock_execute = AsyncMock()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        with patch("src.endpoints.db_execute", new=mock_execute):
            res = client.delete("/me/friends/bcdefgh-ijklmnop")

    assert res.status_code == 204
    mock_execute.assert_awaited_once()

def test_delete_me_friends_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value={"status": "accepted"})):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.delete("/me/friends/bcdefgh-ijklmnop")

    assert res.status_code == 401

def test_delete_me_friends_404():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.delete("/me/friends/bcdefgh-ijklmnop")

    assert res.status_code == 404
