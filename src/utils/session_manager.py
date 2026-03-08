"""Session management for the Student Information System."""
from typing import Optional
from ..models.user import User


class SessionManager:
    """Manages user sessions for the application."""
    
    _instance = None
    _current_user: Optional[User] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_current_user(cls) -> Optional[User]:
        """Get the currently logged-in user."""
        return cls._current_user
    
    @classmethod
    def set_current_user(cls, user: User):
        """Set the current logged-in user."""
        cls._current_user = user
    
    @classmethod
    def clear_session(cls):
        """Clear the current session."""
        cls._current_user = None
    
    @classmethod
    def is_logged_in(cls) -> bool:
        """Check if a user is currently logged in."""
        return cls._current_user is not None
    
    @classmethod
    def is_admin(cls) -> bool:
        """Check if current user is an administrator."""
        return cls._current_user is not None and cls._current_user.is_admin()
    
    @classmethod
    def is_teacher(cls) -> bool:
        """Check if current user is a teacher."""
        return cls._current_user is not None and cls._current_user.is_teacher()
    
    @classmethod
    def is_student(cls) -> bool:
        """Check if current user is a student."""
        return cls._current_user is not None and cls._current_user.is_student()
