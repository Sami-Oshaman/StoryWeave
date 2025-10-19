"""
Cognitive profile prompt templates for story generation
Each profile uses distinct prompt engineering based on therapeutic principles
"""

# Theme elements for story generation
THEMES = {
    "space": {
        "elements": ["rocket", "stars", "planets", "moon", "astronaut", "space station"],
        "activities": ["flying", "exploring", "discovering", "floating", "observing"],
        "safe_objects": ["space helmet", "space suit", "spacecraft", "control panel"]
    },
    "animals": {
        "elements": ["forest", "meadow", "pond", "nest", "burrow", "tree"],
        "activities": ["playing", "exploring", "resting", "eating", "watching"],
        "safe_objects": ["soft grass", "cozy nest", "warm den", "gentle stream"]
    },
    "adventure": {
        "elements": ["path", "bridge", "garden", "treehouse", "meadow", "hill"],
        "activities": ["walking", "discovering", "building", "creating", "climbing"],
        "safe_objects": ["compass", "map", "backpack", "blanket", "lantern"]
    }
}


def calculate_sentence_count(minutes, profile_type, demo_mode=False):
    """
    Convert story length in minutes to approximate sentence count
    based on reading speed and profile type

    Args:
        minutes: Target story length in minutes
        profile_type: Cognitive profile type
        demo_mode: If True, generate a very short demo story (1-2 min, ~15 slides)
    """
    # Map neurotypical to general for calculations
    if profile_type == 'neurotypical':
        profile_type = 'general'

    # Demo mode: target 1.5 minutes regardless of profile
    if demo_mode:
        # Calculate for ~1.5 minutes to ensure we stay under 2 min
        minutes = 1.5
        # Return a fixed count that results in ~15 slides
        return 15

    words_per_minute = {
        "adhd": 80,      # Slower due to short sentences
        "autism": 100,   # Moderate pace
        "anxiety": 90,   # Slower, calming pace
        "general": 120   # Standard reading pace
    }

    avg_words_per_sentence = {
        "adhd": 6,       # Very short sentences
        "autism": 12,    # Medium sentences
        "anxiety": 15,   # Longer, flowing sentences
        "general": 14    # Natural variation
    }

    total_words = words_per_minute.get(profile_type, 100) * minutes
    sentence_count = total_words // avg_words_per_sentence.get(profile_type, 14)

    return max(sentence_count, 20)  # Minimum 20 sentences


def get_adhd_prompt(age, theme, interests, story_length, demo_mode=False):
    """Generate ADHD-specific prompt"""
    sentence_count = calculate_sentence_count(story_length, "adhd", demo_mode)
    theme_elements = ", ".join(THEMES.get(theme, THEMES["adventure"])["elements"])
    interest_list = ", ".join(interests) if interests else "exciting adventures"

    return f"""Generate a bedtime story for a {age}-year-old child with ADHD. Use these specific guidelines:

STRUCTURE REQUIREMENTS:
- Very short sentences (5-7 words maximum per sentence)
- Frequent paragraph breaks (every 2-3 sentences)
- Total of approximately {sentence_count} sentences
- Story gradually slows from high energy to calm

LANGUAGE STYLE:
- Action-oriented verbs (jump, run, fly, discover, zoom, blast)
- "Surprise" moments or hooks every 2-3 sentences to re-engage attention
- Direct questions to the reader (e.g., "What do you think happened next?")
- Concrete rewards or achievements for the main character
- NO long descriptive passages

THEME & CONTENT:
- Theme: {theme}
- Include these elements: {theme_elements}
- Child's interests: {interest_list}

PACING:
- Start with HIGH energy and excitement
- Gradually become CALMER toward the end
- End with peaceful, sleep-ready language

Example opening style: "Max saw a rocket. It was shiny and red. 'Wow!' he said."

Generate the complete story now, following these requirements exactly."""


