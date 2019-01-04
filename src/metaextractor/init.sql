CREATE TABLE tiles
    ( file_path TEXT PRIMARY KEY
    , tile_name TEXT NOT NULL
    );

CREATE TABLE surfaces
    ( surface TEXT PRIMARY KEY
    );

CREATE TABLE tiles_surfaces
    ( file_path TEXT NOT NULL
    , surface TEXT
    , UNIQUE(file_path, surface));
