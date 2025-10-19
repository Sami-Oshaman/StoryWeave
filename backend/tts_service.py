"""
ElevenLabs Text-to-Speech Service
Handles conversion of story text to audio using ElevenLabs API
"""
import os
import logging
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

logger = logging.getLogger(__name__)

# Initialize ElevenLabs client
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')

if not ELEVENLABS_API_KEY:
    logger.warning("ELEVENLABS_API_KEY not found in environment variables")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Voice mapping based on mood and theme for children's stories
# Using ElevenLabs pre-made voices optimized for storytelling
VOICE_PROFILES = {
    # Calm, gentle voices
    "calm": {
        "default": "EXAVITQu4vr4xnSDxMaL",  # Sarah - warm, soothing female
        "space": "pNInz6obpgDQGcFmaJgB",    # Adam - calm, clear narrator
        "animals": "EXAVITQu4vr4xnSDxMaL",  # Sarah - gentle for animal stories
        "adventure": "Xb7hH8MSUJpSbSDYk0k2", # Alice - soft adventure voice
    },
    # Playful, energetic voices
    "playful": {
        "default": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - bright, cheerful
        "space": "pNInz6obpgDQGcFmaJgB",    # Adam - enthusiastic explorer
        "animals": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - fun, animated
        "adventure": "N2lVS1w4EtoT3dr4eOWO",  # Callum - energetic storyteller
    },
    # Curious, wondering voices
    "curious": {
        "default": "Xb7hH8MSUJpSbSDYk0k2", # Alice - curious, thoughtful
        "space": "pNInz6obpgDQGcFmaJgB",    # Adam - scientific wonder
        "animals": "EXAVITQu4vr4xnSDxMaL",  # Sarah - gentle curiosity
        "adventure": "Xb7hH8MSUJpSbSDYk0k2", # Alice - exploratory
    },
    # Brave, confident voices
    "brave": {
        "default": "pNInz6obpgDQGcFmaJgB",  # Adam - strong, confident
        "space": "pNInz6obpgDQGcFmaJgB",    # Adam - heroic explorer
        "animals": "N2lVS1w4EtoT3dr4eOWO",  # Callum - brave adventurer
        "adventure": "N2lVS1w4EtoT3dr4eOWO", # Callum - courageous hero
    },
}

def select_voice(mood="calm", theme=""):
    """
    Select the most appropriate voice based on story mood and theme

    Args:
        mood (str): Story mood (calm, playful, curious, brave)
        theme (str): Story theme/genre (space, animals, adventure, etc.)

    Returns:
        str: Voice ID to use for narration
    """
    mood = mood.lower() if mood else "calm"
    theme_key = None

    # Normalize theme to match our categories
    theme_lower = theme.lower() if theme else ""
    if "space" in theme_lower or "rocket" in theme_lower or "planet" in theme_lower:
        theme_key = "space"
    elif "animal" in theme_lower or "forest" in theme_lower or "jungle" in theme_lower:
        theme_key = "animals"
    elif "adventure" in theme_lower or "quest" in theme_lower or "journey" in theme_lower:
        theme_key = "adventure"

    # Get voice profile for mood
    mood_profile = VOICE_PROFILES.get(mood, VOICE_PROFILES["calm"])

    # Select voice based on theme, or use default for this mood
    voice_id = mood_profile.get(theme_key, mood_profile["default"])

    logger.info(f"Selected voice for mood='{mood}', theme='{theme}': {voice_id}")
    return voice_id

def generate_audio(text, voice_id=None, mood="calm", theme=""):
    """
    Generate audio from text using ElevenLabs API v3

    Args:
        text (str): The text to convert to speech
        voice_id (str, optional): Voice ID to use. If not provided, selects based on mood/theme
        mood (str, optional): Story mood (calm, playful, curious, brave)
        theme (str, optional): Story theme/genre

    Returns:
        bytes: Audio data in MP3 format

    Raises:
        Exception: If audio generation fails
    """
    if not ELEVENLABS_API_KEY:
        raise Exception("ElevenLabs API key not configured")

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    try:
        logger.info(f"Generating audio for text of length {len(text)} characters")

        # Select voice based on mood and theme if not explicitly provided
        if not voice_id:
            voice_id = select_voice(mood, theme)

        logger.info(f"Using voice ID: {voice_id}")

        # Generate audio using the client with Turbo v3 model
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_turbo_v2_5",  # Latest v3 model - faster and higher quality
            voice_settings=VoiceSettings(
                stability=0.6,  # Slightly more stable for children's narration
                similarity_boost=0.8,  # Higher clarity for young listeners
                style=0.3,  # Slight expressiveness for storytelling
                use_speaker_boost=True  # Enhance clarity and presence
            )
        )

        # Collect audio chunks
        audio_bytes = b''
        for chunk in audio_generator:
            if chunk:
                audio_bytes += chunk

        logger.info(f"Audio generated successfully with v3 model, size: {len(audio_bytes)} bytes")
        return audio_bytes

    except Exception as e:
        logger.error(f"Failed to generate audio: {str(e)}")
        raise


def get_available_voices():
    """
    Get list of available voices from ElevenLabs

    Returns:
        list: List of voice dictionaries with id, name, and other metadata
    """
    if not ELEVENLABS_API_KEY:
        raise Exception("ElevenLabs API key not configured")

    try:
        voices = client.voices.get_all()
        return voices.voices
    except Exception as e:
        logger.error(f"Failed to get voices: {str(e)}")
        raise


def generate_audio_for_page(page_text, voice_id=None, mood="calm", theme=""):
    """
    Generate audio for a single page of the story
    Convenience wrapper around generate_audio

    Args:
        page_text (str): The text of the page
        voice_id (str, optional): Voice ID to use
        mood (str, optional): Story mood
        theme (str, optional): Story theme

    Returns:
        bytes: Audio data in MP3 format
    """
    return generate_audio(page_text, voice_id, mood, theme)
