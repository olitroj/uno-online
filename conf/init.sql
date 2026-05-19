CREATE TYPE account_status AS ENUM ('online', 'offline');

CREATE TYPE friend_status AS ENUM ('pending', 'accepted', 'rejected');

CREATE TABLE Accounts (
    uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT  NOT NULL UNIQUE,
    password TEXT NOT NULL
    status account_status NOT NULL DEFAULT 'offline',
    description TEXT,
);


CREATE TABLE participants (
    account_uid UUID NOT NULL,
    game_id UUID NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    win BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_account_id
        FOREIGN KEY (account_uid)
        REFERENCES Accounts(uid)
        ON DELETE CASCADE,
    CONSTRAINT pk_participants PRIMARY KEY (account_uid, game_id)
);

CREATE TABLE Games (
    game_id UUID PRIMARY KEY DEFAULT gen_random_uuid() ,
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ
    );

CREATE TABLE Friends (
    status friend_status NOT NULL DEFAULT 'pending',
    uid1 UUID NOT NULL,
    uid2 UUID NOT NULL,

    CONSTRAINT fk_friends_user1
        FOREIGN KEY (uid1)
        REFERENCES Accounts(uid)
        ON DELETE CASCADE,

    CONSTRAINT fk_friends_user2
        FOREIGN KEY (uid2)
        REFERENCES Accounts(uid)
        ON DELETE CASCADE,

    CONSTRAINT unique_friend_pair UNIQUE (uid1, uid2),
    CONSTRAINT no_self_friend CHECK (uid1 <> uid2)
    CONSTRAINT pk_friends PRIMARY KEY (uid1, uid2)
);