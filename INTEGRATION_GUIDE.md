# StoryWeave Frontend-Backend Integration Guide

**Date:** October 18, 2025

---

## Integration Complete ✅

The StoryWeave frontend has been successfully integrated with the backend API.

---

## Project Structure

```
StoryWeave/
├── backend/               # Flask API (Python)
│   ├── app.py            # Main API server
│   ├── database.py       # DynamoDB operations
│   ├── story_generator.py # Claude Sonnet 4.5 integration
│   ├── prompts.py        # Profile-specific prompts
│   ├── api.js            # API client (NEW)
│   └── .env              # Backend config (PORT=5001)
│
└── storyweave/           # React Frontend (Vite)
    ├── src/
    │   ├── App.jsx       # Main app (UPDATED)
    │   ├── api.js        # API client (NEW)
    │   └── main.jsx      # Entry point
    ├── .env              # Frontend config (NEW)
    └── package.json      # Dependencies

```

---

## Changes Made

### 1. Frontend API Client (`storyweave/src/api.js`)

Created a new API client module with functions:

- `healthCheck()` - Test API connection
- `createProfile(profileData)` - Create child profile
- `generateStory(profile, storyParams)` - Generate personalized story
- `getStoryHistory(childId)` - Get past stories
- `getProfile(childId)` - Retrieve profile

**Key Features:**
- Automatic profile type mapping (ADHD, Autism, Anxiety, General)
- Story length conversion (short/medium/long → 5/10/15 minutes)
- Interest extraction from multiple form fields
- Error handling and logging

### 2. Frontend Configuration (`.env`)

```bash
VITE_API_URL=http://localhost:5001/api
```

### 3. Updated App.jsx

**ProfileSetup Component:**
- ✅ Added API integration for profile creation
- ✅ Added loading states
- ✅ Added error handling
- ✅ Stores `child_id` from backend response

**StoryGenerator Component:**
- ✅ Added API integration for story generation
- ✅ Added loading states with progress indicator
- ✅ Added error handling
- ✅ Shows generation time (30-40 seconds)

**StoryDisplay Component:**
- ✅ Updated to accept `storyData` prop
- ✅ Automatically splits story into pages
- ✅ Handles markdown formatting from backend

---

## API Endpoint Mapping

| Frontend Function | Backend Endpoint | Method | Purpose |
|-------------------|------------------|--------|---------|
| `createProfile()` | `/api/save-profile` | POST | Create child profile |
| `generateStory()` | `/api/generate-story` | POST | Generate story |
| `getStoryHistory()` | `/api/story-history/:id` | GET | Get past stories |
| `getProfile()` | `/api/get-profile/:id` | GET | Retrieve profile |
| `healthCheck()` | `/api/health` | GET | API health check |

---

## Profile Type Mapping

Frontend conditions are automatically mapped to backend profile types:

| Frontend Condition | Backend `profile_type` |
|--------------------|------------------------|
| ADHD | `adhd` |
| Autism Spectrum | `autism` |
| Sensory Processing Disorder | `anxiety` |
| No conditions selected | `general` |

---

## Story Length Mapping

| Frontend Selection | Backend `story_length` |
|--------------------|------------------------|
| Short (~3 min) | 5 minutes |
| Medium (~5 min) | 10 minutes |
| Long (~8 min) | 15 minutes |

---

## Running the Full Stack

### Terminal 1: Start Backend
```bash
cd backend
source venv/bin/activate
PORT=5001 python app.py
```

Backend runs on: `http://localhost:5001`

### Terminal 2: Start Frontend
```bash
cd storyweave
npm run dev
```

Frontend runs on: `http://localhost:5173` (Vite default)

---

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:5001/api/health
```

Expected:
```json
{
  "service": "StoryWeave API",
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Open Frontend
Navigate to: `http://localhost:5173`

### 3. Create Profile
1. Enter child's name and age
2. Select any conditions (optional)
3. Add favorite themes
4. Click "Create Profile & Continue"

### 4. Generate Story
1. Choose story length
2. Select tonight's mood
3. Enter genre/theme
4. Add characters (optional)
5. Click "Generate Story"
6. Wait 30-40 seconds for Claude Sonnet 4.5 to generate

### 5. Read Story
- Navigate through pages
- Use audio playback
- Generate new stories

---

## Error Handling

Both frontend and backend include comprehensive error handling:

**Frontend:**
- Displays user-friendly error messages
- Shows loading states
- Disables buttons during operations
- Logs errors to console

**Backend:**
- Returns structured error responses
- Includes error codes and messages
- Logs all errors
- Graceful degradation to fallback stories

---

## CORS Configuration

Backend (`app.py`) is configured to allow frontend connections:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173"  # Vite default port
        ]
    }
})
```

---

## Environment Variables

### Backend (`.env`)
```bash
# API Configuration
PORT=5001
HOST=0.0.0.0

# AWS Configuration
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-west-2

# Claude Model (Inference Profile ARN)
AWS_BEDROCK_MODEL_TIER=medium
AWS_BEDROCK_MODEL_MEDIUM=arn:aws:bedrock:us-west-2:296062573602:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

### Frontend (`.env`)
```bash
VITE_API_URL=http://localhost:5001/api
```

---

## Production Deployment

### Backend
1. Set environment variables
2. Update CORS origins for production domain
3. Deploy to Railway/Heroku/AWS
4. Note the production URL

### Frontend
1. Update `.env`:
   ```bash
   VITE_API_URL=https://your-backend.com/api
   ```
2. Build: `npm run build`
3. Deploy `dist/` folder to Vercel/Netlify

---

## Troubleshooting

### Issue: "Failed to fetch"
- **Cause:** Backend not running
- **Fix:** Start backend on port 5001

### Issue: "CORS error"
- **Cause:** Frontend running on unexpected port
- **Fix:** Add port to CORS config in `backend/app.py`

### Issue: "Profile creation failed"
- **Cause:** DynamoDB permissions
- **Fix:** Check AWS credentials and IAM permissions

### Issue: "Story generation timeout"
- **Cause:** Claude model taking longer than expected
- **Fix:** Normal for first request, should be ~30-40s

---

## Next Steps

✅ **Integration Complete**
✅ **All 4 Profile Types Working**
✅ **Frontend-Backend Communication Established**

**Optional Enhancements:**
- Add story history view
- Implement profile editing
- Add story favoriting
- Create shareable story links
- Add more themes and customization

---

**Status:** 🎉 **Production Ready** - Full stack integrated and working!
