"""CREATE DATABASE IF NOT EXISTS tt_db;
USE tt_db;

-- Bảng quản lý người dùng
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(10) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    role VARCHAR(20) DEFAULT 'Nhân viên'
);
INSERT INTO users (username, password, name, email, phone, role)
VALUES ('admin', SHA2('admin123', 256), 'admin', 'admin@example.com', '0123456789', 'admin');


-- Bảng quản lý nhân viên
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    address VARCHAR(255),
    position VARCHAR(50),
    salary INT,
    start_date DATE
);

-- Bảng quản lý sản phẩm
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    image_path VARCHAR(255),
    import_date DATE
);

-- Bảng quản lý đơn hàng
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(10) PRIMARY KEY,
    user_id VARCHAR(10),
    customer_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Bảng chi tiết đơn hàng
CREATE TABLE IF NOT EXISTS order_items (
    order_id VARCHAR(10),
    product_id VARCHAR(10),
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Bảng quản lý giỏ hàng
CREATE TABLE IF NOT EXISTS cart (
    user_id VARCHAR(10),
    product_id VARCHAR(10),
    quantity INT NOT NULL,
    PRIMARY KEY (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Bảng quản lý hóa đơn
CREATE TABLE IF NOT EXISTS invoices (
    id VARCHAR(10) PRIMARY KEY,
    order_id VARCHAR(10),
    customer_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    invoice_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(10),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
DELETE FROM order_items WHERE product_id NOT IN (SELECT id FROM products);

"""