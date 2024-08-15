from PyQt5.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import os
from .tabs.main_tab import MainTab
from .tabs.ai_sandbox_tab import AISandboxTab
from .tabs.settings_tab import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self, image_processor):
        super().__init__()
        self.image_processor = image_processor
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Face Cropping and Captioning App")
        self.setGeometry(100, 100, 1200, 800)

        # Set icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')
        self.setWindowIcon(QIcon(icon_path))

        # Set font
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.settings_tab = SettingsTab(self.image_processor)
        self.main_tab = MainTab(self.image_processor, self.settings_tab)
        self.ai_sandbox_tab = AISandboxTab(self.image_processor)

        self.tab_widget.addTab(self.main_tab, "Process")
        self.tab_widget.addTab(self.ai_sandbox_tab, "AI Sandbox")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Initializing...")

        # Load initial model
        self.load_initial_model()

        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 8px 20px;
                margin: 2px;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QComboBox {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
    def load_initial_model(self):
            self.settings_tab.ai_settings.load_initial_model()
            model = self.settings_tab.ai_settings.model_select.currentText()
            self.status_bar.showMessage(f"Running:🟢 | Ollama: 🟢 | Model: {model}")