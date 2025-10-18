#!/usr/bin/env python3
"""
Interactive Story Generation Test Tool
Prompts user for all parameters, generates story, and saves to file + database
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Force use of Claude Sonnet 4.5 (medium tier with inference profile ARN)
os.environ['AWS_BEDROCK_MODEL_TIER'] = 'medium'

# Import our modules
from story_generator import create_story, get_model_id
from prompts import build_prompt
from database import save_story

def print_header(text):
    """Print a styled header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ {text}")

def get_profile_type():
    """Prompt for cognitive profile type"""
    print("\n📋 Select Story Profile:")
    print("  1. ADHD (short sentences, high→calm energy)")
    print("  2. Autism (First-Then-Finally structure)")
    print("  3. Anxiety (calming, gentle, safe)")
    print("  4. General (creative freedom, natural flow)")

    while True:
        choice = input("\nEnter choice (1-4): ").strip()
        if choice == "1":
            return "adhd"
        elif choice == "2":
            return "autism"
        elif choice == "3":
            return "anxiety"
        elif choice == "4":
            return "general"
        else:
            print_error("Invalid choice. Please enter 1, 2, 3, or 4.")

def get_age():
    """Prompt for child's age"""
    while True:
        age_input = input("\n👶 Enter child's age (3-12): ").strip()
        try:
            age = int(age_input)
            if 3 <= age <= 12:
                return age
            else:
                print_error("Age must be between 3 and 12.")
        except ValueError:
            print_error("Please enter a valid number.")

def get_theme():
    """Prompt for story theme"""
    print("\n🎨 Popular themes:")
    print("  • space, ocean, forest, animals, dinosaurs")
    print("  • magic, adventure, friendship, family")
    print("  • robots, vehicles, nature, bedtime")

    theme = input("\nEnter theme: ").strip()
    if not theme:
        theme = "adventure"
        print_info(f"Using default theme: {theme}")
    return theme

def get_interests():
    """Prompt for child's interests"""
    print("\n⭐ Enter child's interests (comma-separated):")
    print("  Example: rockets, astronauts, stars")

    interests_input = input("\nInterests: ").strip()
    if not interests_input:
        interests = ["adventure", "friends"]
        print_info(f"Using default interests: {', '.join(interests)}")
    else:
        interests = [i.strip() for i in interests_input.split(",") if i.strip()]

    return interests

def get_story_length():
    """Prompt for story length"""
    print("\n⏱️  Story length:")
    print("  1. Short (5 minutes)")
    print("  2. Medium (10 minutes)")
    print("  3. Long (15 minutes)")

    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        if choice == "1":
            return 5
        elif choice == "2":
            return 10
        elif choice == "3":
            return 15
        else:
            print_error("Invalid choice. Please enter 1, 2, or 3.")

def save_to_file(story_data, output_dir="test_stories"):
    """Save story to file with all metadata"""
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    profile = story_data['metadata']['profile_type']
    theme = story_data['metadata']['theme'].replace(" ", "_")
    filename = f"story_{timestamp}_{profile}_{theme}"

    # Save as JSON (full metadata)
    json_path = Path(output_dir) / f"{filename}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, indent=2, ensure_ascii=False)
    print_success(f"Saved JSON: {json_path}")

    # Save as TXT (story only)
    txt_path = Path(output_dir) / f"{filename}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"StoryWeave - Generated Story\n")
        f.write(f"{'=' * 60}\n\n")
        f.write(f"Profile: {story_data['metadata']['profile_type'].upper()}\n")
        f.write(f"Age: {story_data['metadata']['age']}\n")
        f.write(f"Theme: {story_data['metadata']['theme']}\n")
        f.write(f"Interests: {', '.join(story_data['metadata']['interests'])}\n")
        f.write(f"Length: {story_data['metadata']['story_length']} minutes\n")
        f.write(f"Model: {story_data['metadata']['model_used']}\n")
        f.write(f"Generated: {story_data['metadata']['generated_at']}\n")
        f.write(f"\n{'=' * 60}\n\n")
        f.write("PROMPT USED:\n")
        f.write(f"{'-' * 60}\n")
        f.write(f"{story_data['prompt']}\n")
        f.write(f"{'-' * 60}\n\n")
        f.write("STORY:\n")
        f.write(f"{'-' * 60}\n")
        f.write(f"{story_data['story']}\n")
        f.write(f"{'-' * 60}\n\n")
        f.write(f"Statistics:\n")
        f.write(f"  - Characters: {story_data['statistics']['character_count']}\n")
        f.write(f"  - Words: {story_data['statistics']['word_count']}\n")
        f.write(f"  - Sentences: {story_data['statistics']['sentence_count']}\n")
        f.write(f"  - Paragraphs: {story_data['statistics']['paragraph_count']}\n")
        if story_data['statistics']['avg_sentence_length']:
            f.write(f"  - Avg sentence length: {story_data['statistics']['avg_sentence_length']:.1f} words\n")
    print_success(f"Saved TXT: {txt_path}")

    # Save as Markdown (formatted)
    md_path = Path(output_dir) / f"{filename}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# StoryWeave Generated Story\n\n")
        f.write(f"## Metadata\n\n")
        f.write(f"- **Profile:** {story_data['metadata']['profile_type'].upper()}\n")
        f.write(f"- **Age:** {story_data['metadata']['age']}\n")
        f.write(f"- **Theme:** {story_data['metadata']['theme']}\n")
        f.write(f"- **Interests:** {', '.join(story_data['metadata']['interests'])}\n")
        f.write(f"- **Length:** {story_data['metadata']['story_length']} minutes\n")
        f.write(f"- **Model:** `{story_data['metadata']['model_used']}`\n")
        f.write(f"- **Generated:** {story_data['metadata']['generated_at']}\n\n")
        f.write(f"## Prompt\n\n")
        f.write(f"```\n{story_data['prompt']}\n```\n\n")
        f.write(f"## Story\n\n")
        f.write(f"{story_data['story']}\n\n")
        f.write(f"## Statistics\n\n")
        f.write(f"- Characters: {story_data['statistics']['character_count']}\n")
        f.write(f"- Words: {story_data['statistics']['word_count']}\n")
        f.write(f"- Sentences: {story_data['statistics']['sentence_count']}\n")
        f.write(f"- Paragraphs: {story_data['statistics']['paragraph_count']}\n")
        if story_data['statistics']['avg_sentence_length']:
            f.write(f"- Average sentence length: {story_data['statistics']['avg_sentence_length']:.1f} words\n")
    print_success(f"Saved MD: {md_path}")

    return json_path, txt_path, md_path

