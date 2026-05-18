# UNO Online Multiplayer Card Game
### Oliver Trojanowski - Wint Kay Khine Myint - Chantelle Kwenda

## Specification

### Endpoints
#### Home:
GET / -> Home page
- Request: Session token (header)
- Response:
  - 200 OK, Home page (text/html)
  - 401 Unauthorized

#### Login:
GET /login -> Login page
- Request: N/A
- Response:
  - 200 OK, Login page (text/html)

POST /token -> Logging in
- Request: Username and password (application/x-www-form-urlencoded)
- Response:
  - 201 Created, Session token (application/json)
  - 401 Unauthorized
  - 422 Unprocessable Content

DELETE /token -> Logging out
- Request: Session token (header)
- Response:
  - 204 No Content

#### Account:
GET /account -> Account page
- Request: Session token (header)
- Response:
  - 200 OK, User account page (text/html)
  - 401 Unauthorized

POST /account -> Register account
- Request: Username and password (application/x-www-form-urlencoded)
- Response:
  - 201 Created, Session token (application/json)
  - 409 Conflict
  - 422 Unprocessable Content

GET /account/statistics -> Get account statistics
  - Request: Session token (header)
  - Response:
    - 200 OK, Account statistics (application/json)
    - 401 Unauthorized
    - 404 Not found

PATCH /account/statistics -> Update account statistics
- Request: Session token (header), Account statistics (application/json)
- Response:
  - 204 No Content
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not found
  - 422 Unprocessable Content

DELETE /account -> Delete account
- Request: Session token (header)
- Response:
  - 204 No Content
  - 401 Unauthorized
  - 404 Not found

#### Friends:
GET /friends -> Get friends list
- Request: Session token (header)
- Response:
  - 200 OK, friends list (application/json)
  - 401 Unauthorized

POST /friends -> Send friend request
- Request: Session token (header), Friend username (application/x-www-form-urlencoded)
- Response:
  - 201 Created
  - 401 Unauthorized
  - 422 Unprocessable Content

PATCH /friends/{fid} -> Accept/Reject friend request
- Request: Session token (header), Action (application/x-www-form-urlencoded)
- Response:
  - 204 No Content
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
  - 422 Unprocessable Content

DELETE /friends/{fid} -> Delete friend
- Request: Session token (header)
- Response:
  - 204 No Content
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
  - 422 Unprocessable Content

#### Game:
GET /game/{gid} -> Game page
- Request: Session token (header)
- Response:
  - 101 Switching Protocols
  - 200 OK, Game page (text/html)
  - 401 Unauthorized

### Database
#### Tables:
Accounts:
- Username (string, primary key)
- Password (hashed string)

Statistics:
- Status (enum ex. online)
- Description (string)
- Wins (int)
- Losses (int)\
...
- Account (unique)

Friends:
- FID (guid, primary key)
- Status (enum ex. pending, accept, reject)
- Username1
- Username2

#### Relation:
- Accounts -- Statistics (one-to-one)
- Accounts <-> Accounts (many=to-many via Friends table)

### Architecture
![Diagram](uno_arch.drawio.svg)