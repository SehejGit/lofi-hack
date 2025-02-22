import { useBasic, useQuery } from '@basictech/react'
import { useState, useEffect, useRef } from 'react'
import { PlayCircle, PauseCircle, Bookmark, Share2 } from 'lucide-react'
import './App.css'

function App() {
  const { db } = useBasic()
  const [currentPrompt, setCurrentPrompt] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  
  const moodSuggestions = [
    'sunset vibes', 'city dreams', 'peaceful evening', 'golden hour', 'urban calm'
  ]

  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
    }
    setIsPlaying(!isPlaying)
  }

  const handlePromptClick = (mood: string) => {
    setCurrentPrompt(mood)
    if (!isPlaying && videoRef.current) {
      videoRef.current.play()
      setIsPlaying(true)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-black">
      {/* Video Background */}
      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-cover opacity-90"
        loop
        muted
        playsInline
        src="/background.mp4"
      >
        Your browser does not support the video tag.
      </video>

      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/70" />

      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col justify-end pb-24 px-6">
        <div className="w-full max-w-4xl mx-auto">
          {/* Title */}
          <h1 className="text-8xl font-light text-white/90 mb-12">
            lofi mood
          </h1>

          {/* Input */}
          <input
            type="text"
            value={currentPrompt}
            onChange={(e) => setCurrentPrompt(e.target.value)}
            placeholder="how are you feeling..."
            className="w-full bg-transparent border-b border-white/20 pb-2 text-xl
                     text-white placeholder-white/50 focus:outline-none focus:border-white/40
                     transition-all mb-8"
          />

          {/* Mood Suggestions */}
          <div className="flex flex-wrap gap-4 mb-8">
            {moodSuggestions.map(mood => (
              <button
                key={mood}
                onClick={() => handlePromptClick(mood)}
                className="text-white/70 hover:text-white transition-colors"
              >
                {mood}
              </button>
            ))}
          </div>

          {/* Controls */}
          <div className="flex items-center gap-6">
            <button
              onClick={togglePlayPause}
              className="text-white/90 hover:text-white transition-colors"
            >
              {isPlaying ? (
                <PauseCircle className="w-12 h-12" strokeWidth={1} />
              ) : (
                <PlayCircle className="w-12 h-12" strokeWidth={1} />
              )}
            </button>
            
            <button className="text-white/60 hover:text-white/80 transition-colors">
              <Bookmark className="w-6 h-6" strokeWidth={1} />
            </button>
            
            <button className="text-white/60 hover:text-white/80 transition-colors">
              <Share2 className="w-6 h-6" strokeWidth={1} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App