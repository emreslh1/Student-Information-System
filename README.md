# Student Information System

A desktop application for managing student information with role-based access control, built with Python, PyQt6, and SQLite.

## Features

- **Three Authorization Levels:**
  - **Administrator**: Full system access, can create and manage all user accounts
  - **Teacher**: Can only be created by administrators with a subject assignment, manage class schedules
  - **Student**: Can self-register, access to student features

- **Subject Assignment for Teachers:**
  - Teachers must be assigned a subject when created by administrators
  - 12 available subjects: Mathematics, Science, English, History, Physics, Chemistry, Biology, Computer Science, Art, Music, Physical Education, Geography

- **Class Schedule Management (Teachers):**
  - Teachers can add classes for their assigned subject only
  - Schedule classes by day and time
  - Specify room/location for each class
  - View and manage weekly schedule

- **Secure Authentication:**
  - PBKDF2 password hashing with SHA-256
  - Per-user salt for password storage
  - Session management

- **User Management (Admin only):**
  - Create Teacher accounts (with subject assignment)
  - Create Administrator accounts
  - Activate/deactivate user accounts
  - Delete user accounts
  - Reset user passwords
  - Filter users by role
  - View subject assignments for teachers

## Requirements

- Python 3.10+
- PyQt6

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Student-Information-System
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### Default Administrator Account

The system creates a default administrator account on first run:
- **Username:** `admin`
- **Password:** `admin123`

**Important:** Change the default password immediately after first login!

### User Registration

- **Students** can register themselves by clicking "Register as Student" on the login screen
- **Teachers** cannot register themselves - accounts must be created by an Administrator with a subject assignment
- **Administrators** are created by existing Administrators through the User Management panel

### Creating Teacher Accounts

1. Log in as Administrator
2. Go to "User Management" panel
3. Click "Add Teacher"
4. Fill in the required information and select a subject
5. Click "Create Teacher"

### Managing Class Schedules (Teachers)

1. Log in as a Teacher
2. Go to "My Schedule" panel
3. Click "Add Class"
4. Enter class name, select day and time
5. The subject is automatically set to your assigned subject

## Project Structure

```
Student-Information-System/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── data/                      # Database storage (auto-created)
│   └── student_info_system.db
└── src/
    ├── __init__.py
    ├── database/
    │   ├── __init__.py
    │   └── database_manager.py    # SQLite database operations
    ├── models/
    │   ├── __init__.py
    │   └── user.py                # User, UserRole, Subject, DayOfWeek, ClassSchedule models
    ├── ui/
    │   ├── __init__.py
    │   ├── login_dialog.py        # Login screen
    │   ├── registration_dialog.py # Student registration
    │   ├── admin_user_management.py # Admin user management panel
    │   ├── teacher_schedule_panel.py # Teacher class schedule management
    │   └── main_window.py         # Main application window
    └── utils/
        ├── __init__.py
        ├── password_utils.py      # Password hashing utilities
        └── session_manager.py     # Session management
```

## Authorization Levels

### Administrator
- Create and manage Teacher accounts (with subject assignment)
- Create and manage other Administrator accounts
- View, edit, activate/deactivate, and delete all user accounts
- Reset passwords for any user
- Full access to all system features

### Teacher
- Assigned subject by administrator (cannot be changed)
- Manage class schedules for assigned subject only
- Add classes with day, time, and room
- View and delete scheduled classes
- View student information

### Student
- Self-registration capability
- View personal information
- Access enrolled courses (future feature)
- Submit assignments (future feature)
- View grades and feedback (future feature)

## Security Features

- **Password Hashing**: Uses PBKDF2 with SHA-256 and 100,000 iterations
- **Per-User Salt**: Each password has a unique random salt
- **Constant-Time Comparison**: Password verification uses `secrets.compare_digest` to prevent timing attacks

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Unique username |
| password_hash | TEXT | PBKDF2 hashed password |
| salt | TEXT | Random salt for password |
| role | TEXT | Administrator, Teacher, or Student |
| subject | TEXT | Subject for teachers (optional) |
| email | TEXT | Email address (optional) |
| first_name | TEXT | First name |
| last_name | TEXT | Last name |
| created_at | TIMESTAMP | Account creation time |
| is_active | BOOLEAN | Account active status |

### Class Schedules Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| teacher_id | INTEGER | Foreign key to users table |
| subject | TEXT | Subject of the class |
| class_name | TEXT | Name/description of the class |
| day_of_week | TEXT | Day of the week (Monday-Sunday) |
| start_time | TEXT | Start time (HH:MM format) |
| end_time | TEXT | End time (HH:MM format) |
| room | TEXT | Room/location (optional) |
| created_at | TIMESTAMP | Schedule creation time |

## License

This project is for educational purposes.
