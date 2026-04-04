import sys
import pymysql
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui import MainWindow

def check_connection():
    try:
        import database as db
        conn = db.get_conn()
        conn.close()
        return True
    except Exception as e:
        QMessageBox.critical(None, "Database Connection Failed",
            f"Could not connect to MySQL database 'sms_db'.\n\n"
            f"Make sure:\n"
            f"  - MySQL server is running\n"
            f"  - Database 'sms_db' exists\n"
            f"  - Password is correct\n\n"
            f"Error: {e}")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    if not check_connection():
        sys.exit(1)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())