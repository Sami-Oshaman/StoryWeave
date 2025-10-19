# StoryWeave Backend API

Flask REST API for generating personalized bedtime stories for neurodivergent children.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file should already be configured. Verify it contains:
- AWS credentials (Access Key ID and Secret Access Key)
- AWS region (us-west-2)
- Model tier configuration

### 3. Create DynamoDB Tables

```bash
python database.py
```

This will create three tables:
- `StoryWeave-Profiles` - Child profiles
- `StoryWeave-Stories` - Story history
- `StoryWeave-Cache` - Story cache with 24hr TTL

### 4. Run the API

```bash
python app.py
```

The API will start on `http://0.0.0.0:5000`

## API Endpoints

### Health Check
```
GET /api/health
```

### Generate Story
```
POST /api/generate-story

Request Body:
{
  "profile_type": "adhd|autism|anxiety",
  "age": 7,
  "theme": "space",
  "story_length": 10,
  "interests": ["rockets", "astronauts"],
  "child_id": "optional-uuid"
}

Response:
{
  "story_id": "uuid",
  "story_text": "Once upon a time...",
  "profile_used": "adhd",
  "generation_time": 2.34,
  "cached": false
}
```

### Save Profile
```
POST /api/save-profile

Request Body:
{
  "age": 7,
  "cognitive_profile": ["adhd"],
  "sensory_preferences": {},
  "interests": ["space", "animals"],
  "story_length_preference": 10
}

Response:
{
  "child_id": "uuid",
  "profile_created": "2024-01-01T00:00:00Z",
  "success": true
}
```

### Get Story History
```
GET /api/get-history?child_id=uuid&limit=10

Response:
{
  "child_id": "uuid",
  "stories": [...],
  "count": 10
}
```

### Get Profile
```
GET /api/get-profile?child_id=uuid

Response:
{
  "child_id": "uuid",
  "age": 7,
  "cognitive_profile": ["adhd"],
  ...
}
```

## Model Tiers

The backend supports multiple AI model tiers for different use cases:

- **cheap**: Mistral 7B (fast, low cost - good for testing)
- **medium**: Llama 3.1 8B (balanced)
- **demo**: Claude Haiku (good quality)
- **quality**: Claude 3.5 Sonnet (best quality - for production)

Change the tier in `.env`:
```
AWS_BEDROCK_MODEL_TIER=cheap
```

## Testing

### Test Story Generation
```bash
python story_generator.py
```

### Test API with curl
```bash
# Generate a story
curl -X POST http://localhost:5000/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{
    "profile_type": "adhd",
    "age": 7,
    "theme": "space",
    "story_length": 5,
    "interests": ["rockets"]
  }'
```

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── database.py            # DynamoDB operations
├── story_generator.py     # AWS Bedrock integration
├── prompts.py            # Cognitive profile prompts
├── utils.py              # Helper functions
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (gitignored)
└── .env.example          # Environment template
```

## Troubleshooting

### AWS Credentials Error
- Verify `.env` has correct AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- Check IAM user has `AmazonBedrockFullAccess` and `AmazonDynamoDBFullAccess`

### Table Not Found
- Run `python database.py` to create tables
- Wait 10-15 seconds for tables to become active

### Model Not Available
- Ensure AWS Bedrock model access is enabled in your AWS region
- Try switching to a different model tier

### Import Errors
- Ensure you activated the virtual environment
- Run `pip install -r requirements.txt`

## Development

The API uses:
- Flask 3.0 for REST API
- boto3 for AWS services
- python-dotenv for environment management
- Flask-CORS for cross-origin requests

All configuration is in `.env` - never commit this file!
