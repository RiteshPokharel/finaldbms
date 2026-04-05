from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QStackedWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QLabel, QComboBox, QSpinBox, QMessageBox, QFormLayout,
    QGroupBox, QTimeEdit, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QTime
import database as db


# ── HELPERS ───────────────────────────────────────────────────────────────────

def make_table(headers):
    t = QTableWidget()
    t.setColumnCount(len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setAlternatingRowColors(True)
    t.horizontalHeader().setStretchLastSection(True)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    t.verticalHeader().setVisible(False)
    t.setSortingEnabled(True)
    return t

def fill_table(table, rows, keys):
    table.setSortingEnabled(False)
    table.setRowCount(0)
    for r in rows:
        row = table.rowCount()
        table.insertRow(row)
        for col, k in enumerate(keys):
            val = str(r[k]) if r[k] is not None else ""
            table.setItem(row, col, QTableWidgetItem(val))
    table.setSortingEnabled(True)

def err(msg):
    box = QMessageBox()
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle("Error")
    box.setText(str(msg))
    box.exec_()

def ok(msg):
    box = QMessageBox()
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle("Success")
    box.setText(msg)
    box.exec_()

def confirm(msg):
    r = QMessageBox.question(None, "Confirm", msg, QMessageBox.Yes | QMessageBox.No)
    return r == QMessageBox.Yes

def refresh_combo(combo, items):
    combo.blockSignals(True)
    combo.clear()
    combo.addItem("-- select --", None)
    for item in items:
        if isinstance(item, tuple):
            combo.addItem(str(item[1]), item[0])
        else:
            combo.addItem(str(item), item)
    combo.blockSignals(False)


# ── BASE VIEW ─────────────────────────────────────────────────────────────────

class BaseView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout_ = QVBoxLayout(self)
        self.layout_.setSpacing(8)
        self.layout_.setContentsMargins(12, 12, 12, 12)

    def refresh_btn(self, callback):
        btn = QPushButton("Refresh")
        btn.setFixedWidth(100)
        btn.clicked.connect(callback)
        return btn


# ── DEPARTMENT VIEW ───────────────────────────────────────────────────────────

class DeptView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Departments"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["ID", "Department Name"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Add / Edit Department")
        form = QFormLayout(box)
        self.f_id = QSpinBox(); self.f_id.setRange(1, 99999)
        self.f_name = QLineEdit()
        form.addRow("Dept ID:", self.f_id)
        form.addRow("Dept Name:", self.f_name)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Edit", self.edit), ("Delete", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.table.itemSelectionChanged.connect(self.on_select)
        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_depts(), ["deptid", "deptname"])
        except Exception as e: err(e)

    def on_select(self):
        rows = self.table.selectedItems()
        if rows:
            self.f_id.setValue(int(rows[0].text()))
            self.f_name.setText(rows[1].text())

    def add(self):
        if not self.f_name.text().strip(): err("Dept Name required."); return
        try:
            db.add_dept(self.f_id.value(), self.f_name.text().strip())
            self.load(); ok("Department added.")
        except Exception as e: err(e)

    def edit(self):
        if not self.f_name.text().strip(): err("Dept Name required."); return
        try:
            db.update_dept(self.f_id.value(), self.f_name.text().strip())
            self.load(); ok("Department updated.")
        except Exception as e: err(e)

    def delete(self):
        if not confirm("Delete this department?"): return
        try:
            db.delete_dept(self.f_id.value())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── PROGRAM DEPT VIEW ─────────────────────────────────────────────────────────

