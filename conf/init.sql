CREATE TYPE account_status AS ENUM ('online', 'offline', 'ingame');

CREATE TYPE friend_status AS ENUM ('pending', 'accepted', 'rejected');

CREATE TABLE Accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    status account_status NOT NULL DEFAULT 'offline',
    description TEXT
);

CREATE TABLE Participants (
    account_id UUID NOT NULL,
    game_id UUID NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    win BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_account_id
        FOREIGN KEY (account_id)
        REFERENCES Accounts(account_id)
        ON DELETE CASCADE,
    CONSTRAINT pk_participants PRIMARY KEY (account_id, game_id)
);

CREATE TABLE Games (
    game_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ
);

CREATE TABLE Friends (
    status friend_status NOT NULL DEFAULT 'pending',
    account_id1 UUID NOT NULL,
    account_id2 UUID NOT NULL,

    CONSTRAINT fk_friends_user1
        FOREIGN KEY (account_id1)
        REFERENCES Accounts(account_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_friends_user2
        FOREIGN KEY (account_id2)
        REFERENCES Accounts(account_id)
        ON DELETE CASCADE,

    CONSTRAINT pk_friends PRIMARY KEY (account_id1, account_id2),
    CONSTRAINT no_self_friend CHECK (account_id1 <> account_id2),
    CONSTRAINT ordered_pair CHECK (account_id1 < account_id2)
);