"""
Utility functions for StoryWeave backend
"""
import hashlib
import uuid
from datetime import datetime


def create_cache_key(data):
    """
    Create a cache key from generation parameters

    Args:
        data: dict with profile_type, theme, age, story_length

    Returns:
        MD5 hash string
    """
    # Create a consistent string from relevant parameters
    key_parts = [
        str(data.get('profile_type', '')),
        str(data.get('theme', '')),
        str(data.get('age', '')),
        str(data.get('story_length', ''))
    ]

    key_string = '_'.join(key_parts)

    # Hash for consistent key length
    return hashlib.md5(key_string.encode()).hexdigest()


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


def get_current_timestamp():
    """Get current timestamp in ISO 8601 format"""
    return datetime.now().isoformat()


def get_ttl_timestamp(hours=24):
    """
    Get Unix timestamp for TTL (Time To Live)

    Args:
        hours: Number of hours until expiration

    Returns:
        Unix timestamp (integer)
    """
    from datetime import timedelta
    expiry_time = datetime.now() + timedelta(hours=hours)
    return int(expiry_time.timestamp())


def validate_profile_type(profile_type):
    """
    Validate cognitive profile type

    Args:
        profile_type: Profile type string

    Returns:
        bool: True if valid
    """
    valid_profiles = ['adhd', 'autism', 'anxiety']
    return profile_type in valid_profiles


def validate_story_length(length):
    """
    Validate story length

    Args:
        length: Length in minutes

    Returns:
        bool: True if valid
    """
    valid_lengths = [5, 10, 15]
    return length in valid_lengths


def validate_age(age):
    """
    Validate child age

    Args:
        age: Age as integer

    Returns:
        bool: True if valid
    """
    return isinstance(age, int) and 3 <= age <= 12


def sanitize_input(text, max_length=100):
    """
    Sanitize user input text

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""

    # Remove any potential injection characters
    sanitized = text.strip()[:max_length]

    return sanitized


def format_error_response(error_message, status_code=400):
    """
    Format a consistent error response

    Args:
        error_message: Error message string
        status_code: HTTP status code

    Returns:
        tuple of (dict, int)
    """
    return {"error": error_message}, status_code


def format_success_response(data):
    """
    Format a consistent success response

    Args:
        data: Response data dict

    Returns:
        dict
    """
    return data
