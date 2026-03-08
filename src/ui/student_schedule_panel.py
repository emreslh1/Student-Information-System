"""Student schedule panel with split interface - course list and weekly schedule."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QComboBox, QPushButton, QMessageBox,
    QTabWidget, QAbstractItemView, QSplitter, QScrollArea,
    QGridLayout, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ..models.user import User, Subject, DayOfWeek


class ScheduleSlot(QFrame):
    """A clickable schedule slot representing a time block in the weekly schedule."""
    
    def __init__(self, day, time_slot, parent=None):
        super().__init__(parent)
        self.day = day
        self.time_slot = time_slot
        self.course = None
        self.is_selected = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.setMinimumHeight(60)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            ScheduleSlot {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 6px;
            }
            ScheduleSlot:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            ScheduleSlot[selected="true"] {
                background-color: #fff3cd;
                border-color: #ffc107;
            }
            ScheduleSlot[hasCourse="true"] {
                background-color: #d4edda;
                border-color: #28a745;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(2)
        
        # Time label
        self.time_label = QLabel(self.time_slot)
        self.time_label.setFont(QFont("Arial", 8))
        self.time_label.setStyleSheet("color: #6c757d;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.time_label)
        
        # Course info label
        self.course_label = QLabel("")
        self.course_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.course_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.course_label.setWordWrap(True)
        self.layout.addWidget(self.course_label)
        
        self.setProperty("selected", False)
        self.setProperty("hasCourse", False)
    
    def set_course(self, course):
        """Set a course for this slot."""
        self.course = course
        if course:
            self.course_label.setText(f"{course.class_name}\n({course.subject.value})")
            self.course_label.setStyleSheet("color: #155724;")
            self.setProperty("hasCourse", True)
        else:
            self.course_label.setText("")
            self.setProperty("hasCourse", False)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def clear_course(self):
        """Clear the course from this slot."""
        self.course = None
        self.course_label.setText("")
        self.setProperty("hasCourse", False)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def mousePressEvent(self, event):
        """Handle mouse click to select this slot."""
        if event.button() == Qt.MouseButton.LeftButton:
            parent = self.parent()
            while parent and not isinstance(parent, WeeklyScheduleWidget):
                parent = parent.parent()
            if parent:
                parent.select_slot(self)
        super().mousePressEvent(event)


class WeeklyScheduleWidget(QWidget):
    """Weekly schedule grid showing Monday-Friday with time slots."""
    
    TIME_SLOTS = [
        "08:00 - 09:00",
        "09:00 - 10:00",
        "10:00 - 11:00",
        "11:00 - 12:00",
        "12:00 - 13:00",
        "13:00 - 14:00",
        "14:00 - 15:00",
        "15:00 - 16:00",
        "16:00 - 17:00",
        "17:00 - 18:00"
    ]
    
    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.slots = {}  # (day, time_slot) -> ScheduleSlot
        self.selected_slot = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("Weekly Class Schedule")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Schedule grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white;")
        
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(5)
        
        # Day headers
        grid.addWidget(QLabel(""), 0, 0)  # Empty corner
        for col, day in enumerate(self.DAYS, 1):
            day_label = QLabel(day)
            day_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_label.setStyleSheet("background-color: #0078d4; color: white; padding: 8px; border-radius: 4px;")
            grid.addWidget(day_label, 0, col)
        
        # Time slots
        for row, time_slot in enumerate(self.TIME_SLOTS, 1):
            # Time label
            time_label = QLabel(time_slot)
            time_label.setFont(QFont("Arial", 9))
            time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            time_label.setStyleSheet("background-color: #f8f9fa; padding: 5px;")
            grid.addWidget(time_label, row, 0)
            
            # Schedule slots
            for col, day in enumerate(self.DAYS, 1):
                slot = ScheduleSlot(day, time_slot)
                self.slots[(day, time_slot)] = slot
                grid.addWidget(slot, row, col)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        
        # Available slot
        available = QFrame()
        available.setFixedSize(20, 20)
        available.setStyleSheet("background-color: #f8f9fa; border: 2px solid #dee2e6; border-radius: 4px;")
        legend_layout.addWidget(available)
        legend_layout.addWidget(QLabel("Available"))
        legend_layout.addSpacing(15)
        
        # Selected slot
        selected = QFrame()
        selected.setFixedSize(20, 20)
        selected.setStyleSheet("background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 4px;")
        legend_layout.addWidget(selected)
        legend_layout.addWidget(QLabel("Selected"))
        legend_layout.addSpacing(15)
        
        # Occupied slot
        occupied = QFrame()
        occupied.setFixedSize(20, 20)
        occupied.setStyleSheet("background-color: #d4edda; border: 2px solid #28a745; border-radius: 4px;")
        legend_layout.addWidget(occupied)
        legend_layout.addWidget(QLabel("Your Course"))
        legend_layout.addStretch()
        
        layout.addLayout(legend_layout)
    
    def select_slot(self, slot):
        """Select a schedule slot."""
        # Deselect previous
        if self.selected_slot:
            self.selected_slot.setProperty("selected", False)
            self.selected_slot.style().unpolish(self.selected_slot)
            self.selected_slot.style().polish(self.selected_slot)
        
        # Select new
        self.selected_slot = slot
        slot.setProperty("selected", True)
        slot.style().unpolish(slot)
        slot.style().polish(slot)
    
    def get_selected_slot(self):
        """Get the currently selected slot."""
        return self.selected_slot
    
    def add_course_to_slot(self, course, day, time_slot):
        """Add a course to a specific slot."""
        key = (day, time_slot)
        if key in self.slots:
            self.slots[key].set_course(course)
            return True
        return False
    
    def clear_all_courses(self):
        """Clear all courses from the schedule."""
        for slot in self.slots.values():
            slot.clear_course()
    
    def find_slot_for_course(self, course):
        """Find the slot that matches a course's day and time."""
        day = course.day_of_week.value
        time_range = f"{course.start_time} - {course.end_time}"
        
        # Find matching time slot
        for slot_time in self.TIME_SLOTS:
            if self._time_overlaps(slot_time, time_range):
                key = (day, slot_time)
                if key in self.slots:
                    return self.slots[key]
        return None
    
    def _time_overlaps(self, slot_time, course_time):
        """Check if course time overlaps with slot time."""
        # Parse times
        slot_start, slot_end = slot_time.split(" - ")
        course_start, course_end = course_time.split(" - ")
        
        # Simple string comparison works for HH:MM format
        return (course_start <= slot_start < course_end or 
                slot_start <= course_start < slot_end)


