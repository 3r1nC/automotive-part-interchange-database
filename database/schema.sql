CREATE TABLE vehicles (
    vehicle_id INTEGER PRIMARY KEY,
    year INTEGER,
    make TEXT,
    model TEXT,
    engine TEXT,
    fuel_type TEXT
);

CREATE TABLE parts (
    part_id INTEGER PRIMARY KEY,
    part_type TEXT,
    oe_part_number TEXT,
    oem_brand TEXT,
    description TEXT
);

CREATE TABLE cross_references (
    cross_ref_id INTEGER PRIMARY KEY,
    part_id INTEGER,
    brand TEXT,
    part_number TEXT,
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);

CREATE TABLE fitment (
    fitment_id INTEGER PRIMARY KEY,
    part_id INTEGER,
    vehicle_id INTEGER,
    fitment_type TEXT,
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);