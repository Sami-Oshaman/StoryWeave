# StoryWeave

## Accessibility-First AI Bedtime Stories for Every Child

---

## Project Overview

### The Problem

1 in 6 children has a developmental disability. Traditional bedtime stories use one-size-fits-all pacing, language, and sensory input—which fails neurodivergent children. Parents spend hours searching for appropriate content, often settling for inadequate solutions.

### The Solution

StoryWeave uses AI to generate personalized bedtime stories that adapt to each child's cognitive profile, sensory needs, and emotional state. The system generates fundamentally different story structures based on disability profiles—not just adjusting formatting or presentation, but restructuring the narrative architecture itself.

---

## Core Features

### Cognitive Adaptation Profiles

Stories are generated with fundamentally different structures based on disability profiles:

**1. ADHD Profile**
- Short sentences (5-7 words)
- Frequent "hooks" and transitions
- High-energy pacing with reward points
- Reduced descriptive text, more action

**2. Autism Spectrum Profile**
- Predictable "First-Then-Finally" structure
- Concrete, literal language (no idioms)
- Consistent character behaviors
- Visual routine mapping

**3. Anxiety Profile**
- Calming, repetitive phrases
- Predictable story arc
- Safe resolution emphasis
- Breathing/grounding cues embedded

### Multi-Modal Output
- **Text:** Large, dyslexia-friendly fonts
- **Audio:** Natural TTS with adjustable pacing
- **Visual:** Optional illustrations (stretch goal)

### Parent Controls
- Child profile creation (age, disabilities, interests, sensory preferences)
- Story length selection (5, 10, 15 minutes)
- Theme preferences (adventure, animals, space, etc.)
- Sensory settings (sound/visual intensity)

---

## Technical Architecture

### Backend Stack

**Core Technology:**
- Python 3.9+
- Flask 2.3+ (REST API)
- AWS Bedrock (Claude 3.5 Sonnet)
- MongoDB Atlas (M0 free tier)
- Railway/Heroku deployment

**API Endpoints:**

```python
POST /api/generate-story
# Generate new story with cognitive profile
Request Body:
{
  "child_id": "string",
  "profile_type": "adhd|autism|anxiety",
  "age": "number",
  "theme": "string",
  "story_length": "5|10|15",  # minutes
  "interests": ["string"],
  "sensory_preferences": {
    "sound_sensitivity": "low|medium|high",
    "visual_preference": "minimal|moderate|rich"
  }
}

Response:
{
  "story_id": "string",
  "story_text": "string",
  "audio_url": "string" (optional),
  "profile_used": "string",
  "generation_time": "number"
}
```

```python
POST /api/save-profile
# Store child profile
Request Body:
{
  "age": "number",
  "cognitive_profile": "adhd|autism|anxiety|multiple",
  "sensory_preferences": "object",
  "interests": ["string"],
  "story_length_preference": "number"
}

Response:
{
  "child_id": "string",
  "profile_created": "timestamp"
}
```

```python
GET /api/get-history?child_id={id}&limit={n}
# Retrieve past stories
Response:
{
  "stories": [
    {
      "story_id": "string",
      "story_text": "string",
      "timestamp": "datetime",
      "profile_used": "string",
      "user_rating": "number"
    }
  ]
}
```

```python
PUT /api/update-preferences
# Modify user settings
Request Body:
{
  "child_id": "string",
  "preferences": "object"
}

Response:
{
  "success": "boolean",
  "updated_fields": ["string"]
}
```

**Key Backend Features:**
- Cognitive adaptation engine with 2-3 disability profiles
- Story caching system for common requests (Redis optional)
- Error handling with retry logic (3 attempts)
- Rate limiting for API protection (50 requests/hour per user)
- Response time target: <3 seconds
- Logging for debugging and analytics

**Database Schema (MongoDB):**

```javascript
// Child Profile Collection
{
  "_id": ObjectId,
  "child_id": "uuid",
  "age": Number,
  "cognitive_profile": ["adhd", "autism", "anxiety"],  // Can be multiple
  "sensory_preferences": {
    "sound_sensitivity": String,  // "low", "medium", "high"
    "visual_preference": String,  // "minimal", "moderate", "rich"
    "texture_descriptions": Boolean,  // Include tactile descriptions
    "avoid_triggers": [String]  // e.g., ["loud noises", "darkness"]
  },
  "interests": [String],  // e.g., ["dinosaurs", "space", "animals"]
  "story_length_preference": Number,  // in minutes
  "created_at": Date,
  "updated_at": Date
}

// Story History Collection
{
  "_id": ObjectId,
  "story_id": "uuid",
  "child_id": "uuid",
  "story_text": String,
  "profile_used": String,
  "theme": String,
  "generation_parameters": {
    "age": Number,
    "interests": [String],
    "story_length": Number
  },
  "audio_url": String,  // if TTS generated
  "user_rating": Number,  // 1-5 stars, optional
  "timestamp": Date
}

// Story Cache Collection (for performance)
{
  "_id": ObjectId,
  "cache_key": String,  // hash of generation parameters
  "story_text": String,
  "profile_type": String,
  "created_at": Date,
  "access_count": Number,
  "expires_at": Date  // TTL index
}
```

