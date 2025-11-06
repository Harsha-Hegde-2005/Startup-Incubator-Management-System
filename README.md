# 🚀 Startup Incubator Management System

## 📘 Project Overview

The **Startup Incubator Management System** is a database-driven application designed to automate and streamline the management of startup incubators.  
It provides an efficient way to manage startups, founders, mentors, investors, and funding details, while maintaining data integrity and automation through stored procedures, functions, and triggers.

This project was developed as part of the **UE23CS351A – Database Management Systems (DBMS)** course at **PES University**.

---

## 🎯 Objectives

- Design and implement a **normalized relational database schema** for startup incubation management.
- Use **DDL and DML** statements to manage data creation, manipulation, and updates.
- Implement **stored procedures, functions, and triggers** to add automation and enforce business rules.
- Demonstrate **complex SQL queries** including joins, nested, and aggregate queries.
- Build a **Python (CustomTkinter)** based GUI frontend to interact with the MySQL database seamlessly.

---

## 🧩 Features

### 🗃️ Database Features
- ✅ **Create / Read / Update / Delete (CRUD)** operations for startups, founders, mentors, and investors.
- ✅ **Many-to-Many Relationship** between startups and mentors via a junction table.
- ✅ **Funding tracking system** linking investors with startups.
- ✅ **Audit logging triggers** to monitor updates and new records.
- ✅ **Stored procedures** for adding startups with founders and assigning mentors.
- ✅ **Functions** for total funding calculation and mentor count.
- ✅ **Complex queries** (JOIN, Nested, Aggregate).

### 💻 GUI Frontend Features
- 🧭 Multi-tab interface using **CustomTkinter**:
  1. View All Data  
  2. Manage Startups (CRUD)  
  3. Procedures & Functions  
  4. Complex Queries & Triggers
- 🧾 Real-time database interaction via **mysql-connector-python**.
- ⚙️ Validations for email (`@gmail.com`) and 10-digit phone numbers.
- 🪶 Audit Log Viewer tab to display trigger-generated logs.

---

## 🧠 System Architecture

**Frontend:** Python (CustomTkinter)  
**Backend:** MySQL  
**Connector:** mysql-connector-python  
**Database Name:** `startup_incubator_management_system`

### Entity Relationships
- One-to-Many: `Startups → Founders`, `Startups → Funding`
- Many-to-Many: `Startups ↔ Mentors`
- One-to-Many: `Investors → Funding`

---

## 🏗️ Database Schema Overview

### Tables:
1. `startups` – Startup details  
2. `founders` – Founder information linked to startups  
3. `mentors` – Mentor profiles  
4. `investors` – Investor details  
5. `funding` – Funding events linking investors and startups  
6. `startup_mentors` – Junction table for startups ↔ mentors  
7. `audit_log` – Logs updates and inserts via triggers  

---

## ⚙️ Setup Instructions

### 🔧 Prerequisites
- MySQL 8.0 or higher  
- Python 3.10+  
- The following Python libraries:
  ```bash
  pip install mysql-connector-python customtkinter
🧭 Steps to Run

Create Database

CREATE SCHEMA startup_incubator_management_system;
USE startup_incubator_management_system;


Run DDL & DML Script

Execute all table creation and insert statements from startup_schema.sql.

Set up DB Config
Edit db_config.py with your MySQL credentials:

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password_here',
    'database': 'startup_incubator_management_system'
}


Run the GUI

python app.py
