from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QRect, QResource, QThread, pyqtSignal, QSize, QMetaObject
from PyQt5 import QtGui, QtWidgets
import os , re
import requests
import socket
import configparser

global init
global game_ip
version = '2'
appdata_path = os.getenv('APPDATA')
KSHDIR = os.path.join(appdata_path, 'KSH-Soft')
KSHRPDIR = os.path.join(appdata_path, 'KSH-Soft', 'RenylandProxy')
KSHRPDIR = os.path.join(appdata_path, 'KSH-Soft', 'RenylandProxy')
KSHRPFile = os.path.join(appdata_path, 'KSH-Soft', 'RenylandProxy', 'config.ini')
game_ip = "0.0.0.0"
port = 8000

HOSTS_FILE_PATH = r"C:\Windows\System32\drivers\etc\hosts"

TARGET_ADDRESSES = [
    "d26e4xubm8adxu.cloudfront.net",
    "d6ccx151yatz6.cloudfront.net",
    "app.anyland.com"
]

SECTION_START = "####ANYLAND-DNS####"
SECTION_END = "#### BY AXSYS #####"

class InternetTestThread(QThread):
    update_status_signal = pyqtSignal(str)
    update_led_signal = pyqtSignal(str)

    def __init__(self, ui_instance):
        super().__init__()
        self.ui_instance = ui_instance

    def run(self):

        status_message = "Status : Check en cours..."
        self.update_status_signal.emit(status_message)

        game_ip = self.ui_instance.read_value_from_ini('Config', 'ip')
        if game_ip != "0.0.0.0":
            if self.ui_instance.internet_connection():
                self.update_led_signal.emit("orange")
                self.update_status_signal.emit("Status : Connexion internet réussie... Check du serveur...")

                url = "http://kashi.world.free.fr/REnyland/HOTD"
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        HOTD = response.text
                        self.ui_instance.HOTD.setText(HOTD)
                except requests.RequestException:
                    self.update_status_signal.emit("Status : Erreur de connexion au serveur HOTD")

                url = "http://kashi.world.free.fr/REnyland/LASTV"
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        LASTV = response.text
                        if LASTV > version:
                            self.update_status_signal.emit("/!\\ NEED UPDATE /!\\")
                except requests.RequestException:
                    self.update_status_signal.emit("Status : Erreur de connexion pour vérifier la version")

                if self.ui_instance.is_port_open(game_ip, port):
                    self.update_led_signal.emit("vert")
                    self.update_status_signal.emit("Status : La redirection DNS est activée")
                else:
                    self.update_led_signal.emit("orange")
                    self.update_status_signal.emit("Status : Problème avec le serveur ou mauvaise IP...")
            else:
                self.update_led_signal.emit("rouge")
                self.update_status_signal.emit("Status : Pas de connexion Internet")
        else:
            self.update_led_signal.emit("rouge")
            self.update_status_signal.emit("Status : Adresse IP non configurée.")

