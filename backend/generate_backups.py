#!/usr/bin/env python3
"""
Generate high-quality backup stories for all profiles
These stories can be used as fallbacks when API calls fail
"""
import os
import json
from datetime import datetime
from pathlib import Path

# Force use of Claude Sonnet 4.5
os.environ['AWS_BEDROCK_MODEL_TIER'] = 'medium'

from story_generator import create_story
from prompts import build_prompt

# Define 5 diverse story configurations
BACKUP_STORIES = [
    {
        "name": "adhd_space_adventure",
        "profile": "adhd",
        "age": 7,
        "theme": "space",
        "interests": ["rockets", "stars", "astronauts"],
        "length": 5
    },
    {
        "name": "autism_ocean_exploration",
        "profile": "autism",
        "age": 8,
        "theme": "ocean",
        "interests": ["fish", "dolphins", "coral"],
        "length": 10
    },
    {
        "name": "anxiety_forest_calm",
        "profile": "anxiety",
        "age": 6,
        "theme": "forest",
        "interests": ["trees", "birds", "nature"],
        "length": 5
    },
    {
        "name": "general_magic_adventure",
        "profile": "general",
        "age": 8,
        "theme": "magic",
        "interests": ["wizards", "potions", "friendship"],
        "length": 10
    },
    {
        "name": "adhd_dinosaur_discovery",
        "profile": "adhd",
        "age": 6,
        "theme": "dinosaurs",
        "interests": ["T-Rex", "fossils", "adventure"],
        "length": 5
    }
]

def main():
    print("=" * 60)
    print("  Generating High-Quality Backup Stories")
    print("=" * 60)
    print(f"\nUsing Claude Sonnet 4.5 via Inference Profile")
    print(f"Total stories to generate: {len(BACKUP_STORIES)}\n")

    # Create output directory
    output_dir = Path("backup_stories")
    output_dir.mkdir(exist_ok=True)

    all_stories = []

    for i, config in enumerate(BACKUP_STORIES, 1):
        print(f"\n[{i}/{len(BACKUP_STORIES)}] Generating: {config['name']}")
        print(f"  Profile: {config['profile'].upper()}")
        print(f"  Age: {config['age']}, Theme: {config['theme']}")
        print(f"  Length: {config['length']} minutes")

        try:
            # Generate the story
            result = create_story(
                profile_type=config['profile'],
                age=config['age'],
                theme=config['theme'],
                interests=config['interests'],
                story_length=config['length']
            )

            if result.get('success'):
                print(f"  ✓ Generated ({len(result['story'])} chars)")

                # Get the prompt used
                prompt = build_prompt(
                    config['profile'],
                    config['age'],
                    config['theme'],
                    config['interests'],
                    config['length']
                )

                # Build story data
                story_data = {
                    "name": config['name'],
                    "profile": config['profile'],
                    "age": config['age'],
                    "theme": config['theme'],
                    "interests": config['interests'],
                    "length": config['length'],
                    "story": result['story'],
                    "prompt": prompt,
                    "generated_at": datetime.now().isoformat()
                }

                all_stories.append(story_data)

                # Save individual story
                story_file = output_dir / f"{config['name']}.txt"
                with open(story_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {config['name'].replace('_', ' ').title()}\n\n")
                    f.write(result['story'])
                print(f"  ✓ Saved: {story_file}")

            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    # Save all stories as JSON
    if all_stories:
        json_file = output_dir / "all_backup_stories.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_stories, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 60)
        print(f"✓ Successfully generated {len(all_stories)} backup stories")
        print(f"✓ Saved to: {output_dir}/")
        print(f"✓ JSON compilation: {json_file}")
        print("=" * 60)
    else:
        print("\n✗ No stories were generated successfully")

if __name__ == "__main__":
    main()
