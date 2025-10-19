"""
Google Gemini 2.5 Flash Image (Nano Banana) integration
Generates child-friendly story illustrations
"""
import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Initialize Gemini client
def get_gemini_client():
    """Get Gemini client with API key from environment"""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    return genai.Client(api_key=api_key)

# Model ID for Gemini 2.5 Flash Image (Nano Banana)
IMAGE_MODEL_ID = 'gemini-2.5-flash-image'


def extract_character_description(story_text):
    """
    Extract character description from the beginning of the story for consistency

    Args:
        story_text: Full story text

    Returns:
        str: Concise character description or empty string
    """
    import re

    # Look for character descriptions in the first 500 characters
    intro = story_text[:500].lower()

    # Common character description patterns
    character_desc = ""

    # Look for main character with descriptors
    patterns = [
        r"(a|an|the) (little|young|small|tiny|brave|curious) (\w+) (named|called) (\w+)",
        r"(\w+) (was|is) a (little|young|small|tiny|brave|curious) (\w+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, intro)
        if match:
            # Extract key descriptive words
            words = match.group(0).split()
            # Get adjectives and nouns (skip articles)
            descriptors = [w for w in words if w not in ['a', 'an', 'the', 'was', 'is', 'named', 'called']]
            if len(descriptors) >= 2:
                character_desc = " ".join(descriptors[:4])  # Max 4 words
                break

    return character_desc


def create_child_friendly_prompt(story_excerpt, age, theme, character_description=""):
    """
    Create a child-friendly image prompt from story excerpt

    Args:
        story_excerpt: Text from the story to illustrate
        age: Child's age (for age-appropriate imagery)
        theme: Story theme
        character_description: Concise description of main character(s) for consistency

    Returns:
        str: Optimized prompt for image generation
    """
    # Base style for all children's book illustrations
    base_style = "children's book illustration, watercolor style, soft colors, whimsical, friendly, safe for children"

    # Age-appropriate adjustments
    if age <= 5:
        style = f"{base_style}, simple shapes, bright colors, very cute, gentle"
    elif age <= 8:
        style = f"{base_style}, detailed but clear, colorful, adventurous, engaging"
    else:
        style = f"{base_style}, detailed illustration, rich colors, captivating, age-appropriate"

    # Safety constraints
    safety = "IMPORTANT: No scary elements, no violence, no weapons, no dark themes. Only positive, uplifting, child-safe imagery."

    # Add character consistency instruction if we have a description
    character_note = ""
    if character_description:
        character_note = f"\nCharacter consistency: Main character is {character_description}. Keep this appearance consistent."

    # Create comprehensive prompt
    prompt = f"""Create a beautiful children's book illustration for this scene:

{story_excerpt}

Style: {style}
{character_note}
{safety}

The illustration should be warm, inviting, and appropriate for a {age}-year-old child's bedtime story."""

    return prompt


def generate_image(prompt):
    """
    Generate an image using Google Gemini 2.5 Flash Image

    Args:
        prompt: Text description of image to generate

    Returns:
        dict with 'success', 'image_data' (base64), and optional 'error' keys
    """
    try:
        client = get_gemini_client()

        logger.info(f"Generating image with Gemini 2.5 Flash: {prompt[:100]}...")

        # Create content with text prompt
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]

        # Configure for image generation
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )

        # Generate image (streaming to get binary data)
        image_data = None
        for chunk in client.models.generate_content_stream(
            model=IMAGE_MODEL_ID,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue

            # Extract image data
            if (chunk.candidates[0].content.parts[0].inline_data and
                chunk.candidates[0].content.parts[0].inline_data.data):
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                # Convert bytes to base64 string
                import base64
                image_data = base64.b64encode(inline_data.data).decode('utf-8')
                break

        if image_data:
            logger.info(f"Image generated successfully")
            return {
                "success": True,
                "image_data": image_data,  # Base64 encoded image
                "prompt": prompt
            }
        else:
            logger.error("No image data in response")
            return {
                "success": False,
                "error": "NoImageData",
                "error_message": "No image returned from model"
            }

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return {
            "success": False,
            "error": "ConfigurationError",
            "error_message": str(e)
        }

    except Exception as e:
        logger.error(f"Unexpected error generating image: {str(e)}")
        return {
            "success": False,
            "error": "UnknownError",
            "error_message": str(e)
        }


def generate_story_images(story_text, age, theme, num_images=3):
    """
    Generate multiple images for a story

    Args:
        story_text: Full story text
        age: Child's age
        theme: Story theme
        num_images: Number of images to generate

    Returns:
        list of dicts with image data and metadata
    """
    images = []

    # Extract character description once for consistency across all images
    character_description = extract_character_description(story_text)
    if character_description:
        logger.info(f"Extracted character description for consistency: '{character_description}'")

    # Split story into paragraphs
    paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip()]

    if len(paragraphs) == 0:
        logger.warning("No paragraphs found in story")
        return images

    # Calculate which paragraphs to illustrate
    if num_images >= len(paragraphs):
        # Illustrate all paragraphs
        selected_indices = list(range(len(paragraphs)))
    else:
        # Evenly distribute images across story
        step = len(paragraphs) / num_images
        selected_indices = [int(i * step) for i in range(num_images)]

    logger.info(f"Generating {len(selected_indices)} images for story with {len(paragraphs)} paragraphs")

    # Generate image for each selected paragraph
    for idx, para_idx in enumerate(selected_indices):
        paragraph = paragraphs[para_idx]

        # Create child-friendly prompt with character description for consistency
        prompt = create_child_friendly_prompt(paragraph, age, theme, character_description)

        logger.info(f"Generating image {idx + 1}/{len(selected_indices)} for paragraph {para_idx}")

        # Generate image
        result = generate_image(prompt)

        if result["success"]:
            images.append({
                "image_index": idx,
                "paragraph_index": para_idx,
                "image_data": result["image_data"],
                "prompt": result["prompt"],
                "character_description": character_description
            })
        else:
            logger.error(f"Failed to generate image {idx + 1}: {result.get('error')}")
            # Continue generating other images even if one fails

    logger.info(f"Successfully generated {len(images)}/{len(selected_indices)} images")

    return images


def extract_scene_description(paragraph, max_length=400):
    """
    Extract the most visual/descriptive part of a paragraph for image generation

    Args:
        paragraph: Text paragraph
        max_length: Maximum length of description

    Returns:
        str: Scene description optimized for image generation
    """
    # Remove dialogue (text in quotes)
    import re
    no_dialogue = re.sub(r'"[^"]*"', '', paragraph)
    no_dialogue = re.sub(r"'[^']*'", '', no_dialogue)

    # Get first few sentences (most important)
    sentences = [s.strip() for s in no_dialogue.split('.') if s.strip()]

    description = ""
    for sentence in sentences:
        if len(description) + len(sentence) + 2 <= max_length:
            description += sentence + ". "
        else:
            break

    return description.strip() if description else paragraph[:max_length]
