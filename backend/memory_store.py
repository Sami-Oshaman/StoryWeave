"""
In-memory data store fallback for when DynamoDB is unavailable
This allows the app to work without database tables
"""
from datetime import datetime

# In-memory storage
users = {}  # email -> user_data
profiles = {}  # child_id -> profile_data
user_profiles = {}  # user_email -> [child_ids]
stories = {}  # story_id -> story_data
cache = {}  # cache_key -> story_data


def create_user_memory(email, password_hash, name):
    """Store user in memory"""
    if email in users:
        return {'error': 'User with this email already exists'}, False

    user_data = {
        'email': email,
        'password_hash': password_hash,
        'name': name,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    users[email] = user_data
    user_profiles[email] = []
    return user_data, True


def get_user_memory(email):
    """Get user from memory"""
    return users.get(email)


def save_profile_memory(profile_data):
    """Save profile to memory"""
    child_id = profile_data['child_id']
    user_email = profile_data['user_email']

    profiles[child_id] = profile_data

    if user_email not in user_profiles:
        user_profiles[user_email] = []

    if child_id not in user_profiles[user_email]:
        user_profiles[user_email].append(child_id)

    return True


def get_profile_memory(child_id):
    """Get profile from memory"""
    return profiles.get(child_id)


def get_profiles_by_user_memory(user_email):
    """Get all profiles for a user"""
    child_ids = user_profiles.get(user_email, [])
    return [profiles[cid] for cid in child_ids if cid in profiles]


def save_story_memory(story_data):
    """Save story to memory"""
    story_id = story_data['story_id']
    stories[story_id] = story_data
    return True


def get_cached_story_memory(cache_key):
    """Get cached story from memory"""
    cached = cache.get(cache_key)
    if cached and cached.get('expires_at', 0) > datetime.now().timestamp():
        return cached
    return None


def save_cached_story_memory(cache_key, story_text, expires_at):
    """Save story to cache in memory"""
    cache[cache_key] = {
        'cache_key': cache_key,
        'story': story_text,
        'expires_at': expires_at,
        'access_count': 0
    }
    return True
