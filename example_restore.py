import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QMessageBox, \
    QFileDialog, QDialog
from PyQt5.QtCore import QThread, QTimer, QEventLoop, pyqtSignal, QSettings, QObject
from PyQt5.QtGui import QIcon
import time
import pymysql
from pymysql.constants import CLIENT
import os
from PyQt5 import uic

from io import StringIO
import re
import shutil
import py7zr


def my_excepthook(type, value, tback):
    print(type, value, tback)
    sys.__excepthook__(type, value, tback)


class DlgSetting(QDialog):
    def __init__(self):
        super(DlgSetting, self).__init__()
        uic.loadUi('dlg_setting.ui', self)
        self.settings = QSettings('mRestore', 'setting')

        self.host.setText(self.settings.value('host'))
        self.user.setText(self.settings.value('user'))
        self.passwd.setText(self.settings.value('passwd'))
        self.db.setText(self.settings.value('db'))
        self.port.setText(self.settings.value('port'))
        self.charset.setText(self.settings.value('charset'))

        self.btn_save.clicked.connect(self.save)
        self.btn_test.clicked.connect(self.test)

    def test(self):
        try:
            self.conn = pymysql.connect(
                host=self.host.text(),
                user=self.user.text(),
                password=self.passwd.text(),
                port=int(self.port.text()),
                db=self.db.text(),
                charset=self.charset.text()
            )
            QMessageBox.about(self, "Info", "OK")
            self.save()
        except Exception as e:
            QMessageBox.about(self, "Info", str(e))

    def save(self):
        self.settings.setValue('host', self.host.text())
        self.settings.setValue('user', self.user.text())
        self.settings.setValue('passwd', self.passwd.text())
        self.settings.setValue('db', self.db.text())
        self.settings.setValue('port', self.port.text())
        self.settings.setValue('charset', self.charset.text())
        self.close()


class WorkerUnzip(QThread):
    finished = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, zip, folder):
        super().__init__()
        self.zip = zip
        self.folder = folder

    def run(self):
        print('Extract File..', self.zip, self.folder)
        with py7zr.SevenZipFile(self.zip, mode='r') as z:
            try:
                z.extractall(self.folder)
                print('Extract File..Done')
                self.finished.emit()
            except Exception as e:
                print('Extract File..Err', str(e))
                self.error.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.settings = QSettings('mRestore', 'setting')
        uic.loadUi('m_restore.ui', self)
        self.setWindowTitle("mRetore 1.0.4 (2023-01-17)")
        self.setWindowIcon(QIcon('restore.ico'))

        self.btn_browse.clicked.connect(self.browse)
        self.btn_begin.clicked.connect(self.begin)
        self.btn_pause.clicked.connect(self.pause_resume)
        self.btn_setting.clicked.connect(self.setting)

        self.is_pause = False
        self.files = None
        self.folder = None
        self.sql_files = list()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.tm = 0
        self.timer.timeout.connect(self._time)
        self.progressBar.setValue(0)
        self.progressBar2.setValue(0)
        self.progressBar2.setStyleSheet("QProgressBar::chunk "
                                        "{"
                                        "background-color: #00aaff;"
                                        "}")

        self.progressBar.setStyleSheet("QProgressBar::chunk "
                                       "{"
                                       "background-color: #00aaff;"
                                       "}")

    def _time(self):
        self.tm = self.tm + 1
        sec = self.tm
        if sec < 60:
            self.lb_time.setText(f"ใช้เวลา {sec} วินาที")
        else:
            m = int(sec / 60)
            s = sec % 60
            self.lb_time.setText(f"ใช้เวลา {m} นาที {s} วินาที")

    def setting(self):
        q = DlgSetting()
        q.exec_()

    def browse(self):
        last_dir = self.settings.value('last_dir')
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Select file", last_dir, "7z Files (*.7z);;zip Files (*.zip)",
                                                  options=options)
        if fileName:
            self.zip = fileName
            self.txt_folder.setText(self.zip)
            dirname, filename = os.path.split(fileName)
            filename, ext = os.path.splitext(filename)
            extract_dir = f"{dirname}/{filename}"
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            os.mkdir(extract_dir)
            self.folder = extract_dir
            self.settings.setValue('last_dir', dirname)

    def list_file(self, folder):
        self.sql_files.clear()
        self.txt_info.clear()
        self.files = os.listdir(folder)
        for f in self.files:
            path = folder + '//' + f
            if os.path.isfile(path):
                self.sql_files.append(f)
                self.txt_info.append(f)
                self.lb_cnt.setText(f"นำเข้า 0 จาก {len(self.sql_files)}")

    """
    def browse2(self):
        self.folder = None
        self.files = None
        self.sql_files.clear()
        last_dir = self.settings.value('last_dir')
        print(last_dir)
        self.folder = str(QFileDialog.getExistingDirectory(self, "Select Directory", last_dir))

        if self.folder:
            self.settings.setValue('last_dir', self.folder)
            self.txt_info.clear()
            self.txt_folder.setText(self.folder)
            self.files = os.listdir(self.folder)
            for f in self.files:
                path = self.folder + '//' + f
                if os.path.isfile(path):
                    self.sql_files.append(f)
                    self.txt_info.append(f)
                    self.lb_cnt.setText(f"นำเข้า 0 จาก {len(self.sql_files)}")
    """

    def begin(self):
        self.btn_begin.setEnabled(False)
        self.lb_table.setText('กำลัง Extract File ....')
        self.unzip = WorkerUnzip(self.zip, self.folder)
        self.unzip.start()
        self.unzip.finished.connect(self.begin_restore)
        self.unzip.error.connect(lambda: [
            QMessageBox.critical(self, "ข้อผิดพลาด", "Extract File ไม่สำเร็จ")
            , self.lb_table.setText('-')
            , self.btn_begin.setEnabled(True)

        ])

    def begin_restore(self):
        self.list_file(self.folder)
        if len(self.sql_files) == 0:
            QMessageBox.warning(self, "คำเตือน", "ยังไม่ได้เลือกโฟรเดอร์")
            return False
        self.txt_info.clear()
        self.lb_time.clear()
        self.w = Worker(self.folder, self.sql_files)

        self.w.signal_progress.connect(self.progress)
        self.w.signal_progress2.connect(self.progress2)
        self.w.signal_progress3.connect(self.progress3)
        self.w.signal_err.connect(self.error)
        self.w.signal_finish.connect(self.finish)
        self.w.start()
        self.btn_begin.setEnabled(False)
        self.timer.start()

    def progress(self, data):
        self.lb_cnt.setText(data['n'])
        p = (data['cnt'] * 100) / data['all']
        self.progressBar.setValue(int(p))

    def progress2(self, data):
        self.progressBar2.setValue(int(data['p']))

    def progress3(self, data):
        self.lb_table.setText(data['tb'])

    def pause_resume(self):
        self.is_pause = not self.is_pause
        print(self.is_pause)
        if self.is_pause:
            self.btn_pause.setText('Resume')
            self.w.pause()
            self.timer.stop()
        else:
            self.btn_pause.setText('Pause')
            self.w.resume()
            self.timer.start()

    def error(self, data):
        err = data
        self.txt_info.append(err + "\n")

    def finish(self, data):
        print('finish', data)
        self.timer.stop()
        self.tm = 0
        self.btn_begin.setEnabled(True)
        QMessageBox.information(self, 'OK', data)
        self.lb_table.setText('-')
        self.progressBar.setValue(0)
        self.progressBar2.setValue(0)


