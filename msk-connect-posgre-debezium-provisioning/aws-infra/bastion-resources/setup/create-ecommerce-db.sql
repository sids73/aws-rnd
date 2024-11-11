CREATE TABLE IF NOT EXISTS customers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  total INTEGER NOT NULL,
  created TIMESTAMP DEFAULT now(),
  CONSTRAINT customer_fk FOREIGN KEY (customer_id) 
    REFERENCES customers(id)
);

INSERT INTO customers (name)
VALUES
('Hooli Corp'),
('Acme Corp'),
('Wayne Enterprise'),
('Mystery Inc');

