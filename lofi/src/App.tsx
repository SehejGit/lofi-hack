import { useBasic, useQuery } from '@basictech/react'
import { useState } from 'react'
import { Music, Play, Pause, RefreshCw, Save } from 'lucide-react'
import './App.css'

// Types for our data structures
interface Theme {
  id: string
  name: string
  description: string
  backgroundUrl: string
  musicParams: {
    tempo: number
    mood: string
    instruments: string[]
  }
}

interface SavedTheme {
  id: string
  name: string
  prompt: string
  createdAt: number
}

function App() {
  const { db } = useBasic()
  const [currentPrompt, setCurrentPrompt] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentTheme, setCurrentTheme] = useState<Theme | null>(null)
  
  // Fetch saved themes from Basic Tech database
  const savedThemes = useQuery(() => db.collection('saved_themes').getAll())

  // Suggested prompts for inspiration
  const suggestedPrompts = [
    'Rainy night in Tokyo',
    'Cozy coffee shop ambiance',
    'Beach sunset meditation',
    'Late night coding session',
    'Forest meditation retreat'
  ]

  const generateTheme = async (prompt: string) => {
    setIsGenerating(true)
    try {
      // Here you would integrate with your music generation API
      // For now, we'll simulate the response
      const theme: Theme = {
        id: Date.now().toString(),
        name: prompt,
        description: `Generated theme based on: ${prompt}`,
        backgroundUrl: '/api/placeholder/1920/1080', // Replace with actual generated image
        musicParams: {
          tempo: 70 + Math.random() * 20,
          mood: prompt.toLowerCase().includes('night') ? 'calm' : 'upbeat',
          instruments: ['piano', 'synth', 'drums']
        }
      }
      setCurrentTheme(theme)
      setIsPlaying(true)
    } catch (error) {
      console.error('Error generating theme:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const saveTheme = async () => {
    if (!currentTheme) return
    await db.collection('saved_themes').add({
      name: currentTheme.name,
      prompt: currentPrompt,
      createdAt: Date.now()
    })
  }

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  return (
    <div className="min-h-screen relative">
      {/* Background with overlay */}
      <div 
        className="fixed inset-0 bg-cover bg-center transition-all duration-1000"
        style={{ 
          backgroundImage: currentTheme 
            ? `url(${currentTheme.backgroundUrl})` 
            : 'linear-gradient(to bottom right, #1e293b, #0f172a)'
        }}
      >
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <div className="flex items-center gap-3 mb-8">
          <Music className="w-8 h-8 text-purple-400" />
          <h1 className="text-4xl font-bold text-white">Lofi Vibe Generator</h1>
        </div>

        {/* Prompt input */}
        <div className="max-w-2xl mx-auto mb-8">
          <input
            type="text"
            value={currentPrompt}
            onChange={(e) => setCurrentPrompt(e.target.value)}
            placeholder="Describe your desired vibe..."
            className="w-full px-4 py-3 bg-white/10 rounded-lg border border-purple-400/30 
                     text-white placeholder-purple-200/50 focus:outline-none focus:border-purple-400"
          />
          
          {/* Suggestion chips */}
          <div className="flex flex-wrap gap-2 mt-4">
            {suggestedPrompts.map(prompt => (
              <button
                key={prompt}
                onClick={() => setCurrentPrompt(prompt)}
                className="px-3 py-1 rounded-full bg-purple-400/20 text-purple-200 
                         hover:bg-purple-400/30 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Controls */}
        <div className="max-w-2xl mx-auto flex gap-4 justify-center mb-8">
          <button
            onClick={() => generateTheme(currentPrompt)}
            disabled={isGenerating || !currentPrompt}
            className="px-6 py-3 rounded-lg bg-purple-500 text-white flex items-center gap-2
                     hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Generating...
              </>
            ) : (
              'Generate'
            )}
          </button>

          {currentTheme && (
            <>
              <button
                onClick={togglePlayPause}
                className="px-6 py-3 rounded-lg bg-white/10 text-white flex items-center gap-2
                         hover:bg-white/20"
              >
                {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                {isPlaying ? 'Pause' : 'Play'}
              </button>

              <button
                onClick={saveTheme}
                className="px-6 py-3 rounded-lg bg-white/10 text-white flex items-center gap-2
                         hover:bg-white/20"
              >
                <Save className="w-5 h-5" />
                Save
              </button>
            </>
          )}
        </div>

        {/* Saved themes */}
        {savedThemes && savedThemes.length > 0 && (
          <div className="max-w-4xl mx-auto mt-16">
            <h2 className="text-2xl font-semibold text-white mb-4">Saved Themes</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {savedThemes.map((theme: SavedTheme) => (
                <div
                  key={theme.id}
                  onClick={() => {
                    setCurrentPrompt(theme.prompt)
                    generateTheme(theme.prompt)
                  }}
                  className="p-4 rounded-lg bg-white/10 backdrop-blur-md cursor-pointer
                           hover:bg-white/20 transition-colors"
                >
                  <h3 className="text-lg font-medium text-white">{theme.name}</h3>
                  <p className="text-sm text-purple-200/70">
                    {new Date(theme.createdAt).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App