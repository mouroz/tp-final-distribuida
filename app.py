# -*- coding: utf-8 -*-
"""
Main entry point for the distributed messaging system.
Initializes the PyQt application and starts the server configuration window.
"""

import sys
import os

# Add src folder to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import QApplication
from ui import ServerConfigWindow


def main():
    """Main entry point - starts the PyQt application."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Messenger Distribuído")
    app.setOrganizationName("TP Final")
    
    # Apply dark theme style
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QLineEdit, QTextEdit, QListWidget {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid #4CAF50;
        }
        QPushButton {
            background-color: #555555;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #666666;
        }
        QLabel {
            color: #ffffff;
        }
        QFrame {
            background-color: #333333;
            border-radius: 5px;
            padding: 10px;
        }
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #444444;
        }
        QListWidget::item:selected {
            background-color: #4CAF50;
        }
    """)
    
    # Create and show the server config window
    config_window = ServerConfigWindow()
    config_window.show()
    
    # Run the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
