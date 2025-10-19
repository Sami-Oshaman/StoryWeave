"""
StoryWeave Flask Backend API
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from database import (
    save_profile, 
    get_profile, 
    save_story, 
    get_story_history,
    get_cached_story,
    save_cached_story
)
from utils import generate_uuid, get_current_timestamp
import hashlib
import json
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Simple user storage (for hackathon - replace with proper auth later)
USERS = {}


# ============ HELPER FUNCTIONS ============

def generate_cache_key(profile_data, story_params):
    """Generate a cache key for story requests"""
    cache_string = json.dumps({
        'conditions': sorted(profile_data.get('conditions', [])),
        'pacing': story_params.get('tonightsPacing'),
        'genre': story_params.get('genre', ''),
        'mood': story_params.get('mood'),
        'length': story_params.get('length')
    }, sort_keys=True)
    return hashlib.md5(cache_string.encode()).hexdigest()


# ============ AUTHENTICATION ENDPOINTS ============

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Create a new user account"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        if email in USERS:
            return jsonify({'error': 'User already exists'}), 400

        # Simple storage (use proper password hashing in production!)
        user_id = generate_uuid()
        USERS[email] = {
            'user_id': user_id,
            'email': email,
            'name': name or email.split('@')[0],
            'password': password  # NEVER do this in production!
        }

        logger.info(f"New user created: {email}")

        return jsonify({
            'user': {
                'user_id': user_id,
                'email': email,
                'name': USERS[email]['name']
            }
        }), 201

    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'Signup failed'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        user = USERS.get(email)
        if not user or user['password'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401

        logger.info(f"User logged in: {email}")

        return jsonify({
            'user': {
                'user_id': user['user_id'],
                'email': user['email'],
                'name': user['name']
            }
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


# ============ PROFILE ENDPOINTS ============

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    """Create or update a child profile"""
    try:
        data = request.json
        user_id = data.get('userId')
        profile = data.get('profile')

        if not user_id or not profile:
            return jsonify({'error': 'User ID and profile required'}), 400

        # Generate child_id if not exists
        child_id = profile.get('child_id') or generate_uuid()
        
        profile_data = {
            'child_id': child_id,
            'user_id': user_id,
            'child_name': profile.get('childName'),
            'age': int(profile.get('age')),
            'conditions': profile.get('conditions', []),
            'preferences': profile.get('preferences', {}),
            'created_at': get_current_timestamp(),
            'updated_at': get_current_timestamp()
        }

        save_profile(profile_data)
        logger.info(f"Profile saved for child: {profile_data['child_name']}")

        return jsonify({
            'child_id': child_id,
            'message': 'Profile saved successfully'
        }), 200

    except Exception as e:
        logger.error(f"Profile creation error: {str(e)}")
        return jsonify({'error': 'Failed to save profile'}), 500


@app.route('/api/profiles/<child_id>', methods=['GET'])
def fetch_profile(child_id):
    """Get a child profile"""
    try:
        profile = get_profile(child_id)
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        return jsonify({'profile': profile}), 200

    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch profile'}), 500


# ============ STORY GENERATION ENDPOINT ============

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    """Generate a bedtime story using AWS Bedrock"""
    try:
        data = request.json
        profile = data.get('profile')
        story_params = data.get('storyParams')

        if not profile or not story_params:
            return jsonify({'error': 'Profile and story params required'}), 400

        # Check cache first
        cache_key = generate_cache_key(profile, story_params)
        cached = get_cached_story(cache_key)
        
        if cached:
            logger.info(f"Returning cached story: {cache_key}")
            return jsonify({
                'story': cached['story'],
                'cached': True
            }), 200

        # TODO: Integrate AWS Bedrock here
        # For now, generate a sample story
        child_name = profile.get('childName', 'the child')
        genre = story_params.get('genre') or 'adventure'
        mood = story_params.get('mood', 'calm')
        
        # This is a placeholder - replace with actual Bedrock call
        sample_story = f"""Once upon a time, {child_name} discovered a magical world filled with {genre}.
        
The {mood} atmosphere made everything feel just right. As {child_name} explored, wonderful things happened.

And they all lived happily ever after. The end."""

        # Save to DynamoDB
        child_id = profile.get('child_id') or generate_uuid()
        save_story(
            child_id=child_id,
            story_text=sample_story,
            profile_type=','.join(profile.get('conditions', [])),
            theme=story_params.get('genre', ''),
            age=int(profile.get('age', 5)),
            interests=profile.get('preferences', {}).get('favoriteThemes', ''),
            story_length=len(sample_story)
        )

        # Cache the story (expires in 1 hour)
        expires_at = int(get_current_timestamp()) + 3600
        save_cached_story(cache_key, sample_story, expires_at)

        logger.info(f"Story generated for {child_name}")

        return jsonify({
            'story': sample_story,
            'cached': False
        }), 200

    except Exception as e:
        logger.error(f"Story generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate story'}), 500


# ============ STORY HISTORY ENDPOINT ============

@app.route('/api/stories/<child_id>', methods=['GET'])
def get_stories(child_id):
    """Get story history for a child"""
    try:
        limit = request.args.get('limit', 10, type=int)
        stories = get_story_history(child_id, limit)

        return jsonify({'stories': stories}), 200

    except Exception as e:
        logger.error(f"Story history error: {str(e)}")
        return jsonify({'error': 'Failed to fetch stories'}), 500


# ============ HEALTH CHECK ============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'StoryWeave API'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)