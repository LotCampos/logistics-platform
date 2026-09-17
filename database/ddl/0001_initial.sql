BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE logistics_vehicle (
    id uuid PRIMARY KEY,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    unit_number varchar(30) NOT NULL UNIQUE,
    plates varchar(20) NOT NULL UNIQUE,
    brand varchar(80) NOT NULL,
    model varchar(80) NOT NULL,
    year integer NOT NULL,
    vin varchar(40) NOT NULL,
    vehicle_type varchar(50) NOT NULL,
    fuel_type varchar(30) NOT NULL,
    current_mileage numeric(12,1) NOT NULL DEFAULT 0,
    status varchar(20) NOT NULL DEFAULT 'AVAILABLE'
);

COMMIT;
