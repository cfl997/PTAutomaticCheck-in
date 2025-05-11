import os
import schedule
import time
import sys
import configparser
import datetime
import threading
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTimeEdit, QTextEdit
from PyQt5.QtCore import QTime

CONFIG_FILE = "config.ini"

def open_edge(url):
    subprocess.Popen(['start', 'msedge', url], shell=True)

def close_edge():
    subprocess.call(['taskkill', '/f', '/im', 'msedge.exe'])

def job(urls):
    print(f"Executing job for URLs: {', '.join(urls)} at {datetime.datetime.now().strftime('%H:%M:%S')}")
    for url in urls:
        open_edge(url)
    time.sleep(600)  # 等待10分钟
    close_edge()

def schedule_job(time1, time2, urls):
    schedule.clear()  # 清除之前的任务
    hour1, minute1 = time1.hour(), time1.minute()
    hour2, minute2 = time2.hour(), time2.minute()
    schedule.every().day.at(f"{hour1:02d}:{minute1:02d}").do(job, urls)
    schedule.every().day.at(f"{hour2:02d}:{minute2:02d}").do(job, urls)
    print(f"Scheduled job at {hour1:02d}:{minute1:02d} and {hour2:02d}:{minute2:02d} for URLs: {', '.join(urls)}")

def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'settings' in config:
        urls = config['settings'].get('urls', '').split('\n')
        time_str1 = config['settings'].get('time1', '08:00')
        time_str2 = config['settings'].get('time2', '18:00')
        hour1, minute1 = map(int, time_str1.split(':'))
        hour2, minute2 = map(int, time_str2.split(':'))
        return urls, QTime(hour1, minute1), QTime(hour2, minute2)
    return [], QTime.currentTime(), QTime(18, 0)

def save_config(urls, time1, time2):
    config = configparser.ConfigParser()
    config['settings'] = {
        'urls': '\n'.join(urls),
        'time1': time1.toString('HH:mm'),
        'time2': time2.toString('HH:mm')
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

class SchedulerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('定时网页打开器')
        self.setGeometry(100, 100, 600, 350)  # 稍微增加高度

        layout = QVBoxLayout()

        # 第一个时间选择
        time_layout1 = QHBoxLayout()
        time_label1 = QLabel('每天执行时间 1:')
        self.time_edit1 = QTimeEdit()
        self.time_edit1.setDisplayFormat('HH:mm')
        urls, time1, time2 = load_config()
        self.time_edit1.setTime(time1)
        time_layout1.addWidget(time_label1)
        time_layout1.addWidget(self.time_edit1)
        layout.addLayout(time_layout1)

        # 第二个时间选择
        time_layout2 = QHBoxLayout()
        time_label2 = QLabel('每天执行时间 2:')
        self.time_edit2 = QTimeEdit()
        self.time_edit2.setDisplayFormat('HH:mm')
        self.time_edit2.setTime(time2)
        time_layout2.addWidget(time_label2)
        time_layout2.addWidget(self.time_edit2)
        layout.addLayout(time_layout2)

        url_layout = QHBoxLayout()
        url_label = QLabel('网页链接 (每行一个):')
        self.url_edit = QTextEdit()
        self.url_edit.setText('\n'.join(urls))
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)

        submit_button = QPushButton('提交')
        submit_button.clicked.connect(self.on_submit)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def on_submit(self):
        time1 = self.time_edit1.time()
        time2 = self.time_edit2.time()
        urls = self.url_edit.toPlainText().split('\n')
        schedule_job(time1, time2, urls)
        save_config(urls, time1, time2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SchedulerApp()
    ex.show()

    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    sys.exit(app.exec_())