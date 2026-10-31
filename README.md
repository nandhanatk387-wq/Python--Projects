# Library Management System

## Project Overview
A command-line, database-driven application developed using **Python 3.x** and **SQLite3** to manage library books, user accounts, and borrowing transactions. This project demonstrates core database concepts including relational table design, Foreign Key constraints, User Authentication, Role-Based Access Control (RBAC), and full CRUD operations.

---

## Features
- **User Authentication & Role-Based Authorization:**
  - Secure user registration and login system.
  - Two distinct roles: **Administrator** (full CRUD access to inventory and transaction logs) and **Member** (ability to browse and borrow books).
- **Database Design & Relationships:**
  - Uses 3 relational tables (`users`, `books`, and `transactions`) linked via Primary and Foreign Keys to maintain data integrity.
- **Full CRUD Functionality:**
  - Administrators can **C**reate, **R**ead, **U**pdate, and **D**elete book inventory records.
- **Input Validation & Exception Handling:**
  - Protects against empty fields, duplicate usernames, invalid data types, and database runtime errors, ensuring the app runs smoothly without crashing.
- **Automatic Database Initialization:**
  - The SQLite database (`library.db`) is created automatically upon the first application run.

---

## Technical Requirements
- **Language:** Python 3.x
- **Database:** SQLite3 (Built-in Python module)
- **Interface:** Command Line Interface (CLI)

---

## How to Run the Project

1. **Prerequisites:** Ensure you have Python 3.x installed on your computer.
2. **Open Project:** Open your project directory in an IDE like **PyCharm**.
3. **Run the Application:** Open your terminal or run the main script file:
   ```bash
   python main.py