class CourseListWidget(QWidget):
    """List of available courses with filtering."""
    
    course_selected = pyqtSignal(object)  # Emits course when selected
    
    def __init__(self, db_manager, user: User, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = user
        self.courses = []
        self.selected_course = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("Available Courses")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Select a course to add to your schedule. Click on a time slot in the weekly schedule, then select a course.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Subject:"))
        
        self.subject_filter = QComboBox()
        self.subject_filter.addItem("All Subjects", None)
        for subject in Subject:
            self.subject_filter.addItem(subject.value, subject)
        self.subject_filter.currentIndexChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.subject_filter)
        filter_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_courses)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Course table
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(5)
        self.course_table.setHorizontalHeaderLabels([
            "Subject", "Class Name", "Day", "Time", "Teacher"
        ])
        
        self.course_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        
        header = self.course_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.course_table.setAlternatingRowColors(True)
        self.course_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.course_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.course_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.course_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.add_btn = QPushButton("Add to Schedule")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._add_selected_course)
        btn_layout.addWidget(self.add_btn)
        
        layout.addLayout(btn_layout)
        
        # Status
        self.status_label = QLabel("Loading courses...")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
    
    def _load_courses(self):
        """Load available courses from database."""
        try:
            self.all_courses = self.db_manager.get_all_class_schedules()
            self._apply_filter()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load courses: {str(e)}")
    
    def _apply_filter(self):
        """Apply subject filter."""
        subject_data = self.subject_filter.currentData()
        
        if subject_data is None:
            self.courses = self.all_courses
        else:
            self.courses = [c for c in self.all_courses if c.subject == subject_data]
        
        self._update_table()
    
    def _update_table(self):
        """Update the course table."""
        self.course_table.setRowCount(len(self.courses))
        
        for row, course in enumerate(self.courses):
            self.course_table.setItem(row, 0, QTableWidgetItem(course.subject.value))
            
            name_item = QTableWidgetItem(course.class_name)
            name_item.setData(Qt.ItemDataRole.UserRole, course)
            self.course_table.setItem(row, 1, name_item)
            
            self.course_table.setItem(row, 2, QTableWidgetItem(course.day_of_week.value))
            
            time_str = f"{course.start_time} - {course.end_time}"
            self.course_table.setItem(row, 3, QTableWidgetItem(time_str))
            
            teacher_name = getattr(course, 'teacher_name', 'Unknown')
            self.course_table.setItem(row, 4, QTableWidgetItem(teacher_name))
        
        if len(self.courses) == 0:
            self.status_label.setText("No courses available.")
        else:
            self.status_label.setText(f"{len(self.courses)} course(s) available.")
    
    def _on_selection_changed(self):
        """Handle course selection."""
        selected = self.course_table.selectedItems()
        if selected:
            row = selected[0].row()
            self.selected_course = self.course_table.item(row, 1).data(Qt.ItemDataRole.UserRole)
            self.add_btn.setEnabled(True)
            self.course_selected.emit(self.selected_course)
        else:
            self.selected_course = None
            self.add_btn.setEnabled(False)
    
    def _add_selected_course(self):
        """Emit signal to add selected course."""
        if self.selected_course:
            self.course_selected.emit(self.selected_course)
    
    def get_selected_course(self):
        """Get currently selected course."""
        return self.selected_course
    
    def refresh(self):
        """Refresh the course list."""
        self._load_courses()


