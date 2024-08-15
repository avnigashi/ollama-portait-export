import sys
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from model.image_processor import ImageProcessor

if __name__ == '__main__':
    app = QApplication(sys.argv)
    image_processor = ImageProcessor()
    main_window = MainWindow(image_processor)
    main_window.show()
    sys.exit(app.exec_())
