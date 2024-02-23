CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    hashpass TEXT NOT NULL,

    /* holocron */
    holocronstage INTEGER NOT NULL DEFAULT 0,
    holoscore NUMERIC NOT NULL DEFAULT 0,

    /* dark archive */
    archscore NUMERIC NOT NULL DEFAULT 0,

    /* imperialNet */
    imperialscore NUMERIC NOT NULL DEFAULT 0,

    /* score */
    score NUMERIC NOT NULL DEFAULT 0
);
