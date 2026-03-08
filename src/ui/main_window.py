"""Main application window for the Student Information System."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QSpacerItem, QSizePolicy,
    QMessageBox, QMenuBar, QMenu, QToolBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction

from ..models.user import User, UserRole
from .admin_user_management import AdminUserManagementWidget
from .teacher_schedule_panel import TeacherScheduleWidget
from .student_schedule_panel import StudentScheduleWidget


class DashboardWidget(QWidget):
    """Dashboard widget showing user-specific information."""
    
    def __init__(self, user: User, db_manager, parent=None):
        super().__init__(parent)
        self.user = user
        self.db_manager = db_manager
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome message
        welcome_label = QLabel(f"Welcome, {self.user.full_name()}!")
        welcome_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(welcome_label)
        
        # Role badge
        role_frame = QFrame()
        role_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self._get_role_color()};
                border-radius: 4px;
                padding: 5px 10px;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
            }}
        """)
        role_layout = QHBoxLayout(role_frame)
        role_layout.setContentsMargins(10, 5, 10, 5)
        role_label = QLabel(self.user.role.value)
        role_layout.addWidget(role_label)
        role_layout.addStretch()
        layout.addWidget(role_frame)
        
        # User info section
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(20, 20, 20, 20)
        
        info_title = QLabel("Account Information")
        info_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        info_layout.addWidget(info_title)
        
        # User details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(5)
        
        self._add_info_row(details_layout, "Username:", self.user.username)
        self._add_info_row(details_layout, "Email:", self.user.email or "Not provided")
        
        # Add subject for teachers
        if self.user.is_teacher() and self.user.subject:
            self._add_info_row(details_layout, "Subject:", self.user.subject.value)
        
        self._add_info_row(details_layout, "Account Created:", 
                          self.user.created_at.strftime("%Y-%m-%d %H:%M") if self.user.created_at else "N/A")
        
        info_layout.addLayout(details_layout)
        layout.addWidget(info_frame)
        
        # Role-specific information
        layout.addWidget(self._create_role_specific_widget())
        
        layout.addStretch()
    
    def _get_role_color(self) -> str:
        """Get the color associated with the user's role."""
        colors = {
            UserRole.ADMINISTRATOR: "#6f42c1",
            UserRole.TEACHER: "#fd7e14",
            UserRole.STUDENT: "#28a745"
        }
        return colors.get(self.user.role, "#6c757d")
    
    def _add_info_row(self, layout: QVBoxLayout, label: str, value: str):
        """Add a label-value row to the layout."""
        row_layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Arial", 10))
        label_widget.setStyleSheet("color: #666;")
        label_widget.setMinimumWidth(120)
        
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        row_layout.addWidget(label_widget)
        row_layout.addWidget(value_widget)
        row_layout.addStretch()
        
        layout.addLayout(row_layout)
    
    def _create_role_specific_widget(self) -> QFrame:
        """Create role-specific information widget."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #e7f3ff;
                border: 1px solid #b8daff;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        if self.user.is_admin():
            title = QLabel("Administrator Privileges")
            title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            layout.addWidget(title)
            
            privileges = [
                "• Create and manage Teacher accounts (with subject assignment)",
                "• Create and manage Administrator accounts",
                "• View, edit, activate/deactivate, and delete all user accounts",
                "• Reset passwords for any user",
                "• Full access to all system features"
            ]
        elif self.user.is_teacher():
            title = QLabel("Teacher Privileges")
            title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            layout.addWidget(title)
            
            subject_text = self.user.subject.value if self.user.subject else "Not assigned"
            privileges = [
                f"• Subject: {subject_text}",
                "• Manage your class schedule",
                "• Add classes for your assigned subject only",
                "• View student information",
                "• Grade student work"
            ]
        else:  # Student
            title = QLabel("Student Access")
            title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            layout.addWidget(title)
            
            privileges = [
                "• View your personal information",
                "• Browse and select available courses",
                "• Add courses to your schedule",
                "• View your enrolled courses",
                "• Remove courses from your schedule"
            ]
        
        for privilege in privileges:
            label = QLabel(privilege)
            label.setFont(QFont("Arial", 10))
            layout.addWidget(label)
        
        return frame


class MainWindow(QMainWindow):
    """Main application window."""
    
    logout_requested = pyqtSignal()
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = None
        
        # Track widgets that need cleanup on logout
        self.sidebar = None
        self.content_area = None
        
        self._setup_ui()
        
    def set_user(self, user: User):
        """Set the current user and rebuild the UI."""
        self.user = user
        self._clear_ui()
        self._setup_logged_in_ui()
        self._create_menus()
        
    def _clear_ui(self):
        """Clear the current UI for logout/login transition."""
        # Remove old central widget if exists
        old_central = self.centralWidget()
        if old_central:
            old_central.deleteLater()
        
        # Clear menu bar
        self.menuBar().clear()
        
    def _setup_ui(self):
        """Set up the initial UI (empty or login redirect)."""
        self.setWindowTitle("Student Information System")
        self.setMinimumSize(900, 600)
        
    def _setup_logged_in_ui(self):
        """Set up the UI when a user is logged in."""
        if not self.user:
            return
            
        self.setWindowTitle(f"Student Information System - {self.user.role.value}")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #ffffff;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_widget, 1)
        
        # Add widgets to stack
        self._add_stacked_widgets()
        
        # Set default view
        self.stacked_widget.setCurrentIndex(0)
    

    
    def _create_sidebar(self) -> QWidget:
        """Create the navigation sidebar."""
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
            }
            QPushButton {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                text-align: left;
                padding: 12px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # App title
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #1a252f; padding: 15px;")
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("SIS")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Student Information\nSystem")
        subtitle_label.setStyleSheet("color: #bdc3c7; font-size: 10px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_frame)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Dashboard (available to all)
        dashboard_btn = QPushButton("📊  Dashboard")
        dashboard_btn.setCheckable(True)
        dashboard_btn.setChecked(True)
        dashboard_btn.clicked.connect(lambda: self._switch_view(0))
        layout.addWidget(dashboard_btn)
        self.nav_buttons.append(dashboard_btn)
        
        # Role-specific panels
        if self.user.is_admin():
            # User Management (admin only)
            user_mgmt_btn = QPushButton("👥  User Management")
            user_mgmt_btn.setCheckable(True)
            user_mgmt_btn.clicked.connect(lambda: self._switch_view(1))
            layout.addWidget(user_mgmt_btn)
            self.nav_buttons.append(user_mgmt_btn)
        elif self.user.is_teacher():
            # Class Schedule (teacher only)
            schedule_btn = QPushButton("📅  My Schedule")
            schedule_btn.setCheckable(True)
            schedule_btn.clicked.connect(lambda: self._switch_view(1))
            layout.addWidget(schedule_btn)
            self.nav_buttons.append(schedule_btn)
        else:
            # Class Schedule (student view - course selection)
            schedule_btn = QPushButton("📚  Course Selection")
            schedule_btn.setCheckable(True)
            schedule_btn.clicked.connect(lambda: self._switch_view(1))
            layout.addWidget(schedule_btn)
            self.nav_buttons.append(schedule_btn)
        
        # Spacer
        layout.addStretch()
        
        # User info at bottom
        user_frame = QFrame()
        user_frame.setStyleSheet("background-color: #1a252f; padding: 10px;")
        user_layout = QVBoxLayout(user_frame)
        
        user_label = QLabel(self.user.username)
        user_label.setStyleSheet("color: white; font-weight: bold;")
        user_layout.addWidget(user_label)
        
        role_label = QLabel(self.user.role.value)
        role_label.setStyleSheet("color: #3498db; font-size: 11px;")
        user_layout.addWidget(role_label)
        
        # Show subject for teachers
        if self.user.is_teacher() and self.user.subject:
            subject_label = QLabel(self.user.subject.value)
            subject_label.setStyleSheet("color: #fd7e14; font-size: 10px;")
            user_layout.addWidget(subject_label)
        
        layout.addWidget(user_frame)
        
        # Logout button
        logout_btn = QPushButton("🚪  Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border-radius: 0;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self._logout)
        layout.addWidget(logout_btn)
        
        return sidebar
    
    def _add_stacked_widgets(self):
        """Add widgets to the stacked widget."""
        # Dashboard
        self.dashboard_widget = DashboardWidget(self.user, self.db_manager)
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        # Role-specific widgets
        if self.user.is_admin():
            self.user_management_widget = AdminUserManagementWidget(
                self.db_manager, self.user
            )
            self.stacked_widget.addWidget(self.user_management_widget)
        elif self.user.is_teacher():
            self.schedule_widget = TeacherScheduleWidget(
                self.db_manager, self.user
            )
            self.stacked_widget.addWidget(self.schedule_widget)
        else:
            # Student schedule view
            self.schedule_widget = StudentScheduleWidget(
                self.db_manager, self.user
            )
            self.stacked_widget.addWidget(self.schedule_widget)
    
    def _create_menus(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        logout_action = QAction("Logout", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self._logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.setShortcut("Ctrl+D")
        dashboard_action.triggered.connect(lambda: self._switch_view(0))
        view_menu.addAction(dashboard_action)
        
        if self.user.is_admin():
            user_mgmt_action = QAction("User Management", self)
            user_mgmt_action.setShortcut("Ctrl+U")
            user_mgmt_action.triggered.connect(lambda: self._switch_view(1))
            view_menu.addAction(user_mgmt_action)
        elif self.user.is_teacher():
            schedule_action = QAction("My Schedule", self)
            schedule_action.setShortcut("Ctrl+S")
            schedule_action.triggered.connect(lambda: self._switch_view(1))
            view_menu.addAction(schedule_action)
        else:
            # Student schedule view
            schedule_action = QAction("Course Selection", self)
            schedule_action.setShortcut("Ctrl+S")
            schedule_action.triggered.connect(lambda: self._switch_view(1))
            view_menu.addAction(schedule_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """Connect signals."""
        pass
    
    def _switch_view(self, index: int):
        """Switch to a different view."""
        self.stacked_widget.setCurrentIndex(index)
        
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
    
    def _logout(self):
        """Handle logout request - emit signal to main app."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emit signal - main.py will handle the transition
            self.logout_requested.emit()
    
    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Student Information System",
            """<h3>Student Information System</h3>
            <p>Version 1.0.0</p>
            <p>A desktop application for managing student information.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Role-based access control (Administrator, Teacher, Student)</li>
                <li>Student self-registration</li>
                <li>Teacher account management by administrators</li>
                <li>Subject assignment for teachers</li>
                <li>Class schedule management for teachers</li>
                <li>Secure password storage with PBKDF2</li>
            </ul>
            <p>Built with Python, PyQt6, and SQLite.</p>
            """
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        event.accept()