class ProgramDeptView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Program — Department Links"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["Program Name", "Dept ID", "Dept Name"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Add Program-Department Link")
        form = QFormLayout(box)
        self.f_prog = QLineEdit()
        self.f_dept = QComboBox()
        form.addRow("Program Name:", self.f_prog)
        form.addRow("Department:", self.f_dept)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Delete Selected", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.table.itemSelectionChanged.connect(self.on_select)
        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_program_depts(), ["program_name", "deptid", "deptname"])
            refresh_combo(self.f_dept, db.get_dept_options())
        except Exception as e: err(e)

    def on_select(self):
        rows = self.table.selectedItems()
        if rows: self.f_prog.setText(rows[0].text())

    def add(self):
        dept_id = self.f_dept.currentData()
        prog = self.f_prog.text().strip()
        if dept_id is None: err("Select a department."); return
        if not prog: err("Program Name required."); return
        try:
            db.add_program_dept(prog, dept_id)
            self.load(); ok("Link added.")
        except Exception as e: err(e)

    def delete(self):
        rows = self.table.selectedItems()
        if not rows: err("Select a row."); return
        if not confirm("Delete this link?"): return
        try:
            db.delete_program_dept(rows[0].text())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── PROGRAM VIEW ──────────────────────────────────────────────────────────────

class ProgramView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Programs"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["PID", "Program Name", "Year", "Sem", "Dept ID"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Add / Edit Program")
        form = QFormLayout(box)
        self.f_pid = QSpinBox(); self.f_pid.setRange(1, 99999)
        self.f_prog = QComboBox()
        self.f_year = QSpinBox(); self.f_year.setRange(1, 4)
        self.f_sem = QComboBox(); self.f_sem.addItems(["1", "2"])
        form.addRow("PID:", self.f_pid)
        form.addRow("Program Name:", self.f_prog)
        form.addRow("Year:", self.f_year)
        form.addRow("Semester:", self.f_sem)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Edit", self.edit), ("Delete", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.table.itemSelectionChanged.connect(self.on_select)
        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_programs(), ["pid", "program_name", "year", "sem", "deptid"])
            refresh_combo(self.f_prog, db.get_program_name_options())
        except Exception as e: err(e)

    def on_select(self):
        rows = self.table.selectedItems()
        if rows:
            self.f_pid.setValue(int(rows[0].text()))
            for i in range(self.f_prog.count()):
                if self.f_prog.itemData(i) == rows[1].text():
                    self.f_prog.setCurrentIndex(i); break
            self.f_year.setValue(int(rows[2].text()))
            self.f_sem.setCurrentText(rows[3].text())

    def add(self):
        prog = self.f_prog.currentData()
        if prog is None: err("Select a program name."); return
        try:
            db.add_program(self.f_pid.value(), prog, self.f_year.value(), int(self.f_sem.currentText()))
            self.load(); ok("Program added.")
        except Exception as e: err(e)

    def edit(self):
        prog = self.f_prog.currentData()
        if prog is None: err("Select a program name."); return
        try:
            db.update_program(self.f_pid.value(), prog, self.f_year.value(), int(self.f_sem.currentText()))
            self.load(); ok("Program updated.")
        except Exception as e: err(e)

    def delete(self):
        if not confirm("Delete this program?"): return
        try:
            db.delete_program(self.f_pid.value())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── COURSE VIEW ───────────────────────────────────────────────────────────────

class CourseView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Courses"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["Course Code", "Course Name", "Credit Hours"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Add / Edit Course")
        form = QFormLayout(box)
        self.f_code = QLineEdit()
        self.f_name = QLineEdit()
        self.f_credit = QSpinBox(); self.f_credit.setRange(1, 10)
        form.addRow("Course Code:", self.f_code)
        form.addRow("Course Name:", self.f_name)
        form.addRow("Credit Hours:", self.f_credit)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Edit", self.edit), ("Delete", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.table.itemSelectionChanged.connect(self.on_select)
        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_courses(), ["coursecode", "coursename", "credithour"])
        except Exception as e: err(e)

    def on_select(self):
        rows = self.table.selectedItems()
        if rows:
            self.f_code.setText(rows[0].text())
            self.f_name.setText(rows[1].text())
            self.f_credit.setValue(int(rows[2].text()))

    def add(self):
        if not self.f_code.text().strip() or not self.f_name.text().strip():
            err("Course Code and Name required."); return
        try:
            db.add_course(self.f_code.text().strip(), self.f_name.text().strip(), self.f_credit.value())
            self.load(); ok("Course added.")
        except Exception as e: err(e)

    def edit(self):
        if not self.f_code.text().strip(): err("Select a course from the table first."); return
        try:
            db.update_course(self.f_code.text().strip(), self.f_name.text().strip(), self.f_credit.value())
            self.load(); ok("Course updated.")
        except Exception as e: err(e)

    def delete(self):
        if not self.f_code.text().strip(): err("Select a course from the table first."); return
        if not confirm("Delete this course?"): return
        try:
            db.delete_course(self.f_code.text().strip())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── PROGRAM COURSE VIEW ───────────────────────────────────────────────────────

