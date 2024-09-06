import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSlider, QSpinBox, QLabel, QHBoxLayout, QColorDialog, QComboBox, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPainter, QPen, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer
import win32api
import win32con
import win32gui

class CrosshairWidget(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.size = settings.get('size', 10)
        self.gap = settings.get('gap', 5)
        self.shape = settings.get('shape', 'Cross')
        self.color = QColor(settings.get('color', '#FF0000'))
        
        # Initially set to (0, 0), positions will be updated after the widget is shown
        self.x_position = settings.get('x_position', 0)
        self.y_position = settings.get('y_position', 0)
        
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        
        # Ensure the crosshair is drawn in the correct position after the widget is shown
        QTimer.singleShot(0, self.center_crosshair)

        self.ensure_on_top_timer = QTimer()
        self.ensure_on_top_timer.timeout.connect(self.ensure_on_top)
        self.ensure_on_top_timer.start(10000)  # Ensure on top every second

    def center_crosshair(self):
        # Update x_position and y_position once the widget dimensions are available
        if self.x_position == 0:
            self.x_position = self.width() // 2
        if self.y_position == 0:
            self.y_position = self.height() // 2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.color, 2)
        painter.setPen(pen)
        gap_half = self.gap // 2
        size_half = self.size // 2

        if self.shape == 'Cross':
            # Horizontal line
            painter.drawLine(self.x_position - size_half, self.y_position, self.x_position - gap_half, self.y_position)
            painter.drawLine(self.x_position + gap_half, self.y_position, self.x_position + size_half, self.y_position)
            # Vertical line
            painter.drawLine(self.x_position, self.y_position - size_half, self.x_position, self.y_position - gap_half)
            painter.drawLine(self.x_position, self.y_position + gap_half, self.x_position, self.y_position + size_half)

    def update_color(self, color):
        self.color = color
        self.update()

    def update_size(self, size):
        self.size = size
        self.update()

    def update_gap(self, gap):
        self.gap = gap
        self.update()

    def update_shape(self, shape):
        self.shape = shape
        self.update()

    def update_position(self, x, y):
        self.x_position = x
        self.y_position = y
        self.update()

    def ensure_on_top(self):
        hwnd = self.winId()
        win32gui.SetWindowPos(int(hwnd), win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

class CustomizationWindow(QWidget):
    def __init__(self, crosshair_widget, settings):
        super().__init__()
        self.crosshair_widget = crosshair_widget
        self.settings = settings
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Position controls for X and Y
        pos_layout_x = QHBoxLayout()
        self.pos_label_x = QLabel('X Position:')
        pos_layout_x.addWidget(self.pos_label_x)
        self.pos_slider_x = QSlider(Qt.Horizontal)
        self.pos_slider_x.setRange(0, self.crosshair_widget.width())
        self.pos_slider_x.setValue(self.crosshair_widget.x_position)
        self.pos_slider_x.valueChanged.connect(self.update_x_position)
        pos_layout_x.addWidget(self.pos_slider_x)
        layout.addLayout(pos_layout_x)

        pos_layout_y = QHBoxLayout()
        self.pos_label_y = QLabel('Y Position:')
        pos_layout_y.addWidget(self.pos_label_y)
        self.pos_slider_y = QSlider(Qt.Horizontal)
        self.pos_slider_y.setRange(0, self.crosshair_widget.height())
        self.pos_slider_y.setValue(self.crosshair_widget.y_position)
        self.pos_slider_y.valueChanged.connect(self.update_y_position)
        pos_layout_y.addWidget(self.pos_slider_y)
        layout.addLayout(pos_layout_y)

        # Title
        self.setWindowTitle('Crosshair Customization')
        self.setWindowIcon(QIcon('icon.png'))  # Set a custom icon if available
        
        # Apply stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #FFF;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(255, 0, 0, 255), stop:1 rgba(0, 0, 255, 255));
                color: white;
                border: 2px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(255, 100, 100, 255), stop:1 rgba(100, 100, 255, 255));
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(255, 150, 150, 255), stop:1 rgba(150, 150, 255, 255));
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #555;
            }
            QSlider::handle:horizontal {
                background: #FF0000;
                width: 20px;
            }
            QLabel {
                padding: 5px;
            }
        """)

        # Color button
        self.color_button = QPushButton('Select Color')
        self.color_button.clicked.connect(self.select_color)
        layout.addWidget(self.color_button)

        # Size control using QSlider and QSpinBox
        size_layout = QHBoxLayout()
        self.size_label = QLabel('Size:')
        size_layout.addWidget(self.size_label)
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(self.crosshair_widget.size)
        self.size_slider.valueChanged.connect(self.update_size_from_slider)
        size_layout.addWidget(self.size_slider)
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 50)
        self.size_spinbox.setValue(self.crosshair_widget.size)
        self.size_spinbox.setFocusPolicy(Qt.StrongFocus)
        self.size_spinbox.valueChanged.connect(self.update_size_from_spinbox)
        size_layout.addWidget(self.size_spinbox)
        layout.addLayout(size_layout)

        # Gap size control using QSlider and QSpinBox
        gap_layout = QHBoxLayout()
        self.gap_label = QLabel('Gap Size:')
        gap_layout.addWidget(self.gap_label)
        self.gap_slider = QSlider(Qt.Horizontal)
        self.gap_slider.setRange(1, 20)
        self.gap_slider.setValue(self.crosshair_widget.gap)
        self.gap_slider.valueChanged.connect(self.update_gap_from_slider)
        gap_layout.addWidget(self.gap_slider)
        self.gap_spinbox = QSpinBox()
        self.gap_spinbox.setRange(1, 20)
        self.gap_spinbox.setValue(self.crosshair_widget.gap)
        self.gap_spinbox.setFocusPolicy(Qt.StrongFocus)
        self.gap_spinbox.valueChanged.connect(self.update_gap_from_spinbox)
        gap_layout.addWidget(self.gap_spinbox)
        layout.addLayout(gap_layout)

        # Shape control
        shape_layout = QHBoxLayout()
        self.shape_label = QLabel('Shape:')
        shape_layout.addWidget(self.shape_label)
        self.shape_combobox = QComboBox()
        self.shape_combobox.addItems(['Cross', 'Circle'])
        self.shape_combobox.setCurrentText(self.crosshair_widget.shape)
        self.shape_combobox.currentTextChanged.connect(self.update_shape)
        shape_layout.addWidget(self.shape_combobox)
        layout.addLayout(shape_layout)

        # Add some space at the bottom
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)
        
        # Set default size for the window
        self.resize(400, 300)  # Width: 400px, Height: 300px
        
        self.show()

    def update_x_position(self, x):
        self.crosshair_widget.update_position(x, self.crosshair_widget.y_position)
        self.settings['x_position'] = x

    def update_y_position(self, y):
        self.crosshair_widget.update_position(self.crosshair_widget.x_position, y)
        self.settings['y_position'] = y

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.crosshair_widget.update_color(color)
            self.settings['color'] = color.name()

    def update_size_from_slider(self, size):
        self.size_spinbox.setValue(size)  # Update spinbox when slider changes
        self.crosshair_widget.update_size(size)
        self.settings['size'] = size

    def update_size_from_spinbox(self, size):
        self.size_slider.setValue(size)  # Update slider when spinbox changes
        self.crosshair_widget.update_size(size)
        self.settings['size'] = size

    def update_gap_from_slider(self, gap):
        self.gap_spinbox.setValue(gap)  # Update spinbox when slider changes
        self.crosshair_widget.update_gap(gap)
        self.settings['gap'] = gap

    def update_gap_from_spinbox(self, gap):
        self.gap_slider.setValue(gap)  # Update slider when spinbox changes
        self.crosshair_widget.update_gap(gap)
        self.settings['gap'] = gap

    def update_shape(self, shape):
        self.crosshair_widget.update_shape(shape)
        self.settings['shape'] = shape

def load_settings():
    # Placeholder for actual settings loading logic
    return {
        'size': 10,
        'gap': 5,
        'shape': 'Cross',
        'color': '#FF0000',
        'x_position': 500,  # Example default x position
        'y_position': 500   # Example default y position
    }

def save_settings(settings):
    # Placeholder for actual settings saving logic
    print("Settings saved:", settings)

def main():
    app = QApplication(sys.argv)
    settings = load_settings()
    crosshair = CrosshairWidget(settings)
    customization_window = CustomizationWindow(crosshair, settings)
    
    app.exec_()
    save_settings(settings)

if __name__ == '__main__':
    main()






