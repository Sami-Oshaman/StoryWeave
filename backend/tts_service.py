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

# Available narrator voices - randomly selected for variety
NARRATOR_VOICES = [
    "dAcds2QMcvmv86jQMC3Y",  # Jayce
    "RKCbSROXui75bk1SVpy8",  # Shaun
    "7p1Ofvcwsv7UBPoFNcpI",  # Julian
    "L1aJrPa7pLJEyYlh3Ilq",  # Oliver
]

# Voice mapping based on mood and theme for children's stories
# Now using random selection from narrator pool
VOICE_PROFILES = {
    # Calm, gentle voices
    "calm": {
        "default": None,  # Will be randomly selected
        "space": None,
        "animals": None,
        "adventure": None,
    },
    # Playful, energetic voices
    "playful": {
        "default": None,
        "space": None,
        "animals": None,
        "adventure": None,
    },
    # Curious, wondering voices
    "curious": {
        "default": None,
        "space": None,
        "animals": None,
        "adventure": None,
    },
    # Brave, confident voices
    "brave": {
        "default": None,
        "space": None,
        "animals": None,
        "adventure": None,
    },
}

def select_voice(mood="calm", theme=""):
    """
    Randomly select a narrator voice from the available pool

    Args:
        mood (str): Story mood (calm, playful, curious, brave) - currently not used, all random
        theme (str): Story theme/genre - currently not used, all random

    Returns:
        str: Voice ID to use for narration
    """
    import random

    # Randomly select from narrator voices for variety
    voice_id = random.choice(NARRATOR_VOICES)

    logger.info(f"Randomly selected narrator voice: {voice_id}")
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