def get_autism_prompt(age, theme, interests, story_length, demo_mode=False):
    """Generate Autism-specific prompt"""
    sentence_count = calculate_sentence_count(story_length, "autism", demo_mode)
    theme_elements = ", ".join(THEMES.get(theme, THEMES["adventure"])["elements"])
    interest_list = ", ".join(interests) if interests else "familiar, comforting things"

    return f"""Generate a bedtime story for a {age}-year-old child with autism. Use these specific guidelines:

STRUCTURE REQUIREMENTS:
- Clear "First-Then-Finally" structure (explicitly use these transition words throughout)
- Total of approximately {sentence_count} sentences
- Predictable story arc with NO sudden surprises

LANGUAGE STYLE:
- Concrete, literal language ONLY (NO metaphors, idioms, or figurative language)
- Consistent character behaviors (characters must act predictably)
- Clear cause-and-effect sequences (use "because" and "so" to show connections)
- Repetitive comforting phrases throughout the story
- Specific routines described step-by-step

THEME & CONTENT:
- Theme: {theme}
- Include these elements: {theme_elements}
- Child's interests: {interest_list}

PATTERN REQUIREMENTS:
- Characters must behave logically and consistently
- Use counting and sequencing (e.g., "One, two, three, four, five")
- Include phrases like "just like always" and "the same as last time"
- Everything should feel safe and predictable

Example opening style: "First, Luna put on her space helmet. It was blue, just like always. Then, she checked her space backpack. Everything was in the right place."

Generate the complete story now, following these requirements exactly."""


def get_anxiety_prompt(age, theme, interests, story_length, demo_mode=False):
    """Generate Anxiety-specific prompt"""
    sentence_count = calculate_sentence_count(story_length, "anxiety", demo_mode)
    theme_elements = ", ".join(THEMES.get(theme, THEMES["adventure"])["elements"])
    interest_list = ", ".join(interests) if interests else "peaceful, comforting things"

    return f"""Generate a calming bedtime story for a {age}-year-old child with anxiety. Use these specific guidelines:

STRUCTURE REQUIREMENTS:
- Gentle, reassuring tone throughout
- Total of approximately {sentence_count} sentences
- Predictable, SAFE story arc (NO conflict, danger, or uncertainty)

LANGUAGE STYLE:
- Repetitive calming phrases (e.g., "everything is safe," "you are loved," "all is well")
- Emphasis on comfort, security, and safety
- Breathing cues embedded naturally (e.g., "she took a slow, deep breath")
- Positive, peaceful resolution guaranteed
- Soft, descriptive language focused on pleasant sensory details

THEME & CONTENT:
- Theme: {theme}
- Include these elements: {theme_elements}
- Child's interests: {interest_list}

EMOTIONAL TONE:
- Create a sense of complete safety and calm
- Avoid ANY tension, conflict, or scary elements
- Focus on peaceful imagery and comforting repetition
- Include phrases about being loved, safe, and warm
- Use gentle, slow pacing throughout

Example opening style: "In a cozy little garden, everything was peaceful and safe. The flowers swayed gently in the soft breeze. Everything was calm."

Generate the complete story now, following these requirements exactly."""


def get_general_prompt(age, theme, interests, story_length, demo_mode=False):
    """Generate prompt for general audience with maximum creative freedom"""
    sentence_count = calculate_sentence_count(story_length, "general", demo_mode)
    theme_elements = ", ".join(THEMES.get(theme, THEMES["adventure"])["elements"])
    interest_list = ", ".join(interests) if interests else "adventures and fun activities"

    return f"""Create a bedtime story for a {age}-year-old child. You have complete creative freedom to write in whatever style feels natural and engaging.

CREATIVE FREEDOM:
- Write in any style that feels right for the story
- Use your natural storytelling voice - let the narrative flow organically
- Vary sentence length and structure as the story demands
- Include dialogue, description, action, or reflection as you see fit
- No structural restrictions - tell the story however you envision it
- Total story should be approximately {sentence_count} sentences, but this is flexible

CONTENT GUIDELINES:
- Age-appropriate for {age} years old (no profanity or inappropriate content)
- Theme: {theme}
- Incorporate these elements naturally: {theme_elements}
- Child's interests: {interest_list}
- Suitable for bedtime (should end on a peaceful, calm note)

YOUR CREATIVE CONTROL:
You may:
- Use any narrative perspective (first person, third person, etc.)
- Include humor, wonder, gentle excitement, or calm reflection
- Create memorable characters with distinct personalities
- Use metaphors, similes, vivid imagery, or simple language
- Build tension and release it (age-appropriately)
- Write in a classic fairy tale style, modern prose, or anything in between
- Let the story flow naturally without worrying about rigid formulas

The only requirements are: age-appropriate content, incorporate the theme and interests, and end peacefully for bedtime.

Write the complete story now with your full creative expression."""


