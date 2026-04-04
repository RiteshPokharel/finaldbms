import pymysql

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root1234",
    "database": "sms_db",
    "cursorclass": pymysql.cursors.DictCursor,
}

def get_conn():
    return pymysql.connect(**DB_CONFIG)

def fetch(query, params=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()

def execute(query, params=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()
    finally:
        conn.close()

# ── DEPT ──────────────────────────────────────────────────────────────────────
def get_depts():
    return fetch("SELECT * FROM dept ORDER BY deptid")

def add_dept(deptid, deptname):
    execute("INSERT INTO dept VALUES (%s, %s)", (deptid, deptname))

def delete_dept(deptid):
    execute("DELETE FROM dept WHERE deptid=%s", (deptid,))

def update_dept(deptid, deptname):
    execute("UPDATE dept SET deptname=%s WHERE deptid=%s", (deptname, deptid))

# ── PROGRAM_DEPT ───────────────────────────────────────────────────────────────
def get_program_depts():
    return fetch("""
        SELECT pd.program_name, pd.deptid, d.deptname
        FROM program_dept pd JOIN dept d ON pd.deptid=d.deptid
        ORDER BY pd.program_name
    """)

def add_program_dept(program_name, deptid):
    execute("INSERT INTO program_dept VALUES (%s, %s)", (program_name, deptid))

def delete_program_dept(program_name):
    execute("DELETE FROM program_dept WHERE program_name=%s", (program_name,))

# ── PROGRAM ───────────────────────────────────────────────────────────────────
def get_programs():
    return fetch("""
        SELECT p.pid, p.program_name, p.year, p.sem, pd.deptid
        FROM program p JOIN program_dept pd ON p.program_name=pd.program_name
        ORDER BY p.pid
    """)

def add_program(pid, program_name, year, sem):
    execute("INSERT INTO program VALUES (%s, %s, %s, %s)", (pid, program_name, year, sem))

def delete_program(pid):
    execute("DELETE FROM program WHERE pid=%s", (pid,))

def update_program(pid, program_name, year, sem):
    execute("UPDATE program SET program_name=%s, year=%s, sem=%s WHERE pid=%s",
            (program_name, year, sem, pid))

# ── COURSE ────────────────────────────────────────────────────────────────────
def get_courses():
    return fetch("SELECT * FROM coursetable ORDER BY coursecode")

def add_course(coursecode, coursename, credithour):
    execute("INSERT INTO coursetable VALUES (%s, %s, %s)", (coursecode, coursename, credithour))

def delete_course(coursecode):
    execute("DELETE FROM coursetable WHERE coursecode=%s", (coursecode,))

def update_course(coursecode, coursename, credithour):
    execute("UPDATE coursetable SET coursename=%s, credithour=%s WHERE coursecode=%s",
            (coursename, credithour, coursecode))

# ── PROGRAM_COURSE ────────────────────────────────────────────────────────────
def get_program_courses():
    return fetch("""
        SELECT pc.pid, p.program_name, pc.coursecode, c.coursename
        FROM program_course pc
        JOIN program p ON pc.pid=p.pid
        JOIN coursetable c ON pc.coursecode=c.coursecode
        ORDER BY pc.pid
    """)

def add_program_course(pid, coursecode):
    execute("INSERT INTO program_course VALUES (%s, %s)", (pid, coursecode))

def delete_program_course(pid, coursecode):
    execute("DELETE FROM program_course WHERE pid=%s AND coursecode=%s", (pid, coursecode))

# ── ROOM ──────────────────────────────────────────────────────────────────────
def get_rooms():
    return fetch("SELECT * FROM room ORDER BY roomno")

def add_room(roomno, capacity):
    execute("INSERT INTO room VALUES (%s, %s)", (roomno, capacity))

def delete_room(roomno):
    execute("DELETE FROM room WHERE roomno=%s", (roomno,))

def update_room(roomno, capacity):
    execute("UPDATE room SET capacity=%s WHERE roomno=%s", (capacity, roomno))

# ── NAME_INITIAL ──────────────────────────────────────────────────────────────
def get_name_initials():
    return fetch("SELECT * FROM name_initial ORDER BY name")

def add_name_initial(name, initial):
    execute("INSERT INTO name_initial VALUES (%s, %s)", (name, initial))

def delete_name_initial(name):
    execute("DELETE FROM name_initial WHERE name=%s", (name,))

# ── LECT_DEPT ─────────────────────────────────────────────────────────────────
def get_lecturers():
    return fetch("""
        SELECT ld.lect_id, ld.name, ni.initial, ld.workload, ld.deptid, d.deptname
        FROM lect_dept ld
        JOIN name_initial ni ON ld.name=ni.name
        JOIN dept d ON ld.deptid=d.deptid
        ORDER BY ld.lect_id
    """)

def add_lecturer(lect_id, name, initial, workload, deptid):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO name_initial VALUES (%s, %s)", (name, initial))
            cur.execute("INSERT INTO lect_dept VALUES (%s, %s, %s, %s)", (lect_id, name, workload, deptid))
        conn.commit()
    finally:
        conn.close()

def delete_lecturer(lect_id):
    execute("DELETE FROM lect_dept WHERE lect_id=%s", (lect_id,))

def update_lecturer(lect_id, workload, deptid):
    execute("UPDATE lect_dept SET workload=%s, deptid=%s WHERE lect_id=%s",
            (workload, deptid, lect_id))

# ── LECT_PHONENO ──────────────────────────────────────────────────────────────
def get_phone_numbers():
    return fetch("""
        SELECT lect_phoneno.lect_id, lect_dept.name, lect_phoneno.phoneno
        FROM lect_phoneno
        JOIN lect_dept ON lect_phoneno.lect_id = lect_dept.lect_id
        ORDER BY lect_phoneno.lect_id
    """)

def add_phone(lect_id, phoneno):
    execute("INSERT INTO lect_phoneno VALUES (%s, %s)", (lect_id, phoneno))

def delete_phone(lect_id, phoneno):
    execute("DELETE FROM lect_phoneno WHERE lect_id=%s AND phoneno=%s", (lect_id, phoneno))

# ── LECTURER_COURSE ───────────────────────────────────────────────────────────
def get_lecturer_courses():
    return fetch("""
        SELECT lc.lec_id, ld.name, lc.coursecode, c.coursename
        FROM lecturer_course lc
        JOIN lect_dept ld ON lc.lec_id=ld.lect_id
        JOIN coursetable c ON lc.coursecode=c.coursecode
        ORDER BY lc.lec_id
    """)

def add_lecturer_course(lec_id, coursecode):
    execute("INSERT INTO lecturer_course VALUES (%s, %s)", (lec_id, coursecode))

def delete_lecturer_course(lec_id, coursecode):
    execute("DELETE FROM lecturer_course WHERE lec_id=%s AND coursecode=%s", (lec_id, coursecode))

# ── CLASS SCHEDULE ────────────────────────────────────────────────────────────
def get_schedules():
    return fetch("""
        SELECT cs.classid, cs.day, cs.start_time, cs.end_time,
               cs.roomid, cs.lec_id, ld.name AS lec_name,
               cs.course_id, c.coursename, cs.pid, p.program_name
        FROM class_schedule cs
        JOIN room r ON cs.roomid=r.roomno
        JOIN lect_dept ld ON cs.lec_id=ld.lect_id
        JOIN coursetable c ON cs.course_id=c.coursecode
        JOIN program p ON cs.pid=p.pid
        ORDER BY cs.day, cs.start_time
    """)

def add_schedule(classid, day, start_time, end_time, roomid, lec_id, course_id, pid):
    execute("""
        INSERT INTO class_schedule VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (classid, day, start_time, end_time, roomid, lec_id, course_id, pid))

def delete_schedule(classid):
    execute("DELETE FROM class_schedule WHERE classid=%s", (classid,))

def update_schedule(classid, day, start_time, end_time, roomid, lec_id, course_id, pid):
    execute("""
        UPDATE class_schedule SET day=%s, start_time=%s, end_time=%s,
        roomid=%s, lec_id=%s, course_id=%s, pid=%s WHERE classid=%s
    """, (day, start_time, end_time, roomid, lec_id, course_id, pid, classid))

# ── DROPDOWN HELPERS ──────────────────────────────────────────────────────────
def get_dept_options():
    rows = fetch("SELECT deptid, deptname FROM dept ORDER BY deptname")
    return [(r["deptid"], r["deptname"]) for r in rows]

def get_program_name_options():
    rows = fetch("SELECT program_name FROM program_dept ORDER BY program_name")
    return [r["program_name"] for r in rows]

def get_program_options():
    rows = fetch("SELECT pid, program_name, year, sem FROM program ORDER BY pid")
    return [(r["pid"], f"{r['program_name']} Y{r['year']}S{r['sem']}") for r in rows]

def get_course_options():
    rows = fetch("SELECT coursecode, coursename FROM coursetable ORDER BY coursecode")
    return [(r["coursecode"], r["coursename"]) for r in rows]

def get_room_options():
    rows = fetch("SELECT roomno FROM room ORDER BY roomno")
    return [r["roomno"] for r in rows]

def get_lecturer_options():
    rows = fetch("SELECT lect_id, name FROM lect_dept ORDER BY name")
    return [(r["lect_id"], r["name"]) for r in rows]

def get_name_options():
    rows = fetch("SELECT name FROM name_initial ORDER BY name")
    return [r["name"] for r in rows]

def get_lec_course_pairs():
    """Returns valid (lec_id, coursecode) pairs for schedule validation."""
    rows = fetch("SELECT lec_id, coursecode FROM lecturer_course")
    return {(r["lec_id"], r["coursecode"]) for r in rows}

def get_pid_course_pairs():
    """Returns valid (pid, coursecode) pairs for schedule validation."""
    rows = fetch("SELECT pid, coursecode FROM program_course")
    return {(r["pid"], r["coursecode"]) for r in rows}