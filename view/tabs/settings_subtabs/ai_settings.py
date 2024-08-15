from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QLabel, QPushButton, QComboBox, QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import pyqtSignal
import requests

class AISettingsTab(QWidget):
    model_changed = pyqtSignal(str)

    def __init__(self, image_processor):
        super().__init__()
        self.image_processor = image_processor
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # API connection group
        connection_group = QGroupBox("API Connection")
        connection_layout = QFormLayout()
        self.url_input = QLineEdit("http://localhost:11434")
        self.url_refresh_btn = QPushButton("Refresh")
        connection_layout.addRow("Base URL:", self.url_input)
        connection_layout.addRow("", self.url_refresh_btn)
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)

        # Model selection group
        model_group = QGroupBox("Model Selection")
        model_layout = QHBoxLayout()
        self.model_select = QComboBox()
        self.model_refresh_btn = QPushButton("Refresh")
        model_layout.addWidget(self.model_select)
        model_layout.addWidget(self.model_refresh_btn)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # API parameters group
        params_group = QGroupBox("API Parameters")
        params_layout = QFormLayout()
        self.api_params = {}
        for param, default in [
            ('generate_uri', "/api/generate"),
            ('prompt', "Is the woman's face completely visible, without any obstruction or covering, including hair? Answer 'yes' or 'no'."),
            ('temperature', "0.7"),
            ('max_tokens', "1000"),
            ('top_p', "1"),
            ('frequency_penalty', "0"),
            ('presence_penalty', "0")
        ]:
            self.api_params[param] = QLineEdit(default)
            params_layout.addRow(f"{param.capitalize()}:", self.api_params[param])
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Connect signals
        self.url_refresh_btn.clicked.connect(self.refresh_url)
        self.model_refresh_btn.clicked.connect(self.refresh_models)
        self.model_select.currentTextChanged.connect(self.on_model_changed)

        # Load initial model
        self.load_initial_model()

    def load_initial_model(self):
        try:
            response = requests.get(f"{self.url_input.text()}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.model_select.clear()
                clip_model = None
                for model in models:
                    self.model_select.addItem(model['name'])
                    if clip_model is None and 'clip' in model.get('details', {}).get('families', []):
                        clip_model = model['name']
                if clip_model:
                    self.model_select.setCurrentText(clip_model)
                    self.image_processor.set_model(clip_model)
                    self.update_status_bar(f"Running:🟢 | Ollama: 🟢 | Model: {clip_model}")
                else:
                    QMessageBox.warning(self, "Model Loading", "No CLIP-capable model found. Please pull a suitable model.")
            else:
                raise Exception(f"Server returned status code {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "Model Loading Error", f"Failed to load initial model: {str(e)}")
            self.update_status_bar(f"Running:🔴 | Ollama: 🔴 | Failed to connect to {self.url_input.text()}")

    def refresh_url(self):
        try:
            response = requests.get(self.url_input.text())
            if response.status_code == 200:
                self.refresh_models()
                self.update_status_bar(f"Running:🟢 | Ollama: 🟢 | Model: {self.model_select.currentText()}")
            else:
                raise Exception(f"Server returned status code {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "Connection Error", f"Failed to connect to the server: {str(e)}")
            self.update_status_bar(f"Running:🔴 | Ollama: 🔴 | Failed to connect to {self.url_input.text()}")

    def refresh_models(self):
        try:
            response = requests.get(f"{self.url_input.text()}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.model_select.clear()
                for model in models:
                    self.model_select.addItem(model['name'])
                self.update_status_bar(f"Running:🟢 | Ollama: 🟢 | Model: {self.model_select.currentText()}")
            else:
                raise Exception(f"Server returned status code {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "Model Refresh Error", f"Failed to refresh models: {str(e)}")
            self.update_status_bar(f"Running:🔴 | Ollama: 🔴 | Failed to connect to {self.url_input.text()}")

    def on_model_changed(self, model):
        self.image_processor.set_model(model)
        self.model_changed.emit(model)
        self.update_status_bar(f"Running:🟢 | Ollama: 🟢 | Model: {model}")

    def update_status_bar(self, message):
        main_window = self.window()
        if hasattr(main_window, 'status_bar'):
            main_window.status_bar.showMessage(message)

    def get_settings(self):
        return {
            'url': self.url_input.text(),
            'model': self.model_select.currentText(),
            'api_params': {param: widget.text() for param, widget in self.api_params.items()}
        }

    def load_settings(self, settings):
        self.url_input.setText(settings.get('url', 'http://localhost:11434'))
        self.model_select.setCurrentText(settings.get('model', ''))
        for param, value in settings.get('api_params', {}).items():
            if param in self.api_params:
                self.api_params[param].setText(str(value))