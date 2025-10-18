"""
Generate and save sample stories with prompts and metadata
Creates a comprehensive library of stories for testing and demonstration
"""
import sys
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import our modules
from story_generator import create_story, get_model_id
from prompts import build_prompt

def generate_story_collection():
    """
    Generate a collection of stories across all profiles, themes, and ages
    """
    # Configuration for story generation
    configurations = [
        # ADHD Profile Stories
        {"profile_type": "adhd", "age": 5, "theme": "space", "story_length": 5, "interests": ["rockets", "stars"]},
        {"profile_type": "adhd", "age": 7, "theme": "animals", "story_length": 10, "interests": ["dinosaurs", "dragons"]},
        {"profile_type": "adhd", "age": 9, "theme": "adventure", "story_length": 5, "interests": ["treasure", "exploring"]},

        # Autism Profile Stories
        {"profile_type": "autism", "age": 6, "theme": "animals", "story_length": 5, "interests": ["cats", "dogs"]},
        {"profile_type": "autism", "age": 8, "theme": "space", "story_length": 10, "interests": ["planets", "moon"]},
        {"profile_type": "autism", "age": 10, "theme": "adventure", "story_length": 5, "interests": ["trains", "bridges"]},

        # Anxiety Profile Stories
        {"profile_type": "anxiety", "age": 5, "theme": "animals", "story_length": 5, "interests": ["bunnies", "flowers"]},
        {"profile_type": "anxiety", "age": 7, "theme": "adventure", "story_length": 10, "interests": ["gardens", "nature"]},
        {"profile_type": "anxiety", "age": 9, "theme": "space", "story_length": 5, "interests": ["stars", "peaceful"]},
    ]

    story_collection = []
    model_id = get_model_id()

    print(f"Generating {len(configurations)} sample stories...")
    print(f"Using model: {model_id}")
    print("=" * 70)

    for i, config in enumerate(configurations, 1):
        print(f"\n[{i}/{len(configurations)}] Generating {config['profile_type'].upper()} story...")
        print(f"  Age: {config['age']}, Theme: {config['theme']}, Length: {config['story_length']}min")

        try:
            # Build the prompt
            prompt = build_prompt(
                profile_type=config['profile_type'],
                age=config['age'],
                theme=config['theme'],
                interests=config['interests'],
                story_length=config['story_length']
            )

            # Generate the story
            result = create_story(
                profile_type=config['profile_type'],
                age=config['age'],
                theme=config['theme'],
                interests=config['interests'],
                story_length=config['story_length']
            )

            # Create story entry
            story_entry = {
                "story_number": i,
                "metadata": {
                    "profile_type": config['profile_type'],
                    "age": config['age'],
                    "theme": config['theme'],
                    "story_length_minutes": config['story_length'],
                    "interests": config['interests'],
                    "model_used": model_id,
                    "model_tier": os.environ.get('AWS_BEDROCK_MODEL_TIER', 'cheap'),
                    "generated_at": datetime.now().isoformat(),
                    "success": result.get('success', False),
                    "fallback_used": result.get('fallback', False)
                },
                "prompt": prompt,
                "story": result['story'],
                "statistics": {
                    "character_count": len(result['story']),
                    "word_count": len(result['story'].split()),
                    "sentence_count": len([s for s in result['story'].split('.') if s.strip()]),
                    "avg_words_per_sentence": round(
                        len(result['story'].split()) / max(len([s for s in result['story'].split('.') if s.strip()]), 1),
                        1
                    )
                }
            }

            story_collection.append(story_entry)

            print(f"  ✓ Generated ({story_entry['statistics']['character_count']} chars, "
                  f"{story_entry['statistics']['avg_words_per_sentence']} words/sentence)")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            story_collection.append({
                "story_number": i,
                "metadata": config,
                "error": str(e),
                "prompt": None,
                "story": None
            })

    return story_collection