class Ui_MainWindow(object):
    global game_ip
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setWindowTitle("Renyland_Proxy")
        MainWindow.setObjectName("Renyland_Proxy")
        MainWindow.setEnabled(True)
        MainWindow.resize(400, 200)
        MainWindow.setFixedSize(400, 200)
        
        self.internet_thread = None
        
        MainWindow.setWindowFlags(Qt.FramelessWindowHint)
        
        app_icon = QtGui.QIcon()
        app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
        MainWindow.setWindowIcon(app_icon)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QRect(330, 170, 61, 21))
        self.pushButton.setStyleSheet("")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.mousePressEvent = self.OnPlay
        self.pushButton.setFont(QtGui.QFont('Arial', 8))
        button_style = """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2C5AA0;
            }
        """
        self.pushButton.setStyleSheet(button_style)
        
        self.IMG_LED = QtWidgets.QLabel(self.centralwidget)
        self.IMG_LED.setGeometry(QRect(0, 180, 20, 20))
        self.IMG_LED.setStyleSheet("image: url(:/Asset/led-r.png);")
        self.IMG_LED.setText("")
        self.IMG_LED.setObjectName("IMG_LED")
        
        self.STATUS = QtWidgets.QLabel(self.centralwidget)
        self.STATUS.setGeometry(QRect(21, 181, 281, 16))
        self.STATUS.setObjectName("STATUS")
        self.STATUS.mousePressEvent = self.internettest
        self.STATUS.setFont(QtGui.QFont('Arial', 8))
        
        self.BG = QtWidgets.QLabel(self.centralwidget)
        self.BG.setGeometry(QRect(0, -10, 401, 221))
        self.BG.setStyleSheet("image: url(:/Asset/bg.png);")
        self.BG.setText("")
        self.BG.setObjectName("BG")
        self.BG.mousePressEvent = self.mousePressEvent
        self.BG.mouseMoveEvent = self.mouseMoveEvent
        self.BG.mouseReleaseEvent = self.mouseReleaseEvent
        
        self.VersionUI = QLabel(self.centralwidget)
        self.VersionUI.setObjectName(u"Version")
        self.VersionUI.setGeometry(QRect(370, 150, 61, 21))
        self.VersionUI.setText("V." + version)
        VersionUI_sheet = """
        QLabel{
        color: #357ABD;
        }
    """
        self.VersionUI.setStyleSheet(VersionUI_sheet)
        self.VersionUI.setFont(QtGui.QFont('Arial', 8))

        self.HOTD = QtWidgets.QLabel(self.centralwidget)
        self.HOTD.setGeometry(QRect(17, 88, 181, 81))
        self.HOTD.setLayoutDirection(Qt.LeftToRight)
        self.HOTD.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.HOTD.setObjectName("HOTD")
        self.HOTD.setFont(QtGui.QFont('Arial', 8))
        
        self.CROSS = QtWidgets.QLabel(self.centralwidget)
        self.CROSS.setGeometry(QRect(381, 4, 15, 15))
        self.CROSS.setStyleSheet("image: url(:/Asset/croixx.png);")
        self.CROSS.setText("")
        self.CROSS.setObjectName("CROSS")
        self.CROSS.mousePressEvent = self.exit_clicked
        
        self.PARAM = QtWidgets.QLabel(self.centralwidget)
        self.PARAM.setGeometry(QRect(4, 4, 16, 16))
        self.PARAM.setStyleSheet("image: url(:/Asset/param.png);")
        self.PARAM.setText("")
        self.PARAM.setObjectName("PARAM")
        self.PARAM.mousePressEvent = self.param_click
         
        self.BG.raise_()
        self.pushButton.raise_()
        self.IMG_LED.raise_()
        self.STATUS.raise_()
        self.HOTD.raise_()
        self.CROSS.raise_()
        self.PARAM.raise_()
        self.VersionUI.raise_()
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        
        if not os.path.exists(KSHDIR):
            try:
                os.mkdir(KSHDIR)
            except:
                pass
        if not os.path.exists(KSHRPDIR):
            try:
                os.mkdir(KSHRPDIR)
            except:
                pass
        if not os.path.exists(KSHRPFile):
            self.save_to_ini(KSHRPFile, 'Config', 'ip', '0.0.0.0')
            self.check_comment()
        game_ip = self.read_value_from_ini('Config', 'ip')

    def param_click(self, event):
        self.param()
        
    def param(self):
        
        game_ip = self.read_value_from_ini('Config', 'ip')
        
        dialog = QDialog(self.MainWindow, Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        dialog.setWindowTitle("Configuration")
        app_icon = QtGui.QIcon()
        app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
        dialog.setWindowIcon(app_icon)
    
        layout = QVBoxLayout(dialog)
    
        self.label_ip = QLabel("Adresse IP du serveur:", dialog)
        self.label_ip.setFont(QtGui.QFont('Arial', 8))        
        self.ip_input = QtWidgets.QLineEdit(dialog)
        if game_ip == '0.0.0.0':
            self.ip_input.setPlaceholderText("Entrez l'IP du serveur")
            self.ip_input.setFont(QtGui.QFont('Arial', 8))
        else:
            self.ip_input.setPlaceholderText(game_ip)
        layout.addWidget(self.label_ip)
        layout.addWidget(self.ip_input)
    
        self.save_button = QtWidgets.QPushButton("Sauvegarder IP", dialog)
        self.save_button.setFont(QtGui.QFont('Arial', 8))
        # self.save_button.clicked.connect(self.save_ip)
        self.save_button.clicked.connect((lambda: self.save_ip(dialog)))
        layout.addWidget(self.save_button)
    
        button_layout = QHBoxLayout()
        self.disable_button = QtWidgets.QPushButton('Désactiver', dialog)
        self.disable_button.setFont(QtGui.QFont('Arial', 8))
        self.disable_button.clicked.connect(self.on_disable_button_click)
        button_layout.addWidget(self.disable_button)
    
        self.exe_button = QtWidgets.QPushButton('EXE du jeu', dialog)
        self.exe_button.setFont(QtGui.QFont('Arial', 8))
        self.exe_button.clicked.connect(self.on_exe_button_click)
        button_layout.addWidget(self.exe_button)
    
        layout.addLayout(button_layout)
        
        text_icon_layout = QHBoxLayout()
        
        # Texte centré
        self.info_label = QLabel("Do What The Fuck You Want to Public License", dialog)
        self.info_label.setFont(QtGui.QFont('Arial', 8))
        self.info_label.setAlignment(Qt.AlignCenter)
        text_icon_layout.addWidget(self.info_label)
    
        # Icône à droite du texte
        self.icon_label = QLabel(dialog)
        icon = QtGui.QPixmap(":/Asset/wtfpl.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(icon)
        text_icon_layout.addWidget(self.icon_label)
    
        # Centrer le layout horizontal dans le layout principal
        text_icon_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(text_icon_layout)
    
        dialog.setLayout(layout)
        dialog.exec_()
    
    def save_ip(self, dialog):
        ip = self.ip_input.text()
        if ip:
            self.save_to_ini(KSHRPFile, 'Config', 'ip', ip)
        dialog.accept()
    
    def on_disable_button_click(self):
        self.check_comment()
        self.show_info_desactive()

    def on_exe_button_click(self):
        loc = self.open_file_chooser()
        self.save_to_ini(KSHRPFile, 'Config', 'exec', loc)
        
            
    def read_value_from_ini(self, section, key, filename=KSHRPFile):
        config = configparser.ConfigParser()
        config.read(filename)
        if config.has_section(section) and config.has_option(section, key):
            value = config.get(section, key)
            return value
        else:
            return None

    def save_to_ini(self, ini_file, section, option, value):
        config = configparser.ConfigParser()
        try:
            config.read(ini_file)
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, option, value)
            with open(ini_file, 'w') as configfile:
                config.write(configfile)
            game_ip = value
            self.replace(game_ip)
        except Exception as e:
            pass    
        self.STATUS.setText("Status : Check en cours...")
        self.launch_internet_test_thread()
        # self.internet_test()
    
    def check_exec_key_ini(self):
        config = configparser.ConfigParser()
        config.read(KSHRPFile)
        if 'Config' in config and 'exec' in config['Config']:
            self.pushButton.setText("PLAY")
        else:
            self.pushButton.setText("CONFIG")
            
    def is_port_open(self, game_ip, port, timeout=5):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((game_ip, port))
        except (socket.timeout, socket.error) as e:
            return False
        finally:
            sock.close()
        return True

    def internet_connection(self):
        try:
            response = requests.get("https://www.google.com", timeout=5, verify=False)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.RequestException as e:
            return False

    def show_info_desactive(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle('Anyland-SAD')
        box.setFont(QtGui.QFont('Arial', 8))
        box.setText("La redirection DNS a été désactivé.")
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()
        
    def show_info_message(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Information)
        box.setWindowTitle('Anyland-EXE-Finder')
        box.setFont(QtGui.QFont('Arial', 8))
        box.setText("Veuillez choisir le .EXE d'Anyland :")
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()

    def show_info_message_deux(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Information)
        box.setWindowTitle('Anyland-Server-Finder')
        box.setFont(QtGui.QFont('Arial', 8))
        box.setText("Veuillez choisir entrer l'adresse du serveur :")
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()
        
    def open_file_chooser(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Executables (*.exe)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            return file_path
        else:
            return None
        
    def check_comment(self):
        if not os.path.exists(HOSTS_FILE_PATH):
            return
        with open(HOSTS_FILE_PATH, 'r') as file:
            lines = file.readlines()
        modified_lines = []
        inside_block = False
        for line in lines:
            if '####ANYLAND-DNS####' in line:
                inside_block = True
                continue
            if inside_block and '#### BY AXSYS #####' in line:
                inside_block = False
                continue
            if not inside_block:
                if any(address in line for address in TARGET_ADDRESSES) and not line.startswith("#"):
                    modified_lines.append(f"# {line}")
                else:
                    modified_lines.append(line)
        with open(HOSTS_FILE_PATH, 'w') as file:
            file.writelines(modified_lines)

    def replace(self, ip):
        if not os.path.exists(HOSTS_FILE_PATH):
            return
        pattern = re.compile(rf"{SECTION_START}.*?{SECTION_END}", re.DOTALL)
        with open(HOSTS_FILE_PATH, 'r') as file:
            content = file.read()
        content = re.sub(pattern, '', content).strip()
        new_entries = [f"{ip} {address}" for address in TARGET_ADDRESSES]
        new_section = f"{SECTION_START}\n" + "\n".join(new_entries) + f"\n{SECTION_END}"
        if content:
            content += f"\n{new_section}\n"
        else:
            content = f"{new_section}\n"
        with open(HOSTS_FILE_PATH, 'w') as file:
            file.write(content)
           
    def exit_clicked(self, event):
        sys.exit(0)
        
    def OnPlay(self,event):
        text = self.pushButton.text()
        if text == 'CONFIG':
            self.show_info_message()
            loc = self.open_file_chooser()
            if loc:
                self.save_to_ini(KSHRPFile, 'Config', 'exec', loc)
            self.show_info_message_deux()
            self.param()
        elif text == 'PLAY':
            game = self.read_value_from_ini('Config', 'exec')
            os.system('start "" "'+ game +'"')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - MainWindow.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_position') and event.buttons() == Qt.LeftButton:
            MainWindow.move(event.globalPos() - self.drag_position)
            event.accept()
    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_position'):
            del self.drag_position
            
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("MainWindow")
        self.pushButton.setText("Anyland")
        self.STATUS.setText("Status : ")
        self.HOTD.setText("Annonce :")

    def handle_update(self, message):
        self.STATUS.setText(message)
        
    def launch_internet_test_thread(self):
        self.STATUS.setText("Status : Check en cours...")
        self.internet_thread = InternetTestThread(self)
        self.internet_thread.update_status_signal.connect(self.handle_update)
        self.internet_thread.update_led_signal.connect(self.update_led)
        self.internet_thread.start()
        
    def update_led(self, color):
        if color == "vert":
            self.IMG_LED.setStyleSheet("image: url(:/Asset/led-v.png);")
        elif color == "orange":
            self.IMG_LED.setStyleSheet("image: url(:/Asset/led-o.png);")
        elif color == "rouge":
            self.IMG_LED.setStyleSheet("image: url(:/Asset/led-r.png);")

    def internettest(self, event):
        self.launch_internet_test_thread()

import ressources

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setStyle("Fusion")
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.launch_internet_test_thread()
    ui.check_exec_key_ini()
    sys.exit(app.exec_())