def get_fairy_tale_mix_prompt(profile_type, age, story_length, demo_mode=False):
    """Generate prompt for fairy tale mixing when theme/characters are empty"""
    sentence_count = calculate_sentence_count(story_length, profile_type, demo_mode)

    # Profile-specific instructions
    profile_instructions = {
        "adhd": """
ADHD-SPECIFIC REQUIREMENTS:
- Very short sentences (5-7 words maximum per sentence)
- Frequent paragraph breaks (every 2-3 sentences)
- Story gradually slows from high energy to calm
- Action-oriented verbs and frequent hooks
- NO long descriptive passages""",

        "autism": """
AUTISM-SPECIFIC REQUIREMENTS:
- Clear "First-Then-Finally" structure (use these transition words)
- Concrete, literal language ONLY (NO metaphors or idioms)
- Predictable story arc with NO sudden surprises
- Repetitive comforting phrases
- Characters behave consistently and logically""",

        "anxiety": """
ANXIETY-SPECIFIC REQUIREMENTS:
- Gentle, reassuring tone throughout
- Repetitive calming phrases (e.g., "everything is safe," "you are loved")
- Breathing cues embedded naturally
- NO conflict, danger, or uncertainty
- Focus on comfort, security, and safety""",

        "general": """
CREATIVE FREEDOM:
- Write in your natural storytelling voice
- Vary sentence length and structure as feels right
- Include dialogue, description, action as you see fit
- Let the narrative flow organically"""
    }

    profile_specific = profile_instructions.get(profile_type, profile_instructions["general"])

    return f"""Create a magical bedtime story for a {age}-year-old child by blending elements from classic fairy tales in a fresh, creative way.

FAIRY TALE MIXING INSTRUCTIONS:
- Draw inspiration from beloved fairy tales like Cinderella, Little Red Riding Hood, Jack and the Beanstalk, The Three Little Pigs, Goldilocks, Sleeping Beauty, etc.
- Mix and match characters, settings, or plot elements in unexpected ways
- Create something NEW and UNIQUE - not just retelling one fairy tale
- Examples of mixing: Red Riding Hood helps the Three Little Pigs build a house, Cinderella discovers Jack's beanstalk, Goldilocks visits Sleeping Beauty's castle
- Keep the magic and wonder of classic tales while creating something fresh

STORY REQUIREMENTS:
- Approximately {sentence_count} sentences total
- Age-appropriate for {age} years old
- End on a peaceful, calm note suitable for bedtime
{profile_specific}

YOUR CREATIVE TASK:
Blend the best elements of classic fairy tales into an original, enchanting bedtime story. Make it magical, memorable, and perfect for sweet dreams.

Write the complete story now."""


PROFILE_PROMPTS = {
    "adhd": get_adhd_prompt,
    "autism": get_autism_prompt,
    "anxiety": get_anxiety_prompt,
    "general": get_general_prompt
}


def build_prompt(profile_type, age, theme, interests, story_length, demo_mode=False):
    """
    Build the complete prompt for story generation

    Args:
        profile_type: 'adhd', 'autism', 'anxiety', 'general', or 'neurotypical'
        age: child's age (number)
        theme: story theme (string)
        interests: list of interests (list of strings)
        story_length: minutes (number)
        demo_mode: If True, generate a short demo story (1-2 min, ~15 slides)

    Returns:
        Complete prompt string
    """
    # Map neurotypical to general
    if profile_type == 'neurotypical':
        profile_type = 'general'

    # Check if theme and interests are empty or minimal
    is_theme_empty = not theme or theme.strip() == '' or theme.lower() == 'adventure'
    is_interests_empty = not interests or len(interests) == 0 or (len(interests) == 1 and interests[0].strip() == '')

    # If both are empty, use fairy tale mixing mode
    if is_theme_empty and is_interests_empty:
        return get_fairy_tale_mix_prompt(profile_type, age, story_length, demo_mode)

    prompt_func = PROFILE_PROMPTS.get(profile_type)

    if not prompt_func:
        raise ValueError(f"Invalid profile type: {profile_type}")

    return prompt_func(age, theme, interests, story_length, demo_mode)


