/**
 * API client for StoryWeave backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

/**
 * Health check endpoint
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
};

/**
 * Map frontend profile to backend profile_type
 */
const mapProfileType = (conditions) => {
  if (!conditions || conditions.length === 0) {
    return 'general';
  }

  // Priority: ADHD > Autism > Anxiety
  if (conditions.some(c => c.toLowerCase().includes('adhd'))) {
    return 'adhd';
  }
  if (conditions.some(c => c.toLowerCase().includes('autism'))) {
    return 'autism';
  }
  if (conditions.some(c => c.toLowerCase().includes('anxiety') || c.toLowerCase().includes('sensory'))) {
    return 'anxiety';
  }

  return 'general';
};

/**
 * Map frontend length to backend story_length (in minutes)
 */
const mapStoryLength = (length) => {
  const lengthMap = {
    'short': 5,
    'medium': 10,
    'long': 15
  };
  return lengthMap[length] || 10;
};

/**
 * Create a child profile
 */
export const createProfile = async (profileData) => {
  try {
    // Normalize cognitive profile values to lowercase
    const normalizedConditions = (profileData.conditions || []).map(c => {
      const lower = c.toLowerCase();
      if (lower.includes('adhd')) return 'adhd';
      if (lower.includes('autism')) return 'autism';
      if (lower.includes('anxiety') || lower.includes('sensory')) return 'anxiety';
      return 'general';
    });

    const response = await fetch(`${API_URL}/save-profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        age: parseInt(profileData.age),
        cognitive_profile: normalizedConditions.length > 0 ? normalizedConditions : ['general'],
        interests: profileData.preferences.favoriteThemes
          ? profileData.preferences.favoriteThemes.split(',').map(t => t.trim()).filter(t => t)
          : [],
        story_length_preference: mapStoryLength(profileData.preferences.pacing)
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create profile');
    }

    const data = await response.json();
    return {
      ...data,
      childName: profileData.childName
    };
  } catch (error) {
    console.error('Create profile error:', error);
    throw error;
  }
};

/**
 * Generate a story
 */
export const generateStory = async (profile, storyParams, imageConfig = null) => {
  try {
    const profile_type = mapProfileType(profile.conditions);
    const story_length = mapStoryLength(storyParams.length);

    // Extract interests from both fields
    const favoriteThemes = profile.preferences.favoriteThemes
      ? profile.preferences.favoriteThemes.split(',').map(t => t.trim()).filter(t => t)
      : [];
    const characters = storyParams.characters
      ? storyParams.characters.split(',').map(t => t.trim()).filter(t => t)
      : [];
    const interests = [...new Set([...favoriteThemes, ...characters])]; // Remove duplicates

    const requestBody = {
      profile_type,
      age: parseInt(profile.age),
      theme: storyParams.genre || 'adventure',
      story_length,
      interests: interests.length > 0 ? interests : ['adventure', 'friendship'],
      child_id: profile.child_id, // Include if available from profile creation
      generate_images: imageConfig?.enabled || false,
      pages_per_image: imageConfig?.pagesPerImage || 4
    };

    console.log('Generating story with params:', requestBody);

    const response = await fetch(`${API_URL}/generate-story`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to generate story');
    }

    const data = await response.json();

    // Log generation details
    console.log('✅ Story generated successfully:');
    console.log(`   Profile: ${data.profile_used || profile_type}`);
    console.log(`   Generation time: ${data.generation_time?.toFixed(2)}s`);
    console.log(`   Cached: ${data.cached ? 'Yes' : 'No'}`);
    console.log(`   Fallback: ${data.fallback ? 'YES (using backup story)' : 'No (Claude-generated)'}`);
    console.log(`   Story length: ${data.story_text?.length} characters`);

    return {
      story: data.story_text,
      images: data.images || [],
      metadata: {
        profile_type: data.profile_used,
        generation_time: data.generation_time,
        cached: data.cached,
        fallback: data.fallback,
        story_id: data.story_id
      }
    };
  } catch (error) {
    console.error('Generate story error:', error);
    throw error;
  }
};

/**
 * Get story history for a child
 */
export const getStoryHistory = async (childId) => {
  try {
    const response = await fetch(`${API_URL}/story-history/${childId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get story history');
    }

    return await response.json();
  } catch (error) {
    console.error('Get story history error:', error);
    throw error;
  }
};

/**
 * Get a child profile
 */
export const getProfile = async (childId) => {
  try {
    const response = await fetch(`${API_URL}/get-profile/${childId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get profile');
    }

    return await response.json();
  } catch (error) {
    console.error('Get profile error:', error);
    throw error;
  }
};

/**
 * Generate audio narration for text using ElevenLabs v3
 */
export const generateAudio = async (text, mood = 'calm', theme = '', voiceId = null) => {
  try {
    const response = await fetch(`${API_URL}/generate-audio`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        mood,
        theme,
        voice_id: voiceId
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to generate audio');
    }

    const data = await response.json();

    // Convert base64 to blob URL for audio playback
    const audioBlob = base64ToBlob(data.audio_data, 'audio/mpeg');
    const audioUrl = URL.createObjectURL(audioBlob);

    return {
      audioUrl,
      audioBlob,
      textLength: data.text_length,
      mood: data.mood,
      theme: data.theme
    };
  } catch (error) {
    console.error('Generate audio error:', error);
    throw error;
  }
};

/**
 * Helper function to convert base64 to blob
 */
const base64ToBlob = (base64, contentType) => {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);

  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }

  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: contentType });
};
