-- Mock Data for E-commerce Schema

-- Insert Regions
INSERT INTO regions (name) VALUES ('North'), ('South'), ('East'), ('West');

-- Insert Sales Reps
INSERT INTO sales_reps (name, region_id) VALUES 
('Alice', (SELECT id FROM regions WHERE name='North')),
('Bob', (SELECT id FROM regions WHERE name='South')),
('Charlie', (SELECT id FROM regions WHERE name='East')),
('David', (SELECT id FROM regions WHERE name='West'));

-- Insert Products
INSERT INTO products (name, category, price) VALUES 
('Laptop', 'Electronics', 1200.0),
('Phone', 'Electronics', 800.0),
('Monitor', 'Electronics', 300.0),
('Desk Chair', 'Furniture', 150.0),
('Coffee Mug', 'Kitchen', 15.0);

-- Insert Orders (Historical)
INSERT INTO orders (order_date, sales_rep_id) VALUES 
(CURRENT_TIMESTAMP - INTERVAL '80 days', (SELECT id FROM sales_reps WHERE name='Alice')),
(CURRENT_TIMESTAMP - INTERVAL '70 days', (SELECT id FROM sales_reps WHERE name='Bob')),
(CURRENT_TIMESTAMP - INTERVAL '60 days', (SELECT id FROM sales_reps WHERE name='Charlie')),
(CURRENT_TIMESTAMP - INTERVAL '50 days', (SELECT id FROM sales_reps WHERE name='David')),
(CURRENT_TIMESTAMP - INTERVAL '5 days', (SELECT id FROM sales_reps WHERE name='Alice'));

-- Insert Order Items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES 
(1, (SELECT id FROM products WHERE name='Laptop'), 1, 1200.0),
(2, (SELECT id FROM products WHERE name='Phone'), 2, 800.0),
(3, (SELECT id FROM products WHERE name='Monitor'), 3, 300.0),
(4, (SELECT id FROM products WHERE name='Desk Chair'), 1, 150.0),
(5, (SELECT id FROM products WHERE name='Coffee Mug'), 10, 15.0);
