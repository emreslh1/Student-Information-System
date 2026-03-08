"""Database manager for the Student Information System."""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

from ..models.user import User, UserRole, Subject, DayOfWeek, ClassSchedule
from ..utils.password_utils import hash_password, verify_password


class DatabaseManager:
    """Manages SQLite database operations for the Student Information System."""
    
    def __init__(self, db_path: str = "student_info_system.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._connection = None  # Persistent connection for in-memory databases
        self._initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        # For in-memory databases, use a persistent connection
        if self.db_path == ':memory:':
            if self._connection is None:
                self._connection = sqlite3.connect(self.db_path)
                self._connection.row_factory = sqlite3.Row
            yield self._connection
            self._connection.commit()
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    subject TEXT
                )
            ''')
            
            # Class schedules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS class_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    day_of_week TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    room TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Student course selections table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    schedule_id INTEGER NOT NULL,
                    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (schedule_id) REFERENCES class_schedules(id) ON DELETE CASCADE,
                    UNIQUE(student_id, schedule_id)
                )
            ''')
            
            # Create default admin account if no users exist
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self._create_default_admin(conn)
    
    def _create_default_admin(self, conn):
        """Create the default administrator account."""
        cursor = conn.cursor()
        password_hash, salt = hash_password("admin123")
        cursor.execute('''
            INSERT INTO users (username, password_hash, salt, role, email, first_name, last_name, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("admin", password_hash, salt, UserRole.ADMINISTRATOR.value, 
              "admin@school.edu", "System", "Administrator", None))
    
    # ==================== User Management ====================
    
    def create_user(self, username: str, password: str, role: UserRole,
                    email: Optional[str] = None, first_name: Optional[str] = None,
                    last_name: Optional[str] = None, 
                    subject: Optional[Subject] = None) -> User:
        """
        Create a new user in the database.
        
        Args:
            username: Unique username
            password: Plain text password
            role: User role (Administrator, Teacher, Student)
            email: Optional email address
            first_name: Optional first name
            last_name: Optional last name
            subject: Subject for teachers (required for teachers)
            
        Returns:
            The created User object
            
        Raises:
            ValueError: If username already exists or teacher has no subject
        """
        # Validate teacher has a subject
        if role == UserRole.TEACHER and subject is None:
            raise ValueError("Teachers must have a subject assigned")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                raise ValueError(f"Username '{username}' already exists")
            
            # Hash password
            password_hash, salt = hash_password(password)
            
            # Insert user
            subject_str = subject.value if subject else None
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, role, email, first_name, last_name, subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, salt, role.value, email, first_name, last_name, subject_str))
            
            user_id = cursor.lastrowid
            
            return User(
                id=user_id,
                username=username,
                password_hash=password_hash,
                role=role,
                email=email,
                first_name=first_name,
                last_name=last_name,
                created_at=datetime.now(),
                is_active=True,
                subject=subject
            )
    
    def _row_to_user(self, row) -> User:
        """Convert a database row to a User object."""
        subject = None
        if row['subject']:
            try:
                subject = Subject.from_string(row['subject'])
            except ValueError:
                pass
        
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            role=UserRole.from_string(row['role']),
            email=row['email'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            is_active=bool(row['is_active']),
            subject=subject
        )
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.
        
        Args:
            username: The username to authenticate
            password: The plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, password_hash, salt, role, email, 
                       first_name, last_name, created_at, is_active, subject
                FROM users 
                WHERE username = ?
            ''', (username,))
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            if not row['is_active']:
                return None
            
            # Verify password
            if not verify_password(password, row['password_hash'], row['salt']):
                return None
            
            return self._row_to_user(row)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by their ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, password_hash, salt, role, email, 
                       first_name, last_name, created_at, is_active, subject
                FROM users 
                WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_user(row)
    
    def get_all_users(self) -> List[User]:
        """Get all users from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, password_hash, salt, role, email, 
                       first_name, last_name, created_at, is_active, subject
                FROM users
                ORDER BY username
            ''')
            
            return [self._row_to_user(row) for row in cursor.fetchall()]
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users with a specific role."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, password_hash, salt, role, email, 
                       first_name, last_name, created_at, is_active, subject
                FROM users
                WHERE role = ?
                ORDER BY username
            ''', (role.value,))
            
            return [self._row_to_user(row) for row in cursor.fetchall()]
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """
        Update user information.
        
        Args:
            user_id: The ID of the user to update
            **kwargs: Fields to update (email, first_name, last_name, is_active, subject)
            
        Returns:
            True if update successful, False otherwise
        """
        allowed_fields = {'email', 'first_name', 'last_name', 'is_active', 'subject'}
        update_fields = {}
        
        for k, v in kwargs.items():
            if k in allowed_fields:
                if k == 'subject' and v is not None:
                    update_fields[k] = v.value if isinstance(v, Subject) else v
                else:
                    update_fields[k] = v
        
        if not update_fields:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            set_clause = ', '.join(f"{k} = ?" for k in update_fields.keys())
            values = list(update_fields.values()) + [user_id]
            
            cursor.execute(f'''
                UPDATE users 
                SET {set_clause}
                WHERE id = ?
            ''', values)
            
            return cursor.rowcount > 0
    
    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Update a user's password."""
        password_hash, salt = hash_password(new_password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, salt = ?
                WHERE id = ?
            ''', (password_hash, salt, user_id))
            
            return cursor.rowcount > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            return cursor.rowcount > 0
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        return self.update_user(user_id, is_active=False)
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user account."""
        return self.update_user(user_id, is_active=True)
    
    def username_exists(self, username: str) -> bool:
        """Check if a username already exists."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
    
    # ==================== Class Schedule Management ====================
    
    def create_class_schedule(self, teacher_id: int, subject: Subject, 
                              class_name: str, day_of_week: DayOfWeek,
                              start_time: str, end_time: str,
                              room: Optional[str] = None) -> ClassSchedule:
        """
        Create a new class schedule.
        
        Args:
            teacher_id: The ID of the teacher
            subject: The subject of the class
            class_name: Name/description of the class
            day_of_week: Day of the week
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            room: Optional room/location
            
        Returns:
            The created ClassSchedule object
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO class_schedules 
                (teacher_id, subject, class_name, day_of_week, start_time, end_time, room)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (teacher_id, subject.value, class_name, day_of_week.value, 
                  start_time, end_time, room))
            
            schedule_id = cursor.lastrowid
            
            return ClassSchedule(
                id=schedule_id,
                teacher_id=teacher_id,
                subject=subject,
                class_name=class_name,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                room=room
            )
    
    def get_schedules_by_teacher(self, teacher_id: int) -> List[ClassSchedule]:
        """Get all class schedules for a teacher."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, teacher_id, subject, class_name, day_of_week, 
                       start_time, end_time, room
                FROM class_schedules
                WHERE teacher_id = ?
                ORDER BY 
                    CASE day_of_week
                        WHEN 'Monday' THEN 1
                        WHEN 'Tuesday' THEN 2
                        WHEN 'Wednesday' THEN 3
                        WHEN 'Thursday' THEN 4
                        WHEN 'Friday' THEN 5
                        WHEN 'Saturday' THEN 6
                        WHEN 'Sunday' THEN 7
                    END,
                    start_time
            ''', (teacher_id,))
            
            schedules = []
            for row in cursor.fetchall():
                schedules.append(ClassSchedule(
                    id=row['id'],
                    teacher_id=row['teacher_id'],
                    subject=Subject.from_string(row['subject']),
                    class_name=row['class_name'],
                    day_of_week=DayOfWeek.from_string(row['day_of_week']),
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    room=row['room']
                ))
            
            return schedules
    
    def get_schedule_by_id(self, schedule_id: int) -> Optional[ClassSchedule]:
        """Get a class schedule by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, teacher_id, subject, class_name, day_of_week, 
                       start_time, end_time, room
                FROM class_schedules
                WHERE id = ?
            ''', (schedule_id,))
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return ClassSchedule(
                id=row['id'],
                teacher_id=row['teacher_id'],
                subject=Subject.from_string(row['subject']),
                class_name=row['class_name'],
                day_of_week=DayOfWeek.from_string(row['day_of_week']),
                start_time=row['start_time'],
                end_time=row['end_time'],
                room=row['room']
            )
    
    def update_class_schedule(self, schedule_id: int, **kwargs) -> bool:
        """Update a class schedule."""
        allowed_fields = {'class_name', 'day_of_week', 'start_time', 'end_time', 'room'}
        update_fields = {}
        
        for k, v in kwargs.items():
            if k in allowed_fields:
                if k == 'day_of_week' and isinstance(v, DayOfWeek):
                    update_fields[k] = v.value
                else:
                    update_fields[k] = v
        
        if not update_fields:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            set_clause = ', '.join(f"{k} = ?" for k in update_fields.keys())
            values = list(update_fields.values()) + [schedule_id]
            
            cursor.execute(f'''
                UPDATE class_schedules 
                SET {set_clause}
                WHERE id = ?
            ''', values)
            
            return cursor.rowcount > 0
    
    def delete_class_schedule(self, schedule_id: int) -> bool:
        """Delete a class schedule."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM class_schedules WHERE id = ?", (schedule_id,))
            
            return cursor.rowcount > 0
    
    def delete_all_schedules_for_teacher(self, teacher_id: int) -> int:
        """Delete all class schedules for a teacher. Returns count deleted."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM class_schedules WHERE teacher_id = ?", (teacher_id,))
            
            return cursor.rowcount
    
    def get_all_class_schedules(self) -> List[ClassSchedule]:
        """Get all class schedules (for students to view available classes)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cs.id, cs.teacher_id, cs.subject, cs.class_name, cs.day_of_week, 
                       cs.start_time, cs.end_time, cs.room, u.first_name, u.last_name
                FROM class_schedules cs
                JOIN users u ON cs.teacher_id = u.id
                ORDER BY 
                    CASE cs.day_of_week
                        WHEN 'Monday' THEN 1
                        WHEN 'Tuesday' THEN 2
                        WHEN 'Wednesday' THEN 3
                        WHEN 'Thursday' THEN 4
                        WHEN 'Friday' THEN 5
                        WHEN 'Saturday' THEN 6
                        WHEN 'Sunday' THEN 7
                    END,
                    cs.start_time
            ''')
            
            schedules = []
            for row in cursor.fetchall():
                schedule = ClassSchedule(
                    id=row['id'],
                    teacher_id=row['teacher_id'],
                    subject=Subject.from_string(row['subject']),
                    class_name=row['class_name'],
                    day_of_week=DayOfWeek.from_string(row['day_of_week']),
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    room=row['room']
                )
                # Add teacher name for display
                schedule.teacher_name = f"{row['first_name'] or ''} {row['last_name'] or ''}".strip() or "Unknown"
                schedules.append(schedule)
            
            return schedules
    
    # ==================== Student Course Selection ====================
    
    def enroll_student_in_course(self, student_id: int, schedule_id: int) -> bool:
        """
        Enroll a student in a course.
        
        Args:
            student_id: The ID of the student
            schedule_id: The ID of the class schedule
            
        Returns:
            True if enrollment successful, False if already enrolled
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO student_courses (student_id, schedule_id)
                    VALUES (?, ?)
                ''', (student_id, schedule_id))
                return True
            except sqlite3.IntegrityError:
                # Already enrolled
                return False
    
    def unenroll_student_from_course(self, student_id: int, schedule_id: int) -> bool:
        """
        Remove a student from a course.
        
        Args:
            student_id: The ID of the student
            schedule_id: The ID of the class schedule
            
        Returns:
            True if unenrollment successful, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM student_courses 
                WHERE student_id = ? AND schedule_id = ?
            ''', (student_id, schedule_id))
            
            return cursor.rowcount > 0
    
    def get_student_courses(self, student_id: int) -> List[ClassSchedule]:
        """
        Get all courses a student is enrolled in.
        
        Args:
            student_id: The ID of the student
            
        Returns:
            List of ClassSchedule objects the student is enrolled in
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cs.id, cs.teacher_id, cs.subject, cs.class_name, cs.day_of_week, 
                       cs.start_time, cs.end_time, cs.room, u.first_name, u.last_name
                FROM student_courses sc
                JOIN class_schedules cs ON sc.schedule_id = cs.id
                JOIN users u ON cs.teacher_id = u.id
                WHERE sc.student_id = ?
                ORDER BY 
                    CASE cs.day_of_week
                        WHEN 'Monday' THEN 1
                        WHEN 'Tuesday' THEN 2
                        WHEN 'Wednesday' THEN 3
                        WHEN 'Thursday' THEN 4
                        WHEN 'Friday' THEN 5
                        WHEN 'Saturday' THEN 6
                        WHEN 'Sunday' THEN 7
                    END,
                    cs.start_time
            ''', (student_id,))
            
            courses = []
            for row in cursor.fetchall():
                schedule = ClassSchedule(
                    id=row['id'],
                    teacher_id=row['teacher_id'],
                    subject=Subject.from_string(row['subject']),
                    class_name=row['class_name'],
                    day_of_week=DayOfWeek.from_string(row['day_of_week']),
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    room=row['room']
                )
                schedule.teacher_name = f"{row['first_name'] or ''} {row['last_name'] or ''}".strip() or "Unknown"
                courses.append(schedule)
            
            return courses
    
    def is_student_enrolled(self, student_id: int, schedule_id: int) -> bool:
        """Check if a student is enrolled in a specific course."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM student_courses 
                WHERE student_id = ? AND schedule_id = ?
            ''', (student_id, schedule_id))
            
            return cursor.fetchone() is not None
