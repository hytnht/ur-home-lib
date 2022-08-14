create table user
(
    id       INTEGER not null
        primary key
        unique,
    email    TEXT    not null,
    password TEXT    not null,
    date     DATE
);

create table series
(
    id      INTEGER not null
        primary key
        unique,
    title   TEXT,
    current INTEGER,
    end_vol INTEGER,
    status  BOOLEAN,
    user_id INTEGER not null
        references user
);

create table book
(
    id                  INTEGER not null
        primary key
        unique,
    isbn                INTEGER,
    title               TEXT    not null,
    author              TEXT,
    publisher           TEXT,
    volume              INTEGER,
    category            TEXT,
    year                INTEGER,
    edition             TEXT,
    page                INTEGER,
    cover               TEXT,
    status              TEXT,
    ratings             FLOAT,
    country             TEXT,
    original_language   TEXT,
    translated_language TEXT,
    price               INTEGER,
    note                TEXT,
    series_id           INTEGER
        references series,
    user_id             INTEGER
        references user
);

create table accessory
(
    id       INTEGER not null
        primary key
        unique,
    type     TEXT    not null,
    qty      INTEGER default 1 not null,
    material TEXT,
    book_id  INTEGER
        references book,
    status   TEXT
);

create table log
(
    id         INTEGER not null
        constraint log_pk
            primary key,
    date       DATE,
    activities TEXT,
    borrower   TEXT,
    book_id    INTEGER
        references book
);

create unique index log_id_uindex
    on log (id);

create table release_calendar
(
    id        INTEGER not null
        primary key
        unique,
    publisher TEXT,
    series_id INTEGER
        references series,
    volume    INTEGER,
    date      NUMERIC not null
);

create table series_missing
(
    id        INTEGER not null
        constraint series_missing_pk
            primary key,
    series_id INTEGER not null
        references series,
    volume    INTEGER not null
);

create unique index series_missing_id_uindex
    on series_missing (id);

create unique index user_email_uindex
    on user (email);

create table user_custom
(
    id         INTEGER not null
        constraint user_custom_pk
            primary key,
    name       TEXT,
    table_name TEXT,
    user_id    INTEGER not null
        references user
);

create unique index user_custom_id_uindex
    on user_custom (id);
