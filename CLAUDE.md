# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StoryWeave is an AI-powered bedtime story generator that creates personalized, accessibility-first stories for neurodivergent children. The system generates fundamentally different story structures based on cognitive profiles (ADHD, Autism, Anxiety), not just adjusting formatting but restructuring the narrative architecture itself.

**Key Innovation:** Stories are adapted at the prompt engineering level to match how different cognitive profiles process information - short sentences for ADHD, First-Then-Finally structure for Autism, calming repetition for Anxiety.

## Architecture

**Backend:** Flask API with AWS Bedrock (Claude 3.5 Sonnet) for story generation and DynamoDB for data storage
**Frontend:** React 18+ with Chakra UI (not yet implemented)
**Database:** DynamoDB (not MongoDB as originally planned - see .env.example)

### Critical Architectural Details

1. **Single AWS Credentials:** The same AWS credentials are used for BOTH Bedrock and DynamoDB (no separate MongoDB setup)

2. **Model Tier Strategy:** The backend uses a configurable model tier system:
   - `cheap`: mistral.mistral-7b-instruct-v0:2 (development/testing)
   - `medium`: meta.llama3-1-8b-instruct-v1:0
   - `demo`: anthropic.claude-3-haiku-20240307-v1:0
   - `quality`: anthropic.claude-3-5-sonnet-20241022-v2:0 (production)

   Switch tiers via `AWS_BEDROCK_MODEL_TIER` environment variable

3. **Cognitive Profile Prompts:** Each disability profile has distinct prompt templates with specific constraints:
   - **ADHD:** 5-7 word sentences, frequent hooks, action verbs, high-energy pacing that slows
   - **Autism:** First-Then-Finally structure, concrete literal language, predictable patterns, no idioms
   - **Anxiety:** Repetitive calming phrases, breathing cues, no conflict/danger, safe resolutions

## Development Commands

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration
```bash
# 1. Copy environment template
cp backend/.env.example backend/.env

# 2. Generate Flask secret key
python -c "import secrets; print(secrets.token_hex(32))"

# 3. Add AWS credentials to .env (get from AWS IAM Console)
# Required IAM policies: AmazonBedrockFullAccess, AmazonDynamoDBFullAccess

# 4. Create DynamoDB tables
python -c "from database import create_tables; create_tables()"

# 5. Test configuration
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✓ Loaded' if os.getenv('AWS_ACCESS_KEY_ID') else '✗ Failed')"
```

### Running the Backend
```bash
cd backend
source venv/bin/activate
python app.py  # Development server on http://0.0.0.0:5000
```

### Production Deployment
```bash
cd backend
gunicorn app:app  # WSGI server for production
```

## Key API Endpoints

### POST /api/generate-story
Generates a story based on child profile and preferences.

**Required fields:**
- `profile_type`: "adhd" | "autism" | "anxiety"
- `age`: number
- `theme`: string (e.g., "space", "animals", "adventure")
- `story_length`: number (minutes: 5, 10, or 15)

**Optional fields:**
- `child_id`: string (for history tracking)
- `interests`: array of strings

**Response includes:**
- `story_id`: unique identifier
- `story_text`: generated story
- `profile_used`: which cognitive profile was applied
- `generation_time`: seconds taken
- `cached`: boolean (if from cache)

### POST /api/save-profile
Creates a child profile with cognitive settings.

### GET /api/get-history
Retrieves past stories for a child (requires `child_id` query parameter).

## Prompt Engineering System

The core value proposition is in the prompt templates. Each cognitive profile has:

1. **Length Calculation Formula:**
   ```python
   words_per_minute = {"adhd": 80, "autism": 100, "anxiety": 90}
   avg_words_per_sentence = {"adhd": 6, "autism": 12, "anxiety": 15}
   sentence_count = (words_per_minute * minutes) / avg_words_per_sentence
   ```

2. **Theme Integration:** Predefined theme elements (space: rocket/stars/planets, animals: forest/meadow/pond) get injected into prompts

3. **Dynamic Prompt Building:** `build_prompt()` function combines base template + theme + interests + calculated length

## Database Schema (DynamoDB)

**Note:** All DynamoDB tables must be created before running the application. See Environment Configuration section for setup instructions.

**StoryWeave-Profiles Table:**
- `child_id` (partition key): UUID
- `age`: number
- `cognitive_profile`: list of strings (can be multiple)
- `sensory_preferences`: object
- `interests`: list of strings
- `story_length_preference`: number
- `created_at`, `updated_at`: timestamps

**StoryWeave-Stories Table:**
- `story_id` (partition key): UUID
- `child_id`: UUID
- `story_text`: string
- `profile_used`: string
- `theme`: string
- `generation_parameters`: object
- `timestamp`: datetime
- `user_rating`: number (optional)

**Story Cache Table:**
- `cache_key` (partition key): MD5 hash of generation parameters
- `story_text`: string
- `profile_type`: string
- `created_at`: datetime (ISO 8601 string)
- `access_count`: number
- `expires_at`: number (Unix timestamp for TTL)

## Error Handling Strategy

1. **Retry Logic:** `generate_story_with_retry()` attempts 3 times with exponential backoff (2^attempt seconds)
2. **Fallback Stories:** Pre-written stories for each profile type used when API fails
3. **User-Friendly Messages:** Map AWS exceptions to readable error messages (ThrottlingException → "Too many requests...")
4. **Caching:** Reduce API calls by caching stories with identical parameters

## Accessibility Requirements (WCAG 2.1 Level AA)

When implementing frontend:
- Color contrast ≥4.5:1 for normal text, ≥3:1 for large text
- All interactive elements keyboard accessible
- Focus indicators 2px solid outline
- ARIA labels on all custom components
- ARIA live regions for story generation status
- Dyslexia-friendly font option (OpenDyslexic)
- No autoplay audio, pause/stop controls required
- Support prefers-reduced-motion for animations
- Semantic HTML (nav, main, article, section)

## Important Notes

- **No MongoDB:** Despite references in StoryWeave-Project.md, the actual implementation uses DynamoDB
- **AWS Region:** Default is us-west-2, ensure Bedrock is available in chosen region
- **Python Version:** Requires Python 3.9+
- **Response Time Target:** <3 seconds for story generation
- **Rate Limiting:** 30 requests/minute (configurable via RATE_LIMIT)

## Project File Structure

```
StoryWeave/
├── backend/
│   ├── app.py                    # Main Flask application (to be created)
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment variable template
│   └── database.py              # DynamoDB setup (to be created)
├── frontend/                     # React app (not yet implemented)
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── utils/
├── StoryWeave-Project.md        # Comprehensive project specification
└── struc.example                # Expected project structure
```

## Testing Story Generation

To verify cognitive profile differences, check:
- ADHD: Average sentence length <10 words, contains action verbs
- Autism: Contains "First", "Then", "Finally" keywords, no metaphors
- Anxiety: Contains calming phrases like "safe", "calm", breathing cues

## Common Pitfalls

1. **Don't use MongoDB connection strings** - this project uses DynamoDB
2. **Don't skip model tier configuration** - costs vary 100x between cheap and quality models
3. **Don't forget DynamoDB table creation** - tables won't auto-create, run the setup script
4. **Don't hardcode model IDs** - use the tier system for flexibility
5. **Validate story output matches profile** - the prompt engineering is the core IP

## Theme Elements Reference

Quick reference for story generation:
- **Space:** rocket, stars, planets, moon, astronaut, flying, exploring
- **Animals:** forest, meadow, pond, nest, burrow, playing, resting
- **Adventure:** path, bridge, garden, treehouse, walking, discovering
