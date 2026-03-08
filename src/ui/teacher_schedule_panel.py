"""Teacher panel for managing class schedules."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QSpacerItem, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialog, QGridLayout, QAbstractItemView, QTimeEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTime
from PyQt6.QtGui import QFont, QColor

from ..models.user import User, Subject, DayOfWeek, ClassSchedule


class AddClassDialog(QDialog):
    """Dialog for adding a new class schedule."""
    
    class_created = pyqtSignal(object)  # Emits ClassSchedule object
    
    def __init__(self, db_manager, teacher: User, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.teacher = teacher
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Class Schedule")
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title_label = QLabel(f"Add New Class - {self.teacher.subject.value}")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Subject info
        subject_info = QLabel(f"Subject: {self.teacher.subject.value}")
        subject_info.setStyleSheet("color: #666; font-style: italic;")
        subject_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subject_info)
        
        # Form
        form_frame = QFrame()
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(10)
        
        row = 0
        
        # Class Name
        class_name_label = QLabel("Class Name *:")
        self.class_name_input = QLineEdit()
        self.class_name_input.setPlaceholderText("e.g., 'Grade 10A', 'Introduction to Algebra'")
        self.class_name_input.setMinimumHeight(30)
        form_layout.addWidget(class_name_label, row, 0)
        form_layout.addWidget(self.class_name_input, row, 1)
        row += 1
        
        # Day of Week
        day_label = QLabel("Day *:")
        self.day_combo = QComboBox()
        self.day_combo.setMinimumHeight(30)
        for day in DayOfWeek.all_days():
            self.day_combo.addItem(day.value, day)
        form_layout.addWidget(day_label, row, 0)
        form_layout.addWidget(self.day_combo, row, 1)
        row += 1
        
        # Start Time
        start_time_label = QLabel("Start Time *:")
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime(8, 0))  # Default 8:00 AM
        self.start_time_edit.setMinimumHeight(30)
        form_layout.addWidget(start_time_label, row, 0)
        form_layout.addWidget(self.start_time_edit, row, 1)
        row += 1
        
        # End Time
        end_time_label = QLabel("End Time *:")
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        self.end_time_edit.setTime(QTime(9, 0))  # Default 9:00 AM
        self.end_time_edit.setMinimumHeight(30)
        form_layout.addWidget(end_time_label, row, 0)
        form_layout.addWidget(self.end_time_edit, row, 1)
        row += 1
        
        # Room (optional)
        room_label = QLabel("Room:")
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("e.g., 'Room 101', 'Lab A'")
        self.room_input.setMinimumHeight(30)
        form_layout.addWidget(room_label, row, 0)
        form_layout.addWidget(self.room_input, row, 1)
        
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
        
        self.create_button = QPushButton("Add Class")
        self.create_button.setMinimumHeight(32)
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals."""
        self.create_button.clicked.connect(self._create_class)
        self.cancel_button.clicked.connect(self.reject)
    
    def _validate(self) -> tuple[bool, str]:
        """Validate input fields."""
        class_name = self.class_name_input.text().strip()
        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()
        
        if not class_name:
            return False, "Class name is required."
        
        if start_time >= end_time:
            return False, "End time must be after start time."
        
        return True, ""
    
    def _create_class(self):
        """Create the class schedule."""
        is_valid, error = self._validate()
        
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error)
            return
        
        try:
            schedule = self.db_manager.create_class_schedule(
                teacher_id=self.teacher.id,
                subject=self.teacher.subject,
                class_name=self.class_name_input.text().strip(),
                day_of_week=self.day_combo.currentData(),
                start_time=self.start_time_edit.time().toString("HH:mm"),
                end_time=self.end_time_edit.time().toString("HH:mm"),
                room=self.room_input.text().strip() or None
            )
            
            self.class_created.emit(schedule)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create class: {str(e)}")


