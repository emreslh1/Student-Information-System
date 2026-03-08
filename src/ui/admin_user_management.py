"""Admin panel for managing user accounts, especially teacher accounts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QSpacerItem, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialog, QGridLayout, QAbstractItemView, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ..models.user import User, UserRole, Subject


class AddUserDialog(QDialog):
    """Dialog for adding new users (admin only for teachers)."""
    
    user_created = pyqtSignal(object)  # Emits User object
    
    def __init__(self, db_manager, role: UserRole, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.target_role = role
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        role_name = self.target_role.value
        self.setWindowTitle(f"Add {role_name} Account")
        self.setMinimumWidth(450)
        self.setMinimumHeight(480)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title_label = QLabel(f"Create New {role_name} Account")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Form
        form_frame = QFrame()
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(10)
        
        row = 0
        
        # Username
        username_label = QLabel("Username *:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Unique username")
        self.username_input.setMinimumHeight(30)
        form_layout.addWidget(username_label, row, 0)
        form_layout.addWidget(self.username_input, row, 1)
        row += 1
        
        # Password
        password_label = QLabel("Password *:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimum 6 characters")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(30)
        form_layout.addWidget(password_label, row, 0)
        form_layout.addWidget(self.password_input, row, 1)
        row += 1
        
        # Confirm Password
        confirm_label = QLabel("Confirm Password *:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-enter password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(30)
        form_layout.addWidget(confirm_label, row, 0)
        form_layout.addWidget(self.confirm_password_input, row, 1)
        row += 1
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        form_layout.addWidget(separator, row, 0, 1, 2)
        row += 1
        
        # Subject (for teachers only)
        if self.target_role == UserRole.TEACHER:
            subject_label = QLabel("Subject *:")
            self.subject_combo = QComboBox()
            self.subject_combo.setMinimumHeight(30)
            self.subject_combo.addItem("-- Select Subject --", None)
            for subject in Subject.all_subjects():
                self.subject_combo.addItem(subject.value, subject)
            form_layout.addWidget(subject_label, row, 0)
            form_layout.addWidget(self.subject_combo, row, 1)
            row += 1
        
        # First Name
        first_name_label = QLabel("First Name *:")
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("First name")
        self.first_name_input.setMinimumHeight(30)
        form_layout.addWidget(first_name_label, row, 0)
        form_layout.addWidget(self.first_name_input, row, 1)
        row += 1
        
        # Last Name
        last_name_label = QLabel("Last Name *:")
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Last name")
        self.last_name_input.setMinimumHeight(30)
        form_layout.addWidget(last_name_label, row, 0)
        form_layout.addWidget(self.last_name_input, row, 1)
        row += 1
        
        # Email
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        self.email_input.setMinimumHeight(30)
        form_layout.addWidget(email_label, row, 0)
        form_layout.addWidget(self.email_input, row, 1)
        
        layout.addWidget(form_frame)
        
        # Required note
        required_label = QLabel("* Required fields")
        required_label.setStyleSheet("color: #999; font-style: italic; font-size: 9px;")
        layout.addWidget(required_label)
        
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(32)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        self.create_button = QPushButton(f"Create {role_name}")
        self.create_button.setMinimumHeight(32)
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals."""
        self.create_button.clicked.connect(self._create_user)
        self.cancel_button.clicked.connect(self.reject)
    
    def _validate(self) -> tuple[bool, str]:
        """Validate input fields."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters."
        
        if self.db_manager.username_exists(username):
            return False, f"Username '{username}' already exists."
        
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters."
        
        if password != confirm:
            return False, "Passwords do not match."
        
        # Validate subject for teachers
        if self.target_role == UserRole.TEACHER:
            subject = self.subject_combo.currentData()
            if subject is None:
                return False, "Please select a subject for the teacher."
        
        if not first_name:
            return False, "First name is required."
        
        if not last_name:
            return False, "Last name is required."
        
        if email and '@' not in email:
            return False, "Invalid email address."
        
        return True, ""
    
    def _create_user(self):
        """Create the user account."""
        is_valid, error = self._validate()
        
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error)
            return
        
        try:
            # Get subject for teachers
            subject = None
            if self.target_role == UserRole.TEACHER:
                subject = self.subject_combo.currentData()
            
            user = self.db_manager.create_user(
                username=self.username_input.text().strip(),
                password=self.password_input.text(),
                role=self.target_role,
                email=self.email_input.text().strip() or None,
                first_name=self.first_name_input.text().strip(),
                last_name=self.last_name_input.text().strip(),
                subject=subject
            )
            
            self.user_created.emit(user)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create user: {str(e)}")


class AdminUserManagementWidget(QWidget):
    """Widget for administrators to manage user accounts."""
    
    users_changed = pyqtSignal()
    
    def __init__(self, db_manager, current_user: User, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_user = current_user
        
        self._setup_ui()
        self._connect_signals()
        self._load_users()
    
    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("User Management")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Filter and actions bar
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Filter by Role:")
        self.role_filter = QComboBox()
        self.role_filter.addItem("All Users", None)
        self.role_filter.addItem("Administrators", UserRole.ADMINISTRATOR)
        self.role_filter.addItem("Teachers", UserRole.TEACHER)
        self.role_filter.addItem("Students", UserRole.STUDENT)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.role_filter)
        
        filter_layout.addStretch()
        
        # Add Teacher button (only admin can add teachers)
        self.add_teacher_button = QPushButton("Add Teacher")
        self.add_teacher_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        filter_layout.addWidget(self.add_teacher_button)
        
        # Add Admin button
        self.add_admin_button = QPushButton("Add Administrator")
        self.add_admin_button.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        filter_layout.addWidget(self.add_admin_button)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        filter_layout.addWidget(self.refresh_button)
        
        layout.addLayout(filter_layout)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(8)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Username", "Role", "Subject", "Name", "Email", "Status", "Actions"
        ])
        
        # Set column widths
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.users_table)
        
        # Info label
        info_label = QLabel("Note: Teacher accounts can only be created by Administrators. Students can self-register.")
        info_label.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        layout.addWidget(info_label)
    
    def _connect_signals(self):
        """Connect signals."""
        self.role_filter.currentIndexChanged.connect(self._load_users)
        self.add_teacher_button.clicked.connect(self._add_teacher)
        self.add_admin_button.clicked.connect(self._add_admin)
        self.refresh_button.clicked.connect(self._load_users)
    
    def _load_users(self):
        """Load users into the table."""
        filter_role = self.role_filter.currentData()
        
        if filter_role:
            users = self.db_manager.get_users_by_role(filter_role)
        else:
            users = self.db_manager.get_all_users()
        
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            # ID
            id_item = QTableWidgetItem(str(user.id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.users_table.setItem(row, 0, id_item)
            
            # Username
            self.users_table.setItem(row, 1, QTableWidgetItem(user.username))
            
            # Role
            role_item = QTableWidgetItem(user.role.value)
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if user.role == UserRole.ADMINISTRATOR:
                role_item.setBackground(QColor("#e6f2ff"))
            elif user.role == UserRole.TEACHER:
                role_item.setBackground(QColor("#fff3e6"))
            else:
                role_item.setBackground(QColor("#e6ffe6"))
            self.users_table.setItem(row, 2, role_item)
            
            # Subject
            subject_text = user.get_subject_name() if user.role == UserRole.TEACHER else "-"
            self.users_table.setItem(row, 3, QTableWidgetItem(subject_text))
            
            # Name
            self.users_table.setItem(row, 4, QTableWidgetItem(user.full_name()))
            
            # Email
            self.users_table.setItem(row, 5, QTableWidgetItem(user.email or "-"))
            
            # Status
            status_item = QTableWidgetItem("Active" if user.is_active else "Inactive")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if not user.is_active:
                status_item.setForeground(QColor("#dc3545"))
            self.users_table.setItem(row, 6, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)
            
            # Toggle active/inactive button
            toggle_btn = QPushButton()
            if user.is_active:
                toggle_btn.setText("Deactivate")
                toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffc107;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #e0a800;
                    }
                """)
            else:
                toggle_btn.setText("Activate")
                toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """)
            toggle_btn.clicked.connect(lambda checked, u=user: self._toggle_user_status(u))
            actions_layout.addWidget(toggle_btn)
            
            # Delete button (can't delete self)
            if user.id != self.current_user.id:
                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, u=user: self._delete_user(u))
                actions_layout.addWidget(delete_btn)
            
            # Reset password button
            reset_btn = QPushButton("Reset PW")
            reset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            reset_btn.clicked.connect(lambda checked, u=user: self._reset_password(u))
            actions_layout.addWidget(reset_btn)
            
            self.users_table.setCellWidget(row, 7, actions_widget)
    
    def _add_teacher(self):
        """Open dialog to add a teacher."""
        dialog = AddUserDialog(self.db_manager, UserRole.TEACHER, self)
        dialog.user_created.connect(self._on_user_created)
        dialog.exec()
    
    def _add_admin(self):
        """Open dialog to add an administrator."""
        dialog = AddUserDialog(self.db_manager, UserRole.ADMINISTRATOR, self)
        dialog.user_created.connect(self._on_user_created)
        dialog.exec()
    
    def _on_user_created(self, user: User):
        """Handle user creation."""
        self._load_users()
        self.users_changed.emit()
        QMessageBox.information(
            self,
            "User Created",
            f"{user.role.value} account '{user.username}' created successfully!"
        )
    
    def _toggle_user_status(self, user: User):
        """Toggle user active/inactive status."""
        if user.id == self.current_user.id:
            QMessageBox.warning(self, "Error", "Cannot deactivate your own account.")
            return
        
        action = "deactivate" if user.is_active else "activate"
        reply = QMessageBox.question(
            self,
            f"Confirm {action.capitalize()}",
            f"Are you sure you want to {action} user '{user.username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if user.is_active:
                self.db_manager.deactivate_user(user.id)
            else:
                self.db_manager.activate_user(user.id)
            
            self._load_users()
            self.users_changed.emit()
    
    def _delete_user(self, user: User):
        """Delete a user."""
        if user.id == self.current_user.id:
            QMessageBox.warning(self, "Error", "Cannot delete your own account.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to permanently delete user '{user.username}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_user(user.id)
            self._load_users()
            self.users_changed.emit()
            QMessageBox.information(self, "Deleted", f"User '{user.username}' has been deleted.")
    
    def _reset_password(self, user: User):
        """Reset a user's password."""
        from PyQt6.QtWidgets import QInputDialog
        new_password, ok = QInputDialog.getText(
            self,
            "Reset Password",
            f"Enter new password for '{user.username}':",
            QLineEdit.EchoMode.Password
        )
        
        if ok and new_password:
            if len(new_password) < 6:
                QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
                return
            
            self.db_manager.update_user_password(user.id, new_password)
            QMessageBox.information(
                self,
                "Password Reset",
                f"Password for '{user.username}' has been reset successfully."
            )
