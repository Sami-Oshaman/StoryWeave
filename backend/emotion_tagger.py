"""
Emotion Tagging Service using Claude 4.5 Haiku
Adds emotional expression tags to story text for enhanced TTS narration
"""
import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Initialize Bedrock client
bedrock = boto3.client(
    'bedrock-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-west-2')
)

# Claude 4.5 Haiku model for fast emotion tagging
HAIKU_MODEL_ID = "anthropic.claude-haiku-4-5-20251001-v1:0"


def add_emotion_tags(text, mood="calm", theme=""):
    """
    Add emotion tags to story text using Claude 4.5 Haiku

    Tags include things like [gentle laughter], [excited], [whisper], etc.
    These tags enhance the expressiveness of TTS narration.

    Args:
        text (str): Original story text
        mood (str): Story mood (calm, playful, curious, brave)
        theme (str): Story theme/genre

    Returns:
        str: Text with emotion tags added in brackets
    """
    if not text or not text.strip():
        return text

    try:
        logger.info(f"Adding emotion tags to text ({len(text)} chars) with mood={mood}")

        # Build prompt for Claude Haiku
        prompt = f"""You are an expert at adding emotional expression tags to children's bedtime stories for text-to-speech narration.

Your task: Add emotion tags in brackets [like this] throughout the story to guide the narrator's voice. These tags tell the voice actor how to perform each line.

Common emotion tags to use:
- [gentle laughter] - soft, kind laughter
- [excited] - enthusiastic, energetic tone
- [whisper] - quiet, soft voice
- [happy] - joyful, cheerful tone
- [wonder] - amazed, curious voice
- [calm] - peaceful, soothing tone
- [sleepy] - drowsy, yawning quality
- [playful] - fun, bouncy delivery
- [warm] - affectionate, loving tone
- [giggle] - small, light laughter
- [sigh] - content, relaxed breathing
- [soft] - gentle, tender voice

Story mood: {mood}
Story theme: {theme}

Guidelines:
1. Add 1-3 emotion tags per paragraph (don't overdo it)
2. Place tags at the START of sentences or phrases where emotion shifts
3. Match the overall mood ({mood}) - use calming tags for calm stories, excited tags for playful stories
4. End stories with sleepy/drowsy tags to help children wind down
5. Keep the original text EXACTLY the same - only add tags in brackets
6. Do NOT add explanations or comments - just return the tagged text

Original story:
{text}

Return ONLY the story with emotion tags added. No explanations, no extra text."""

        # Call Claude Haiku via Bedrock
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.3,  # Low temperature for consistent tagging
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId=HAIKU_MODEL_ID,
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )

        response_body = json.loads(response['body'].read())
        tagged_text = response_body['content'][0]['text'].strip()

        logger.info(f"Successfully added emotion tags ({len(tagged_text)} chars)")

        return tagged_text

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"AWS Bedrock error adding emotion tags: {error_code} - {str(e)}")
        # Return original text on error
        return text
    except Exception as e:
        logger.error(f"Error adding emotion tags: {str(e)}")
        # Return original text on error
        return text


def add_emotion_tags_to_pages(pages, mood="calm", theme=""):
    """
    Add emotion tags to multiple story pages

    Args:
        pages (list): List of page text strings
        mood (str): Story mood
        theme (str): Story theme

    Returns:
        list: List of emotion-tagged page texts
    """
    if not pages:
        return []

    # Combine all pages into one text for consistent emotion tagging
    combined_text = "\n\n".join(pages)

    # Get emotion-tagged version
    tagged_combined = add_emotion_tags(combined_text, mood, theme)

    # Split back into pages
    tagged_pages = tagged_combined.split("\n\n")

    # Ensure we have the same number of pages
    if len(tagged_pages) != len(pages):
        logger.warning(f"Page count mismatch after tagging: {len(pages)} -> {len(tagged_pages)}, using original")
        return pages

    return tagged_pages
