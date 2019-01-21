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

CREATE TABLE orthos
    ( image_number TEXT PRIMARY KEY
    , file_path TEXT NOT NULL
    , width_px INT NOT NULL
    , height_px INT NOT NULL
    , east_min FLOAT NOT NULL
    , east_max FLOAT NOT NULL
    , north_min FLOAT NOT NULL
    , north_max FLOAT NOT NULL
    , UNIQUE(file_path));
