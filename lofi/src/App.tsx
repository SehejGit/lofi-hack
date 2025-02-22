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