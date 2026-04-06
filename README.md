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

run the following SQL locally to connect it through PyMySQL :

```sql
-- ------------------------------------------------------------
-- 1. Department
-- ------------------------------------------------------------
CREATE TABLE dept (
    deptid INT PRIMARY KEY,
    deptname VARCHAR(100) UNIQUE NOT NULL
);

-- ------------------------------------------------------------
-- 2. Program-Department
-- ------------------------------------------------------------
CREATE TABLE program_dept (
    program_name VARCHAR(100) PRIMARY KEY,
    deptid INT NOT NULL,
    FOREIGN KEY (deptid) REFERENCES dept(deptid) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 3. Program (specific year+sem offering)
-- ------------------------------------------------------------
CREATE TABLE program (
    pid INT PRIMARY KEY,
    program_name VARCHAR(100) NOT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
    sem INT NOT NULL CHECK (sem IN (1, 2)),
    FOREIGN KEY (program_name) REFERENCES program_dept(program_name) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 4. Course
-- ------------------------------------------------------------
CREATE TABLE coursetable (
    coursecode VARCHAR(20) PRIMARY KEY,
    coursename VARCHAR(200) NOT NULL,
    credithour INT NOT NULL CHECK (credithour > 0)
);

-- ------------------------------------------------------------
-- 5. Program-Course junction
-- ------------------------------------------------------------
CREATE TABLE program_course (
    pid INT NOT NULL,
    coursecode VARCHAR(20) NOT NULL,
    PRIMARY KEY (pid, coursecode),
    FOREIGN KEY (pid) REFERENCES program(pid) ON DELETE CASCADE,
    FOREIGN KEY (coursecode) REFERENCES coursetable(coursecode) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 6. Room
-- ------------------------------------------------------------
CREATE TABLE room (
    roomno VARCHAR(20) PRIMARY KEY,
    capacity INT NOT NULL CHECK (capacity > 0)
);

-- ------------------------------------------------------------
-- 7. Name-Initial (unique name -> fixed initial)
-- ------------------------------------------------------------
CREATE TABLE name_initial (
    name VARCHAR(100) PRIMARY KEY,
    initial VARCHAR(10) NOT NULL
);

-- ------------------------------------------------------------
-- 8. Lecturer (allows same name in different departments)
-- ------------------------------------------------------------
CREATE TABLE lect_dept (
    lect_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    workload INT NOT NULL CHECK (workload >= 0),
    deptid INT NOT NULL,
    UNIQUE KEY (name, deptid),   -- prevents duplicate (name,dept)
    FOREIGN KEY (name) REFERENCES name_initial(name) ON DELETE RESTRICT,  -- shared, don't cascade
    FOREIGN KEY (deptid) REFERENCES dept(deptid) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 9. Lecturer phones
-- ------------------------------------------------------------
CREATE TABLE lect_phoneno (
    lect_id INT NOT NULL,
    phoneno VARCHAR(20) NOT NULL,
    PRIMARY KEY (lect_id, phoneno),
    FOREIGN KEY (lect_id) REFERENCES lect_dept(lect_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 10. Lecturer-Course qualification
-- ------------------------------------------------------------
CREATE TABLE lecturer_course (
    lect_id INT NOT NULL,
    coursecode VARCHAR(20) NOT NULL,
    PRIMARY KEY (lect_id, coursecode),
    FOREIGN KEY (lect_id) REFERENCES lect_dept(lect_id) ON DELETE CASCADE,
    FOREIGN KEY (coursecode) REFERENCES coursetable(coursecode) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 11. Class Schedule (with all validation triggers)
-- ------------------------------------------------------------
CREATE TABLE class_schedule (
    classid INT PRIMARY KEY,
    day VARCHAR(10) NOT NULL CHECK (day IN ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    roomid VARCHAR(20) NOT NULL,
    lect_id INT NOT NULL,
    course_id VARCHAR(20) NOT NULL,
    pid INT NOT NULL,
    CHECK (end_time > start_time),
    FOREIGN KEY (roomid) REFERENCES room(roomno) ON DELETE CASCADE,
    FOREIGN KEY (lect_id) REFERENCES lect_dept(lect_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES coursetable(coursecode) ON DELETE CASCADE,
    FOREIGN KEY (pid) REFERENCES program(pid) ON DELETE CASCADE,
    FOREIGN KEY (pid, course_id) REFERENCES program_course(pid, coursecode) ON DELETE CASCADE,
    FOREIGN KEY (lect_id, course_id) REFERENCES lecturer_course(lect_id, coursecode) ON DELETE CASCADE
);

DELIMITER $$

-- Trigger 1: Validate 45-min periods and break time
CREATE TRIGGER validate_period BEFORE INSERT ON class_schedule
FOR EACH ROW
BEGIN
    IF NEW.start_time NOT IN ('10:15:00','11:00:00','11:45:00','12:30:00','14:15:00','15:00:00','15:45:00','16:30:00') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid start time. Allowed: 10:15,11:00,11:45,12:30,14:15,15:00,15:45,16:30';
    END IF;
    IF TIMESTAMPDIFF(MINUTE, NEW.start_time, NEW.end_time) != 45 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Class duration must be exactly 45 minutes.';
    END IF;
    IF (NEW.start_time < '14:15:00' AND NEW.end_time > '13:30:00') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot schedule class during break time (13:30-14:15).';
    END IF;
END$$

-- Trigger 2: Prevent room overlap
CREATE TRIGGER check_room_overlap BEFORE INSERT ON class_schedule
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM class_schedule
        WHERE day = NEW.day AND roomid = NEW.roomid
          AND (NEW.start_time < end_time AND NEW.end_time > start_time)
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Room already booked for overlapping time on this day.';
    END IF;
END$$

-- Trigger 3: Prevent lecturer overlap
CREATE TRIGGER check_lecturer_overlap BEFORE INSERT ON class_schedule
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM class_schedule
        WHERE day = NEW.day AND lect_id = NEW.lect_id
          AND (NEW.start_time < end_time AND NEW.end_time > start_time)
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lecturer already assigned to another class at overlapping time.';
    END IF;
END$$

-- Trigger 4: Prevent program-course overlap (same program, same course, same day)
CREATE TRIGGER check_program_course_overlap BEFORE INSERT ON class_schedule
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM class_schedule
        WHERE day = NEW.day AND pid = NEW.pid AND course_id = NEW.course_id
          AND (NEW.start_time < end_time AND NEW.end_time > start_time)
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This course already scheduled for the program at overlapping time.';
    END IF;
END$$

-- Trigger 5: Enforce lecturer cumulative workload (total minutes ever assigned)
CREATE TRIGGER check_lecturer_workload BEFORE INSERT ON class_schedule
FOR EACH ROW
BEGIN
    DECLARE total_minutes INT;
    SELECT COALESCE(SUM(TIMESTAMPDIFF(MINUTE, start_time, end_time)), 0)
    INTO total_minutes
    FROM class_schedule
    WHERE lect_id = NEW.lect_id;
    SET total_minutes = total_minutes + TIMESTAMPDIFF(MINUTE, NEW.start_time, NEW.end_time);
    IF total_minutes > (SELECT workload FROM lect_dept WHERE lect_id = NEW.lect_id) * 60 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lecturer total assigned hours would exceed their workload limit.';
    END IF;
END$$

DELIMITER ;

```

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