class TeacherScheduleWidget(QWidget):
    """Widget for teachers to manage their class schedules."""
    
    schedule_changed = pyqtSignal()
    
    def __init__(self, db_manager, current_user: User, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_user = current_user
        
        self._setup_ui()
        self._connect_signals()
        self._load_schedules()
    
    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and subject info
        header_layout = QHBoxLayout()
        
        title_label = QLabel("My Class Schedule")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Subject badge
        if self.current_user.subject:
            subject_frame = QFrame()
            subject_frame.setStyleSheet("""
                QFrame {
                    background-color: #fd7e14;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
            subject_layout = QHBoxLayout(subject_frame)
            subject_layout.setContentsMargins(10, 5, 10, 5)
            subject_label = QLabel(f"Subject: {self.current_user.subject.value}")
            subject_layout.addWidget(subject_label)
            header_layout.addWidget(subject_frame)
        
        layout.addLayout(header_layout)
        
        # Actions bar
        actions_layout = QHBoxLayout()
        
        self.add_class_button = QPushButton("Add Class")
        self.add_class_button.setStyleSheet("""
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
        actions_layout.addWidget(self.add_class_button)
        
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
        actions_layout.addWidget(self.refresh_button)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels([
            "Day", "Time", "Class Name", "Room", "Subject", "Actions"
        ])
        
        # Set column widths
        header = self.schedule_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.schedule_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.schedule_table)
        
        # Info label
        info_label = QLabel("Note: You can only add classes for your assigned subject.")
        info_label.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        layout.addWidget(info_label)
    
    def _connect_signals(self):
        """Connect signals."""
        self.add_class_button.clicked.connect(self._add_class)
        self.refresh_button.clicked.connect(self._load_schedules)
    
    def _load_schedules(self):
        """Load schedules into the table."""
        schedules = self.db_manager.get_schedules_by_teacher(self.current_user.id)
        
        self.schedule_table.setRowCount(len(schedules))
        
        for row, schedule in enumerate(schedules):
            # Day
            day_item = QTableWidgetItem(schedule.get_day_name())
            day_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Color code by day
            day_colors = {
                DayOfWeek.MONDAY: "#ffe6e6",
                DayOfWeek.TUESDAY: "#e6ffe6",
                DayOfWeek.WEDNESDAY: "#e6e6ff",
                DayOfWeek.THURSDAY: "#ffffe6",
                DayOfWeek.FRIDAY: "#ffe6ff",
                DayOfWeek.SATURDAY: "#e6ffff",
                DayOfWeek.SUNDAY: "#f0f0f0"
            }
            day_item.setBackground(QColor(day_colors.get(schedule.day_of_week, "#ffffff")))
            self.schedule_table.setItem(row, 0, day_item)
            
            # Time
            time_item = QTableWidgetItem(schedule.get_time_range())
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.schedule_table.setItem(row, 1, time_item)
            
            # Class Name
            self.schedule_table.setItem(row, 2, QTableWidgetItem(schedule.class_name))
            
            # Room
            room_item = QTableWidgetItem(schedule.room or "-")
            room_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.schedule_table.setItem(row, 3, room_item)
            
            # Subject
            subject_item = QTableWidgetItem(schedule.subject.value)
            subject_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            subject_item.setBackground(QColor("#fff3e6"))
            self.schedule_table.setItem(row, 4, subject_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)
            
            # Delete button
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
            delete_btn.clicked.connect(lambda checked, s=schedule: self._delete_schedule(s))
            actions_layout.addWidget(delete_btn)
            
            self.schedule_table.setCellWidget(row, 5, actions_widget)
    
    def _add_class(self):
        """Open dialog to add a class."""
        dialog = AddClassDialog(self.db_manager, self.current_user, self)
        dialog.class_created.connect(self._on_class_created)
        dialog.exec()
    
    def _on_class_created(self, schedule: ClassSchedule):
        """Handle class creation."""
        self._load_schedules()
        self.schedule_changed.emit()
        QMessageBox.information(
            self,
            "Class Added",
            f"Class '{schedule.class_name}' added successfully!"
        )
    
    def _delete_schedule(self, schedule: ClassSchedule):
        """Delete a class schedule."""
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the class '{schedule.class_name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_class_schedule(schedule.id)
            self._load_schedules()
            self.schedule_changed.emit()
            QMessageBox.information(self, "Deleted", f"Class '{schedule.class_name}' has been deleted.")
