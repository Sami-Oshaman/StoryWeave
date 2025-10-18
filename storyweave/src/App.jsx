import React, { useState } from 'react';
import { Moon, Sun, Volume2, VolumeX, ChevronLeft, ChevronRight, Sparkles, Star } from 'lucide-react';

// Child Profile Screen
const ProfileSetup = ({ onComplete }) => {
  const [profile, setProfile] = useState({
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

  const handleSubmit = (e) => {
    e.preventDefault();
    onComplete(profile);
  };

  const toggleCondition = (condition) => {
    if (profile.conditions.includes(condition)) {
      setProfile({...profile, conditions: profile.conditions.filter(c => c !== condition)});
    } else {
      setProfile({...profile, conditions: [...profile.conditions, condition]});
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-purple-300 mb-3">
          ✨ Create Your Child's Profile
        </h1>
        <p className="text-xl text-purple-200">
          Help us personalize bedtime stories for your little one
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white/5 backdrop-blur-md rounded-3xl p-8 border border-purple-800/30">
        <div className="space-y-6">
          {/* Basic Info */}
          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Child's Name *
            </label>
            <input
              type="text"
              placeholder="Emma"
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
              min="2"
              max="12"
              value={profile.age}
              onChange={(e) => setProfile({...profile, age: e.target.value})}
              className="w-full px-4 py-3 text-lg bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400"
              required
            />
            <p className="text-sm text-purple-300 mt-2">Ages 2-12 supported</p>
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
              {['ADHD', 'Autism Spectrum', 'Sensory Processing Disorder', 'Visual Impairment', 'Dyslexia'].map((condition) => (
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
            <label className="block text-lg text-purple-200 mb-3 font-medium">
              Sensory Complexity
            </label>
            <p className="text-sm text-purple-300 mb-4">
              Lower = simpler descriptions, Higher = richer details
            </p>
            <input
              type="range"
              min="0"
              max="100"
              step="10"
              value={profile.preferences.sensoryLevel}
              onChange={(e) => setProfile({...profile, preferences: {...profile.preferences, sensoryLevel: parseInt(e.target.value)}})}
              className="w-full h-2 bg-purple-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-purple-300">Minimal</span>
              <span className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm font-medium">
                {profile.preferences.sensoryLevel}
              </span>
              <span className="text-sm text-purple-300">Rich</span>
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

          <div>
            <label className="block text-lg text-purple-200 mb-2 font-medium">
              Topics to Avoid
            </label>
            <textarea
              placeholder="Scary things, loud noises, separation..."
              value={profile.preferences.avoidThemes}
              onChange={(e) => setProfile({...profile, preferences: {...profile.preferences, avoidThemes: e.target.value}})}
              className="w-full px-4 py-3 text-base bg-white/5 border-2 border-purple-700 rounded-xl focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 text-white placeholder-purple-400 resize-none"
              rows={2}
            />
          </div>

          <button
            type="submit"
            disabled={!profile.childName || !profile.age}
            className="w-full py-4 px-6 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 disabled:cursor-not-allowed text-white text-xl font-semibold rounded-xl transition-colors mt-6 focus:outline-none focus:ring-4 focus:ring-purple-500/50"
          >
            Create Profile & Continue
          </button>
        </div>
      </form>
    </div>
  );
};

// Story Generation Screen
const StoryGenerator = ({ profile, onGenerate, onBack }) => {
  const [generating, setGenerating] = useState(false);
  const [storyParams, setStoryParams] = useState({
    length: 'medium',
    tonightsPacing: profile.preferences.pacing,
    genre: '',
    characters: '',
    mood: 'calm'
  });

  const handleGenerate = async () => {
    setGenerating(true);
    setTimeout(() => {
      onGenerate({ profile, storyParams });
      setGenerating(false);
    }, 2000);
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <div className="flex justify-between items-center mb-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-purple-300 hover:text-purple-200 transition-colors"
        >
          <ChevronLeft size={20} />
          Back to Profile
        </button>
        <span className="px-4 py-2 bg-purple-600 text-white rounded-full text-sm font-medium">
          {profile.childName}'s Story
        </span>
      </div>

      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-purple-300 mb-3">
          🌙 Tonight's Story
        </h1>
        <p className="text-xl text-purple-200">
          What adventure shall we dream about?
        </p>
      </div>

      <div className="bg-white/5 backdrop-blur-md rounded-3xl p-8 border border-purple-800/30">
        <div className="space-y-6">
          <div>
            <label className="block text-lg text-purple-200 mb-3 font-medium">
              Story Length
            </label>
            <div className="space-y-3">
              {[
                { value: 'short', label: 'Quick Story', time: '~3 min' },
                { value: 'medium', label: 'Perfect Length', time: '~5 min' },
                { value: 'long', label: 'Long Adventure', time: '~8 min' }
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

          <div className="border-t border-purple-700/30 pt-6"></div>

          <div>
            <label className="block text-lg text-purple-200 mb-3 font-medium">
              Tonight's Pacing
            </label>
            <div className="space-y-3">
              {['slow', 'medium', 'fast'].map((pace) => (
                <label key={pace} className="flex items-center gap-3 cursor-pointer group">
                  <input
                    type="radio"
                    name="tonightsPacing"
                    value={pace}
                    checked={storyParams.tonightsPacing === pace}
                    onChange={(e) => setStoryParams({...storyParams, tonightsPacing: e.target.value})}
                    className="w-5 h-5 border-2 border-purple-600 bg-white/5 checked:bg-purple-600 focus:ring-2 focus:ring-purple-500/20 cursor-pointer"
                  />
                  <span className="text-base text-purple-100 group-hover:text-white capitalize">
                    {pace === 'slow' ? 'Slow & Gentle' : pace === 'medium' ? 'Balanced' : 'Quick & Engaging'}
                  </span>
                </label>
              ))}
            </div>
            <p className="text-sm text-purple-300 mt-2">
              Default: {profile.preferences.pacing}
            </p>
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full py-4 px-6 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 text-white text-xl font-semibold rounded-xl transition-colors mt-6 focus:outline-none focus:ring-4 focus:ring-purple-500/50 flex items-center justify-center gap-2"
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
          <div className="w-full max-w-md mx-auto mt-4 h-2 bg-purple-900 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-purple-600 to-blue-600 animate-pulse"></div>
          </div>
        </div>
      )}
    </div>
  );
};

// Story Display Screen
const StoryDisplay = ({ story, profile, onBack, onNewStory }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);

  const pages = [
    {
      text: "Once upon a time, in a peaceful forest where the moonlight danced through the leaves, there lived a little fox named Luna.",
      image: "🦊🌙"
    },
    {
      text: "Luna loved to explore, but tonight she felt extra sleepy. The stars twinkled softly above, each one saying 'goodnight' in its own special way.",
      image: "⭐✨"
    },
    {
      text: "As Luna curled up in her cozy den, she heard the gentle hoot of her friend, the wise old owl. 'Sweet dreams, little one,' hooted the owl.",
      image: "🦉💤"
    },
    {
      text: "Luna closed her eyes and drifted off to sleep, dreaming of tomorrow's adventures. The end.",
      image: "😴🌟"
    }
  ];

  const handlePlayPause = () => {
    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    } else {
      const utterance = new SpeechSynthesisUtterance(pages[currentPage].text);
      utterance.rate = playbackSpeed;
      utterance.onend = () => setIsPlaying(false);
      window.speechSynthesis.speak(utterance);
      setIsPlaying(true);
    }
  };

  const nextPage = () => {
    if (currentPage < pages.length - 1) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 0) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      setCurrentPage(currentPage - 1);
    }
  };

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
            {pages[currentPage].image}
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
            aria-label="Previous page"
          >
            <ChevronLeft size={32} />
          </button>
          <button
            onClick={nextPage}
            disabled={currentPage === pages.length - 1}
            className="p-3 rounded-xl bg-purple-600/50 hover:bg-purple-600 disabled:bg-purple-900/30 disabled:cursor-not-allowed transition-colors"
            aria-label="Next page"
          >
            <ChevronRight size={32} />
          </button>
        </div>
      </div>

      {/* Audio Controls */}
      <div className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-purple-800/30 mb-4">
        <div className="space-y-4">
          <div className="flex justify-center">
            <button
              onClick={handlePlayPause}
              className="flex items-center gap-2 px-8 py-3 bg-purple-600 hover:bg-purple-500 text-white text-lg font-semibold rounded-xl transition-colors"
            >
              {isPlaying ? <VolumeX size={20} /> : <Volume2 size={20} />}
              {isPlaying ? 'Stop Audio' : 'Play Audio'}
            </button>
          </div>

          <div>
            <label className="block text-sm text-purple-200 text-center mb-2">
              Narration Speed: {playbackSpeed}x
            </label>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.25"
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
              className="w-full h-2 bg-purple-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-xs text-purple-300 mt-1">
              <span>Slower</span>
              <span>Faster</span>
            </div>
          </div>
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
  const [screen, setScreen] = useState('profile');
  const [profile, setProfile] = useState(null);
  const [story, setStory] = useState(null);

  const handleProfileComplete = (profileData) => {
    setProfile(profileData);
    setScreen('generate');
  };

  const handleStoryGenerate = (storyData) => {
    setStory(storyData);
    setScreen('display');
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
        {/* Dark Mode Toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="fixed top-4 right-4 p-3 bg-purple-600/50 hover:bg-purple-600 rounded-xl transition-colors z-50"
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        {/* Header */}
        <div className="text-center pt-8 pb-4">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent mb-2">
            StoryWeave
          </h1>
          <p className="text-purple-300 text-base">
            AI Bedtime Stories for Every Child
          </p>
        </div>

        {/* Main Content */}
        {screen === 'profile' && (
          <ProfileSetup onComplete={handleProfileComplete} />
        )}
        
        {screen === 'generate' && profile && (
          <StoryGenerator
            profile={profile}
            onGenerate={handleStoryGenerate}
            onBack={() => setScreen('profile')}
          />
        )}
        
        {screen === 'display' && story && (
          <StoryDisplay
            story={story}
            profile={profile}
            onBack={() => setScreen('generate')}
            onNewStory={() => setScreen('generate')}
          />
        )}

        {/* Footer */}
        <div className="text-center py-8 text-purple-400 text-sm">
          <p>DubHacks 2025 • Made with 💜 for every child</p>
        </div>
      </div>
    </div>
  );
}