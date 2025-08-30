import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = "bank.db"

def create_tables(cur):
    cur.executescript("""
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS accounts;
    DROP TABLE IF EXISTS transactions;
    DROP TABLE IF EXISTS branches;
    DROP TABLE IF EXISTS loans;
    DROP TABLE IF EXISTS cards;
    DROP TABLE IF EXISTS employees;
    DROP TABLE IF EXISTS beneficiaries;
    DROP TABLE IF EXISTS loan_payments;
    DROP TABLE IF EXISTS atm;
    DROP TABLE IF EXISTS audit_logs;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT
    );

    CREATE TABLE accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        account_type TEXT,
        balance REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        amount REAL,
        transaction_type TEXT,
        transaction_date TEXT,
        FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    );

    CREATE TABLE branches (
        branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_name TEXT,
        location TEXT
    );

    CREATE TABLE loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        branch_id INTEGER,
        loan_amount REAL,
        status TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
    );

    CREATE TABLE cards (
        card_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        card_type TEXT,
        expiry_date TEXT,
        FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    );

    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        branch_id INTEGER,
        salary REAL,
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
    );

    CREATE TABLE beneficiaries (
        beneficiary_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        name TEXT,
        relation TEXT,
        FOREIGN KEY (account_id) REFERENCES accounts(account_id)
    );

    CREATE TABLE loan_payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER,
        payment_date TEXT,
        amount REAL,
        FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
    );

    CREATE TABLE atm (
        atm_id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_id INTEGER,
        location TEXT,
        status TEXT,
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
    );

    CREATE TABLE audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        action TEXT,
        timestamp TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    """)
     
def seed_data(cur):
    # Customers
    for i in range(1, 51):
        cur.execute("INSERT INTO customers (name,email,phone) VALUES (?,?,?)",
                    (f"Customer {i}", f"cust{i}@bank.com", f"90000{i:04}"))

    # Branches
    for i in range(1, 11):
        cur.execute("INSERT INTO branches (branch_name,location) VALUES (?,?)",
                    (f"Branch {i}", f"City {i}"))

    # Accounts
    for i in range(1, 101):
        cust_id = random.randint(1, 50)
        cur.execute("INSERT INTO accounts (customer_id,account_type,balance) VALUES (?,?,?)",
                    (cust_id, random.choice(["Savings","Checking"]), random.randint(1000,20000)))

    # Transactions
    for i in range(1, 301):
        acc_id = random.randint(1, 100)
        amt = random.randint(100, 5000)
        cur.execute("INSERT INTO transactions (account_id,amount,transaction_type,transaction_date) VALUES (?,?,?,?)",
                    (acc_id, amt, random.choice(["Credit","Debit"]),
                     (datetime.now()-timedelta(days=random.randint(0,365))).strftime("%Y-%m-%d")))

    # Loans
    for i in range(1, 51):
        cust_id = random.randint(1, 50)
        branch_id = random.randint(1, 10)
        cur.execute("INSERT INTO loans (customer_id,branch_id,loan_amount,status) VALUES (?,?,?,?)",
                    (cust_id, branch_id, random.randint(5000,50000), random.choice(["Active","Closed"])))

    # Cards
    for i in range(1, 101):
        acc_id = random.randint(1, 100)
        cur.execute("INSERT INTO cards (account_id,card_type,expiry_date) VALUES (?,?,?)",
                    (acc_id, random.choice(["Debit","Credit"]),
                     (datetime.now()+timedelta(days=365*3)).strftime("%Y-%m-%d")))

    # Employees
    for i in range(1, 51):
        branch_id = random.randint(1, 10)
        cur.execute("INSERT INTO employees (name,role,branch_id,salary) VALUES (?,?,?,?)",
                    (f"Employee {i}", random.choice(["Manager","Teller","Loan Officer"]),
                     branch_id, random.randint(30000,80000)))

    # Beneficiaries
    for i in range(1, 51):
        acc_id = random.randint(1, 100)
        cur.execute("INSERT INTO beneficiaries (account_id,name,relation) VALUES (?,?,?)",
                    (acc_id, f"Beneficiary {i}", random.choice(["Spouse","Child","Parent","Sibling"])))

    # Loan Payments
    for i in range(1, 101):
        loan_id = random.randint(1, 50)
        cur.execute("INSERT INTO loan_payments (loan_id,payment_date,amount) VALUES (?,?,?)",
                    (loan_id, (datetime.now()-timedelta(days=random.randint(0,200))).strftime("%Y-%m-%d"),
                     random.randint(500,5000)))

    # ATMs
    for i in range(1, 21):
        branch_id = random.randint(1, 10)
        cur.execute("INSERT INTO atm (branch_id,location,status) VALUES (?,?,?)",
                    (branch_id, f"ATM Location {i}", random.choice(["Active","Out of Service"])))

    # Audit Logs
    for i in range(1, 201):
        emp_id = random.randint(1, 50)
        cur.execute("INSERT INTO audit_logs (employee_id,action,timestamp) VALUES (?,?,?)",
                    (emp_id, random.choice(["Login","Approve Loan","Update Account"]),
                     (datetime.now()-timedelta(days=random.randint(0,90))).strftime("%Y-%m-%d %H:%M:%S")))

def main():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    create_tables(cur)
    seed_data(cur)
    conn.commit()
    conn.close()
    print("Database created and seeded with 50+ rows per table.")

if __name__ == "__main__":
    main()