class ProgramCourseView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Program — Course Links"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["PID", "Program Name", "Course Code", "Course Name"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Assign Course to Program")
        form = QFormLayout(box)
        self.f_pid = QComboBox()
        self.f_course = QComboBox()
        form.addRow("Program:", self.f_pid)
        form.addRow("Course:", self.f_course)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Delete Selected", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_program_courses(), ["pid", "program_name", "coursecode", "coursename"])
            refresh_combo(self.f_pid, db.get_program_options())
            refresh_combo(self.f_course, db.get_course_options())
        except Exception as e: err(e)

    def add(self):
        pid = self.f_pid.currentData()
        code = self.f_course.currentData()
        if pid is None or code is None: err("Select both a program and a course."); return
        try:
            db.add_program_course(pid, code)
            self.load(); ok("Course assigned to program.")
        except Exception as e: err(e)

    def delete(self):
        rows = self.table.selectedItems()
        if not rows: err("Select a row."); return
        if not confirm("Remove this assignment?"): return
        try:
            db.delete_program_course(int(rows[0].text()), rows[2].text())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── ROOM VIEW ─────────────────────────────────────────────────────────────────

class RoomView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Rooms"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["Room No", "Capacity"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Add / Edit Room")
        form = QFormLayout(box)
        self.f_no = QLineEdit()
        self.f_cap = QSpinBox(); self.f_cap.setRange(1, 9999)
        form.addRow("Room No:", self.f_no)
        form.addRow("Capacity:", self.f_cap)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Edit", self.edit), ("Delete", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.table.itemSelectionChanged.connect(self.on_select)
        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_rooms(), ["roomno", "capacity"])
        except Exception as e: err(e)

    def on_select(self):
        rows = self.table.selectedItems()
        if rows:
            self.f_no.setText(rows[0].text())
            self.f_cap.setValue(int(rows[1].text()))

    def add(self):
        if not self.f_no.text().strip(): err("Room No required."); return
        try:
            db.add_room(self.f_no.text().strip(), self.f_cap.value())
            self.load(); ok("Room added.")
        except Exception as e: err(e)

    def edit(self):
        if not self.f_no.text().strip(): err("Select a room from the table first."); return
        try:
            db.update_room(self.f_no.text().strip(), self.f_cap.value())
            self.load(); ok("Room updated.")
        except Exception as e: err(e)

    def delete(self):
        if not self.f_no.text().strip(): err("Select a room from the table first."); return
        if not confirm("Delete this room?"): return
        try:
            db.delete_room(self.f_no.text().strip())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── LECTURER VIEW ─────────────────────────────────────────────────────────────

