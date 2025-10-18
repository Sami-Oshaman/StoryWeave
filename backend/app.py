"""
StoryWeave Flask API
Main application file with API endpoints
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from decimal import Decimal

# Load environment variables
load_dotenv()

# Import our modules
from database import (
    get_cached_story,
    save_cached_story,
    save_profile,
    get_profile,
    save_story,
    get_story_history
)
from story_generator import create_story, handle_generation_error
from utils import (
    create_cache_key,
    generate_uuid,
    get_current_timestamp,
    get_ttl_timestamp,
    validate_profile_type,
    validate_story_length,
    validate_age,
    format_error_response
)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
CORS(app, resources={r"/api/*": {"origins": [frontend_url, "http://localhost:3000"]}})

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "StoryWeave API",
        "version": "1.0.0"
    })


@app.route('/api/generate-story', methods=['POST'])
def generate_story_endpoint():
    """
    Generate a personalized story based on child profile and preferences

    Required fields:
        - profile_type: 'adhd', 'autism', or 'anxiety'
        - age: integer (3-12)
        - theme: string
        - story_length: integer (5, 10, or 15 minutes)

    Optional fields:
        - child_id: string (for history tracking)
        - interests: list of strings
    """
    try:
        data = request.json

        if not data:
            return format_error_response("No data provided")

        # Validate required fields
        required_fields = ['profile_type', 'age', 'theme', 'story_length']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return format_error_response(f"Missing required fields: {', '.join(missing_fields)}")

        # Validate profile type
        if not validate_profile_type(data['profile_type']):
            return format_error_response("Invalid profile_type. Must be 'adhd', 'autism', 'anxiety', or 'general'")

        # Validate age
        if not validate_age(data['age']):
            return format_error_response("Invalid age. Must be between 3 and 12")

        # Validate story length
        if not validate_story_length(data['story_length']):
            return format_error_response("Invalid story_length. Must be 5, 10, or 15")

        # Check cache first
        cache_key = create_cache_key(data)
        logger.info(f"Checking cache for key: {cache_key}")

        cached_story = get_cached_story(cache_key)

        if cached_story:
            logger.info(f"Cache hit for key: {cache_key}")

            return jsonify({
                "story_id": generate_uuid(),
                "story_text": cached_story['story'],
                "cached": True,
                "generation_time": 0
            })

        # Cache miss - generate new story
        logger.info("Cache miss - generating new story")

        start_time = datetime.now()

        # Generate story
        result = create_story(
            profile_type=data['profile_type'],
            age=data['age'],
            theme=data['theme'],
            interests=data.get('interests', []),
            story_length=data['story_length']
        )

        generation_time = (datetime.now() - start_time).total_seconds()

        # Generate story ID
        story_id = generate_uuid()
        timestamp = get_current_timestamp()

        # Check if generation was successful or fallback was used
        if not result.get("success") and result.get("fallback"):
            logger.warning("Using fallback story due to generation failure")

            return jsonify({
                "story_id": story_id,
                "story_text": result["story"],
                "profile_used": data['profile_type'],
                "generation_time": generation_time,
                "fallback": True,
                "warning": handle_generation_error(result.get('error'))
            }), 200

        # Save to story history
        child_id = data.get('child_id', 'anonymous')

        try:
            save_story(
                child_id=child_id,
                story_text=result["story"],
                profile_type=data['profile_type'],
                theme=data['theme'],
                age=data['age'],
                interests=data.get('interests', []),
                story_length=data['story_length']
            )
        except Exception as e:
            logger.error(f"Failed to save story to history: {str(e)}")
            # Continue anyway - story generation succeeded

        # Cache the story
        try:
            save_cached_story(
                cache_key=cache_key,
                story_text=result["story"],
                expires_at=get_ttl_timestamp(24)  # 24 hour TTL
            )
        except Exception as e:
            logger.error(f"Failed to cache story: {str(e)}")
            # Continue anyway - story was generated successfully

        logger.info(f"Story generated successfully in {generation_time:.2f}s")

        return jsonify({
            "story_id": story_id,
            "story_text": result["story"],
            "profile_used": data['profile_type'],
            "generation_time": generation_time,
            "cached": False
        })

    except Exception as e:
        logger.error(f"Unexpected error in generate_story_endpoint: {str(e)}")
        return format_error_response("Internal server error", 500)


@app.route('/api/save-profile', methods=['POST'])
def save_profile_endpoint():
    """
    Create or update a child profile

    Required fields:
        - age: integer (3-12)
        - cognitive_profile: list of strings

    Optional fields:
        - sensory_preferences: dict
        - interests: list of strings
        - story_length_preference: integer (5, 10, or 15)
    """
    try:
        data = request.json

        if not data:
            return format_error_response("No data provided")

        # Validate required fields
        if 'age' not in data:
            return format_error_response("Missing required field: age")

        if 'cognitive_profile' not in data:
            return format_error_response("Missing required field: cognitive_profile")

        # Validate age
        if not validate_age(data['age']):
            return format_error_response("Invalid age. Must be between 3 and 12")

        # Validate cognitive profiles
        cognitive_profile = data['cognitive_profile']
        if not isinstance(cognitive_profile, list) or not cognitive_profile:
            return format_error_response("cognitive_profile must be a non-empty list")

        for profile in cognitive_profile:
            if not validate_profile_type(profile):
                return format_error_response(f"Invalid profile type: {profile}")

        # Generate child ID and timestamp
        child_id = generate_uuid()
        now = get_current_timestamp()

        # Build profile document
        profile_doc = {
            "child_id": child_id,
            "age": data['age'],
            "cognitive_profile": cognitive_profile,
            "sensory_preferences": data.get('sensory_preferences', {}),
            "interests": data.get('interests', []),
            "story_length_preference": data.get('story_length_preference', 10),
            "created_at": now,
            "updated_at": now
        }

        # Save to DynamoDB
        save_profile(profile_doc)

        logger.info(f"Profile created: {child_id}")

        return jsonify({
            "child_id": child_id,
            "profile_created": now,
            "success": True
        }), 201

    except Exception as e:
        logger.error(f"Error saving profile: {str(e)}")
        return format_error_response("Failed to save profile", 500)


@app.route('/api/get-history', methods=['GET'])
def get_history_endpoint():
    """
    Retrieve story history for a child

    Query parameters:
        - child_id: string (required)
        - limit: integer (optional, default 10, max 50)
    """
    try:
        child_id = request.args.get('child_id')

        if not child_id:
            return format_error_response("child_id query parameter is required")

        # Get limit parameter
        limit = request.args.get('limit', 10)
        try:
            limit = int(limit)
            limit = min(limit, 50)  # Cap at 50
            limit = max(limit, 1)   # Minimum 1
        except ValueError:
            return format_error_response("limit must be a number")

        # Get story history from DynamoDB
        story_list = get_story_history(child_id, limit)

        logger.info(f"Retrieved {len(story_list)} stories for child {child_id}")

        return jsonify({
            "child_id": child_id,
            "stories": story_list,
            "count": len(story_list)
        })

    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        return format_error_response("Failed to retrieve history", 500)


@app.route('/api/get-profile', methods=['GET'])
def get_profile_endpoint():
    """
    Retrieve a child profile

    Query parameters:
        - child_id: string (required)
    """
    try:
        child_id = request.args.get('child_id')

        if not child_id:
            return format_error_response("child_id query parameter is required")

        # Get profile from DynamoDB
        profile = get_profile(child_id)

        if not profile:
            return format_error_response("Profile not found", 404)

        logger.info(f"Retrieved profile for child {child_id}")

        return jsonify(profile)

    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        return format_error_response("Failed to retrieve profile", 500)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'

    logger.info(f"Starting StoryWeave API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")

    app.run(host=host, port=port, debug=debug)
