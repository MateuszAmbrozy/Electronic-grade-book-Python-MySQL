-- Gradebook 2 uses a new schema. Start with a separate, empty MySQL database.
-- Create the database using your MySQL administrator account:
CREATE DATABASE gradebook CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Configure GRADEBOOK_DB_* variables, then create the application tables:
-- python3 main.py --backend mysql --init-db
-- python3 main.py --backend mysql --create-admin
-- The authoritative table definitions are in gradebook/schema.sql.