class LecturerView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Lecturers"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["ID", "Name", "Initial", "Workload", "Dept ID", "Dept Name"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Add / Edit Lecturer")
        form = QFormLayout(box)
        self.f_id = QSpinBox(); self.f_id.setRange(1, 99999)
        self.f_name = QLineEdit()
        self.f_initial = QLineEdit(); self.f_initial.setMaxLength(10)
        self.f_workload = QSpinBox(); self.f_workload.setRange(0, 999)
        self.f_dept = QComboBox()
        form.addRow("Lect ID:", self.f_id)
        form.addRow("Name:", self.f_name)
        form.addRow("Initial:", self.f_initial)
        form.addRow("Workload:", self.f_workload)
        form.addRow("Department:", self.f_dept)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Edit", self.edit), ("Delete", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.table.itemSelectionChanged.connect(self.on_select)
        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_lecturers(),
                       ["lect_id", "name", "initial", "workload", "deptid", "deptname"])
            refresh_combo(self.f_dept, db.get_dept_options())
        except Exception as e: err(e)

    def on_select(self):
        rows = self.table.selectedItems()
        if rows:
            self.f_id.setValue(int(rows[0].text()))
            self.f_name.setText(rows[1].text())
            self.f_initial.setText(rows[2].text())
            self.f_workload.setValue(int(rows[3].text()))
            for i in range(self.f_dept.count()):
                if self.f_dept.itemData(i) == int(rows[4].text()):
                    self.f_dept.setCurrentIndex(i); break

    def add(self):
        dept = self.f_dept.currentData()
        name = self.f_name.text().strip()
        initial = self.f_initial.text().strip()
        if dept is None: err("Select a department."); return
        if not name or not initial: err("Name and initial required."); return
        try:
            db.add_lecturer(self.f_id.value(), name, initial, self.f_workload.value(), dept)
            self.load(); ok("Lecturer added.")
        except Exception as e: err(e)

    def edit(self):
        dept = self.f_dept.currentData()
        if dept is None: err("Select a department."); return
        try:
            db.update_lecturer(self.f_id.value(), self.f_workload.value(), dept)
            self.load(); ok("Lecturer updated.")
        except Exception as e: err(e)

    def delete(self):
        if not confirm("Delete this lecturer?"): return
        try:
            db.delete_lecturer(self.f_id.value())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── PHONE VIEW ────────────────────────────────────────────────────────────────

class PhoneView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Lecturer Phone Numbers"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["Lect ID", "Name", "Phone No"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Add Phone Number")
        form = QFormLayout(box)
        self.f_lect = QComboBox()
        self.f_phone = QLineEdit()
        form.addRow("Lecturer:", self.f_lect)
        form.addRow("Phone No:", self.f_phone)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Delete Selected", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_phone_numbers(), ["lect_id", "name", "phoneno"])
            refresh_combo(self.f_lect, db.get_lecturer_options())
        except Exception as e: err(e)

    def add(self):
        lect_id = self.f_lect.currentData()
        phone = self.f_phone.text().strip()
        if lect_id is None: err("Select a lecturer."); return
        if not phone: err("Enter a phone number."); return
        try:
            db.add_phone(lect_id, phone)
            self.f_phone.clear()
            self.load(); ok("Phone number added.")
        except Exception as e: err(e)

    def delete(self):
        rows = self.table.selectedItems()
        if not rows: err("Select a row."); return
        if not confirm("Delete this phone number?"): return
        try:
            db.delete_phone(rows[0].text(), rows[2].text())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── LECTURER COURSE VIEW ──────────────────────────────────────────────────────

class LecturerCourseView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Lecturer — Course Qualifications"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table(["Lect ID", "Lecturer Name", "Course Code", "Course Name"])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Assign Course to Lecturer")
        form = QFormLayout(box)
        self.f_lect = QComboBox()
        self.f_course = QComboBox()
        form.addRow("Lecturer:", self.f_lect)
        form.addRow("Course:", self.f_course)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Delete Selected", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.load()

    def load(self):
        try:
            fill_table(self.table, db.get_lecturer_courses(),
                       ["lec_id", "name", "coursecode", "coursename"])
            refresh_combo(self.f_lect, db.get_lecturer_options())
            refresh_combo(self.f_course, db.get_course_options())
        except Exception as e: err(e)

    def add(self):
        lec_id = self.f_lect.currentData()
        code = self.f_course.currentData()
        if lec_id is None or code is None: err("Select both a lecturer and a course."); return
        try:
            db.add_lecturer_course(lec_id, code)
            self.load(); ok("Qualification added.")
        except Exception as e: err(e)

    def delete(self):
        rows = self.table.selectedItems()
        if not rows: err("Select a row."); return
        if not confirm("Remove this qualification?"): return
        try:
            db.delete_lecturer_course(int(rows[0].text()), rows[2].text())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── SCHEDULE VIEW ─────────────────────────────────────────────────────────────

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