# Fallback stories for each profile (used when API fails)
FALLBACK_STORIES = {
    "adhd": """Max found a rocket. It was red and shiny. He jumped inside quickly.

The rocket started to glow. "Wow!" said Max. He pressed a big button.

Up, up, up! The rocket flew into space. Stars zoomed past the window.

Max counted the stars. One, two, three! A friendly alien waved hello.

They played a quick game. Max won a golden star! He held it tight.

Time to go home. The rocket flew back down. Down, down, down to Earth.

Max landed in his cozy bed. He hugged his golden star close.

"What an adventure," Max whispered. His eyes felt heavy now.

Sweet dreams, Max. Sleep tight. The end.""",

    "autism": """First, Luna put on her space helmet. It was blue, just like always.
Then, she checked her space backpack. Everything was in the right place.

First, Luna walked to her rocket. She counted her steps. One, two, three, four, five.
Then, she climbed inside. She sat in the same seat as always because it felt safe.

First, the rocket counted down. Five, four, three, two, one.
Then, the rocket flew up into space. Luna knew this would happen because rockets always fly up.

In space, Luna saw the same stars she sees every night. This made her feel calm.
She waved to the moon. The moon was round and bright, just like last time.

Finally, Luna flew home. She landed in her bed.
She said, "Goodnight, stars. Goodnight, moon. Goodnight, space."
Luna closed her eyes. Everything was the same and safe. The end.""",

    "anxiety": """In a cozy little garden, everything was peaceful and safe.
The flowers swayed gently in the soft breeze. Everything was calm.

A small bunny named Willow lived in the garden. Willow was always safe and loved.
Willow took a slow, deep breath and smelled the sweet flowers. Everything felt warm and good.

Willow's friends came to visit. They sat together on the soft grass.
They watched the clouds float by, slowly and gently. Everything moved at a peaceful pace.

"We are safe here together," said Willow softly. The friends agreed.
They all took a deep breath together. In... and out... Everything was calm.

The sun began to set, painting the sky in gentle colors.
Willow snuggled into the warm, soft grass. "I am safe. I am loved. All is well."

The stars came out one by one, like friends saying goodnight.
Willow closed her eyes, feeling warm and peaceful. Everything was safe.
Sweet dreams, Willow. You are loved. The end.""",

    "general": """Once upon a time, in a magical forest filled with twinkling fireflies, a young fox named Oliver discovered something extraordinary hidden beneath the old oak tree.

It was a glowing acorn, shimmering with starlight. Oliver picked it up carefully and noticed it felt warm and gentle in his paws. "What could this be?" he wondered aloud.

As he held the acorn, the forest around him began to sparkle. The trees whispered ancient stories, and the flowers hummed soft lullabies. Oliver realized this was a wishing acorn, one that only appeared once in a hundred years.

Oliver thought carefully about his wish. He could wish for anything—treasure, adventure, or magical powers. But as he looked around at the peaceful forest, his friends sleeping in their cozy homes, he knew exactly what to wish for.

"I wish for sweet dreams for everyone in the forest tonight," Oliver whispered to the acorn. The acorn glowed brighter, then gently dissolved into a thousand tiny sparkles that floated up into the night sky, becoming new stars.

Oliver smiled and made his way home to his warm den. As he curled up in his soft bed of leaves, he felt happy knowing that everyone would have wonderful dreams tonight.

The stars twinkled overhead, the moon smiled down, and Oliver closed his eyes. Sweet dreams, Oliver. The end."""
}
