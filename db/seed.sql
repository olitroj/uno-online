-- Passwords are the username hashed
INSERT INTO Accounts (username, password_hash, description) VALUES
    ('test1', '1b4f0e9851971998e732078544c96b36c3d01cedf7caa332359d6f1d83567014', 'test1 description'),
    ('test2', '60303ae22b998861bce3b28f33eec1be758a213c86c93c076dbe9f558c11c752', 'test2 description'),
    ('test3', 'fd61a03af4f77d870fc21e05e7e80678095c92d808cfb3b5c279ee04c74aca13', 'test3 description');

INSERT INTO Games (start_time, end_time) VALUES
    ('2026-05-31 10:00:00+02', '2026-05-31 10:30:00+02'),
    ('2026-05-20 12:00:00+02', '2026-05-20 12:30:00+02'),
    ('2026-05-24 07:45:00+00', '2026-05-31 08:15:00+00');

INSERT INTO Participants (account_id, game_id, score, win)
    SELECT a.account_id, g.game_id, 100, true
    FROM Accounts a CROSS JOIN Games g
    WHERE a.username = 'test1'
    LIMIT 1;
INSERT INTO Participants (account_id, game_id, score, win)
    SELECT a.account_id, g.game_id, 50, false
    FROM Accounts a CROSS JOIN Games g
    WHERE a.username = 'test2'
    LIMIT 1;
INSERT INTO Participants (account_id, game_id, score, win)
    SELECT a.account_id, g.game_id, 150, true
    FROM Accounts a CROSS JOIN Games g
    WHERE a.username = 'test2'
    LIMIT 1 OFFSET 1;
INSERT INTO Participants (account_id, game_id, score, win)
    SELECT a.account_id, g.game_id, 120, true
    FROM Accounts a CROSS JOIN Games g
    WHERE a.username = 'test3'
    LIMIT 1 OFFSET 1;
INSERT INTO Participants (account_id, game_id, score, win)
    SELECT a.account_id, g.game_id, 100, true
    FROM Accounts a CROSS JOIN Games g
    WHERE a.username = 'test1'
    LIMIT 1 OFFSET 2;
INSERT INTO Participants (account_id, game_id, score, win)
    SELECT a.account_id, g.game_id, 80, false
    FROM Accounts a CROSS JOIN Games g
    WHERE a.username = 'test2'
    LIMIT 1 OFFSET 2;
INSERT INTO Participants (account_id, game_id, score, win)
    SELECT a.account_id, g.game_id, 20, false
    FROM Accounts a CROSS JOIN Games g
    WHERE a.username = 'test3'
    LIMIT 1 OFFSET 2;
    
INSERT INTO Friends (status, account_id1, account_id2, account_id1_started)
    SELECT 'accepted', a1.account_id, a2.account_id, true
    FROM Accounts a1
    JOIN Accounts a2 ON a1.username = 'test1' AND a2.username = 'test2';