from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QGroupBox, QFormLayout

class GeneralSettingsTab(QWidget):
    def __init__(self, image_processor):
        super().__init__()
        self.image_processor = image_processor
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # File types group
        file_types_group = QGroupBox("Allowed File Types")
        file_types_layout = QFormLayout()
        self.allowed_file_types = QLineEdit(".png, .jpg, .jpeg, .webp")
        file_types_layout.addRow("File Extensions:", self.allowed_file_types)
        file_types_group.setLayout(file_types_layout)
        layout.addWidget(file_types_group)
        # Add other general settings here

    def load_settings(self, settings):
        self.allowed_file_types.setText(', '.join(settings.get('allowed_file_types', ['.png', '.jpg', '.jpeg', '.webp'])))
        # Load other general settings here

    def get_settings(self):
        return {
            'allowed_file_types': [ft.strip() for ft in self.allowed_file_types.text().split(',')]
            # Add other general settings here
        }
