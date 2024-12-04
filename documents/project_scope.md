#  1. Introduction

## 1.1. Problem Statement

Software development teams often face challenges in managing and resolving bugs effectively. Many existing tools are either too complex for small teams or lack the customization needed to fit specific workflows. This can lead to inefficiencies, miscommunication, and delays in resolving critical issues.

The goal of this project is to develop a lightweight, user-friendly Bug Tracker System. By incorporating two distinct user roles (Admin and User), this application will facilitate efficient bug reporting, tracking, and resolution. Following an Agile approach, the system will be designed iteratively, emphasizing modularity, usability, and maintainability.

---

# 2. Project Scope

## 2.1. Core Features

#### 2.1.1. User Authentication:
    - Secure registration and login for both Admins and Users
    - Password encryption for data security
#### 2.1.2. Bug Management:
    - Users: Create, View and Update bug records
    - Admins: Perform CRUD operations and assign bugs to specific users for resolution
#### 2.1.3. Database Integration:
    A relational database with two main tables.
    - Users: Tracks user credentials and roles
    - Bugs: Stores bug-related information

#### 2.1.4. Validation and Notifications:
    - (Optional) Projects: Tracks projects and links to bugs
    - Validate all user inputs (no empty fields, valid values)
    - Provide real time feedback with success / error messages
#### 2.1.5. Usability:
    - Clear, intuitive interface
    - Admin dashboard for managing users and bugs
    - Search and filter options

---

# 3. Development Approach

### Modularity:
    Code will follow modular design principles, separating authentication, bug management, and admin tools into distinct modules.

### Agile Process:
    Development will be iterative, with features delivered in sprints.
    Regular feedback loops will guide refinements.

### Deployment:
    The application will initially run locally with SQLite as the database.
    Future deployment on a cloud platform (e.g., Heroku or AWS) for public access.

### Out of scope:
    - Advanced features like automated notifications or API integrations
    - AI-driven bug analysis or prediction