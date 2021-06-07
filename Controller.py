import sys
import os
import threading

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QStyle, QSizePolicy, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette, QMouseEvent, QKeyEvent
from PyQt5.QtCore import Qt, QUrl
import ctypes
from pynput.keyboard import Listener, Key

from Viewer import Viewer_window


user32 = ctypes.windll.user32
this_folder = os.path.dirname(os.path.abspath(__file__))

class Controller_window(QWidget):
    def __init__(self):
        super().__init__()

        # Setting window
        self.setWindowTitle("PVD Controller")
        self.setGeometry(750, 100, 700, 100)
        self.setWindowIcon(QIcon('icons/controller.png'))

        # Window colors
        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        # Init winodow functions
        self.init_ui()
        threading.Thread(target=self.init_keyboard_listener).start()

        # Show window
        self.show()

    def init_ui(self):
        # Create button for playing
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setFocusPolicy(Qt.NoFocus)

        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)

        # Create timer label
        self.timer_label = QLabel()
        self.timer_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.timer_label.setText("0:00:00")
        self.timer_label.setStyleSheet('color: white')

        # Create viewer object
        global viewer
        viewer = Viewer_window(self.slider, self.playBtn, self.close, self.timer_label)

        # Function for slider
        self.slider.sliderMoved.connect(viewer.set_position)

        # Function for playBtn
        self.playBtn.clicked.connect(viewer.play_video)

        # Create open button
        openBtn = QPushButton('Open Media')
        openBtn.clicked.connect(self.open_file)
        openBtn.setFocusPolicy(Qt.NoFocus)

        # Create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        # Create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.timer_label)
        self.setLayout(vboxLayout)

        # Create size slider
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(0, user32.GetSystemMetrics(1) - 200)
        self.size_slider.sliderMoved.connect(viewer.resize_window_from_slider)
        self.size_slider.setValue(500)

        # Set widgets to the hbox layout
        hboxLayout.addWidget(openBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(self.slider)
        hboxLayout.addWidget(self.size_slider)

    def init_keyboard_listener(self):
        # Setup the listener
        with Listener(on_press=self.keyboard_on_press) as listener:
            self.listener = listener
            # Join the thread to the main thread
            listener.join()

    def keyboard_on_press(self, key):
        # Function for space button
        if key == Key.space:
            viewer.play_video()


    # Open and init media
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", os.path.join(this_folder, "media\\"), "Media Files(*mp4 *MOV *WMV *FLV *AVI *AVCHD *WebM *MKV *gif *png *jpg *jpeg *tif *tiff *jfif *bmp *eps *raw *cr2 *nef *orf *sr2)")

        if filename != '':
            # Init media
            viewer.set_media(filename)
            # Enable play button
            self.playBtn.setEnabled(True)


    def closeEvent(self, event):
        # Stop keyboard listener
        self.listener.stop()
        # Close viewer window
        viewer.close_window()


app = QApplication(sys.argv)
Controller_window()
sys.exit(app.exec_())