def save_stories(story_collection, output_dir="sample_stories"):
    """
    Save story collection to multiple formats
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save as JSON (complete data)
    json_file = os.path.join(output_dir, f"stories_{timestamp}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(story_collection, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved JSON: {json_file}")

    # Save as Markdown (readable format)
    md_file = os.path.join(output_dir, f"stories_{timestamp}.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# StoryWeave Sample Stories\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model:** {story_collection[0]['metadata']['model_used'] if story_collection else 'Unknown'}\n")
        f.write(f"**Total Stories:** {len(story_collection)}\n\n")
        f.write("---\n\n")

        for story in story_collection:
            if story.get('error'):
                continue

            metadata = story['metadata']
            stats = story['statistics']

            f.write(f"## Story #{story['story_number']}: {metadata['profile_type'].upper()} Profile\n\n")
            f.write(f"**Configuration:**\n")
            f.write(f"- Profile: {metadata['profile_type'].title()}\n")
            f.write(f"- Age: {metadata['age']} years\n")
            f.write(f"- Theme: {metadata['theme'].title()}\n")
            f.write(f"- Length: {metadata['story_length_minutes']} minutes\n")
            f.write(f"- Interests: {', '.join(metadata['interests'])}\n")
            f.write(f"- Model: {metadata['model_used']}\n\n")

            f.write(f"**Statistics:**\n")
            f.write(f"- Characters: {stats['character_count']}\n")
            f.write(f"- Words: {stats['word_count']}\n")
            f.write(f"- Sentences: {stats['sentence_count']}\n")
            f.write(f"- Avg words/sentence: {stats['avg_words_per_sentence']}\n\n")

            f.write(f"### Prompt Used\n\n")
            f.write("```\n")
            f.write(story['prompt'])
            f.write("\n```\n\n")

            f.write(f"### Generated Story\n\n")
            f.write(story['story'])
            f.write("\n\n---\n\n")

    print(f"✓ Saved Markdown: {md_file}")

    # Save individual story files
    for story in story_collection:
        if story.get('error'):
            continue

        metadata = story['metadata']
        story_filename = f"story_{story['story_number']:02d}_{metadata['profile_type']}_{metadata['theme']}_age{metadata['age']}.txt"
        story_file = os.path.join(output_dir, story_filename)

        with open(story_file, 'w', encoding='utf-8') as f:
            f.write(story['story'])

    print(f"✓ Saved {len([s for s in story_collection if not s.get('error')])} individual story files")

    return json_file, md_file


def generate_summary(story_collection):
    """
    Generate a summary of the story collection
    """
    print("\n" + "=" * 70)
    print("STORY COLLECTION SUMMARY")
    print("=" * 70)

    successful = [s for s in story_collection if not s.get('error')]
    failed = [s for s in story_collection if s.get('error')]

    print(f"\nTotal Stories: {len(story_collection)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")

    if successful:
        print("\nBy Profile Type:")
        for profile in ['adhd', 'autism', 'anxiety']:
            profile_stories = [s for s in successful if s['metadata']['profile_type'] == profile]
            if profile_stories:
                avg_words = sum(s['statistics']['avg_words_per_sentence'] for s in profile_stories) / len(profile_stories)
                print(f"  {profile.upper():8s}: {len(profile_stories)} stories (avg {avg_words:.1f} words/sentence)")

        print("\nBy Theme:")
        for theme in ['space', 'animals', 'adventure']:
            theme_stories = [s for s in successful if s['metadata']['theme'] == theme]
            if theme_stories:
                print(f"  {theme.title():10s}: {len(theme_stories)} stories")

        total_chars = sum(s['statistics']['character_count'] for s in successful)
        total_words = sum(s['statistics']['word_count'] for s in successful)

        print(f"\nTotal Content Generated:")
        print(f"  Characters: {total_chars:,}")
        print(f"  Words: {total_words:,}")
        print(f"  Average story length: {total_chars // len(successful):,} characters")


if __name__ == "__main__":
    print("=" * 70)
    print("STORYWEAVE SAMPLE STORY GENERATOR")
    print("=" * 70)

    # Generate stories
    story_collection = generate_story_collection()

    # Save stories
    json_file, md_file = save_stories(story_collection)

    # Generate summary
    generate_summary(story_collection)

    print("\n" + "=" * 70)
    print("✓ COMPLETE")
    print("=" * 70)
    print(f"\nFiles saved in: ./sample_stories/")
    print(f"  - JSON (full data): {os.path.basename(json_file)}")
    print(f"  - Markdown (readable): {os.path.basename(md_file)}")
    print(f"  - Individual story files: story_*.txt")
    print()
