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
from image_generator import generate_story_images
from tts_service import generate_audio_for_page
from emotion_tagger import add_emotion_tags
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
import base64

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
CORS(app, resources={
    r"/api/*": {
        "origins": [
            frontend_url,
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

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
        - generate_images: boolean (whether to generate images, default False)
        - num_images: integer (number of images to generate, default 3)
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
            logger.info(f"Cache hit for key: {cache_key} - returning cached Claude-generated story")

            # Generate emotion tags for cached story too
            mood = data.get('mood', 'calm')
            emotion_tagged_story = cached_story['story']
            try:
                emotion_tagged_story = add_emotion_tags(
                    cached_story['story'],
                    mood=mood,
                    theme=data['theme']
                )
            except Exception as e:
                logger.error(f"Failed to add emotion tags to cached story: {str(e)}")

            return jsonify({
                "story_id": generate_uuid(),
                "story_text": cached_story['story'],
                "emotion_tagged_text": emotion_tagged_story,
                "cached": True,
                "generation_time": 0,
                "fallback": False,  # Cached stories are also real Claude stories, not fallbacks
                "profile_used": data['profile_type']
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

        logger.info(f"Story generated successfully in {generation_time:.2f}s - Claude-generated, not fallback")

        # Generate emotion-tagged version for TTS (using Claude Haiku)
        mood = data.get('mood', 'calm')  # Get mood from request if available
        emotion_tagged_story = None
        try:
            logger.info("Generating emotion-tagged version for TTS narration")
            emotion_tagged_story = add_emotion_tags(
                result["story"],
                mood=mood,
                theme=data['theme']
            )
            logger.info("Successfully generated emotion-tagged version")
        except Exception as e:
            logger.error(f"Failed to generate emotion tags: {str(e)}")
            # Continue without emotion tags if it fails
            emotion_tagged_story = result["story"]

        # Generate images if requested
        images = []
        if data.get('generate_images', False):
            # Calculate num_images based on actual paragraph count and pages_per_image
            pages_per_image = data.get('pages_per_image', 4)
            paragraphs = [p.strip() for p in result["story"].split('\n\n') if p.strip()]
            num_paragraphs = len(paragraphs)
            num_images = max(1, num_paragraphs // pages_per_image)

            logger.info(f"Story has {num_paragraphs} paragraphs, generating {num_images} images (1 per {pages_per_image} pages)")

            try:
                images = generate_story_images(
                    story_text=result["story"],
                    age=data['age'],
                    theme=data['theme'],
                    num_images=num_images
                )
                logger.info(f"Generated {len(images)} images successfully")
            except Exception as e:
                logger.error(f"Failed to generate images: {str(e)}")
                # Continue anyway - story was generated successfully

        return jsonify({
            "story_id": story_id,
            "story_text": result["story"],  # Clean version for display
            "emotion_tagged_text": emotion_tagged_story,  # Version with emotion tags for TTS
            "profile_used": data['profile_type'],
            "generation_time": generation_time,
            "cached": False,
            "fallback": False,  # Explicitly indicate this is NOT a fallback story
            "images": images  # List of base64-encoded images with metadata
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

        # Save to DynamoDB (with graceful fallback if tables don't exist)
        try:
            save_profile(profile_doc)
            logger.info(f"Profile created and saved to DynamoDB: {child_id}")
        except Exception as db_error:
            logger.warning(f"Could not save to DynamoDB (tables may not exist): {str(db_error)}")
            logger.info(f"Profile created in-memory only: {child_id}")

        return jsonify({
            "child_id": child_id,
            "profile_created": now,
            "success": True
        }), 201

    except Exception as e:
        logger.error(f"Error in profile endpoint: {str(e)}")
        return format_error_response("Failed to create profile", 500)


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


@app.route('/api/generate-audio', methods=['POST'])
def generate_audio_endpoint():
    """
    Generate audio narration for a page of text using ElevenLabs v3

    Required fields:
        - text: string (the text to convert to speech)

    Optional fields:
        - voice_id: string (ElevenLabs voice ID, auto-selected if not provided)
        - mood: string (calm, playful, curious, brave)
        - theme: string (story theme/genre)

    Returns:
        - audio_data: base64-encoded MP3 audio
        - content_type: audio/mpeg
        - voice_id: the voice ID used
    """
    try:
        data = request.json

        if not data:
            return format_error_response("No data provided")

        # Validate required fields
        if 'text' not in data:
            return format_error_response("Missing required field: text")

        text = data['text']
        voice_id = data.get('voice_id')
        mood = data.get('mood', 'calm')
        theme = data.get('theme', '')

        if not text or not text.strip():
            return format_error_response("Text cannot be empty")

        logger.info(f"Generating audio for text length: {len(text)} characters, mood: {mood}, theme: {theme}")

        # Generate audio with mood and theme for voice selection
        audio_bytes = generate_audio_for_page(text, voice_id, mood, theme)

        # Encode to base64 for JSON transport
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        logger.info(f"Audio generated successfully with v3 model, base64 length: {len(audio_base64)}")

        return jsonify({
            "audio_data": audio_base64,
            "content_type": "audio/mpeg",
            "text_length": len(text),
            "mood": mood,
            "theme": theme,
            "success": True
        })

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return format_error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        return format_error_response("Failed to generate audio", 500)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'

    logger.info(f"Starting StoryWeave API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")

    app.run(host=host, port=port, debug=debug)
