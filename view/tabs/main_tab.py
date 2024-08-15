from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QCheckBox, QProgressBar, QFileDialog,
                             QMessageBox, QGroupBox, QFormLayout, QSpinBox, QInputDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt, QSettings
import os

class MainTab(QWidget):
    def __init__(self, image_processor, settings_tab):
        super().__init__()
        self.image_processor = image_processor
        self.settings_tab = settings_tab
        self.settings = QSettings("AvniGashi", "FaceCroppingApp")
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection group
        folder_group = QGroupBox("Input Folders")
        folder_layout = QVBoxLayout()
        self.folder_list = QListWidget()
        self.folder_list.itemDoubleClicked.connect(self.edit_folder)
        folder_layout.addWidget(self.folder_list)

        folder_btn_layout = QHBoxLayout()
        self.add_folder_btn = QPushButton("Add Folder")
        self.remove_folder_btn = QPushButton("Remove Folder")
        folder_btn_layout.addWidget(self.add_folder_btn)
        folder_btn_layout.addWidget(self.remove_folder_btn)
        folder_layout.addLayout(folder_btn_layout)
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)

        # Output directory selection
        output_group = QGroupBox("Output Directory")
        output_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        output_layout.addWidget(self.output_dir)
        output_layout.addWidget(self.browse_btn)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Filters group
        filters_group = QGroupBox("Filters")
        filters_layout = QFormLayout()
        self.min_width = QSpinBox()
        self.min_width.setRange(0, 10000)
        self.min_height = QSpinBox()
        self.min_height.setRange(0, 10000)
        self.ai_validation = QCheckBox()
        filters_layout.addRow("Minimum Width:", self.min_width)
        filters_layout.addRow("Minimum Height:", self.min_height)
        filters_layout.addRow("AI Validation:", self.ai_validation)
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)

        # Actions group
        actions_group = QGroupBox("Actions")
        actions_layout = QFormLayout()
        self.crop_faces = QCheckBox()
        self.generate_captions = QCheckBox()
        self.caption_limit = QSpinBox()
        self.caption_limit.setRange(0, 1000)
        actions_layout.addRow("Crop Faces:", self.crop_faces)
        actions_layout.addRow("Generate Captions:", self.generate_captions)
        actions_layout.addRow("Caption Limit:", self.caption_limit)
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # Process button, progress bar, and current image preview
        process_layout = QHBoxLayout()
        process_left_layout = QVBoxLayout()
        self.process_btn = QPushButton("Process Images")
        process_left_layout.addWidget(self.process_btn)
        self.progress_bar = QProgressBar()
        process_left_layout.addWidget(self.progress_bar)
        process_layout.addLayout(process_left_layout)

        # Current image preview
        preview_layout = QVBoxLayout()
        self.current_image_label = QLabel("Current Image:")
        preview_layout.addWidget(self.current_image_label)
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(150, 150)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border: 1px solid #cccccc;")
        preview_layout.addWidget(self.image_preview)
        process_layout.addLayout(preview_layout)

        layout.addLayout(process_layout)

        # Processed images table
        results_group = QGroupBox("Processing Results")
        results_layout = QVBoxLayout()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["File Name", "Result", "Cropped", "Preview", "AI Response"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Connect signals
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.remove_folder_btn.clicked.connect(self.remove_folder)
        self.browse_btn.clicked.connect(self.browse_output)
        self.process_btn.clicked.connect(self.start_processing)

    def load_settings(self):
        # Load folders
        folders = self.settings.value("folders", [], type=list)
        for folder in folders:
            item = QListWidgetItem(folder)
            self.update_folder_image_count(item)
            self.folder_list.addItem(item)

        # Load other settings
        self.output_dir.setText(self.settings.value("output_dir", "", type=str))
        self.min_width.setValue(self.settings.value("min_width", 0, type=int))
        self.min_height.setValue(self.settings.value("min_height", 0, type=int))
        self.ai_validation.setChecked(self.settings.value("ai_validation", False, type=bool))
        self.crop_faces.setChecked(self.settings.value("crop_faces", False, type=bool))
        self.generate_captions.setChecked(self.settings.value("generate_captions", False, type=bool))
        self.caption_limit.setValue(self.settings.value("caption_limit", 30, type=int))

    def save_settings(self):
        # Save folders
        folders = [self.folder_list.item(i).text().split(" (")[0] for i in range(self.folder_list.count())]
        self.settings.setValue("folders", folders)

        # Save other settings
        self.settings.setValue("output_dir", self.output_dir.text())
        self.settings.setValue("min_width", self.min_width.value())
        self.settings.setValue("min_height", self.min_height.value())
        self.settings.setValue("ai_validation", self.ai_validation.isChecked())
        self.settings.setValue("crop_faces", self.crop_faces.isChecked())
        self.settings.setValue("generate_captions", self.generate_captions.isChecked())
        self.settings.setValue("caption_limit", self.caption_limit.value())

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Process")
        if folder:
            if folder not in [self.folder_list.item(i).text().split(" (")[0] for i in range(self.folder_list.count())]:
                item = QListWidgetItem(folder)
                self.update_folder_image_count(item)
                self.folder_list.addItem(item)
                self.save_settings()
            else:
                QMessageBox.information(self, "Duplicate Folder", "This folder is already in the list.")

    def remove_folder(self):
        current_item = self.folder_list.currentItem()
        if current_item:
            self.folder_list.takeItem(self.folder_list.row(current_item))
            self.save_settings()
        else:
            QMessageBox.information(self, "No Selection", "Please select a folder to remove.")

    def edit_folder(self, item):
        text, ok = QInputDialog.getText(self, "Edit Folder Path", "Folder Path:", QLineEdit.Normal, item.text().split(" (")[0])
        if ok and text:
            item.setText(text)
            self.update_folder_image_count(item)
            self.save_settings()

    def update_folder_image_count(self, item):
        folder = item.text().split(" (")[0]
        if os.path.isdir(folder):
            image_count = len([f for f in os.listdir(folder) if f.lower().endswith(tuple(self.image_processor.allowed_file_types))])
            item.setText(f"{folder} ({image_count} images)")

    def browse_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.output_dir.setText(folder)
            self.save_settings()

    def start_processing(self):
        if not self.image_processor.is_running():
            folders = [self.folder_list.item(i).text().split(" (")[0] for i in range(self.folder_list.count())]
            if not folders:
                QMessageBox.warning(self, "No Folders", "Please add at least one folder to process.")
                return
            if not self.output_dir.text():
                QMessageBox.warning(self, "No Output Directory", "Please select an output directory.")
                return

            try:
                min_width = self.min_width.value()
                min_height = self.min_height.value()
                caption_limit = self.caption_limit.value() if self.generate_captions.isChecked() else None
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter valid integers for minimum width, height, and caption limit.")
                return

            self.results_table.setRowCount(0)  # Clear the table

            # Set API parameters and model
            api_params = self.settings_tab.ai_settings.get_settings()
            self.image_processor.set_api_params(api_params)
            self.image_processor.set_model(self.settings_tab.ai_settings.model_select.currentText())

            self.image_processor.set_parameters(
                folders,
                self.output_dir.text(),
                min_width,
                min_height,
                self.generate_captions.isChecked(),
                caption_limit,
                self.ai_validation.isChecked(),
                self.crop_faces.isChecked()
            )
            self.image_processor.progress_update.connect(self.update_progress)
            self.image_processor.status_update.connect(self.update_status)
            self.image_processor.image_processed.connect(self.update_image_list)
            self.image_processor.processing_finished.connect(self.show_summary)
            self.image_processor.current_image_update.connect(self.update_current_image)
            self.image_processor.start()
            self.process_btn.setText("Cancel Processing")

            # Save settings after starting processing
            self.save_settings()
        else:
            self.cancel_processing()

    def cancel_processing(self):
        if self.image_processor.is_running():
            reply = QMessageBox.question(self, 'Cancel Processing',
                                         "Are you sure you want to cancel the processing?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.image_processor.stop()
                self.update_status("Processing canceled!")
                self.process_btn.setText("Process Images")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)

    def update_image_list(self, image_name, success, reason, cropped, ai_response):
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        # File Name
        self.results_table.setItem(row, 0, QTableWidgetItem(image_name))

        # Result
        result_item = QTableWidgetItem("Yes" if success else "No")
        result_item.setBackground(QColor(200, 255, 200) if success else QColor(255, 200, 200))
        self.results_table.setItem(row, 1, result_item)

        # Cropped
        self.results_table.setItem(row, 2, QTableWidgetItem("Yes" if cropped else "No"))

        # Preview
        preview_label = QLabel()
        preview_pixmap = QPixmap(os.path.join(self.output_dir.text(), image_name))
        if not preview_pixmap.isNull():
            preview_pixmap = preview_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            preview_label.setPixmap(preview_pixmap)
        else:
            preview_label.setText("No preview")
        self.results_table.setCellWidget(row, 3, preview_label)

        # AI Response
        self.results_table.setItem(row, 4, QTableWidgetItem(ai_response))

    def update_current_image(self, image_path):
        # Update the current image label
        self.current_image_label.setText(f"Current Image: {os.path.basename(image_path)}")

        # Load and display the image preview
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview.setPixmap(pixmap)
        else:
            self.image_preview.setText("Unable to load image")

    def show_summary(self, stats):
        summary = f"""
        Processing Summary:
        Total Images: {stats['total_images']}
        Faces Found: {stats['faces_found']}
        No Faces Detected: {stats['no_faces']}
        Small Images Skipped: {stats['small_images']}
        Failed AI Validation: {stats['failed_validation']}
        Successfully Processed: {stats['processed_successfully']}
        """
        self.status_label.setText(summary)
        QMessageBox.information(self, "Processing Complete", summary)
        self.process_btn.setText("Process Images")