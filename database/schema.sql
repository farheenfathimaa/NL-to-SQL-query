-- E-commerce Schema

CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE sales_reps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    region_id INTEGER REFERENCES regions(id)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    price FLOAT NOT NULL
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sales_rep_id INTEGER REFERENCES sales_reps(id)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price FLOAT NOT NULL
);