### Frontend Stack

**Core Technology:**
- React 18+
- Chakra UI component library
- React Router for navigation
- Axios for API calls
- Vercel deployment

**Pages:**

**1. Setup Page (Child Profile Creation)**
- Form with child information inputs
- Cognitive profile selection (checkboxes for multiple)
- Sensory preferences sliders
- Interests selection (multi-select)
- Maximum 3 clicks to complete

**2. Generation Page**
- Story parameter selection (theme, length)
- Generate button
- Loading state with calming animation
- Error handling with retry option

**3. Display Page**
- Story text display with large, readable font
- Audio playback controls (if TTS enabled)
- Save to history button
- Rating system (optional)
- Generate new story button

**Design Requirements:**
- Soft color palette (blues/purples: #4F46E5, #7C3AED, #E0E7FF)
- Large fonts (18px+ minimum, 24px+ for story text)
- Generous whitespace (padding: 24px minimum)
- No jarring animations (fade only, no slide/bounce)
- Dark mode toggle
- Mobile-responsive design (breakpoints: 640px, 768px, 1024px)
- Calming visual aesthetic

**Component Structure:**

```jsx
src/
├── components/
│   ├── ProfileForm.jsx          // Child profile input form
│   ├── StoryDisplay.jsx         // Story text and audio player
│   ├── GenerationControls.jsx   // Theme/length selection
│   ├── LoadingState.jsx         // Calming loading animation
│   ├── ErrorMessage.jsx         // User-friendly error display
│   └── Navigation.jsx           // App navigation header
├── pages/
│   ├── Setup.jsx                // Profile creation page
│   ├── Generate.jsx             // Story generation page
│   └── Display.jsx              // Story viewing page
├── hooks/
│   ├── useStoryGeneration.js    // API call logic
│   └── useProfile.js            // Profile CRUD operations
├── utils/
│   ├── api.js                   // Axios instance and endpoints
│   └── constants.js             // Themes, profiles, etc.
└── App.jsx
```

### Accessibility Implementation

**WCAG 2.1 Level AA Requirements:**
- All images have alt text
- Color contrast ratio ≥4.5:1 for normal text
- Color contrast ratio ≥3:1 for large text
- No information conveyed by color alone
- All interactive elements keyboard accessible
- Focus indicators visible (2px solid outline)
- Proper heading hierarchy (h1 → h2 → h3)
- Form labels properly associated with inputs
- Error messages clearly identify issues
- Skip navigation link present

**Screen Reader Support:**
- ARIA labels on all interactive elements
- ARIA live regions for dynamic content
- ARIA busy state during story generation
- Semantic HTML elements (nav, main, section, article)

**Additional Accessibility Features:**
- Dyslexia-friendly font option (OpenDyslexic)
- Text spacing adjustable (line-height: 1.5-2.0)
- No autoplay audio
- Pause/stop controls for all audio
- Option to disable animations
- High contrast mode
- Focus trap in modals

---

## Cognitive Profile Implementation

### Prompt Engineering Strategy

Each disability profile uses distinct prompt engineering to generate fundamentally different story structures. The prompts are designed based on established occupational therapy and speech therapy principles.

#### ADHD Profile Prompt Template

```python
ADHD_PROMPT = """Generate a bedtime story for a child with ADHD. Use:
- Very short sentences (5-7 words maximum per sentence)
- Frequent paragraph breaks (every 2-3 sentences)
- Action-oriented verbs (jump, run, fly, discover)
- "Surprise" moments or hooks every 2-3 sentences to re-engage attention
- Direct questions to the reader to maintain engagement (e.g., "What do you think happened next?")
- Concrete rewards or achievements for the main character
- High-energy pacing that gradually slows toward the end
- Total story length: approximately {story_length} sentences
- Theme: {theme}
- Child's age: {age}
- Child's interests: {interests}

The story should start with high energy and gradually become calmer to prepare for sleep.
Do not use complex sentence structures or long descriptive passages.
"""
```

**Example ADHD Output Structure:**
```
Max saw a rocket. It was shiny and red. "Wow!" he said.
The rocket started to glow. Max jumped inside quickly.

What happened next? The rocket blasted off! Up, up, up into space!
Stars zoomed past the window. Max counted them. One, two, three!

A friendly alien waved hello. Max waved back excitedly.
They played a quick game. Max won a golden star!

Time to go home now. The rocket flew back down. 
Max landed safely in bed. He hugged his star tight.

Sweet dreams, Max. The end.
```

#### Autism Profile Prompt Template

```python
AUTISM_PROMPT = """Generate a bedtime story for a child with autism. Use:
- Clear "First-Then-Finally" structure (explicitly use these transition words)
- Concrete, literal language (avoid metaphors, idioms, and figurative language)
- Consistent character behaviors (characters should act predictably)
- Clear cause-and-effect sequences (use "because" and "so" to show connections)
- Repetitive comforting phrases throughout the story
- Specific routines described step-by-step
- Predictable story arc with no sudden surprises
- Total story length: approximately {story_length} sentences
- Theme: {theme}
- Child's age: {age}
- Child's interests: {interests}

The story should follow a predictable pattern and end with a comforting routine.
Characters should behave logically and consistently throughout.
"""
```

**Example Autism Output Structure:**
```
First, Luna put on her space helmet. It was blue, just like always.
Then, she checked her space backpack. Everything was in the right place.

First, Luna walked to the rocket. She counted her steps. One, two, three, four, five.
Then, she climbed inside. She sat in the same seat as always because it felt safe.

First, the rocket counted down. Five, four, three, two, one.
Then, the rocket flew up into space. Luna knew this would happen because rockets always fly up.

In space, Luna saw the same stars she sees every night. This made her feel calm.
She waved to the moon. The moon was round and bright, just like last time.

Finally, Luna flew home. She landed in her bed. 
She said, "Goodnight, stars. Goodnight, moon. Goodnight, space."
Luna closed her eyes. Everything was the same and safe. The end.
```

#### Anxiety Profile Prompt Template

```python
ANXIETY_PROMPT = """Generate a calming bedtime story for a child with anxiety. Use:
- Gentle, reassuring tone throughout
- Repetitive calming phrases (e.g., "everything is safe," "you are loved")
- Predictable, safe story arc (no conflict, danger, or uncertainty)
- Emphasis on comfort, security, and safety
- Breathing cues embedded naturally (e.g., "she took a slow, deep breath")
- Positive, peaceful resolution
- Soft, descriptive language focused on pleasant sensory details
- Total story length: approximately {story_length} sentences
- Theme: {theme}
- Child's age: {age}
- Child's interests: {interests}

The story should create a sense of safety and calm. Avoid any tension or conflict.
Focus on peaceful imagery and comforting repetition.
"""
```

**Example Anxiety Output Structure:**
```
In a cozy little garden, everything was peaceful and safe.
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
Sweet dreams, Willow. You are loved. The end.
```

### Prompt Optimization Techniques

**Dynamic Length Calculation:**
```python
def calculate_sentence_count(minutes, profile_type):
    """
    Convert story length in minutes to approximate sentence count
    based on reading speed and profile type
    """
    # Average reading speed adjustments per profile
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
    
    total_words = words_per_minute[profile_type] * minutes
    sentence_count = total_words // avg_words_per_sentence[profile_type]
    
    return sentence_count
```

**Theme Integration:**
```python
THEMES = {
    "space": {
        "elements": ["rocket", "stars", "planets", "moon", "astronaut"],
        "activities": ["flying", "exploring", "discovering", "floating"],
        "safe_objects": ["space helmet", "space suit", "spacecraft"]
    },
    "animals": {
        "elements": ["forest", "meadow", "pond", "nest", "burrow"],
        "activities": ["playing", "exploring", "resting", "eating"],
        "safe_objects": ["soft grass", "cozy nest", "warm den"]
    },
    "adventure": {
        "elements": ["path", "bridge", "garden", "treehouse", "meadow"],
        "activities": ["walking", "discovering", "building", "creating"],
        "safe_objects": ["compass", "map", "backpack", "blanket"]
    }
}

def build_prompt(profile_type, theme, age, interests, story_length_minutes):
    """
    Construct the full prompt with all parameters
    """
    sentence_count = calculate_sentence_count(story_length_minutes, profile_type)
    
    base_prompt = get_base_prompt(profile_type)  # Returns ADHD_PROMPT, etc.
    theme_elements = ", ".join(THEMES[theme]["elements"])
    interest_list = ", ".join(interests)
    
    full_prompt = base_prompt.format(
        story_length=sentence_count,
        theme=theme,
        age=age,
        interests=interest_list,
        theme_elements=theme_elements
    )
    
    return full_prompt
```

---

## AWS Bedrock Integration

### Setup and Configuration

```python
import boto3
import json
from botocore.exceptions import ClientError

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'  # or your preferred region
)

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

def generate_story(prompt, max_tokens=2000):
    """
    Call AWS Bedrock with Claude to generate a story
    """
    try:
        # Prepare the request body
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,  # Some creativity, but consistent
            "top_p": 0.9
        })
        
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            body=body
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        story_text = response_body['content'][0]['text']
        
        return {
            "success": True,
            "story": story_text,
            "tokens_used": response_body.get('usage', {})
        }
        
    except ClientError as e:
        return {
            "success": False,
            "error": str(e),
            "story": None
        }

def generate_story_with_retry(prompt, max_retries=3):
    """
    Generate story with automatic retry on failure
    """
    for attempt in range(max_retries):
        result = generate_story(prompt)
        
        if result["success"]:
            return result
        
        # Wait before retry (exponential backoff)
        time.sleep(2 ** attempt)
    
    # All retries failed, return cached or template story
    return {
        "success": False,
        "story": get_fallback_story(),
        "error": "Max retries exceeded"
    }
```

### Error Handling

```python
def get_fallback_story():
    """
    Return a pre-written story if API fails
    """
    FALLBACK_STORIES = {
        "adhd": "Max found a rocket. It was red. He jumped in. The rocket flew up...",
        "autism": "First, Luna put on her helmet. Then, she got in the rocket. Finally...",
        "anxiety": "In a peaceful garden, Willow the bunny felt safe and calm..."
    }
    
    return FALLBACK_STORIES.get("adhd")  # Default fallback

def handle_generation_error(error):
    """
    Log and return user-friendly error message
    """
    error_messages = {
        "ThrottlingException": "Too many requests. Please wait a moment and try again.",
        "ValidationException": "Invalid request. Please check your story parameters.",
        "ServiceUnavailableException": "Service temporarily unavailable. Using cached story.",
        "ModelTimeoutException": "Story generation took too long. Please try a shorter story."
    }
    
    error_type = type(error).__name__
    user_message = error_messages.get(error_type, "An error occurred. Please try again.")
    
    # Log the actual error for debugging
    logging.error(f"Bedrock Error: {error_type} - {str(error)}")
    
    return user_message
```

---

## Flask Backend Implementation

### App Structure

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import uuid
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# MongoDB setup
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.storyweave

# Collections
profiles = db.child_profiles
stories = db.story_history
cache = db.story_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/generate-story', methods=['POST'])
def generate_story_endpoint():
    """
    Generate a personalized story based on child profile
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['profile_type', 'age', 'theme', 'story_length']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Check cache first
        cache_key = create_cache_key(data)
        cached_story = cache.find_one({"cache_key": cache_key})
        
        if cached_story:
            logger.info(f"Cache hit for key: {cache_key}")
            return jsonify({
                "story_id": str(cached_story['_id']),
                "story_text": cached_story['story_text'],
                "profile_used": cached_story['profile_type'],
                "cached": True
            })
        
        # Build prompt
        prompt = build_prompt(
            profile_type=data['profile_type'],
            theme=data['theme'],
            age=data['age'],
            interests=data.get('interests', []),
            story_length_minutes=data['story_length']
        )
        
        # Generate story with retry
        start_time = datetime.now()
        result = generate_story_with_retry(prompt)
        generation_time = (datetime.now() - start_time).total_seconds()
        
        if not result["success"]:
            logger.error(f"Story generation failed: {result.get('error')}")
            return jsonify({
                "error": "Story generation failed",
                "story_text": result["story"],  # Fallback story
                "fallback": True
            }), 500
        
        # Save to history
        story_id = str(uuid.uuid4())
        story_doc = {
            "story_id": story_id,
            "child_id": data.get('child_id'),
            "story_text": result["story"],
            "profile_used": data['profile_type'],
            "theme": data['theme'],
            "generation_parameters": data,
            "timestamp": datetime.now(),
            "generation_time": generation_time
        }
        stories.insert_one(story_doc)
        
        # Cache the story
        cache_doc = {
            "cache_key": cache_key,
            "story_text": result["story"],
            "profile_type": data['profile_type'],
            "created_at": datetime.now(),
            "access_count": 1
        }
        cache.insert_one(cache_doc)
        
        logger.info(f"Story generated successfully in {generation_time:.2f}s")
        
        return jsonify({
            "story_id": story_id,
            "story_text": result["story"],
            "profile_used": data['profile_type'],
            "generation_time": generation_time,
            "cached": False
        })
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/save-profile', methods=['POST'])
def save_profile_endpoint():
    """
    Create or update a child profile
    """
    try:
        data = request.json
        
        child_id = str(uuid.uuid4())
        profile_doc = {
            "child_id": child_id,
            "age": data['age'],
            "cognitive_profile": data['cognitive_profile'],
            "sensory_preferences": data.get('sensory_preferences', {}),
            "interests": data.get('interests', []),
            "story_length_preference": data.get('story_length_preference', 10),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        profiles.insert_one(profile_doc)
        
        return jsonify({
            "child_id": child_id,
            "profile_created": profile_doc['created_at'].isoformat()
        })
        
    except Exception as e:
        logger.error(f"Profile save error: {str(e)}")
        return jsonify({"error": "Failed to save profile"}), 500

@app.route('/api/get-history', methods=['GET'])
def get_history_endpoint():
    """
    Retrieve story history for a child
    """
    try:
        child_id = request.args.get('child_id')
        limit = int(request.args.get('limit', 10))
        
        if not child_id:
            return jsonify({"error": "child_id required"}), 400
        
        story_list = list(
            stories.find({"child_id": child_id})
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string for JSON serialization
        for story in story_list:
            story['_id'] = str(story['_id'])
            story['timestamp'] = story['timestamp'].isoformat()
        
        return jsonify({"stories": story_list})
        
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        return jsonify({"error": "Failed to retrieve history"}), 500

def create_cache_key(data):
    """
    Create a cache key from generation parameters
    """
    import hashlib
    
    # Create a string from relevant parameters
    key_string = f"{data['profile_type']}_{data['theme']}_{data['age']}_{data['story_length']}"
    
    # Hash it for consistent key length
    return hashlib.md5(key_string.encode()).hexdigest()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## React Frontend Implementation

### Main App Component

```jsx
// src/App.jsx
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Setup from './pages/Setup';
import Generate from './pages/Generate';
import Display from './pages/Display';
import Navigation from './components/Navigation';

// Custom theme for accessibility
const theme = extendTheme({
  colors: {
    brand: {
      50: '#E0E7FF',
      100: '#C7D2FE',
      500: '#4F46E5',
      600: '#4338CA',
      700: '#3730A3',
    },
    purple: {
      500: '#7C3AED',
      600: '#6D28D9',
    },
  },
  fonts: {
    heading: "'Inter', sans-serif",
    body: "'Inter', sans-serif",
  },
  fontSizes: {
    xs: '14px',
    sm: '16px',
    md: '18px',
    lg: '20px',
    xl: '24px',
    '2xl': '28px',
    '3xl': '32px',
  },
  styles: {
    global: {
      body: {
        fontSize: '18px',
        lineHeight: '1.6',
      },
    },
  },
});

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<Setup />} />
          <Route path="/generate" element={<Generate />} />
          <Route path="/display/:storyId" element={<Display />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
```

### Setup Page

```jsx
// src/pages/Setup.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  CheckboxGroup,
  Checkbox,
  VStack,
  Heading,
  Text,
} from '@chakra-ui/react';
import { saveProfile } from '../utils/api';

function Setup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    age: '',
    cognitive_profile: [],
    interests: [],
    story_length_preference: 10,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const result = await saveProfile(formData);
      
      // Store child_id in localStorage for later use
      localStorage.setItem('child_id', result.child_id);
      
      // Navigate to generation page
      navigate('/generate');
    } catch (error) {
      console.error('Failed to save profile:', error);
    }
  };

  return (
    <Box maxW="600px" mx="auto" p={8}>
      <VStack spacing={6} align="stretch">
        <Heading>Create Child Profile</Heading>
        <Text>Tell us about your child so we can create perfect bedtime stories.</Text>
        
        <form onSubmit={handleSubmit}>
          <VStack spacing={5}>
            <FormControl isRequired>
              <FormLabel>Child's Age</FormLabel>
              <Input
                type="number"
                min="3"
                max="12"
                value={formData.age}
                onChange={(e) => setFormData({...formData, age: e.target.value})}
                fontSize="lg"
              />
            </FormControl>

            <FormControl>
              <FormLabel>Cognitive Profile (select all that apply)</FormLabel>
              <CheckboxGroup
                value={formData.cognitive_profile}
                onChange={(values) => setFormData({...formData, cognitive_profile: values})}
              >
                <VStack align="start" spacing={3}>
                  <Checkbox value="adhd" size="lg">ADHD</Checkbox>
                  <Checkbox value="autism" size="lg">Autism Spectrum</Checkbox>
                  <Checkbox value="anxiety" size="lg">Anxiety</Checkbox>
                </VStack>
              </CheckboxGroup>
            </FormControl>

            <FormControl>
              <FormLabel>Story Length Preference</FormLabel>
              <Select
                value={formData.story_length_preference}
                onChange={(e) => setFormData({...formData, story_length_preference: parseInt(e.target.value)})}
                fontSize="lg"
              >
                <option value="5">5 minutes</option>
                <option value="10">10 minutes</option>
                <option value="15">15 minutes</option>
              </Select>
            </FormControl>

            <Button
              type="submit"
              colorScheme="brand"
              size="lg"
              width="100%"
              mt={4}
            >
              Create Profile & Continue
            </Button>
          </VStack>
        </form>
      </VStack>
    </Box>
  );
}

export default Setup;
```

### API Utilities

```javascript
// src/utils/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const generateStory = async (params) => {
  try {
    const response = await api.post('/generate-story', params);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const saveProfile = async (profileData) => {
  try {
    const response = await api.post('/save-profile', profileData);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getStoryHistory = async (childId, limit = 10) => {
  try {
    const response = await api.get('/get-history', {
      params: { child_id: childId, limit },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};
```

---

## Development Timeline

### Phase 1: Foundation (Hours 0-6)
**Backend:**
- Set up Flask project structure
- Configure MongoDB connection
- Initialize AWS Bedrock client
- Create basic API endpoints (skeleton)
- Test Bedrock connection with simple prompt

**Frontend:**
- Initialize React app with Chakra UI
- Set up routing structure
- Create basic component structure
- Design color scheme and typography

**DevOps:**
- Set up GitHub repository
- Configure environment variables
- Create deployment configuration

### Phase 2: Core Development (Hours 6-14)
**Backend:**
- Implement cognitive profile prompts (all 3 types)
- Build story generation pipeline with retry logic
- Implement MongoDB CRUD operations
- Add error handling and logging
- Test API endpoints with Postman

**Frontend:**
- Build ProfileForm component
- Implement story generation page
- Create story display component
- Add loading states and animations
- Connect to backend API

### Phase 3: Integration & Polish (Hours 14-20)
**Backend:**
- Implement story caching
- Add rate limiting
- Performance optimization
- Deploy to Railway/Heroku

**Frontend:**
- Accessibility testing and fixes
- Mobile responsiveness
- Dark mode implementation
- Error handling UI
- Deploy to Vercel

**Testing:**
- End-to-end testing
- Cross-browser testing
- Mobile device testing
- Generate test stories for demo

### Phase 4: Demo Preparation (Hours 20-24)
- Bug fixes
- Demo story pre-generation
- Pitch deck finalization
- Demo rehearsal
- Backup plan testing

---

## Deployment

### Backend Deployment (Railway)

```yaml
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

```txt
# requirements.txt
Flask==2.3.0
flask-cors==4.0.0
pymongo==4.5.0
boto3==1.28.0
gunicorn==21.2.0
python-dotenv==1.0.0
```

### Frontend Deployment (Vercel)

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "REACT_APP_API_URL": "@api-url"
  }
}
```

### Environment Variables

**Backend (.env):**
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/storyweave
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
FLASK_ENV=production
```

**Frontend (.env):**
```
REACT_APP_API_URL=https://your-backend.railway.app/api
```

---

## Testing Strategy

### Backend Testing

```python
# tests/test_generation.py
import pytest
from app import app

def test_generate_story_adhd():
    """Test ADHD story generation"""
    client = app.test_client()
    
    response = client.post('/api/generate-story', json={
        'profile_type': 'adhd',
        'age': 7,
        'theme': 'space',
        'story_length': 5,
        'interests': ['rockets', 'astronauts']
    })
    
    assert response.status_code == 200
    data = response.json
    assert 'story_text' in data
    assert 'story_id' in data
    
    # Check story characteristics
    story = data['story_text']
    sentences = story.split('.')
    avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
    assert avg_length < 10  # ADHD stories should have short sentences

def test_generate_story_autism():
    """Test Autism story generation"""
    client = app.test_client()
    
    response = client.post('/api/generate-story', json={
        'profile_type': 'autism',
        'age': 6,
        'theme': 'animals',
        'story_length': 10,
        'interests': ['dogs', 'cats']
    })
    
    assert response.status_code == 200
    data = response.json
    story = data['story_text']
    
    # Check for "First-Then-Finally" structure
    assert 'First' in story or 'first' in story
    assert 'Then' in story or 'then' in story
    assert 'Finally' in story or 'finally' in story
```

### Frontend Testing

```javascript
// src/__tests__/Setup.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import Setup from '../pages/Setup';

test('renders profile form', () => {
  render(<Setup />);
  
  expect(screen.getByText('Create Child Profile')).toBeInTheDocument();
  expect(screen.getByLabelText("Child's Age")).toBeInTheDocument();
  expect(screen.getByText('ADHD')).toBeInTheDocument();
});

test('submits form with valid data', async () => {
  render(<Setup />);
  
  const ageInput = screen.getByLabelText("Child's Age");
  fireEvent.change(ageInput, { target: { value: '7' } });
  
  const adhdCheckbox = screen.getByText('ADHD');
  fireEvent.click(adhdCheckbox);
  
  const submitButton = screen.getByText('Create Profile & Continue');
  fireEvent.click(submitButton);
  
  // Assert navigation or success state
});
```

---

## Success Metrics

### Backend Success Criteria
- ✅ 3 different cognitive profiles generate noticeably different story structures
- ✅ API response time consistently under 3 seconds
- ✅ API handles 10+ requests/minute without failure
- ✅ Error handling gracefully falls back to cached stories
- ✅ MongoDB operations complete within 100ms

### Frontend Success Criteria
- ✅ Profile creation takes less than 60 seconds
- ✅ UI loads on mobile devices within 2 seconds
- ✅ Zero accessibility warnings in Lighthouse audit
- ✅ Story displays correctly on screens 320px-1920px wide
- ✅ All interactive elements keyboard accessible

### Accessibility Success Criteria
- ✅ WCAG 2.1 Level AA compliance (automated tests pass)
- ✅ Screen reader can navigate entire application
- ✅ All text meets minimum contrast ratios (4.5:1)
- ✅ Focus indicators visible on all interactive elements
- ✅ No information conveyed by color alone

---

## MVP Feature Checklist

### Must Have (Core Demo)
- [ ] Backend API with story generation endpoint
- [ ] AWS Bedrock integration with Claude 3.5
- [ ] 2 cognitive profiles (ADHD + Autism)
- [ ] Child profile creation form
- [ ] Story display page with readable text
- [ ] MongoDB for profile storage
- [ ] Basic error handling
- [ ] Deployed backend (Railway)
- [ ] Deployed frontend (Vercel)

### Should Have (Enhanced Demo)
- [ ] 3rd cognitive profile (Anxiety)
- [ ] Story length selection
- [ ] Theme selection (3+ themes)
- [ ] Dark mode toggle
- [ ] Loading animations
- [ ] Story history view
- [ ] Caching system

### Nice to Have (Stretch Goals)
- [ ] Audio output (TTS integration)
- [ ] Visual illustrations
- [ ] Story rating system
- [ ] Multiple interest tags
- [ ] Parent dashboard with analytics

---

## Technical Dependencies

### Backend Requirements
```txt
Flask==2.3.0
flask-cors==4.0.0
pymongo==4.5.0
boto3==1.28.0
gunicorn==21.2.0
python-dotenv==1.0.0
requests==2.31.0
```

### Frontend Requirements
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.16.0",
    "@chakra-ui/react": "^2.8.0",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "framer-motion": "^10.16.0",
    "axios": "^1.5.0"
  }
}
```

### External Services
- AWS Bedrock (Claude 3.5 Sonnet API)
- MongoDB Atlas (M0 free tier)
- Railway (Backend hosting)
- Vercel (Frontend hosting)
- Optional: ElevenLabs or Google TTS (Audio generation)

---

## Accessibility Implementation Checklist

### WCAG 2.1 Level AA Compliance
- [ ] All images have descriptive alt text
- [ ] Color contrast ratio ≥4.5:1 for normal text (18px)
- [ ] Color contrast ratio ≥3:1 for large text (24px+)
- [ ] No information conveyed by color alone
- [ ] All interactive elements keyboard accessible (Tab, Enter, Space)
- [ ] Focus indicators visible (2px solid outline, high contrast)
- [ ] Proper heading hierarchy (h1 → h2 → h3, no skipping levels)
- [ ] Form labels properly associated with inputs (htmlFor/id)
- [ ] Error messages clearly identify issues
- [ ] Skip navigation link present for keyboard users

### Screen Reader Support
- [ ] Test with NVDA (Windows) or VoiceOver (Mac)
- [ ] All content accessible in logical reading order
- [ ] ARIA labels on custom components
- [ ] ARIA live regions for dynamic content announcements
- [ ] Form validation results announced
- [ ] Loading states announced (aria-busy)
- [ ] Button purposes clearly described

### Additional Features
- [ ] Dyslexia-friendly font option available
- [ ] Text spacing adjustable (line-height 1.5-2.0)
- [ ] No autoplay audio
- [ ] Pause/stop/volume controls for all audio
- [ ] Option to disable animations (prefers-reduced-motion)
- [ ] High contrast mode support
- [ ] Focus trap in modal dialogs
- [ ] Semantic HTML (nav, main, article, section)

---

## Code Quality Guidelines

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions
- Keep functions under 50 lines
- Use descriptive variable names
- Handle exceptions explicitly
- Log all errors with context

### JavaScript/React (Frontend)
- Follow Airbnb style guide
- Use functional components with hooks
- Keep components under 200 lines
- Extract reusable logic to custom hooks
- Use prop-types or TypeScript for type checking
- Follow component naming conventions (PascalCase)
- Use semantic HTML elements

### Git Workflow
- Feature branches for all development
- Descriptive commit messages (present tense)
- Pull requests for all merges to main
- Code review required before merging
- Main branch protected (no direct commits)

---

## Troubleshooting Guide

### Common Issues

**Issue: AWS Bedrock returns ThrottlingException**
- **Solution:** Implement exponential backoff, reduce request frequency, or upgrade AWS tier

**Issue: Story generation takes >10 seconds**
- **Solution:** Reduce max_tokens, simplify prompt, or implement streaming responses

**Issue: MongoDB connection timeout**
- **Solution:** Check network settings, verify connection string, ensure IP whitelist includes deployment server

**Issue: CORS errors on frontend**
- **Solution:** Verify flask-cors configuration, check API_BASE_URL in frontend, ensure credentials included if needed

**Issue: Chakra UI theme not applied**
- **Solution:** Verify ChakraProvider wraps entire app, check theme import, clear browser cache

**Issue: Stories not different across profiles**
- **Solution:** Review prompt templates, increase temperature slightly, add more specific constraints

---

## Performance Optimization

### Backend Optimizations
- Implement Redis caching for frequently requested stories
- Use MongoDB indexes on child_id and timestamp fields
- Compress API responses with gzip
- Implement connection pooling for MongoDB
- Use async/await for concurrent operations
- Cache Bedrock model responses for 24 hours

### Frontend Optimizations
- Lazy load route components with React.lazy()
- Implement virtual scrolling for long story lists
- Optimize images with WebP format
- Use React.memo for expensive components
- Debounce user inputs (search, filters)
- Code-split by route
- Implement service worker for offline support

---

## Security Considerations

### Backend Security
- Validate and sanitize all user inputs
- Implement rate limiting (50 requests/hour per IP)
- Use environment variables for secrets
- Enable CORS only for specific domains (production)
- Implement request size limits (max 1MB)
- Log security events (failed auth, suspicious requests)
- Use HTTPS only in production

### Frontend Security
- Sanitize user-generated content before display
- Implement Content Security Policy headers
- Don't store sensitive data in localStorage
- Use secure HTTP-only cookies for sessions
- Validate data from API before using
- Implement CSRF protection

### Data Privacy
- No personally identifiable information stored
- Child profiles anonymized with UUIDs
- COPPA compliance (no data collection from children)
- Parent controls all data
- Data deletion on request
- No third-party data sharing

---

## Future Enhancements

### Technical Improvements
- Implement real-time story streaming
- Add multi-language support
- Voice cloning for familiar voices
- Dynamic illustration generation with DALL-E
- Emotion detection from input
- Adaptive difficulty based on engagement

### Feature Additions
- Social stories for specific situations
- Educational content integration
- Parent analytics dashboard
- Therapist collaboration tools
- Offline mode with pre-cached stories
- Sibling mode (generate stories for multiple children)

### Platform Expansion
- Mobile apps (iOS/Android)
- Smart speaker integration (Alexa, Google Home)
- School district licensing portal
- Therapy center dashboard
- API for third-party integrations

---

## Resources & References

### Technical Documentation
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Chakra UI Documentation](https://chakra-ui.com/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)

### Accessibility Resources
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility Guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Research on Cognitive Profiles
- CDC Developmental Disabilities Statistics
- Occupational therapy story structure principles
- Speech therapy language guidelines
- ADHD attention span research
- Autism communication patterns
- Childhood anxiety management techniques

---

## License

MIT License - Free to use, modify, and distribute with attribution.

---

**"Every child deserves bedtime stories designed for them."**
