#!/usr/bin/env python3
"""
Student Information System - Main Entry Point

A desktop application for managing student information with role-based access control.
Built with Python, PyQt6, and SQLite.

Features:
- Three authorization levels: Administrator, Teacher, Student
- Student self-registration
- Teacher accounts created only by Administrators (with subject assignment)
- Class schedule management for teachers
- Students can view and select courses
- Secure password storage with PBKDF2
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.database.database_manager import DatabaseManager
from src.ui.login_dialog import LoginDialog
from src.ui.main_window import MainWindow
from src.utils.session_manager import SessionManager


class MainApp(QMainWindow):
    """
    Main application window with stacked widget for login and main content.
    This ensures logout does NOT close/reopen the application - it just
    switches views within the same window.
    """
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.main_page = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the main application UI."""
        self.setWindowTitle("Student Information System - Login")
        self.setMinimumSize(900, 600)
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Stacked widget to switch between login and main content
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Create login page
        self.login_page = None
        self._create_login_page()
        
        # Show login page initially
        self._show_login_page()
    
    def _create_login_page(self):
        """Create or recreate the login page widget."""
        # Remove old login page if exists
        if self.login_page is not None:
            self.stack.removeWidget(self.login_page)
            self.login_page.deleteLater()
            self.login_page = None
        
        # Create new login page
        self.login_page = QWidget()
        layout = QVBoxLayout(self.login_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create login dialog as embedded widget
        self.login_dialog = LoginDialog(self.db_manager, self)
        self.login_dialog.login_successful.connect(self._on_login_success)
        # Make it work as a widget, not a dialog
        self.login_dialog.setWindowFlags(Qt.WindowType.Widget)
        
        layout.addWidget(self.login_dialog)
        
        # Add to stack
        self.stack.addWidget(self.login_page)
    
    def _on_login_success(self, user):
        """Handle successful login."""
        # Set session
        SessionManager.set_current_user(user)
        
        # Create main page with user
        self._create_main_page(user)
        
        # Update window title
        self.setWindowTitle(f"Student Information System - {user.role.value}")
    
    def _create_main_page(self, user):
        """Create the main page after successful login."""
        # Clean up old main page if exists
        if self.main_page is not None:
            self.stack.removeWidget(self.main_page)
            self.main_page.deleteLater()
            self.main_page = None
        
        # Create new main page
        self.main_page = MainWindow(self.db_manager, self)
        self.main_page.set_user(user)
        self.main_page.logout_requested.connect(self._on_logout)
        
        # Add to stack and switch
        self.stack.addWidget(self.main_page)
        self.stack.setCurrentWidget(self.main_page)
    
    def _on_logout(self):
        """Handle logout - clear session and show login page."""
        # Clear session
        SessionManager.clear_session()
        
        # Show login page (this recreates the login widget fresh)
        self._show_login_page()
    
    def _show_login_page(self):
        """Show the login page (called on initial load and after logout)."""
        # Recreate login page to ensure fresh state
        self._create_login_page()
        
        # Switch to login page
        self.stack.setCurrentWidget(self.login_page)
        self.setWindowTitle("Student Information System - Login")
        
        # Clean up main page if exists
        if self.main_page is not None:
            self.stack.removeWidget(self.main_page)
            self.main_page.deleteLater()
            self.main_page = None


class StudentInformationSystem:
    """Main application class for the Student Information System."""
    
    def __init__(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.db_manager = None
        self.main_app = None
        
        self._setup_application()
    
    def _setup_application(self):
        """Set up application-wide settings."""
        # Set application style
        self.app.setStyle('Fusion')
        
        # Set default font
        font = QFont("Arial", 10)
        self.app.setFont(font)
        
        # Set application-wide stylesheet
        self.app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            QMenuBar::item:selected {
                background-color: #e9ecef;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QToolTip {
                background-color: #333;
                color: white;
                border: 1px solid #333;
                padding: 5px;
                border-radius: 3px;
            }
        """)
    
    def initialize_database(self):
        """Initialize the database connection."""
        # Use a data directory for the database
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        db_path = os.path.join(data_dir, 'student_info_system.db')
        self.db_manager = DatabaseManager(db_path)
    
    def run(self):
        """Run the application."""
        # Initialize database
        self.initialize_database()
        
        # Create main application window with stacked widget
        self.main_app = MainApp(self.db_manager)
        self.main_app.show()
        
        # Run the application event loop
        return self.app.exec()


def main():
    """Main entry point."""
    app = StudentInformationSystem()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
