"""User model and role definitions for the Student Information System."""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class UserRole(Enum):
    """Enumeration of user roles in the system."""
    ADMINISTRATOR = "Administrator"
    TEACHER = "Teacher"
    STUDENT = "Student"
    
    @classmethod
    def from_string(cls, role_str: str) -> 'UserRole':
        """Convert string to UserRole enum."""
        for role in cls:
            if role.value.lower() == role_str.lower():
                return role
        raise ValueError(f"Invalid role: {role_str}")


class Subject(Enum):
    """Enumeration of available subjects for teachers."""
    MATH = "Mathematics"
    SCIENCE = "Science"
    ENGLISH = "English"
    HISTORY = "History"
    PHYSICS = "Physics"
    CHEMISTRY = "Chemistry"
    BIOLOGY = "Biology"
    COMPUTER_SCIENCE = "Computer Science"
    ART = "Art"
    MUSIC = "Music"
    PHYSICAL_EDUCATION = "Physical Education"
    GEOGRAPHY = "Geography"
    
    @classmethod
    def from_string(cls, subject_str: str) -> 'Subject':
        """Convert string to Subject enum."""
        for subject in cls:
            if subject.value.lower() == subject_str.lower() or subject.name.lower() == subject_str.lower():
                return subject
        raise ValueError(f"Invalid subject: {subject_str}")
    
    @classmethod
    def all_subjects(cls) -> list:
        """Return list of all subjects."""
        return list(cls)


class DayOfWeek(Enum):
    """Enumeration of days of the week for scheduling."""
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    
    @classmethod
    def from_string(cls, day_str: str) -> 'DayOfWeek':
        """Convert string to DayOfWeek enum."""
        for day in cls:
            if day.value.lower() == day_str.lower():
                return day
        raise ValueError(f"Invalid day: {day_str}")
    
    @classmethod
    def all_days(cls) -> list:
        """Return list of all days."""
        return list(cls)


@dataclass
class User:
    """User model representing a system user."""
    id: int
    username: str
    password_hash: str
    role: UserRole
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True
    subject: Optional[Subject] = None  # For teachers only
    
    def full_name(self) -> str:
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def is_admin(self) -> bool:
        """Check if user has administrator role."""
        return self.role == UserRole.ADMINISTRATOR
    
    def is_teacher(self) -> bool:
        """Check if user has teacher role."""
        return self.role == UserRole.TEACHER
    
    def is_student(self) -> bool:
        """Check if user has student role."""
        return self.role == UserRole.STUDENT
    
    def get_subject_name(self) -> str:
        """Return the subject name for teachers."""
        return self.subject.value if self.subject else "N/A"


@dataclass
class ClassSchedule:
    """Model representing a scheduled class."""
    id: int
    teacher_id: int
    subject: Subject
    class_name: str
    day_of_week: DayOfWeek
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"
    room: Optional[str] = None
    
    def get_day_name(self) -> str:
        """Return the day name."""
        return self.day_of_week.value
    
    def get_time_range(self) -> str:
        """Return formatted time range."""
        return f"{self.start_time} - {self.end_time}"

