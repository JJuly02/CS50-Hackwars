CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    alias TEXT,
    summary TEXT
);
CREATE TABLE JobDescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);
CREATE TABLE Skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skill TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