class ScheduleView(BaseView):
    def __init__(self):
        super().__init__()
        top = QHBoxLayout()
        top.addWidget(QLabel("Class Schedule"))
        top.addStretch()
        top.addWidget(self.refresh_btn(self.load))
        self.layout_.addLayout(top)

        self.table = make_table([
            "Class ID", "Day", "Start", "End",
            "Room", "Lect ID", "Lecturer", "Course Code", "Course", "PID", "Program"
        ])
        self.layout_.addWidget(self.table)

        box = QGroupBox("Add / Edit Schedule")
        form = QFormLayout(box)
        self.f_id = QSpinBox(); self.f_id.setRange(1, 99999)
        self.f_day = QComboBox(); self.f_day.addItems(DAYS)
        self.f_start = QTimeEdit(); self.f_start.setDisplayFormat("HH:mm")
        self.f_end = QTimeEdit(); self.f_end.setDisplayFormat("HH:mm")
        self.f_room = QComboBox()
        self.f_lect = QComboBox()
        self.f_course = QComboBox()
        self.f_pid = QComboBox()
        form.addRow("Class ID:", self.f_id)
        form.addRow("Day:", self.f_day)
        form.addRow("Start Time:", self.f_start)
        form.addRow("End Time:", self.f_end)
        form.addRow("Room:", self.f_room)
        form.addRow("Lecturer:", self.f_lect)
        form.addRow("Course:", self.f_course)
        form.addRow("Program:", self.f_pid)
        btn_row = QHBoxLayout()
        for label, slot in [("Add", self.add), ("Edit", self.edit), ("Delete", self.delete)]:
            b = QPushButton(label); b.clicked.connect(slot); btn_row.addWidget(b)
        form.addRow(btn_row)
        self.layout_.addWidget(box)

        self.table.itemSelectionChanged.connect(self.on_select)
        self.load()

    def load(self):
        try:
            rows = db.get_schedules()
            for r in rows:
                for k in ["start_time", "end_time"]:
                    val = r[k]
                    if hasattr(val, "seconds"):
                        h, rem = divmod(val.seconds, 3600)
                        r[k] = f"{h:02d}:{rem//60:02d}"
                    else:
                        r[k] = str(val)[:5]
            fill_table(self.table, rows, [
                "classid", "day", "start_time", "end_time",
                "roomid", "lec_id", "lec_name", "course_id", "coursename", "pid", "program_name"
            ])
            refresh_combo(self.f_room, db.get_room_options())
            refresh_combo(self.f_lect, db.get_lecturer_options())
            refresh_combo(self.f_course, db.get_course_options())
            refresh_combo(self.f_pid, db.get_program_options())
        except Exception as e: err(e)

    def on_select(self):
        rows = self.table.selectedItems()
        if not rows: return
        self.f_id.setValue(int(rows[0].text()))
        self.f_day.setCurrentText(rows[1].text())
        t_start = QTime.fromString(rows[2].text(), "HH:mm")
        t_end = QTime.fromString(rows[3].text(), "HH:mm")
        if t_start.isValid(): self.f_start.setTime(t_start)
        if t_end.isValid(): self.f_end.setTime(t_end)
        for i in range(self.f_room.count()):
            if self.f_room.itemData(i) == rows[4].text():
                self.f_room.setCurrentIndex(i); break
        lect_id = int(rows[5].text())
        for i in range(self.f_lect.count()):
            if self.f_lect.itemData(i) == lect_id:
                self.f_lect.setCurrentIndex(i); break
        code = rows[7].text()
        for i in range(self.f_course.count()):
            if self.f_course.itemData(i) == code:
                self.f_course.setCurrentIndex(i); break
        pid = int(rows[9].text())
        for i in range(self.f_pid.count()):
            if self.f_pid.itemData(i) == pid:
                self.f_pid.setCurrentIndex(i); break

    def _validate(self):
        if self.f_start.time() >= self.f_end.time():
            err("End time must be after start time."); return False
        lec_id = self.f_lect.currentData()
        course_id = self.f_course.currentData()
        pid = self.f_pid.currentData()
        room = self.f_room.currentData()
        if None in (room, lec_id, course_id, pid):
            err("All fields must be selected."); return False
        if (lec_id, course_id) not in db.get_lec_course_pairs():
            err("Lecturer is not qualified for this course.\nAdd the qualification in Lecturer Courses first."); return False
        if (pid, course_id) not in db.get_pid_course_pairs():
            err("Course not assigned to this program.\nAdd it in Program Courses first."); return False
        return True

    def add(self):
        if not self._validate(): return
        try:
            db.add_schedule(
                self.f_id.value(), self.f_day.currentText(),
                self.f_start.time().toString("HH:mm:ss"),
                self.f_end.time().toString("HH:mm:ss"),
                self.f_room.currentData(), self.f_lect.currentData(),
                self.f_course.currentData(), self.f_pid.currentData()
            )
            self.load(); ok("Schedule added.")
        except Exception as e: err(e)

    def edit(self):
        if not self._validate(): return
        try:
            db.update_schedule(
                self.f_id.value(), self.f_day.currentText(),
                self.f_start.time().toString("HH:mm:ss"),
                self.f_end.time().toString("HH:mm:ss"),
                self.f_room.currentData(), self.f_lect.currentData(),
                self.f_course.currentData(), self.f_pid.currentData()
            )
            self.load(); ok("Schedule updated.")
        except Exception as e: err(e)

    def delete(self):
        if not confirm("Delete this schedule entry?"): return
        try:
            db.delete_schedule(self.f_id.value())
            self.load(); ok("Deleted.")
        except Exception as e: err(e)


