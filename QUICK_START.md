# StoryWeave - Quick Start Guide

**Last Updated:** October 18, 2025

## 🚀 Running the Code (5 Minutes)

### Prerequisites
- Python 3.9+ installed
- AWS account with credentials
- Terminal access

### Step 1: Navigate to Backend
```bash
cd /Users/gilliam/Desktop/stpryweave/StoryWeave/backend
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```
> **Note:** Virtual environment already created with all dependencies installed ✅

### Step 3: Verify Environment Variables
Check that `.env` file exists with AWS credentials:
```bash
cat .env | grep AWS_ACCESS_KEY_ID
```

You should see your AWS credentials (already configured ✅)

### Step 4: Create DynamoDB Tables (First Time Only)

**⚠️ IMPORTANT:** This requires IAM permissions. If you get an error, see "IAM Fix" section below.

```bash
python database.py
```

**Expected output:**
```
Creating DynamoDB tables...
✓ Table StoryWeave-Profiles created successfully
✓ Table StoryWeave-Stories created successfully
✓ Table StoryWeave-Cache created successfully
✓ TTL enabled on StoryWeave-Cache
```

### Step 5: Start the API Server
```bash
python app.py
```

**Expected output:**
```
Starting StoryWeave API on 0.0.0.0:5000
* Running on http://127.0.0.1:5000
```

**If port 5000 is in use:**
```bash
PORT=5001 python app.py
```

---

## 🧪 Testing the Code

### Test 1: Health Check
```bash
curl http://localhost:5000/api/health
```

**Expected:**
```json
{
  "service": "StoryWeave API",
  "status": "healthy",
  "version": "1.0.0"
}
```

### Test 2: Create a Profile
```bash
curl -X POST http://localhost:5000/api/save-profile \
  -H "Content-Type: application/json" \
  -d '{
    "age": 7,
    "cognitive_profile": ["adhd"],
    "interests": ["space", "robots"],
    "story_length_preference": 10
  }'
```

**Expected:**
```json
{
  "child_id": "uuid-string",
  "profile_created": "2025-10-18T...",
  "success": true
}
```

### Test 3: Generate a Story (ADHD)
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

**Expected:** Story generated in <3 seconds with short sentences (5-7 words)

### Test 4: Generate Story (Autism)
```bash
curl -X POST http://localhost:5000/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{
    "profile_type": "autism",
    "age": 8,
    "theme": "animals",
    "story_length": 10,
    "interests": ["cats", "dogs"]
  }'
```

**Expected:** Story with First-Then-Finally structure

### Test 5: Generate Story (Anxiety)
```bash
curl -X POST http://localhost:5000/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{
    "profile_type": "anxiety",
    "age": 6,
    "theme": "adventure",
    "story_length": 5,
    "interests": ["gardens", "nature"]
  }'
```

**Expected:** Calming story with safety phrases

### Test 6: View Sample Stories
Pre-generated sample stories are available:
```bash
ls sample_stories/
cat sample_stories/story_01_adhd_space_age5.txt
```

---

## ⚙️ Advanced Testing

### Generate Sample Story Library
```bash
python generate_sample_stories.py
```

This creates 9 stories (3 per profile) with full metadata in `sample_stories/`

### Test Story Generation Directly
```bash
python story_generator.py
```

This tests AWS Bedrock integration without the API

### Test All Three Profiles
```bash
python -c "
from story_generator import create_story

for profile in ['adhd', 'autism', 'anxiety']:
    result = create_story(profile, 7, 'space', ['rockets'], 5)
    print(f'{profile.upper()}: {len(result[\"story\"])} chars')
"
```

---

## 🔧 IAM Permission Fix (If Tables Won't Create)

If you get `AccessDeniedException` when creating tables:

### Option 1: AWS Console (Easiest)
1. Go to: https://console.aws.amazon.com/iam/
2. Click **Users** → Find user "Sami"
3. Click **Add permissions** → **Attach policies directly**
4. Search and select:
   - `AmazonDynamoDBFullAccess`
   - `AmazonBedrockFullAccess`
5. Click **Add permissions**

### Option 2: AWS CLI
```bash
aws iam attach-user-policy \
  --user-name Sami \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-user-policy \
  --user-name Sami \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

**Then retry:**
```bash
python database.py
```

---

## 📊 What Works Right Now

✅ **Working (Core Features):**
- Story generation for all 3 cognitive profiles
- AWS Bedrock integration (Mistral 7B model)
- Profile creation and storage
- API endpoints (health, save-profile, generate-story)
- Error handling with graceful degradation
- Pre-generated sample stories

⚠️ **Partial (Needs Tables):**
- Story caching (requires StoryWeave-Cache table)
- Story history (requires StoryWeave-Stories table)

**Note:** Even without the missing tables, story generation works perfectly!

---

## 🎯 Quick Test Checklist

- [ ] Virtual environment activated
- [ ] AWS credentials in `.env` file
- [ ] DynamoDB tables created (or IAM fix applied)
- [ ] API server running on port 5000/5001
- [ ] Health endpoint returns "healthy"
- [ ] Profile creation works
- [ ] ADHD story generates (short sentences)
- [ ] Autism story generates (First-Then-Finally)
- [ ] Anxiety story generates (calming language)

---

## 📖 File Locations

```
StoryWeave/
├── QUICK_START.md           ← You are here
├── SETUP.md                 ← Detailed setup guide
├── TEST_RESULTS.md          ← What was tested
├── CLAUDE.md                ← Developer documentation
└── backend/
    ├── README.md            ← Backend-specific docs
    ├── app.py               ← Main API server
    ├── database.py          ← DynamoDB operations
    ├── story_generator.py   ← Story generation
    ├── generate_sample_stories.py  ← Sample story generator
    └── sample_stories/      ← Pre-generated stories
```

---

## 🆘 Common Issues

### "Port 5000 already in use"
**Fix:** Use a different port
```bash
PORT=5001 python app.py
```

### "Module not found: boto3"
**Fix:** Activate virtual environment
```bash
source venv/bin/activate
pip list | grep boto3  # Should show version 1.34.28
```

### "AccessDeniedException" when creating tables
**Fix:** Add IAM permissions (see IAM section above)

### "Float types are not supported"
**Fix:** Already fixed in app.py ✅ (uses Decimal conversion)

### Stories not caching
**Expected:** Cache table missing (needs IAM permissions)
**Impact:** Stories still generate, just not cached

---

## 🚀 Production Deployment (Optional)

### Change Model Tier for Better Quality
Edit `.env`:
```bash
# For production/demo quality:
AWS_BEDROCK_MODEL_TIER=quality

# For development/testing (current):
AWS_BEDROCK_MODEL_TIER=cheap
```

**Restart server after changes**

### Available Model Tiers
- `cheap`: Mistral 7B (~$0.001/story)
- `medium`: Llama 3.1 8B
- `demo`: Claude Haiku (~$0.01/story)
- `quality`: Claude Sonnet 3.5 (~$0.05/story)

---

## 📞 Support

**Issues?** Check these files:
1. `TEST_RESULTS.md` - Known issues and fixes
2. `SETUP.md` - Detailed troubleshooting
3. `backend/README.md` - Backend-specific help

**AWS Account:** 654654509018
**IAM User:** Sami
**Region:** us-west-2

---

## ✨ You're All Set!

The MVP is fully functional. Start the server and test the API to see AI-generated bedtime stories for neurodivergent children!

```bash
# Quick test:
python app.py
# In another terminal:
curl http://localhost:5000/api/health
```
