# StoryWeave MVP Setup Guide

## Current Status

✅ **Complete:**
- Backend API implementation (Flask)
- DynamoDB database layer
- AWS Bedrock story generation
- Cognitive profile prompts (ADHD, Autism, Anxiety)
- Environment configuration
- Dependencies installed

⚠️ **Requires AWS Configuration:**
- DynamoDB table creation
- IAM permissions setup

## AWS IAM Permissions Issue

The current AWS IAM user (`William`) lacks permissions to create DynamoDB tables. This needs to be fixed before the application can run.

### Required AWS Permissions

The IAM user needs the following managed policies attached:

1. **AmazonDynamoDBFullAccess**
   - Allows creating, reading, updating, and deleting DynamoDB tables
   - Required for table creation and all database operations

2. **AmazonBedrockFullAccess**
   - Allows invoking AWS Bedrock models
   - Required for story generation

### How to Fix IAM Permissions

#### Option 1: AWS Console (Recommended)

1. Go to AWS IAM Console: https://console.aws.amazon.com/iam/
2. Click "Users" in the left sidebar
3. Find and click on user "William"
4. Click "Add permissions" → "Attach policies directly"
5. Search for and select:
   - `AmazonDynamoDBFullAccess`
   - `AmazonBedrockFullAccess`
6. Click "Next" then "Add permissions"

#### Option 2: AWS CLI

```bash
aws iam attach-user-policy \
  --user-name William \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-user-policy \
  --user-name William \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

#### Option 3: Create Custom Policy (More Restrictive)

If you want minimal permissions, create a custom policy with only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:UpdateItem",
        "dynamodb:UpdateTimeToLive"
      ],
      "Resource": "arn:aws:dynamodb:us-west-2:654654509018:table/StoryWeave-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

## Setup Steps (Once Permissions are Fixed)

### 1. Create DynamoDB Tables

```bash
cd backend
./venv/bin/python database.py
```

Expected output:
```
Creating DynamoDB tables...
✓ Table StoryWeave-Profiles created successfully
✓ Table StoryWeave-Stories created successfully
✓ Table StoryWeave-Cache created successfully
✓ TTL enabled on StoryWeave-Cache

✓ All tables created successfully!

You can now run the Flask application.
```

### 2. Start the Backend API

```bash
cd backend
./venv/bin/python app.py
```

The API will start on `http://0.0.0.0:5000`

### 3. Test the API

#### Health Check
```bash
curl http://localhost:5000/api/health
```

#### Generate a Story
```bash
curl -X POST http://localhost:5000/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{
    "profile_type": "adhd",
    "age": 7,
    "theme": "space",
    "story_length": 5,
    "interests": ["rockets", "astronauts"]
  }'
```

#### Create a Profile
```bash
curl -X POST http://localhost:5000/api/save-profile \
  -H "Content-Type: application/json" \
  -d '{
    "age": 7,
    "cognitive_profile": ["adhd"],
    "interests": ["space", "animals"],
    "story_length_preference": 10
  }'
```

## Project Structure

```
StoryWeave/
├── backend/
│   ├── app.py                 # Main Flask API ✅
│   ├── database.py            # DynamoDB operations ✅
│   ├── story_generator.py     # AWS Bedrock integration ✅
│   ├── prompts.py            # Cognitive profile prompts ✅
│   ├── utils.py              # Helper functions ✅
│   ├── requirements.txt       # Dependencies ✅
│   ├── .env                  # Environment variables ✅
│   ├── venv/                 # Virtual environment ✅
│   └── README.md             # Backend documentation ✅
├── CLAUDE.md                 # Development guide ✅
├── StoryWeave-Project.md     # Full specification ✅
└── SETUP.md                  # This file ✅
```

## Features Implemented

### API Endpoints

1. **POST /api/generate-story** - Generate personalized stories
   - Supports 3 cognitive profiles (ADHD, Autism, Anxiety)
   - Caching system for performance
   - Retry logic with fallback stories
   - Response time tracking

2. **POST /api/save-profile** - Create child profiles
   - Multiple cognitive profiles supported
   - Sensory preferences
   - Interest tracking

3. **GET /api/get-history** - Retrieve story history
   - Query by child_id
   - Configurable limit
   - Sorted by timestamp (newest first)

4. **GET /api/get-profile** - Retrieve child profile
   - Full profile data returned

5. **GET /api/health** - Health check endpoint

### Story Generation

- **ADHD Profile**: Short sentences (5-7 words), high energy → calm pacing, action verbs
- **Autism Profile**: First-Then-Finally structure, literal language, predictable patterns
- **Anxiety Profile**: Calming phrases, breathing cues, safe and peaceful tone

### Database

- **DynamoDB tables ready** (pending creation):
  - `StoryWeave-Profiles` - Child profiles
  - `StoryWeave-Stories` - Story history with GSI for querying by child
  - `StoryWeave-Cache` - Story cache with 24-hour TTL

### AI Model Support

Flexible model tier system:
- **cheap**: Mistral 7B (for testing)
- **medium**: Llama 3.1 8B
- **demo**: Claude Haiku
- **quality**: Claude 3.5 Sonnet (current setting)

## Cost Estimates

With proper AWS free tier usage:
- **DynamoDB**: Free for first 25GB storage + 25 WCU/RCU
- **Bedrock**: Pay per token
  - Mistral 7B: ~$0.00015 per 1K tokens (cheap)
  - Claude Haiku: ~$0.00025 per 1K tokens (demo)
  - Claude Sonnet: ~$0.003 per 1K tokens (quality)
- **Estimated**: $0.01-0.05 per story generated (depending on model)

## Next Steps

1. **Fix IAM permissions** (see above)
2. **Create DynamoDB tables** (`python database.py`)
3. **Test story generation** with all three cognitive profiles
4. **Deploy to Railway/Heroku** (optional)
5. **Build React frontend** (future work)

## Troubleshooting

### "AccessDeniedException" when creating tables
- **Fix**: Attach DynamoDB permissions to IAM user (see above)

### "Model not found" or Bedrock errors
- **Fix**: Ensure Bedrock model access is enabled in your AWS region
- Go to AWS Bedrock Console → Model Access → Enable models

### Import errors
- **Fix**: Activate virtual environment: `source venv/bin/activate`

### Connection timeout
- **Fix**: Check AWS credentials in `.env` file
- Verify AWS region is correct (`us-west-2`)

## Security Notes

- ✅ `.env` file is gitignored (credentials safe)
- ✅ AWS credentials should be rotated after sharing in chat
- ✅ IAM user should have minimal required permissions
- ✅ CORS is configured for localhost only

## Contact

AWS Account ID: 654654509018
IAM User: Sami
Region: us-west-2

Once IAM permissions are configured, the MVP will be fully operational!
