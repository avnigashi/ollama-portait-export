from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFileDialog, QMessageBox, QTextEdit,
                             QGroupBox, QFormLayout)
import base64
import os

class AISandboxTab(QWidget):
    def __init__(self, image_processor):
        super().__init__()
        self.image_processor = image_processor
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Image selection group
        image_group = QGroupBox("Image Selection")
        image_layout = QHBoxLayout()
        self.image_path = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        image_layout.addWidget(self.image_path)
        image_layout.addWidget(self.browse_btn)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

        # AI options group
        options_group = QGroupBox("AI Options")
        options_layout = QFormLayout()
        self.prompt = QLineEdit("Describe the image.")
        self.temperature = QLineEdit("0.7")
        self.max_tokens = QLineEdit("1000")
        options_layout.addRow("Prompt:", self.prompt)
        options_layout.addRow("Temperature:", self.temperature)
        options_layout.addRow("Max Tokens:", self.max_tokens)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Submit button
        self.submit_btn = QPushButton("Submit to AI")
        layout.addWidget(self.submit_btn)

        # Response area
        response_group = QGroupBox("AI Response")
        response_layout = QVBoxLayout()
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        response_layout.addWidget(self.response_text)
        response_group.setLayout(response_layout)
        layout.addWidget(response_group)

        # Connect signals
        self.browse_btn.clicked.connect(self.browse_image)
        self.submit_btn.clicked.connect(self.submit_to_ai)

    def browse_image(self):
        image_file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.webp)")
        if image_file:
            self.image_path.setText(image_file)

    def submit_to_ai(self):
        image_path = self.image_path.text()
        if not os.path.isfile(image_path):
            QMessageBox.warning(self, "No Image", "Please upload an image.")
            return

        with open(image_path, "rb") as file:
            image_base64 = base64.b64encode(file.read()).decode('utf-8')

        response = self.image_processor.analyze_image_content(
            image_base64,
            self.prompt.text(),
            float(self.temperature.text()),
            int(self.max_tokens.text())
        )

        self.response_text.setText(f"AI Response: {response}")