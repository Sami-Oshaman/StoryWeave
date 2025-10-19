import React, { useState, useEffect, useRef } from 'react';
import { Moon, Sun, Volume2, VolumeX, ChevronLeft, ChevronRight, Sparkles, Play, Pause } from 'lucide-react';
import { signup, login, getUser, createProfile, generateStory, generateAudio } from './api';

// Login/Signup Screen
const AuthScreen = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Basic validation
      if (!isLogin && formData.password !== formData.confirmPassword) {
        setError('Passwords do not match!');
        setLoading(false);
        return;
      }

      let userData;
      if (isLogin) {
        // Login
        userData = await login(formData.email, formData.password);
      } else {
        // Signup
        await signup(formData.email, formData.password, formData.name);
        // Auto-login after signup
        userData = await login(formData.email, formData.password);
      }

      // Store user data
      localStorage.setItem('storyweave_user', JSON.stringify(userData));

      onLogin(userData);
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-6 py-16">
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">🌙</div>
        <h1 className="text-5xl font-bold text-purple-300 mb-3">
          {isLogin ? 'Welcome Back' : 'Join StoryWeave'}
        </h1>
        <p className="text-xl text-purple-200">
          {isLogin ? 'Continue your bedtime story journey' : 'Create magical stories for your little one'}
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-500/20 border border-red-500 rounded-xl text-red-200 text-center">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white/5 backdrop-blur-md rounded-3xl p-8 border border-purple-800/30">
        <div className="space-y-5">
          {!isLogin && (
            <div>
              <label className="block text-base text-purple-200 mb-2 font-medium">
                Parent Name
              </label>
              <input
                type="text"
                placeholder="Your name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
                required={!isLogin}
              />
            </div>
          )}

          <div>
            <label className="block text-base text-purple-200 mb-2 font-medium">
              Email Address
            </label>
            <input
              type="email"
              placeholder="parent@email.com"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
              required
            />
          </div>

          <div>
            <label className="block text-base text-purple-200 mb-2 font-medium">
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
              required
              minLength={6}
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-base text-purple-200 mb-2 font-medium">
                Confirm Password
              </label>
              <input
                type="password"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
                required={!isLogin}
                minLength={6}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 px-6 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 text-white text-lg font-semibold rounded-xl transition-colors mt-4 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                {isLogin ? 'Signing in...' : 'Creating account...'}
              </>
            ) : (
              <>
                <Sparkles size={20} />
                {isLogin ? 'Sign In' : 'Create Account'}
              </>
            )}
          </button>
        </div>
      </form>

      <div className="text-center mt-6">
        <button
          onClick={() => setIsLogin(!isLogin)}
          className="text-purple-300 hover:text-purple-200 transition-colors"
        >
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <span className="font-semibold underline">
            {isLogin ? 'Sign Up' : 'Sign In'}
          </span>
        </button>
      </div>
    </div>
  );
};