class StudentScheduleWidget(QWidget):
    """Main student panel with split interface - course list and weekly schedule."""
    
    def __init__(self, db_manager, user: User, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = user
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Set up the split interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #0078d4; padding: 10px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        title = QLabel("Course Selection & Schedule")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Help text
        help_text = QLabel("Select a time slot -> Choose a course -> Click 'Add to Schedule'")
        help_text.setStyleSheet("color: white;")
        header_layout.addWidget(help_text)
        
        layout.addWidget(header)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Course List
        self.course_list = CourseListWidget(self.db_manager, self.user)
        self.course_list.course_selected.connect(self._on_course_selected)
        splitter.addWidget(self.course_list)
        
        # Right panel: Weekly Schedule
        schedule_container = QWidget()
        schedule_layout = QVBoxLayout(schedule_container)
        schedule_layout.setContentsMargins(10, 10, 10, 10)
        
        self.weekly_schedule = WeeklyScheduleWidget()
        schedule_layout.addWidget(self.weekly_schedule)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.add_btn = QPushButton("Add Selected Course to Schedule")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._add_course_to_schedule)
        btn_layout.addWidget(self.add_btn)
        
        remove_btn = QPushButton("Remove Course from Selected Slot")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        remove_btn.clicked.connect(self._remove_course_from_slot)
        btn_layout.addWidget(remove_btn)
        
        schedule_layout.addLayout(btn_layout)
        
        splitter.addWidget(schedule_container)
        
        # Set splitter sizes (40% courses, 60% schedule)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
    
    def _load_data(self):
        """Load initial data."""
        self.course_list.refresh()
        self._load_my_schedule()
    
    def _load_my_schedule(self):
        """Load student's enrolled courses into the weekly schedule."""
        self.weekly_schedule.clear_all_courses()
        
        try:
            my_courses = self.db_manager.get_student_courses(self.user.id)
            for course in my_courses:
                slot = self.weekly_schedule.find_slot_for_course(course)
                if slot:
                    slot.set_course(course)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load your schedule: {str(e)}")
    
    def _on_course_selected(self, course):
        """Handle course selection from list."""
        self.selected_course = course
        self.add_btn.setEnabled(True)
        
        # Highlight the corresponding slot if empty
        slot = self.weekly_schedule.find_slot_for_course(course)
        if slot and not slot.course:
            self.weekly_schedule.select_slot(slot)
    
    def _add_course_to_schedule(self):
        """Add selected course to schedule."""
        selected_slot = self.weekly_schedule.get_selected_slot()
        selected_course = self.course_list.get_selected_course()
        
        if not selected_slot:
            QMessageBox.warning(self, "No Time Slot Selected", 
                              "Please click on a time slot in the weekly schedule first.")
            return
        
        if not selected_course:
            QMessageBox.warning(self, "No Course Selected", 
                              "Please select a course from the list.")
            return
        
        # Check if slot already has a course
        if selected_slot.course:
            reply = QMessageBox.question(
                self,
                "Replace Course?",
                f"This time slot already has '{selected_slot.course.class_name}'.\n\nDo you want to replace it with '{selected_course.class_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
            # Remove old course first
            self.db_manager.unenroll_student_from_course(self.user.id, selected_slot.course.id)
        
        # Check if course conflicts with existing enrollment
        my_courses = self.db_manager.get_student_courses(self.user.id)
        for existing in my_courses:
            if existing.id == selected_course.id:
                QMessageBox.information(self, "Already Enrolled", 
                                      f"You are already enrolled in '{selected_course.class_name}'.")
                return
            # Check time conflict
            if (existing.day_of_week == selected_course.day_of_week and 
                self._time_conflicts(existing, selected_course)):
                reply = QMessageBox.question(
                    self,
                    "Time Conflict",
                    f"This conflicts with '{existing.class_name}' at {existing.start_time}-{existing.end_time}.\n\nReplace it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.db_manager.unenroll_student_from_course(self.user.id, existing.id)
                else:
                    return
        
        # Enroll in the new course
        try:
            success = self.db_manager.enroll_student_in_course(self.user.id, selected_course.id)
            if success:
                # Update the visual schedule
                selected_slot.set_course(selected_course)
                QMessageBox.information(self, "Success", 
                                      f"'{selected_course.class_name}' has been added to your {selected_slot.day} schedule!")
                self._load_my_schedule()  # Refresh to show all courses
            else:
                QMessageBox.warning(self, "Error", "Failed to add course. You may already be enrolled.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add course: {str(e)}")
    
    def _remove_course_from_slot(self):
        """Remove course from selected time slot."""
        selected_slot = self.weekly_schedule.get_selected_slot()
        
        if not selected_slot:
            QMessageBox.warning(self, "No Selection", 
                              "Please click on a time slot in your schedule.")
            return
        
        if not selected_slot.course:
            QMessageBox.information(self, "Empty Slot", 
                                  "This time slot is empty.")
            return
        
        course = selected_slot.course
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove '{course.class_name}' from your {selected_slot.day} schedule?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.db_manager.unenroll_student_from_course(self.user.id, course.id)
                if success:
                    selected_slot.clear_course()
                    QMessageBox.information(self, "Success", 
                                          f"'{course.class_name}' has been removed from your schedule.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to remove course.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove course: {str(e)}")
    
    def _time_conflicts(self, course1, course2):
        """Check if two courses have conflicting times."""
        if course1.day_of_week != course2.day_of_week:
            return False
        
        # Parse times
        start1 = course1.start_time
        end1 = course1.end_time
        start2 = course2.start_time
        end2 = course2.end_time
        
        # Check for overlap
        return (start1 < end2 and start2 < end1)
