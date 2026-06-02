import os
from fastapi.testclient import TestClient
from asyncpg import UniqueViolationError
from unittest.mock import AsyncMock, patch

os.environ.setdefault("JWT_NAME", "access_token")
os.environ.setdefault("JWT_SECRET", "9bxhAgLv4W5PhW4VNglCj4KQjEmLnLZy")
os.environ.setdefault("JWT_SESSION_LENGTH", "7200")

from src.endpoints import *
from src.auth import validate_jwt, JWT_NAME

from main import app
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
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=UniqueViolationError("username exists"))):
        res = client.post("/me", data={
            "username": "john",
            "password": "12345"
        })
    cookie_str = res.headers.get("set-cookie")

    assert res.status_code == 409
    assert cookie_str is None

def test_post_me_422():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock()):
        res = client.post("/me", data={
            "username": "john"
        })

    assert res.status_code == 422

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

def test_put_me_200():
    set_valid_cookie()
    mock_execute = AsyncMock()
    with patch("src.endpoints.db_execute", new=mock_execute):
        res = client.put("/me", json={
            "username": "john",
            "password": "12345",
            "status": "online",
            "description": "Ready to play"
        })

    assert res.status_code == 200
    mock_execute.assert_awaited_once()

def test_put_me_400():
    set_valid_cookie()
    with patch("src.endpoints.db_execute", new=AsyncMock()):
        res = client.put("/me", json={
            "status": "away"
        })

    assert res.status_code == 400

def test_put_me_malformed_body_400():
    set_valid_cookie()
    with patch("src.endpoints.db_execute", new=AsyncMock()):
        res = client.put("/me", json=["username", "john"])

    assert res.status_code == 400

def test_put_me_malformed_field_400():
    set_valid_cookie()
    with patch("src.endpoints.db_execute", new=AsyncMock()):
        res = client.put("/me", json={
            "password": 12345
        })

    assert res.status_code == 400

def test_put_me_401():
    clear_cookies()
    with patch("src.endpoints.db_execute", new=AsyncMock()):
        res = client.put("/me", json={
            "status": "online"
        })

    assert res.status_code == 401

def test_put_me_409():
    set_valid_cookie()
    with patch("src.endpoints.db_execute", new=AsyncMock(side_effect=UniqueViolationError("username exists"))):
        res = client.put("/me", json={
            "username": "jane"
        })

    assert res.status_code == 409

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

def test_post_me_token_422():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock()):
        res = client.post("/me/token", data={
            "username": "john"
        })

    assert res.status_code == 422

def test_delete_me_token_204():
    set_valid_cookie()
    res = client.delete("/me/token")
    token = res.cookies.get(JWT_NAME)

    assert res.status_code == 204
    assert token is None

def test_get_me_info_200():
    set_valid_cookie()
    mock_query_result = {
        "username": "john",
        "status": "online",
        "description": "Ready to play",
        "wins": 5,
        "losses": 2,
        "total_score": 350
    }
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        res = client.get("/me/info")

    assert res.status_code == 200
    assert res.json() == mock_query_result

def test_get_me_info_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        res = client.get("/me/info")

    assert res.status_code == 401

def test_get_me_games_200():
    set_valid_cookie()
    mock_query_result = [
        {"start_time": 1700000000, "end_time": 1700000300, "score": 120, "win": True},
        {"start_time": 1700000400, "end_time": 1700000700, "score": 80, "win": False}
    ]
    with patch("src.endpoints.db_query", new=AsyncMock(return_value=mock_query_result)):
        res = client.get("/me/games")

    assert res.status_code == 200
    assert res.json() == mock_query_result

def test_get_me_games_401():
    clear_cookies()
    with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
        res = client.get("/me/games")

    assert res.status_code == 401

def test_get_me_games_422():
    set_valid_cookie()
    with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
        res = client.get("/me/games?page=not-a-number")

    assert res.status_code == 422

def test_get_me_games_negative_page_400():
    set_valid_cookie()
    with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
        res = client.get("/me/games?page=-1")

    assert res.status_code == 400

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

def test_get_me_friends_422():
    set_valid_cookie()
    with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
        res = client.get("/me/friends?page=not-a-number")

    assert res.status_code == 422

def test_get_me_friends_negative_page_400():
    set_valid_cookie()
    with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
        res = client.get("/me/friends?page=-1")

    assert res.status_code == 400

def test_post_me_friends_201():
    set_valid_cookie()
    mock_query_result = {"account_id": "bcdefgh-ijklmnop"}
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.post("/me/friends/jane")

    assert res.status_code == 201

def test_post_me_friends_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.post("/me/friends/jane")

    assert res.status_code == 401

def test_post_me_friends_404():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.post("/me/friends/jane")

    assert res.status_code == 404

def test_post_me_friends_self_400():
    set_valid_cookie()
    mock_query_result = {"account_id": "abcdefg-hijklmnop"}
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=mock_query_result)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.post("/me/friends/john")

    assert res.status_code == 400

