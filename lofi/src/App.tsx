import { useBasic, useQuery } from '@basictech/react'
import { useState, useEffect, useRef } from 'react'
import { Headphones, PlayCircle, PauseCircle, BookmarkPlus, Share2 } from 'lucide-react'
import './App.css'

function App() {
  const { db } = useBasic()
  const [currentPrompt, setCurrentPrompt] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
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

  const generateMusic = async () => {
    setIsGenerating(true)
    await new Promise(resolve => setTimeout(resolve, 1500))
    setIsGenerating(false)
    setIsPlaying(true)
    if (videoRef.current) {
      videoRef.current.play()
    }
  }

  const saveTheme = async () => {
    await db.collection('saved_themes').add({
      prompt: currentPrompt,
      createdAt: Date.now()
    })
  }

  return (
    <div className="min-h-screen relative overflow-hidden font-sans">
      {/* Video Background */}
      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-cover"
        loop
        muted
        playsInline
        src="../public/background.mp4"
      >
        Your browser does not support the video tag.
      </video>

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-pink-900/30 via-purple-900/40 to-black/50 backdrop-blur-[1px]" />

      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6">
        <div className="w-full max-w-2xl mx-auto text-center">
          {/* Title */}
          <div className="flex items-center justify-center gap-3 mb-12">
            <Headphones className="w-12 h-12 text-pink-300" strokeWidth={1.5} />
            <h1 className="text-6xl font-light text-white tracking-wide">lofi mood</h1>
          </div>

          {/* Main Input */}
          <div className="mb-8">
            <input
              type="text"
              value={currentPrompt}
              onChange={(e) => setCurrentPrompt(e.target.value)}
              placeholder="how are you feeling..."
              className="w-full px-8 py-4 text-xl bg-white/10 rounded-full 
                       border border-pink-300/20 text-white placeholder-pink-200/50 
                       focus:outline-none focus:border-pink-300/40 transition-all
                       backdrop-blur-sm"
            />
          </div>

          {/* Mood Suggestions */}
          <div className="flex flex-wrap justify-center gap-3 mb-12">
            {moodSuggestions.map(mood => (
              <button
                key={mood}
                onClick={() => setCurrentPrompt(mood)}
                className="px-5 py-2 rounded-full bg-white/5 text-pink-200 
                         border border-pink-300/20 hover:bg-white/10 
                         hover:border-pink-300/40 transition-all duration-300"
              >
                {mood}
              </button>
            ))}
          </div>

          {/* Controls */}
          <div className="flex justify-center items-center gap-6">
            {/* Main Play Button */}
            <button
              onClick={isPlaying ? togglePlayPause : generateMusic}
              disabled={isGenerating}
              className="group flex items-center justify-center w-16 h-16 rounded-full 
                       bg-gradient-to-r from-pink-400/80 to-purple-400/80 
                       hover:from-pink-400 hover:to-purple-400
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-all duration-300"
            >
              {isGenerating ? (
                <div className="w-6 h-6 border-2 border-white border-t-transparent 
                             rounded-full animate-spin" />
              ) : isPlaying ? (
                <PauseCircle className="w-8 h-8 text-white" strokeWidth={1.5} />
              ) : (
                <PlayCircle className="w-8 h-8 text-white" strokeWidth={1.5} />
              )}
            </button>

            {/* Save Button */}
            <button
              onClick={saveTheme}
              className="p-3 rounded-full bg-white/10 hover:bg-white/20 
                       transition-all duration-300"
            >
              <BookmarkPlus className="w-6 h-6 text-pink-200" strokeWidth={1.5} />
            </button>

            {/* Share Button */}
            <button
              className="p-3 rounded-full bg-white/10 hover:bg-white/20 
                       transition-all duration-300"
            >
              <Share2 className="w-6 h-6 text-pink-200" strokeWidth={1.5} />
            </button>
          </div>
        </div>

        {/* Current Status - only show when playing */}
        {isPlaying && (
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 
                         px-6 py-3 rounded-full bg-black/30 backdrop-blur-md
                         border border-pink-300/20 text-pink-200 text-sm">
            Now playing: {currentPrompt || 'Sunset lofi beats'}
          </div>
        )}
      </div>
    </div>
  )
}

export default App