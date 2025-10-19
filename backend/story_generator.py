"""
AWS Bedrock integration for story generation
Handles model selection, API calls, and retry logic
"""
import boto3
import json
import os
import time
import logging
from botocore.exceptions import ClientError
from prompts import build_prompt, FALLBACK_STORIES

logger = logging.getLogger(__name__)

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-west-2')
)

# Model configuration - Claude 4.x Series using Inference Profiles
MODEL_TIERS = {
    'cheap': os.environ.get('AWS_BEDROCK_MODEL_CHEAP', 'anthropic.claude-haiku-4-5-20251001-v1:0'),
    'medium': os.environ.get('AWS_BEDROCK_MODEL_MEDIUM', 'arn:aws:bedrock:us-west-2:296062573602:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0'),
    'quality': os.environ.get('AWS_BEDROCK_MODEL_QUALITY', 'arn:aws:bedrock:us-west-2:296062573602:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0'),
    'expensive': os.environ.get('AWS_BEDROCK_MODEL_EXPENSIVE', 'anthropic.claude-opus-4-1-20250805-v1:0')
}


def get_model_id():
    """Get the current model ID based on tier setting"""
    tier = os.environ.get('AWS_BEDROCK_MODEL_TIER', 'cheap')
    model_id = MODEL_TIERS.get(tier, MODEL_TIERS['cheap'])
    logger.info(f"Using model tier '{tier}': {model_id}")
    return model_id


def generate_story(prompt, max_tokens=None, temperature=None):
    """
    Call AWS Bedrock to generate a story

    Args:
        prompt: The complete prompt string
        max_tokens: Maximum tokens to generate (default from env)
        temperature: Temperature setting (default from env)

    Returns:
        dict with 'success', 'story', and optional 'error' keys
    """
    if max_tokens is None:
        max_tokens = int(os.environ.get('AWS_BEDROCK_MAX_TOKENS', 1500))

    if temperature is None:
        temperature = float(os.environ.get('AWS_BEDROCK_TEMPERATURE', 0.7))

    model_id = get_model_id()

    try:
        # Claude models use Messages API
        # Note: Claude 4.x models don't allow both temperature and top_p
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature
        })

        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )

        # Parse response
        response_body = json.loads(response['body'].read())

        # Extract story text from Claude response
        story_text = response_body['content'][0]['text']

        logger.info(f"Story generated successfully ({len(story_text)} chars)")

        return {
            "success": True,
            "story": story_text.strip(),
            "tokens_used": response_body.get('usage', {})
        }

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Bedrock error ({error_code}): {error_message}")

        return {
            "success": False,
            "error": error_code,
            "error_message": error_message,
            "story": None
        }

    except Exception as e:
        logger.error(f"Unexpected error generating story: {str(e)}")
        return {
            "success": False,
            "error": "UnknownError",
            "error_message": str(e),
            "story": None
        }


def generate_story_with_retry(prompt, profile_type, max_retries=3):
    """
    Generate story with automatic retry on failure

    Args:
        prompt: The complete prompt string
        profile_type: Cognitive profile type for fallback story
        max_retries: Maximum number of retry attempts

    Returns:
        dict with 'success' and 'story' keys
    """
    for attempt in range(max_retries):
        result = generate_story(prompt)

        if result["success"]:
            return result

        # Log the failure
        logger.warning(f"Story generation attempt {attempt + 1} failed: {result.get('error')}")

        # Don't wait after the last attempt
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.info(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)

    # All retries failed, return fallback story
    logger.error(f"All {max_retries} attempts failed, using fallback story")
    fallback_story = FALLBACK_STORIES.get(profile_type, FALLBACK_STORIES['adhd'])

    return {
        "success": False,
        "story": fallback_story,
        "fallback": True,
        "error": "MaxRetriesExceeded"
    }


def create_story(profile_type, age, theme, interests, story_length):
    """
    High-level function to create a story

    Args:
        profile_type: 'adhd', 'autism', or 'anxiety'
        age: child's age
        theme: story theme
        interests: list of interests
        story_length: length in minutes

    Returns:
        dict with 'success' and 'story' keys
    """
    try:
        # Build the prompt
        prompt = build_prompt(profile_type, age, theme, interests, story_length)
        logger.info(f"Creating {profile_type} story for age {age}, theme: {theme}")

        # Generate with retry
        result = generate_story_with_retry(prompt, profile_type)

        return result

    except Exception as e:
        logger.error(f"Error in create_story: {str(e)}")
        fallback_story = FALLBACK_STORIES.get(profile_type, FALLBACK_STORIES['adhd'])

        return {
            "success": False,
            "story": fallback_story,
            "fallback": True,
            "error": str(e)
        }


def handle_generation_error(error):
    """
    Convert error codes to user-friendly messages

    Args:
        error: Error code or exception

    Returns:
        User-friendly error message
    """
    error_messages = {
        "ThrottlingException": "Too many requests. Please wait a moment and try again.",
        "ValidationException": "Invalid request. Please check your story parameters.",
        "ServiceUnavailableException": "Service temporarily unavailable. Using cached story.",
        "ModelTimeoutException": "Story generation took too long. Please try a shorter story.",
        "AccessDeniedException": "AWS credentials issue. Please contact support.",
        "ResourceNotFoundException": "Model not found. Please check configuration.",
        "MaxRetriesExceeded": "Unable to generate story. Using pre-written story instead."
    }

    error_type = str(error)
    return error_messages.get(error_type, "An error occurred. Please try again.")


if __name__ == "__main__":
    # Test story generation
    print("Testing story generation...")

    test_result = create_story(
        profile_type="adhd",
        age=7,
        theme="space",
        interests=["rockets", "astronauts"],
        story_length=5
    )

    if test_result["success"]:
        print("\n✓ Story generated successfully!")
        print(f"\nStory preview ({len(test_result['story'])} chars):")
        print(test_result['story'][:200] + "...")
    else:
        print(f"\n✗ Story generation failed: {test_result.get('error')}")
        print("Using fallback story")