def save_to_database(story_data):
    """Try to save to DynamoDB, skip if fails"""
    try:
        print("\n💾 Attempting to save to DynamoDB...")

        # Generate a test child_id
        child_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save to database
        save_story(
            child_id=child_id,
            story_text=story_data['story'],
            profile_type=story_data['metadata']['profile_type'],
            theme=story_data['metadata']['theme'],
            age=story_data['metadata']['age'],
            interests=story_data['metadata']['interests'],
            story_length=story_data['metadata']['story_length']
        )

        print_success(f"Saved to DynamoDB (child_id: {child_id})")
        return True
    except Exception as e:
        print_error(f"Database save failed (skipping): {str(e)}")
        return False

def calculate_statistics(story_text):
    """Calculate story statistics"""
    # Basic counts
    char_count = len(story_text)
    word_count = len(story_text.split())

    # Sentence count (approximate)
    sentence_endings = ['.', '!', '?']
    sentence_count = sum(story_text.count(end) for end in sentence_endings)

    # Paragraph count
    paragraph_count = len([p for p in story_text.split('\n\n') if p.strip()])

    # Average sentence length
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

    return {
        'character_count': char_count,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'paragraph_count': paragraph_count,
        'avg_sentence_length': avg_sentence_length
    }

def main():
    """Main interactive test function"""
    print_header("StoryWeave Interactive Story Generator")
    print("\nThis tool will help you test story generation with custom parameters.")
    print("All generated stories will be saved to files and optionally to database.")
    print(f"\n🤖 Using Model: Claude Sonnet 4.5 (Inference Profile)")
    print(f"   ARN: {get_model_id()}")

    # Gather all parameters
    profile_type = get_profile_type()
    age = get_age()
    theme = get_theme()
    interests = get_interests()
    story_length = get_story_length()

    # Confirm parameters
    print_header("Story Parameters")
    print(f"Profile Type: {profile_type.upper()}")
    print(f"Age: {age}")
    print(f"Theme: {theme}")
    print(f"Interests: {', '.join(interests)}")
    print(f"Story Length: {story_length} minutes")
    print(f"Model: {get_model_id()}")

    confirm = input("\n✓ Generate story with these parameters? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\nCancelled.")
        return

    # Generate story
    print_header("Generating Story")
    print_info(f"Calling AWS Bedrock with {get_model_id()}...")

    try:
        result = create_story(profile_type, age, theme, interests, story_length)

        if not result.get('success'):
            print_error(f"Story generation failed: {result.get('error', 'Unknown error')}")
            if result.get('fallback'):
                print_info("Using fallback story instead")
            else:
                return

        print_success("Story generated successfully!")

        # Build the prompt that was used
        prompt = build_prompt(profile_type, age, theme, interests, story_length)

        # Calculate statistics
        stats = calculate_statistics(result['story'])

        # Prepare story data
        story_data = {
            'metadata': {
                'profile_type': profile_type,
                'age': age,
                'theme': theme,
                'interests': interests,
                'story_length': story_length,
                'model_used': get_model_id(),
                'generated_at': datetime.now().isoformat(),
                'success': result.get('success', False),
                'fallback': result.get('fallback', False)
            },
            'prompt': prompt,
            'story': result['story'],
            'statistics': stats
        }

        # Display preview
        print_header("Story Preview")
        print(result['story'][:300] + "..." if len(result['story']) > 300 else result['story'])

        # Display statistics
        print_header("Statistics")
        print(f"Characters: {stats['character_count']}")
        print(f"Words: {stats['word_count']}")
        print(f"Sentences: {stats['sentence_count']}")
        print(f"Paragraphs: {stats['paragraph_count']}")
        print(f"Avg sentence length: {stats['avg_sentence_length']:.1f} words")

        # Save to files
        print_header("Saving to Files")
        json_path, txt_path, md_path = save_to_file(story_data)

        # Try to save to database
        db_saved = save_to_database(story_data)

        # Final summary
        print_header("Test Complete!")
        print_success(f"Story generated for {profile_type.upper()} profile")
        print_success(f"Saved 3 files in test_stories/ directory")
        if db_saved:
            print_success("Saved to DynamoDB")
        else:
            print_info("Database save skipped (not critical)")

        print(f"\n📁 Files saved:")
        print(f"   • {json_path}")
        print(f"   • {txt_path}")
        print(f"   • {md_path}")

        print("\n✨ Test completed successfully!\n")

    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
