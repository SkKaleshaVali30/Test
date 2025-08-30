-- ==============================
-- BANKING DATABASE SCHEMA
-- ==============================

DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Account;
DROP TABLE IF EXISTS Employee;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Branch;

-- ------------------------------
-- Branches
-- ------------------------------
CREATE TABLE Branch (
    branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_name TEXT NOT NULL,
    manager_id INTEGER,
    address TEXT
);

-- ------------------------------
-- Employees
-- ------------------------------
CREATE TABLE Employee (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    branch_id INTEGER NOT NULL,
    position TEXT NOT NULL,
    hire_date DATE NOT NULL,
    salary REAL NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);

-- ------------------------------
-- Customers
-- ------------------------------
CREATE TABLE Customer (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    dob DATE NOT NULL,
    gender TEXT CHECK(gender IN ('male','female','other','prefer_not_to_say')),
    address TEXT,
    email TEXT,
    phone TEXT
);

-- ------------------------------
-- Accounts
-- ------------------------------
CREATE TABLE Account (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    account_type TEXT CHECK(account_type IN ('checking','savings','credit','loan')),
    balance REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);

-- ------------------------------
-- Transactions
-- ------------------------------
CREATE TABLE Transaction (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('deposit','withdrawal','fee','loan_payment')),
    amount REAL NOT NULL,
    status TEXT CHECK(status IN ('completed','failed')),
    transaction_date DATE NOT NULL,
    FOREIGN KEY (account_id) REFERENCES Account(account_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- ==============================
-- SAMPLE DATA
-- ==============================

-- Branches
INSERT INTO Branch (branch_name, manager_id, address) VALUES
('Downtown', NULL, '12 Main St'),
('Uptown', NULL, '45 High St'),
('Riverside', NULL, '89 River Rd');

-- Employees
INSERT INTO Employee (first_name, last_name, branch_id, position, hire_date, salary) VALUES
('Raymond','Jefferson',1,'Manager','2021-05-10',90000),
('Alice','Brown',1,'Teller','2022-03-15',50000),
('Bob','Smith',1,'Clerk','2020-07-01',55000),
('Michael','Johnson',2,'Manager','2019-11-20',95000),
('David','Lee',2,'Teller','2023-01-18',48000),
('Sophia','Williams',3,'Manager','2021-02-25',88000),
('Emma','Davis',3,'Teller','2021-06-12',51000);

-- Update managers in Branch
UPDATE Branch SET manager_id = 1 WHERE branch_id = 1;
UPDATE Branch SET manager_id = 4 WHERE branch_id = 2;
UPDATE Branch SET manager_id = 6 WHERE branch_id = 3;

-- Customers
INSERT INTO Customer (first_name,last_name,dob,gender,address,email,phone) VALUES
('John','Doe','1955-04-12','male','12 Main St','john@example.com','1234567890'),
('Jane','Doe','1975-07-20','female','34 Oak St','jane@example.com','9876543210'),
('Alice','Green','1985-12-05','female','56 Pine St','aliceg@example.com','1112223333'),
('Michael','Taylor','1990-08-14','male','78 Maple St','mike@example.com','4445556666'),
('Sophia','Johnson','2000-03-22','female','89 River Rd','sophiaj@example.com','7778889999'),
('David','Jefferson','1982-10-30','male','101 Cedar St','davidj@example.com','2223334444'),
('Emily','Brown','1995-06-10','female','34 Oak St','emilyb@example.com','5556667777');

-- Accounts
INSERT INTO Account (customer_id,branch_id,account_type,balance) VALUES
(1,1,'checking',15000),
(1,1,'savings',25000),
(2,1,'credit',12000),
(2,1,'loan',22000),
(3,2,'checking',8000),
(3,2,'savings',12000),
(4,2,'credit',18000),
(5,3,'savings',5000),
(6,3,'loan',25000),
(6,3,'credit',10000),
(7,1,'checking',7000),
(7,1,'savings',9000);

-- Transactions
INSERT INTO Transaction (account_id,employee_id,transaction_type,amount,status,transaction_date) VALUES
(1,2,'deposit',5000,'completed','2024-01-15'),
(2,3,'withdrawal',2000,'completed','2024-02-20'),
(3,2,'fee',100,'completed','2024-03-01'),
(4,1,'loan_payment',5000,'completed','2025-01-10'),
(5,5,'deposit',2000,'failed','2025-02-12'),
(6,5,'deposit',1500,'completed','2025-03-18'),
(7,4,'withdrawal',3000,'completed','2025-04-05'),
(8,6,'deposit',1000,'completed','2025-01-12'),
(9,7,'loan_payment',4000,'completed','2025-02-22'),
(10,6,'fee',200,'completed','2025-03-30'),
(11,2,'deposit',700,'completed','2024-11-02'),
(12,3,'deposit',900,'completed','2024-12-05'),
(1,2,'withdrawal',1000,'completed','2025-03-15'),
(1,2,'deposit',2000,'completed','2025-03-16'),
(1,2,'deposit',1500,'completed','2025-03-17'),
(1,2,'deposit',2500,'completed','2025-03-18'),
(1,2,'deposit',1000,'completed','2025-03-19'); -- consecutive days
