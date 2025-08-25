INSERT INTO users (first_name, last_name, email, password, is_admin)
VALUES ('Super', 'Admin', 'admin@example.com', '123456', 1)
ON DUPLICATE KEY UPDATE email = email;