// Child Profile Screen
const ProfileSetup = ({ onComplete, user, existingProfile = null }) => {
  const [profile, setProfile] = useState(existingProfile || {
    childName: '',
    age: '',
    conditions: [],
    preferences: {
      pacing: 'medium',
      sensoryLevel: 50,
      favoriteThemes: '',
      avoidThemes: ''
    }
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await createProfile(profile, user.email);
      onComplete({ ...profile, child_id: result.child_id });
    } catch (err) {
      setError(err.message || 'Failed to create profile');
      console.error('Profile creation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleCondition = (condition) => {
    if (profile.conditions.includes(condition)) {
      setProfile({...profile, conditions: profile.conditions.filter(c => c !== condition)});
    } else {
      setProfile({...profile, conditions: [...profile.conditions, condition]});
    }
  };

  const isEditing = existingProfile !== null;

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-purple-300 mb-3">
          ✨ {isEditing ? 'Update' : 'Create'} Your Child's Profile
        </h1>
        <p className="text-xl text-purple-200">
          {isEditing ? 'Make changes to personalize stories even better' : 'Help us personalize bedtime stories for your little one'}
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-500/20 border border-red-500 rounded-xl text-red-200 text-center">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white/5 backdrop-blur-md rounded-3xl p-8 border border-purple-800/30">
        <div className="space-y-6">
          {/* Basic Info */}
          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Child's Name *
            </label>
            <input
              type="text"
              placeholder="Maya"
              value={profile.childName}
              onChange={(e) => setProfile({...profile, childName: e.target.value})}
              className="w-full px-4 py-3 text-lg bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
              required
            />
          </div>

          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Age *
            </label>
            <input
              type="number"
              placeholder="5"
              min="3"
              max="12"
              value={profile.age}
              onChange={(e) => setProfile({...profile, age: e.target.value})}
              className="w-full px-4 py-3 text-lg bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
              required
            />
            <p className="text-sm text-purple-300 mt-2">Ages 3-12 supported</p>
          </div>

          <div className="border-t border-purple-700/30 pt-6"></div>

          {/* Conditions */}
          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Developmental Profile (Optional)
            </label>
            <p className="text-sm text-purple-300 mb-4">
              Help us adapt the story structure for your child
            </p>
            <div className="space-y-3">
              {['ADHD', 'Autism Spectrum', 'Anxiety', 'Sensory Processing Disorder'].map((condition) => (
                <label key={condition} className="flex items-start gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={profile.conditions.includes(condition)}
                    onChange={() => toggleCondition(condition)}
                    className="w-5 h-5 mt-0.5 rounded border-2 border-purple-600 bg-white/5 checked:bg-purple-600 checked:border-purple-600 focus:ring-2 focus:ring-purple-500/20 cursor-pointer"
                  />
                  <span className="text-base text-purple-100 group-hover:text-white">
                    {condition}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="border-t border-purple-700/30 pt-6"></div>

          {/* Story Preferences */}
          <div>
            <label className="block text-lg text-purple-200 mb-3 font-medium">
              Story Pacing
            </label>
            <div className="space-y-3">
              {[
                { value: 'slow', label: 'Slow & Gentle', desc: 'Calming, longer descriptions' },
                { value: 'medium', label: 'Balanced', desc: 'Mix of action and calm' },
                { value: 'fast', label: 'Quick & Engaging', desc: 'Short sentences, frequent hooks' }
              ].map((option) => (
                <label key={option.value} className="flex items-start gap-3 cursor-pointer group">
                  <input
                    type="radio"
                    name="pacing"
                    value={option.value}
                    checked={profile.preferences.pacing === option.value}
                    onChange={(e) => setProfile({...profile, preferences: {...profile.preferences, pacing: e.target.value}})}
                    className="w-5 h-5 mt-0.5 border-2 border-purple-600 bg-white/5 checked:bg-purple-600 focus:ring-2 focus:ring-purple-500/20 cursor-pointer"
                  />
                  <div>
                    <div className="text-base text-purple-100 group-hover:text-white">
                      {option.label}
                    </div>
                    <div className="text-sm text-purple-300">
                      {option.desc}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Favorite Themes
            </label>
            <textarea
              placeholder="Animals, space, princesses, dinosaurs..."
              value={profile.preferences.favoriteThemes}
              onChange={(e) => setProfile({...profile, preferences: {...profile.preferences, favoriteThemes: e.target.value}})}
              className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400 resize-none"
              rows={2}
            />
          </div>

          <button
            type="submit"
            disabled={!profile.childName || !profile.age || loading}
            className="w-full py-4 px-6 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 disabled:cursor-not-allowed text-white text-xl font-semibold rounded-xl transition-colors mt-6"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Saving...
              </span>
            ) : (
              <span>{isEditing ? 'Save Changes & Continue' : 'Create Profile & Start Reading'}</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

// Story Generation Screen (from App_1.jsx)
const StoryGenerator = ({ profile, onGenerate, onEditProfile, user }) => {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [storyParams, setStoryParams] = useState({
    length: 'medium',
    genre: '',
    characters: '',
    mood: 'calm'
  });

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const imageConfig = {
        enabled: true,
        pagesPerImage: 4
      };

      const storyData = await generateStory(profile, storyParams, imageConfig);
      onGenerate({ profile, storyData, storyParams });
    } catch (err) {
      setError(err.message || 'Failed to generate story');
      console.error('Story generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <div className="flex justify-between items-center mb-8">
        <button
          onClick={onEditProfile}
          className="flex items-center gap-2 text-purple-300 hover:text-purple-200 transition-colors text-sm"
        >
          <ChevronLeft size={18} />
          Edit {profile.childName}'s Profile
        </button>
        <span className="px-4 py-2 bg-purple-600 text-white rounded-full text-sm font-medium">
          {profile.childName}, age {profile.age}
        </span>
      </div>

      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-purple-300 mb-3">
          🌙 What Should We Read Tonight?
        </h1>
        <p className="text-xl text-purple-200">
          Tell us what {profile.childName} wants to explore today
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-500/20 border border-red-500 rounded-xl text-red-200 text-center">
          {error}
        </div>
      )}

      <div className="bg-white/5 backdrop-blur-md rounded-3xl p-8 border border-purple-800/30">
        <div className="space-y-6">
          <div>
            <label className="block text-lg text-purple-200 mb-3 font-medium">
              Story Length
            </label>
            <div className="space-y-3">
              {[
                { value: 'short', label: 'Quick Story', time: '~5 min' },
                { value: 'medium', label: 'Perfect Length', time: '~10 min' },
                { value: 'long', label: 'Long Adventure', time: '~15 min' }
              ].map((option) => (
                <label key={option.value} className="flex items-center gap-3 cursor-pointer group">
                  <input
                    type="radio"
                    name="length"
                    value={option.value}
                    checked={storyParams.length === option.value}
                    onChange={(e) => setStoryParams({...storyParams, length: e.target.value})}
                    className="w-5 h-5 border-2 border-purple-600 bg-white/5 checked:bg-purple-600 focus:ring-2 focus:ring-purple-500/20 cursor-pointer"
                  />
                  <div className="flex items-center gap-2">
                    <span className="text-base text-purple-100 group-hover:text-white">
                      {option.label}
                    </span>
                    <span className="px-2 py-0.5 bg-purple-700 text-purple-200 rounded text-xs">
                      {option.time}
                    </span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Tonight's Mood
            </label>
            <select
              value={storyParams.mood}
              onChange={(e) => setStoryParams({...storyParams, mood: e.target.value})}
              className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white cursor-pointer"
            >
              <option value="calm" style={{background: '#9273dcff', color: 'white'}}>Calm & Peaceful</option>
              <option value="playful" style={{background: '#9273dcff', color: 'white'}}>Playful & Fun</option>
              <option value="curious" style={{background: '#9273dcff', color: 'white'}}>Curious & Wondering</option>
              <option value="brave" style={{background: '#9273dcff', color: 'white'}}>Brave & Confident</option>
            </select>
          </div>

          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Genre/Theme
            </label>
            <input
              type="text"
              placeholder="Space adventure, forest friends, underwater..."
              value={storyParams.genre}
              onChange={(e) => setStoryParams({...storyParams, genre: e.target.value})}
              className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
            />
            <p className="text-sm text-purple-300 mt-2">Or leave blank for a surprise!</p>
          </div>

          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Special Characters
            </label>
            <input
              type="text"
              placeholder="A friendly dragon, a curious robot..."
              value={storyParams.characters}
              onChange={(e) => setStoryParams({...storyParams, characters: e.target.value})}
              className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full py-4 px-6 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 text-white text-xl font-semibold rounded-xl transition-colors mt-6 flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Weaving your story...
              </>
            ) : (
              <>
                <Sparkles size={20} />
                Generate Story
              </>
            )}
          </button>
        </div>
      </div>

      {generating && (
        <div className="text-center mt-8">
          <div className="inline-block w-12 h-12 border-4 border-purple-300/30 border-t-purple-300 rounded-full animate-spin mb-4"></div>
          <p className="text-lg text-purple-200">
            Creating a magical story just for {profile.childName}...
          </p>
        </div>
      )}
    </div>
  );
};

// Story Display Screen (from current App.jsx - with audio integration)
const StoryDisplay = ({ story, profile, onBack, onNewStory, storyParams }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [loadingAudio, setLoadingAudio] = useState(false);
  const audioRef = useRef(null);

  // Parse story into pages
  const pages = React.useMemo(() => {
    const storyText = story.story || '';
    const emotionText = story.emotionTaggedStory || storyText;

    const paragraphs = storyText.split('\n\n').filter(p => p.trim());
    const emotionParagraphs = emotionText.split('\n\n').filter(p => p.trim());

    return paragraphs.map((para, index) => {
      const pageImages = story.images || [];
      const imageIndex = Math.floor(index / (storyParams?.pagesPerImage || 4));
      const currentImage = pageImages[imageIndex];

      const fallbackEmoji = '📖';

      return {
        text: para.trim(),
        emotionText: emotionParagraphs[index]?.trim() || para.trim(),
        image: currentImage || fallbackEmoji
      };
    });
  }, [story, storyParams]);

  // Generate and play audio when page changes
  useEffect(() => {
    const playAudioForPage = async () => {
      if (pages.length === 0) return;

      // Stop current audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      setLoadingAudio(true);
      setIsPlaying(false);

      try {
        const textForTTS = pages[currentPage].emotionText || pages[currentPage].text;
        const mood = storyParams?.mood || 'calm';
        const theme = storyParams?.genre || '';

        const { audioUrl: newAudioUrl } = await generateAudio(textForTTS, mood, theme);
        setAudioUrl(newAudioUrl);

        // Create new audio element and auto-play
        const audio = new Audio(newAudioUrl);
        audioRef.current = audio;

        audio.onended = () => setIsPlaying(false);
        audio.onerror = () => {
          console.error('Audio playback error');
          setIsPlaying(false);
        };

        await audio.play();
        setIsPlaying(true);
      } catch (error) {
        console.error('Failed to generate or play audio:', error);
      } finally {
        setLoadingAudio(false);
      }
    };

    playAudioForPage();

    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, [currentPage, pages, storyParams]);

  const togglePlayPause = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const nextPage = () => {
    if (currentPage < pages.length - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  if (pages.length === 0) {
    return <div className="text-center text-purple-300">No story content available</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-purple-300 hover:text-purple-200 transition-colors"
        >
          <ChevronLeft size={20} />
          New Story
        </button>
        <span className="px-4 py-2 bg-purple-600 text-white rounded-full text-sm font-medium">
          Page {currentPage + 1} of {pages.length}
        </span>
      </div>

      {/* Story Display */}
      <div className="bg-white/5 backdrop-blur-md rounded-3xl p-12 border border-purple-800/30 min-h-[500px] flex flex-col justify-center items-center relative mb-6">
        <div className="text-center space-y-8">
          {/* Image/Emoji Display */}
          <div className="text-8xl mb-8">
            {typeof pages[currentPage].image === 'string' && pages[currentPage].image.length < 10
              ? pages[currentPage].image
              : pages[currentPage].image?.image_data
                ? <img src={`data:image/png;base64,${pages[currentPage].image.image_data}`} alt="Story illustration" className="max-w-md mx-auto rounded-xl" />
                : pages[currentPage].image?.url
                  ? <img src={pages[currentPage].image.url} alt="Story illustration" className="max-w-md mx-auto rounded-xl" />
                  : '📖'
            }
          </div>

          {/* Story Text */}
          <p className="text-2xl leading-relaxed text-purple-100 max-w-3xl mx-auto px-8">
            {pages[currentPage].text}
          </p>
        </div>

        {/* Navigation Arrows */}
        <div className="absolute bottom-6 left-6 right-6 flex justify-between">
          <button
            onClick={prevPage}
            disabled={currentPage === 0}
            className="p-3 rounded-xl bg-purple-600/50 hover:bg-purple-600 disabled:bg-purple-900/30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft size={32} />
          </button>
          <button
            onClick={nextPage}
            disabled={currentPage === pages.length - 1}
            className="p-3 rounded-xl bg-purple-600/50 hover:bg-purple-600 disabled:bg-purple-900/30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight size={32} />
          </button>
        </div>
      </div>

      {/* Audio Controls */}
      <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-purple-800/30 mb-4">
        <div className="flex justify-center">
          <button
            onClick={togglePlayPause}
            disabled={loadingAudio}
            className="flex items-center gap-2 px-8 py-3 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 text-white text-lg font-semibold rounded-xl transition-colors"
          >
            {loadingAudio ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Loading...
              </>
            ) : isPlaying ? (
              <>
                <Pause size={20} />
                Pause Audio
              </>
            ) : (
              <>
                <Play size={20} />
                Play Audio
              </>
            )}
          </button>
        </div>
      </div>

      {/* Progress Indicator */}
      <div className="w-full h-2 bg-purple-900 rounded-full overflow-hidden mb-6">
        <div
          className="h-full bg-gradient-to-r from-purple-600 to-blue-600 transition-all duration-300"
          style={{ width: `${((currentPage + 1) / pages.length) * 100}%` }}
        ></div>
      </div>

      {currentPage === pages.length - 1 && (
        <button
          onClick={onNewStory}
          className="w-full py-4 px-6 bg-purple-600 hover:bg-purple-500 text-white text-xl font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
        >
          <Sparkles size={20} />
          Create Another Story
        </button>
      )}
    </div>
  );
};

// Main App Component
export default function StoryWeaveApp() {
  const [darkMode, setDarkMode] = useState(true);
  const [screen, setScreen] = useState('auth');
  const [profile, setProfile] = useState(null);
  const [story, setStory] = useState(null);
  const [storyParams, setStoryParams] = useState(null);
  const [user, setUser] = useState(null);

  // Check if user is already logged in
  useEffect(() => {
    const savedUser = localStorage.getItem('storyweave_user');

    if (savedUser) {
      const userData = JSON.parse(savedUser);
      setUser(userData);

      // If user has profiles, load the first one
      if (userData.profiles && userData.profiles.length > 0) {
        const firstProfile = userData.profiles[0];
        setProfile({
          childName: firstProfile.child_name,
          age: firstProfile.age,
          conditions: firstProfile.cognitive_profile,
          preferences: {
            pacing: 'medium',
            favoriteThemes: firstProfile.interests?.join(', ') || ''
          },
          child_id: firstProfile.child_id
        });
        setScreen('generate');
      } else {
        // No profile yet, go to profile setup
        setScreen('profile');
      }
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);

    // Check if user has profiles
    if (userData.profiles && userData.profiles.length > 0) {
      const firstProfile = userData.profiles[0];
      setProfile({
        childName: firstProfile.child_name,
        age: firstProfile.age,
        conditions: firstProfile.cognitive_profile,
        preferences: {
          pacing: 'medium',
          favoriteThemes: firstProfile.interests?.join(', ') || ''
        },
        child_id: firstProfile.child_id
      });
      setScreen('generate');
    } else {
      // New user - create profile first
      setScreen('profile');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('storyweave_user');
    setUser(null);
    setProfile(null);
    setStory(null);
    setScreen('auth');
  };

  const handleProfileComplete = (profileData) => {
    setProfile(profileData);
    setScreen('generate');
  };

  const handleStoryGenerate = (data) => {
    setStory(data.storyData);
    setStoryParams(data.storyParams);
    setScreen('display');
  };

  const handleEditProfile = () => {
    setScreen('profile');
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
        {/* Top Right Controls */}
        <div className="fixed top-4 right-4 flex items-center gap-3 z-50">
          {user && (
            <div className="flex items-center gap-3">
              <span className="text-purple-300 text-sm hidden sm:block">
                {user.name}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-purple-600/50 hover:bg-purple-600 rounded-xl transition-colors text-sm font-medium"
              >
                Logout
              </button>
            </div>
          )}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-3 bg-purple-600/50 hover:bg-purple-600 rounded-xl transition-colors"
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>

        {/* Header */}
        {screen !== 'auth' && (
          <div className="text-center pt-8 pb-4">
            <h1 className="text-6xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent mb-2">
              StoryWeave
            </h1>
            <p className="text-purple-300 text-base">
              AI Bedtime Stories for Every Child
            </p>
          </div>
        )}

        {/* Main Content */}
        {screen === 'auth' && (
          <AuthScreen onLogin={handleLogin} />
        )}

        {screen === 'profile' && (
          <ProfileSetup
            onComplete={handleProfileComplete}
            user={user}
            existingProfile={profile}
          />
        )}

        {screen === 'generate' && profile && (
          <StoryGenerator
            profile={profile}
            onGenerate={handleStoryGenerate}
            onEditProfile={handleEditProfile}
            user={user}
          />
        )}

        {screen === 'display' && story && (
          <StoryDisplay
            story={story}
            profile={profile}
            storyParams={storyParams}
            onBack={() => setScreen('generate')}
            onNewStory={() => setScreen('generate')}
          />
        )}

        {/* Footer */}
        {screen !== 'auth' && (
          <div className="text-center py-8 text-purple-400 text-sm">
            <p>DubHacks 2025 • Made with 💜 for every child</p>
          </div>
        )}
      </div>
    </div>
  );
}
