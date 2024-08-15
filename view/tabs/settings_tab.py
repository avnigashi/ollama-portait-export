from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QPushButton,
                             QHBoxLayout, QFileDialog, QMessageBox)
from .settings_subtabs.general_settings import GeneralSettingsTab
from .settings_subtabs.ai_settings import AISettingsTab
import json

class SettingsTab(QWidget):
    def __init__(self, image_processor):
        super().__init__()
        self.image_processor = image_processor
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Subtabs
        self.subtabs = QTabWidget()
        self.general_settings = GeneralSettingsTab(self.image_processor)
        self.ai_settings = AISettingsTab(self.image_processor)

        self.subtabs.addTab(self.general_settings, "General")
        self.subtabs.addTab(self.ai_settings, "AI")

        layout.addWidget(self.subtabs)

        # Import/Export buttons
        button_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import Settings")
        self.export_btn = QPushButton("Export Settings")
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.export_btn)
        layout.addLayout(button_layout)

        # Connect signals
        self.import_btn.clicked.connect(self.import_settings)
        self.export_btn.clicked.connect(self.export_settings)

    def import_settings(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Settings", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    settings = json.load(file)
                self.general_settings.load_settings(settings.get('general', {}))
                self.ai_settings.load_settings(settings.get('ai', {}))
                QMessageBox.information(self, "Settings Imported", "Settings have been successfully imported.")
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"An error occurred while importing settings: {str(e)}")

    def export_settings(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Settings", "", "JSON Files (*.json)")
        if file_name:
            settings = {
                'general': self.general_settings.get_settings(),
                'ai': self.ai_settings.get_settings()
            }
            try:
                with open(file_name, 'w') as file:
                    json.dump(settings, file, indent=4)
                QMessageBox.information(self, "Settings Exported", "Settings have been successfully exported.")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"An error occurred while exporting settings: {str(e)}")