# ── MAIN WINDOW ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("University Timetable Management")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #1e2433;
                color: #c8cdd8;
                font-size: 14px;
                border: none;
                padding-top: 10px;
            }
            QListWidget::item { padding: 12px 20px; }
            QListWidget::item:selected {
                background-color: #2e3a52;
                color: #ffffff;
                border-left: 3px solid #4a90d9;
            }
            QListWidget::item:hover:!selected { background-color: #252d3d; }
        """)

        pages = [
            ("Departments",      DeptView),
            ("Program Depts",    ProgramDeptView),
            ("Programs",         ProgramView),
            ("Courses",          CourseView),
            ("Program Courses",  ProgramCourseView),
            ("Rooms",            RoomView),
            ("Lecturers",        LecturerView),
            ("Phone Numbers",    PhoneView),
            ("Lecturer Courses", LecturerCourseView),
            ("Class Schedule",   ScheduleView),
        ]

        self.stack = QStackedWidget()
        for label, ViewClass in pages:
            self.sidebar.addItem(label)
            self.stack.addWidget(ViewClass())

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet("background-color: #1e2433; border-bottom: 1px solid #2e3a52;")
        hl = QHBoxLayout(header)
        title = QLabel("University Timetable System")
        title.setStyleSheet("color:#fff; font-size:16px; font-weight:bold; padding-left:16px;")
        hl.addWidget(title)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        rl.addWidget(header)
        rl.addWidget(self.stack)

        root.addWidget(self.sidebar)
        root.addWidget(right)

        self.stack.setStyleSheet("""
            QWidget { font-size: 13px; }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                margin-top: 8px;
                padding: 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #357abd; }
            QPushButton:pressed { background-color: #2a6099; }
            QTableWidget { border: 1px solid #dcdcdc; gridline-color: #f0f0f0; }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #dcdcdc;
                font-weight: bold;
            }
        """)