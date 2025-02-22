import { useBasic, useQuery } from '@basictech/react'
import { useState, useEffect, useRef } from 'react'
import { Bookmark, Share2 } from 'lucide-react'
import './App.css'

function App() {
  const { db } = useBasic()
  const [currentPrompt, setCurrentPrompt] = useState('')
  const videoRef = useRef<HTMLVideoElement>(null)
  
  const moodSuggestions = [
    'sunset vibes', 'city dreams', 'peaceful evening', 'golden hour', 'urban calm'
  ]

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play()
    }
  }, [])

  const handlePromptClick = (mood: string) => {
    setCurrentPrompt(mood)
  }

  return (
    <div className="fixed inset-0 overflow-hidden bg-black">
      {/* Video Background */}
      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-cover"
        loop
        muted
        playsInline
        autoPlay
        src="/background.mp4"
      >
        Your browser does not support the video tag.
      </video>

      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/70" />

      {/* Content */}
      <div className="relative z-10 h-screen flex flex-col items-center justify-center px-6">
        <div className="w-full max-w-2xl mx-auto text-center">
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
                     transition-all mb-12"
          />

          {/* Mood Suggestions */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-12">
            {moodSuggestions.map(mood => (
              <button
                key={mood}
                onClick={() => handlePromptClick(mood)}
                className="group relative overflow-hidden px-6 py-3 rounded-lg cursor-pointer
                         border border-white/20 bg-white/5 backdrop-blur-sm
                         hover:border-white/40 hover:bg-white/10 transition-all"
              >
                {/* Shiny effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent
                              translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                
                {/* Button text */}
                <span className="relative z-10 text-white/80 group-hover:text-white transition-colors">
                  {mood}
                </span>
              </button>
            ))}
          </div>

          {/* Minimal Controls */}
          <div className="flex justify-center gap-6">
            <button className="p-2 text-white/60 hover:text-white/80 transition-all">
              <Bookmark className="w-5 h-5" strokeWidth={1.5} />
            </button>
            <button className="p-2 text-white/60 hover:text-white/80 transition-all">
              <Share2 className="w-5 h-5" strokeWidth={1.5} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App