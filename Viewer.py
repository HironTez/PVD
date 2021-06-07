import webbrowser

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QStyle, QPushButton
from PyQt5.QtGui import QIcon, QPalette, QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from videoprops import get_video_properties


class Viewer_window(QWidget):
    def __init__(self, slider, playBtn, controls_close, timer_label):
        super().__init__()

        # Control elements
        self.slider = slider
        self.playBtn = playBtn
        self.controls_close = controls_close
        self.timer_label = timer_label
        self.video_length = None
        self.window_size = 700
        self.dif_props = (1.4, 'width')

        # Setting window
        self.setWindowTitle("PVD Viewer")
        self.setGeometry(0, -1, 700, 500)
        self.setWindowIcon(QIcon('icons/viewer.png'))
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Window colors
        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        # Init media player
        self.init_video()

        # Show window
        self.show()

    def init_video(self):

        # Create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Create videowidget object
        self.videowidget = QVideoWidget()

        # Create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.videowidget)
        vboxLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vboxLayout)

        # Selecting a widget for displaying frames
        self.mediaPlayer.setVideoOutput(self.videowidget)

        # Media player signals
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def play_video(self):
        # Switch pause/play button
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        elif self.mediaPlayer.mediaStatus() == 8:
            print('unsupported media type')
            self.alert_window()
        else:
            self.mediaPlayer.play()
            

    def set_media(self, filename):
        self.get_props(filename)
        self.resize_window(self.window_size)
        self.timer_label.setText("0:00:00")

        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))

    def mediastate_changed(self, state):
        # Change icon for play/pause button
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    # Get window properties
    def get_props(self, filename):
        props = get_video_properties(filename)
        width = props['width']
        height = props['height']

        if width > height:
            dif = (width / height, 'width')
        elif width < height:
            dif = (height / width, 'height')
        elif width == height:
            dif = (1, 'none')
        
        self.dif_props = dif

    def resize_window(self, size):
        # Get current window position
        pos = (self.geometry().top(), self.geometry().left())
        args = (pos[1], pos[0])
        # Calculate new window dimensions
        if self.dif_props[1] == 'width':
            args += (size, round(size / self.dif_props[0]))
        elif self.dif_props[1] == 'height':
            args += (round(size / self.dif_props[0]), size)
        elif self.dif_props[1] == 'none':
            args += (size, size)

        # Set new parameters
        self.setGeometry(*args)

    # Video position has changed
    def position_changed(self, position):
        # If this is a photo
        if self.mediaPlayer.duration() == 0:
            # Pause media player
            self.mediaPlayer.pause()
            return

        # Move slider
        self.slider.setValue(position)

        time = int(position / 1000)
        hours, mins, seconds = self.to_time_format(time)
        # Change timer
        self.timer_label.setText(f"{hours}:{mins}:{seconds}")

    # Media duration changet
    def duration_changed(self, duration):
        # Set range for slider
        self.slider.setRange(0, duration)
        # Calculate duration in seconds
        if self.video_length == None:
            self.video_length = int(duration / 1000)

    # Slider was moved
    def set_position(self, position):
        # Move video
        self.mediaPlayer.setPosition(position)


    def resize_window_from_slider(self, position):
        self.resize_window(position + 200)
        self.window_size = position + 200


    def mousePressEvent(self, event):
        self.start_mouse_pos_x = event.pos().x()
        self.start_mouse_pos_y = event.pos().y()

    # Move window when mouse moved
    def mouseMoveEvent(self, event):
        mouse_pos_x = event.pos().x()
        mouse_pos_y = event.pos().y()
        window_pos_x = self.geometry().left()
        window_pos_y = self.geometry().top()
        new_position_x = window_pos_x + mouse_pos_x - self.start_mouse_pos_x
        new_position_y = window_pos_y + mouse_pos_y - self.start_mouse_pos_y
        self.setGeometry(new_position_x, new_position_y, self.geometry().width(),self.geometry().height())


    # Convert seconds to time format
    def to_time_format(self, seconds):
        hours = seconds // 3600
        seconds %= 3600
        mins = seconds // 60
        seconds %= 60

        if mins < 10:
            mins = '0' + str(mins)
        if seconds < 10:
            seconds = '0' + str(seconds)
        
        return str(hours), str(mins), str(seconds)


    def closeEvent(self, event):
        # Close control window
        self.controls_close()

    # Function for close this window
    def close_window(self):
        self.close()

    def alert_window(self):
        self.alert = QWidget()
        self.alert.setWindowTitle("Alert")

        # Window colors
        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.alert.setPalette(p)

        # Create text label
        self.alert.text = QLabel()
        self.alert.text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.alert.text.setText("Unsupported media type. Install the k-lite codec to support many types of media.")
        self.alert.text.setStyleSheet('color: white')

        # Create button
        installBtn = QPushButton('Install')
        installBtn.clicked.connect(lambda: webbrowser.open('https://codecguide.com/download_k-lite_codec_pack_basic.htm'))
        
        Layout = QVBoxLayout()
        Layout.addWidget(self.alert.text)
        Layout.addWidget(installBtn)
        self.alert.setLayout(Layout)

        self.alert.show()