# University Timetable Management System

A desktop application for managing university timetables, built with Python and PyQt5, connected to a MySQL database.

---

## What It Does

This system allows administrators to manage all data related to a university timetable from a single desktop interface. You can manage departments, programs, courses, rooms, lecturers, and class schedules. All relationships between these entities are enforced both at the database level and within the application itself.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| GUI | PyQt5 |
| Database Driver | PyMySQL |
| Database | MySQL 8.0 |

---

## Project Structure

```
university_timetable/
├── main.py         # Entry point, launches the app and checks DB connection
├── database.py     # All database queries and CRUD functions
└── ui.py           # All PyQt5 views, sidebar, and form logic
```

---

## Requirements

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- MySQL Workbench (to set up the database)

---

## Setup

**1. Clone or download the project**

Place `main.py`, `database.py`, and `ui.py` in the same folder.

**2. Install dependencies**

```bash
pip install PyQt5 pymysql
```

**3. Set up the database**

Open MySQL Workbench, create a database named `sys_db`, and run the provided SQL schema file to create all 11 tables.

**4. Configure the connection**

Open `database.py` and confirm these match your setup:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root1234", use your ownpassword here
    "database": "sys_db", use your own database name here
}
```

**5. Run the app**

```bash
python main.py
```

---

## How to Use

The app opens with a sidebar on the left. Click any item to switch views. Each view has a table showing existing records and a form at the bottom to add, edit, or delete entries.

**Recommended order for entering data (to avoid foreign key errors):**

1. Departments
2. Program Depts
3. Programs
4. Courses
5. Program Courses
6. Rooms
7. Lecturers
8. Phone Numbers
9. Lecturer Courses
10. Class Schedule

> The Class Schedule section validates that the selected lecturer is qualified for the selected course and that the course is assigned to the selected program before saving.

---

## Database Schema

The system uses 11 tables:

| Table | Description |
|---|---|
| `dept` | University departments |
| `program_dept` | Links programs to departments |
| `program` | Specific year and semester offerings of a program |
| `coursetable` | Course catalog |
| `program_course` | Courses assigned to each program offering |
| `room` | Rooms and their capacities |
| `name_initial` | Lecturer names and initials |
| `lect_dept` | Lecturer details and department assignments |
| `lect_phoneno` | Lecturer phone numbers |
| `lecturer_course` | Courses a lecturer is qualified to teach |
| `class_schedule` | Scheduled classes with time, room, lecturer, and course |

---

## Notes

- The app connects to a local MySQL instance. Make sure MySQL Server is running before launching.
- Deleting a record that is referenced by another table will be rejected by the database. Delete child records first before deleting parent records.
- The Refresh button on each view reloads data from the database if something looks out of date.