class Worker(QThread):
    signal_progress = pyqtSignal(dict)
    signal_err = pyqtSignal(str)
    signal_finish = pyqtSignal(str)
    signal_sql = pyqtSignal(str)
    signal_progress2 = pyqtSignal(dict)
    signal_progress3 = pyqtSignal(dict)

    def __init__(self, folder, files):
        super(Worker, self).__init__()
        self.settings = QSettings('mRestore', 'setting')

        self.files = files
        self.folder = folder
        self.is_paused = False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def check_is_procedure_or_function(self, f):
        procedure_pattern = b"CREATE (DEFINER=[^\\s]* )?PROCEDURE"
        function_pattern = b"CREATE (DEFINER=[^\\s]* )?FUNCTION"
        for line in f:
            if re.search(procedure_pattern, line):
                return True
            if re.search(function_pattern, line):
                return True
        return False

    def do_restore(self, file):
        conn = pymysql.connect(
            host=self.settings.value('host'),
            port=int(self.settings.value('port')),
            database=self.settings.value('db'),
            user=self.settings.value('user'),
            password=self.settings.value('passwd'),
            charset=self.settings.value('charset'),
            client_flag=CLIENT.MULTI_STATEMENTS,
            # connect_timeout=3600

        )
        with conn.cursor() as cursor:
            set_cmd = f"""
                set innodb_strict_mode = 0 ;
            """
            cursor.execute(set_cmd)

        sql = b""
        all_line = 0
        self.signal_progress2.emit({'p': 0})
        with open(file, 'rb') as f:
            all_line = sum(1 for _ in f)
        with open(file, 'rb') as f:
            at_line = 0
            for line in f:
                at_line += 1
                p = at_line * 100 / all_line
                self.signal_progress2.emit({'p': p})
                sql += line
                if line.endswith(b";\r\n"):
                    try:
                        with conn.cursor(pymysql.cursors.SSCursor) as cursor:
                            cursor.execute(sql)
                            conn.commit()
                        sql = b""
                    except Exception as e:
                        sql = b""
                        self.signal_err.emit(f"{file},{str(e)}")
                        continue

        # conn.commit()
        conn.close()

    def run(self):
        at_file = 0
        for i in self.files:
            while self.is_paused:
                time.sleep(0)
            file = f"{self.folder}\\{i}"

            self.signal_progress3.emit({
                'tb': f"กำลังนำเข้า... {i}",
            })
            self.do_restore(file)
            at_file += 1
            self.signal_progress.emit({
                'n': f"นำเข้า {at_file} จาก {len(self.files)}",
                'cnt': at_file,
                'all': len(self.files)
            })

        self.signal_finish.emit('สิ้นสุดกระบวนการนำเข้า!!!')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.excepthook = my_excepthook
    sys.exit(app.exec_())