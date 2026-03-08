"""Login dialog for the Student Information System."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..models.user import User


class LoginDialog(QDialog):
    """Dialog for user authentication."""
    
    login_successful = pyqtSignal(object)  # Emits User object on successful login
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.logged_in_user = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Student Information System - Login")
        self.setMinimumWidth(400)
        self.setMinimumHeight(350)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel("Student Information System")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Please sign in to continue")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        layout.addWidget(subtitle_label)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Form frame
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)
        
        # Username field
        username_label = QLabel("Username:")
        username_label.setFont(QFont("Arial", 10))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(35)
        self.username_input.returnPressed.connect(self._attempt_login)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 10))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.returnPressed.connect(self._attempt_login)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        layout.addWidget(form_frame)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        self.login_button = QPushButton("Sign In")
        self.login_button.setMinimumHeight(40)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        button_layout.addWidget(self.login_button)
        
        self.register_button = QPushButton("Register as Student")
        self.register_button.setMinimumHeight(35)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0078d4;
                border: 1px solid #0078d4;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f0f8ff;
            }
            QPushButton:pressed {
                background-color: #e6f2ff;
            }
        """)
        button_layout.addWidget(self.register_button)
        
        layout.addLayout(button_layout)
        
        # Default admin info hint
        hint_label = QLabel("Default admin: username 'admin', password 'admin123'")
        hint_label.setFont(QFont("Arial", 8))
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: #999; font-style: italic;")
        layout.addWidget(hint_label)
    
    def _connect_signals(self):
        """Connect button signals to slots."""
        self.login_button.clicked.connect(self._attempt_login)
        self.register_button.clicked.connect(self._open_registration)
    
    def _attempt_login(self):
        """Attempt to authenticate the user."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username:
            QMessageBox.warning(self, "Login Failed", "Please enter your username.")
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Login Failed", "Please enter your password.")
            self.password_input.setFocus()
            return
        
        # Authenticate
        user = self.db_manager.authenticate_user(username, password)
        
        if user:
            self.logged_in_user = user
            self.login_successful.emit(user)
            self.accept()
        else:
            QMessageBox.warning(
                self, 
                "Login Failed", 
                "Invalid username or password.\nPlease try again."
            )
            self.password_input.clear()
            self.password_input.setFocus()
    
    def _open_registration(self):
        """Open the registration dialog for students."""
        from .registration_dialog import RegistrationDialog
        
        dialog = RegistrationDialog(self.db_manager, self)
        dialog.registration_successful.connect(self._on_registration_success)
        dialog.exec()
    
    def _on_registration_success(self, username: str):
        """Handle successful registration by pre-filling username."""
        self.username_input.setText(username)
        self.password_input.setFocus()
        QMessageBox.information(
            self,
            "Registration Successful",
            f"Account created successfully!\nYou can now log in with username: {username}"
        )
