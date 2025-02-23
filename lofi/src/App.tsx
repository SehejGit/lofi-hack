import { useBasic, useQuery } from '@basictech/react'
import { useState, useEffect, useRef } from 'react'

import './App.css'

function App() {
  const { db } = useBasic()
  const [currentPrompt, setCurrentPrompt] = useState('')
  const [backgroundImage, setBackgroundImage] = useState<string | null>(null)
  const [isImageLoading, setIsImageLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(true)
  const [isMuted, setIsMuted] = useState(false)
  const [isGeneratingMusic, setIsGeneratingMusic] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  const moodSuggestions = [
    'sunset vibes', 'city dreams', 'peaceful evening'
  ]

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play()
    }
  }, [])

  // Function to generate image
  const generateImage = async (prompt: string) => {
    try {
      setIsImageLoading(true);
      const response = await fetch('http://localhost:8000/api/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate image');
      }

      const imageBlob = await response.blob();
      const imageUrl = URL.createObjectURL(imageBlob);
      setBackgroundImage(imageUrl);
    } catch (error) {
      console.error('Error generating image:', error);
      setBackgroundImage(null);
    } finally {
      setIsImageLoading(false);
    }
  };

  // Function to generate music
  // Function to generate music
// Function to generate music
const generateMusic = async (prompt: string) => {
  try {
    setIsGeneratingMusic(true);
    const response = await fetch('http://localhost:8000/api/generate-music', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate music');
    }

    const trackData = await response.json();
    console.log('Track Data:', trackData);

    const audioUrl = `http://localhost:8000${trackData.audio_url}`;
    console.log('Attempting to play audio from:', audioUrl);

    if (audioRef.current) {
      try {
        // First try to fetch the audio to ensure it's accessible
        const audioResponse = await fetch(audioUrl);
        if (!audioResponse.ok) {
          throw new Error(`Failed to fetch audio: ${audioResponse.status}`);
        }

        // Set audio element properties
        audioRef.current.src = audioUrl;
        audioRef.current.type = 'audio/mpeg';
        
        // Wait for the audio to be loaded
        await new Promise((resolve, reject) => {
          if (!audioRef.current) return reject('No audio element');
          
          audioRef.current.oncanplaythrough = resolve;
          audioRef.current.onerror = () => reject('Audio loading failed');
          
          // Set a timeout in case loading takes too long
          setTimeout(() => reject('Audio loading timeout'), 5000);
        });

        await audioRef.current.play();
        setIsPlaying(true);
        console.log('Audio playing successfully');
      } catch (error) {
        console.error('Audio playback error:', error);
        // Log the actual audio element error if it exists
        if (audioRef.current?.error) {
          console.error('Audio element error:', audioRef.current.error);
        }
      }
    }
  } catch (error) {
    console.error('Error in generateMusic:', error);
  } finally {
    setIsGeneratingMusic(false);
  }
};

  // Debounced prompt change handler
  useEffect(() => {
    if (currentPrompt.trim()) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        generateImage(currentPrompt);
        generateMusic(currentPrompt);
      }, 2000);
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [currentPrompt]);

  const handlePromptClick = (mood: string) => {
    setCurrentPrompt(mood)
  }

  // const togglePlay = () => {
  //   if (audioRef.current) {
  //     if (isPlaying) {
  //       audioRef.current.pause();
  //     } else {
  //       audioRef.current.play();
  //     }
  //     setIsPlaying(!isPlaying);
  //   }
  // };

  // const toggleMute = () => {
  //   if (audioRef.current) {
  //     audioRef.current.muted = !audioRef.current.muted;
  //     setIsMuted(!isMuted);
  //   }
  // };

  return (
    <div className="fixed inset-0 overflow-hidden bg-black">
      {/* Background Container */}
      <div className="absolute inset-0 w-full h-full">
        {/* Video Background */}
        <video
          ref={videoRef}
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${
            backgroundImage ? 'hidden' : 'block'
          }`}
          loop
          muted
          playsInline
          autoPlay
          src="/background.mp4"
        >
          Your browser does not support the video tag.
        </video>

        {/* Generated Image Background */}
        {backgroundImage && (
          <div
            className="absolute inset-0 w-full h-full bg-cover bg-center transition-opacity duration-1000"
            style={{
              backgroundImage: `url(${backgroundImage})`,
              opacity: isImageLoading ? 0 : 1,
            }}
          />
        )}

        {/* Overlay to darken background slightly */}
        <div className="absolute inset-0 bg-black/20" />
      </div>

      {/* Audio Element */}
      <audio ref={audioRef} loop />

      {/* Content */}
      <div className="relative z-10 h-screen flex flex-col items-center justify-center px-6">
        <div className="w-full max-w-2xl mx-auto text-center">
          {/* Title */}
          <h1 className="text-8xl font-light text-white/90 mb-16">
            lofi mood
          </h1>

          {/* Input */}
          <input
            type="text"
            value={currentPrompt}
            onChange={(e) => setCurrentPrompt(e.target.value)}
            placeholder="how are you feeling..."
            className="w-full bg-transparent border-b border-white/20 pb-2 text-2xl
                     text-white/60 placeholder-white/60 focus:outline-none focus:border-white/40
                     transition-all mb-16"
          />

          {/* Music Controls */}
          {audioUrl && (
            <div className="flex items-center justify-center gap-4 mb-8">
              {/* <button
                onClick={togglePlay}
                className="p-3 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
              >
                {isPlaying ? (
                  <Pause className="w-6 h-6 text-white" />
                ) : (
                  <Play className="w-6 h-6 text-white" />
                )}
              </button>
              <button
                onClick={toggleMute}
                className="p-3 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
              >
                {isMuted ? (
                  <VolumeX className="w-6 h-6 text-white" />
                ) : (
                  <Volume2 className="w-6 h-6 text-white" />
                )}
              </button> */}
              {isGeneratingMusic && (
                <span className="text-white/60">Generating music...</span>
              )}
            </div>
          )}

          {/* Mood Suggestions */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-12">
            {moodSuggestions.map(mood => (
              <div
                key={mood}
                className="group relative overflow-hidden rounded-xl"
              >
                <button
                  onClick={() => handlePromptClick(mood)}
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    backdropFilter: 'blur(8px)'
                  }}
                  className="w-full px-6 py-3 rounded-xl cursor-pointer
                           hover:bg-white/10 transition-all duration-300
                           border border-white/10 hover:border-white/20"
                >
                  {/* Shiny effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent
                                translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                  
                  {/* Button text */}
                  <span className="relative z-10 text-white/80 group-hover:text-white transition-colors">
                    {mood}
                  </span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App