PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS alignment_records;
DROP TABLE IF EXISTS analytics_cache;
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS adjudicators;
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS rounds;
DROP TABLE IF EXISTS categories;

DROP TABLE IF EXISTS competitions;
DROP TABLE IF EXISTS people;

CREATE TABLE people (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    metadata TEXT CHECK(json_valid(metadata))
);

CREATE TABLE competitions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    date TEXT, 
    metadata TEXT CHECK(json_valid(metadata))
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    competition_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    metadata TEXT CHECK(json_valid(metadata)),
    FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE
);

CREATE TABLE rounds (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    metadata TEXT CHECK(json_valid(metadata)),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE adjudicators (
    id INTEGER PRIMARY KEY,
    round_id INTEGER NOT NULL,
    people_id INTEGER NOT NULL,
    letter TEXT,
    metadata TEXT CHECK(json_valid(metadata)),
    FOREIGN KEY (round_id) REFERENCES rounds(id) ON DELETE CASCADE,
    FOREIGN KEY (people_id) REFERENCES people(id)
);

CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    partner1_id INTEGER NOT NULL,
    partner2_id INTEGER,
    number INTEGER,
    place TEXT NOT NULL,
    metadata TEXT CHECK(json_valid(metadata)),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (partner1_id) REFERENCES people(id),
    FOREIGN KEY (partner2_id) REFERENCES people(id)
);

CREATE TABLE marks (
    id INTEGER PRIMARY KEY,
    round_id INTEGER NOT NULL,
    marks TEXT CHECK(json_valid(marks)),
    FOREIGN KEY (round_id) REFERENCES rounds(id) ON DELETE CASCADE
);

CREATE TABLE alignment_records (
    id INTEGER PRIMARY KEY,
    alignment REAL,
    person_id INTEGER,
    marks_id INTEGER,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
    FOREIGN KEY (marks_id) REFERENCES marks(id) ON DELETE CASCADE
);

CREATE TABLE analytics_cache (
    marks_id INTEGER PRIMARY KEY,
    alignment_cache TEXT CHECK(json_valid(alignment_cache)),
    bias_cache TEXT CHECK(json_valid(bias_cache)),
    blocs_cache TEXT CHECK(json_valid(blocs_cache)),
    last_calculated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (marks_id) REFERENCES marks(id) ON DELETE CASCADE
);