def test_patch_me_friends_accept_200():
    set_valid_cookie()
    mock_query_results = [
        {"account_id": "bcdefgh-ijklmnop"},
        {"status": "pending"},
    ]
    mock_execute = AsyncMock()
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=mock_query_results)):
        with patch("src.endpoints.db_execute", new=mock_execute):
            res = client.patch("/me/friends/jane", data={
                "action": "accept"
            })

    assert res.status_code == 200
    mock_execute.assert_awaited_once()

def test_patch_me_friends_reject_200():
    set_valid_cookie()
    mock_query_results = [
        {"account_id": "bcdefgh-ijklmnop"},
        {"status": "pending"},
    ]
    mock_execute = AsyncMock()
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=mock_query_results)):
        with patch("src.endpoints.db_execute", new=mock_execute):
            res = client.patch("/me/friends/jane", data={
                "action": "reject"
            })

    assert res.status_code == 200
    mock_execute.assert_awaited_once()

def test_patch_me_friends_400():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value={"status": "pending"})):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.patch("/me/friends/jane", data={
                "action": "maybe"
            })

    assert res.status_code == 400

def test_patch_me_friends_422():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value={"status": "pending"})):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.patch("/me/friends/jane", data={})

    assert res.status_code == 422

def test_patch_me_friends_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value={"status": "pending"})):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.patch("/me/friends/jane", data={
                "action": "accept"
            })

    assert res.status_code == 401

def test_patch_me_friends_404():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.patch("/me/friends/jane", data={
                "action": "accept"
            })

    assert res.status_code == 404

def test_delete_me_friends_204():
    set_valid_cookie()
    mock_query_results = [
        {"account_id": "bcdefgh-ijklmnop"},
        {"status": "accepted"},
    ]
    mock_execute = AsyncMock()
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=mock_query_results)):
        with patch("src.endpoints.db_execute", new=mock_execute):
            res = client.delete("/me/friends/jane")

    assert res.status_code == 204
    mock_execute.assert_awaited_once()

def test_delete_me_friends_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value={"status": "accepted"})):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.delete("/me/friends/jane")

    assert res.status_code == 401

def test_delete_me_friends_404():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_execute", new=AsyncMock()):
            res = client.delete("/me/friends/jane")

    assert res.status_code == 404

def test_get_account_info_200():
    set_valid_cookie()
    mock_query_results = [
        {"account_id": "bcdefgh-ijklmnop"},
        {"status": "accepted"},
        {
            "username": "jane",
            "status": "online",
            "description": "UNO fan",
            "wins": 3,
            "losses": 1,
            "total_score": 240
        }
    ]
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=mock_query_results)):
        res = client.get("/account/info/jane")

    assert res.status_code == 200
    assert res.json() == mock_query_results[2]

def test_get_account_info_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        res = client.get("/account/info/jane")

    assert res.status_code == 401

def test_get_account_info_403():
    set_valid_cookie()
    mock_query_results = [
        {"account_id": "bcdefgh-ijklmnop"},
        None
    ]
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=mock_query_results)):
        res = client.get("/account/info/jane")

    assert res.status_code == 403

def test_get_account_info_404():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        res = client.get("/account/info/jane")

    assert res.status_code == 404

def test_get_account_games_200():
    set_valid_cookie()
    mock_query_one_results = [
        {"account_id": "bcdefgh-ijklmnop"},
        {"status": "accepted"}
    ]
    mock_query_result = [
        {"start_time": 1700000000, "end_time": 1700000300, "score": 120, "win": True}
    ]
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=mock_query_one_results)):
        with patch("src.endpoints.db_query", new=AsyncMock(return_value=mock_query_result)):
            res = client.get("/account/games/jane")

    assert res.status_code == 200
    assert res.json() == mock_query_result

def test_get_account_games_401():
    clear_cookies()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
            res = client.get("/account/games/jane")

    assert res.status_code == 401

def test_get_account_games_403():
    set_valid_cookie()
    mock_query_one_results = [
        {"account_id": "bcdefgh-ijklmnop"},
        None
    ]
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=mock_query_one_results)):
        with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
            res = client.get("/account/games/jane")

    assert res.status_code == 403

def test_get_account_games_422():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
            res = client.get("/account/games/jane?page=not-a-number")

    assert res.status_code == 422

def test_get_account_games_negative_page_400():
    set_valid_cookie()
    mock_query_one_results = [
        {"account_id": "bcdefgh-ijklmnop"},
        {"status": "accepted"}
    ]
    with patch("src.endpoints.db_query_one", new=AsyncMock(side_effect=mock_query_one_results)):
        with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
            res = client.get("/account/games/jane?page=-1")

    assert res.status_code == 400

def test_get_account_games_404():
    set_valid_cookie()
    with patch("src.endpoints.db_query_one", new=AsyncMock(return_value=None)):
        with patch("src.endpoints.db_query", new=AsyncMock(return_value=[])):
            res = client.get("/account/games/jane")

    assert res.status_code == 404
