CREATE TABLE holocron (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    pass TEXT NOT NULL
);

CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    pass TEXT NOT NULL
);

/* TODO: Add data */

INSERT INTO holocron (username, pass)
VALUES ('DarthVader', 'BestFather1');

INSERT INTO holocron (username, pass)
VALUES ('ColonelYulralen', 'ForEmpire');

INSERT INTO holocron (username, pass)
VALUES ('GrandMoffTarkin', 'General1');

INSERT INTO holocron (username, pass)
VALUES ('AdmiralThrawn', 'Strategis1');

INSERT INTO holocron (username, pass)
VALUES ('Admin1', 'fb001dfcffd1c899f3297871406242f097aecf1a5342ccf3ebcd116146188e4b');
