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
    for url in urls:
        open_edge(url)
    time.sleep(600)  # 等待10分钟
    close_edge()

def schedule_job(hour, minute, urls):
    schedule.clear()  # 清除之前的任务
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(job, urls)
    print(f"Scheduled job at {hour:02d}:{minute:02d} for URLs: {', '.join(urls)}")

def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'settings' in config:
        urls = config['settings'].get('urls', '').split('\n')
        time_str = config['settings'].get('time', '08:00')
        hour, minute = map(int, time_str.split(':'))
        return urls, QTime(hour, minute)
    return [], QTime.currentTime()

def save_config(urls, time):
    config = configparser.ConfigParser()
    config['settings'] = {
        'urls': '\n'.join(urls),
        'time': time.toString('HH:mm')
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

class SchedulerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('定时网页打开器')
        self.setGeometry(100, 100, 600, 300)

        layout = QVBoxLayout()

        time_layout = QHBoxLayout()
        time_label = QLabel('每天执行时间:')
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat('HH:mm')
        urls, time = load_config()
        self.time_edit.setTime(time)
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        layout.addLayout(time_layout)

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
        time = self.time_edit.time()
        hour = time.hour()
        minute = time.minute()
        urls = self.url_edit.toPlainText().split('\n')
        schedule_job(hour, minute, urls)
        save_config(urls, time)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SchedulerApp()
    ex.show()

    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    sys.exit(app.exec_())