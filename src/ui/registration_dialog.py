"""Registration dialog for student accounts."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QSpacerItem, QSizePolicy,
    QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..models.user import UserRole


class RegistrationDialog(QDialog):
    """Dialog for student self-registration."""
    
    registration_successful = pyqtSignal(str)  # Emits username on successful registration
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Student Registration")
        self.setMinimumWidth(450)
        self.setMinimumHeight(500)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Create Student Account")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Info label
        info_label = QLabel("Fill in your details to create a student account")
        info_label.setFont(QFont("Arial", 9))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666;")
        layout.addWidget(info_label)
        
        # Form frame
        form_frame = QFrame()
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        row = 0
        
        # Username field
        username_label = QLabel("Username *:")
        username_label.setFont(QFont("Arial", 10))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a unique username")
        self.username_input.setMinimumHeight(32)
        form_layout.addWidget(username_label, row, 0)
        form_layout.addWidget(self.username_input, row, 1)
        row += 1
        
        # Password field
        password_label = QLabel("Password *:")
        password_label.setFont(QFont("Arial", 10))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimum 6 characters")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(32)
        form_layout.addWidget(password_label, row, 0)
        form_layout.addWidget(self.password_input, row, 1)
        row += 1
        
        # Confirm Password field
        confirm_password_label = QLabel("Confirm Password *:")
        confirm_password_label.setFont(QFont("Arial", 10))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-enter your password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(32)
        form_layout.addWidget(confirm_password_label, row, 0)
        form_layout.addWidget(self.confirm_password_input, row, 1)
        row += 1
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addWidget(separator, row, 0, 1, 2)
        row += 1
        
        # First Name field
        first_name_label = QLabel("First Name *:")
        first_name_label.setFont(QFont("Arial", 10))
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Your first name")
        self.first_name_input.setMinimumHeight(32)
        form_layout.addWidget(first_name_label, row, 0)
        form_layout.addWidget(self.first_name_input, row, 1)
        row += 1
        
        # Last Name field
        last_name_label = QLabel("Last Name *:")
        last_name_label.setFont(QFont("Arial", 10))
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Your last name")
        self.last_name_input.setMinimumHeight(32)
        form_layout.addWidget(last_name_label, row, 0)
        form_layout.addWidget(self.last_name_input, row, 1)
        row += 1
        
        # Email field
        email_label = QLabel("Email:")
        email_label.setFont(QFont("Arial", 10))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        self.email_input.setMinimumHeight(32)
        form_layout.addWidget(email_label, row, 0)
        form_layout.addWidget(self.email_input, row, 1)
        
        layout.addWidget(form_frame)
        
        # Required fields note
        required_label = QLabel("* Required fields")
        required_label.setFont(QFont("Arial", 8))
        required_label.setStyleSheet("color: #999; font-style: italic;")
        layout.addWidget(required_label)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        self.register_button = QPushButton("Create Account")
        self.register_button.setMinimumHeight(35)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        button_layout.addWidget(self.register_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect button signals to slots."""
        self.register_button.clicked.connect(self._attempt_registration)
        self.cancel_button.clicked.connect(self.reject)
    
    def _validate_input(self) -> tuple[bool, str]:
        """Validate all input fields."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        
        # Check required fields
        if not username:
            return False, "Username is required."
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long."
        
        if not password:
            return False, "Password is required."
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."
        
        if password != confirm_password:
            return False, "Passwords do not match."
        
        if not first_name:
            return False, "First name is required."
        
        if not last_name:
            return False, "Last name is required."
        
        # Validate email format if provided
        if email and '@' not in email:
            return False, "Please enter a valid email address."
        
        # Check if username already exists
        if self.db_manager.username_exists(username):
            return False, f"Username '{username}' is already taken."
        
        return True, ""
    
    def _attempt_registration(self):
        """Attempt to register the student."""
        # Validate input
        is_valid, error_message = self._validate_input()
        
        if not is_valid:
            QMessageBox.warning(self, "Registration Failed", error_message)
            return
        
        # Get input values
        username = self.username_input.text().strip()
        password = self.password_input.text()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip() or None
        
        try:
            # Create the student user
            user = self.db_manager.create_user(
                username=username,
                password=password,
                role=UserRole.STUDENT,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            self.registration_successful.emit(username)
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Registration Failed", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Registration Error", 
                f"An error occurred during registration:\n{str(e)}"
            )
