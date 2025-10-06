CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    code_client VARCHAR(50),
    nom_client VARCHAR(100),
    jours_livraison VARCHAR(10),
    adresse_complete TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    couleur VARCHAR(20),
    tournee INTEGER
);
