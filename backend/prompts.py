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


def calculate_sentence_count(minutes, profile_type):
    """
    Convert story length in minutes to approximate sentence count
    based on reading speed and profile type
    """
    words_per_minute = {
        "adhd": 80,      # Slower due to short sentences
        "autism": 100,   # Moderate pace
        "anxiety": 90    # Slower, calming pace
    }

    avg_words_per_sentence = {
        "adhd": 6,       # Very short sentences
        "autism": 12,    # Medium sentences
        "anxiety": 15    # Longer, flowing sentences
    }

    total_words = words_per_minute.get(profile_type, 90) * minutes
    sentence_count = total_words // avg_words_per_sentence.get(profile_type, 12)

    return max(sentence_count, 20)  # Minimum 20 sentences


def get_adhd_prompt(age, theme, interests, story_length):
    """Generate ADHD-specific prompt"""
    sentence_count = calculate_sentence_count(story_length, "adhd")
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


def get_autism_prompt(age, theme, interests, story_length):
    """Generate Autism-specific prompt"""
    sentence_count = calculate_sentence_count(story_length, "autism")
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


def get_anxiety_prompt(age, theme, interests, story_length):
    """Generate Anxiety-specific prompt"""
    sentence_count = calculate_sentence_count(story_length, "anxiety")
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


PROFILE_PROMPTS = {
    "adhd": get_adhd_prompt,
    "autism": get_autism_prompt,
    "anxiety": get_anxiety_prompt
}


def build_prompt(profile_type, age, theme, interests, story_length):
    """
    Build the complete prompt for story generation

    Args:
        profile_type: 'adhd', 'autism', or 'anxiety'
        age: child's age (number)
        theme: story theme (string)
        interests: list of interests (list of strings)
        story_length: minutes (number)

    Returns:
        Complete prompt string
    """
    prompt_func = PROFILE_PROMPTS.get(profile_type)

    if not prompt_func:
        raise ValueError(f"Invalid profile type: {profile_type}")

    return prompt_func(age, theme, interests, story_length)


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
Sweet dreams, Willow. You are loved. The end."""
}
