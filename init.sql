CREATE TYPE account_status AS ENUM ('online', 'offline');

CREATE TYPE friend_status AS ENUM ('pending', 'accepted', 'rejected');

CREATE TABLE Accounts (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

CREATE TABLE Statistics (
    account_username TEXT PRIMARY KEY,
    status account_status NOT NULL DEFAULT 'offline',
    description TEXT,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT fk_statistics_account
        FOREIGN KEY (account_username)
        REFERENCES Accounts(username)
        ON DELETE CASCADE
);

CREATE TABLE Friends (
    fid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status friend_status NOT NULL DEFAULT 'pending',
    username1 TEXT NOT NULL,
    username2 TEXT NOT NULL,

    CONSTRAINT fk_friends_user1
        FOREIGN KEY (username1)
        REFERENCES Accounts(username)
        ON DELETE CASCADE,

    CONSTRAINT fk_friends_user2
        FOREIGN KEY (username2)
        REFERENCES Accounts(username)
        ON DELETE CASCADE,

    CONSTRAINT unique_friend_pair UNIQUE (username1, username2),
    CONSTRAINT no_self_friend CHECK (username1 <> username2)
);